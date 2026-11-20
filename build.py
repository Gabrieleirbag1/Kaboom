"""Builds the compiled game (#21): Python, Qt and the game's files in one folder, nothing to install.

    python build.py             -> dist/<os>/Kaboom/ (the Steam build), and dist/macos/Kaboom.app on macOS
    python build.py --archive   -> also dist/Kaboom-<version>-<os>.zip (Windows) / .tar.gz (Linux)
                                   / Kaboom-<version>-macos-<arch>.tar.gz (macOS, the .app)
    python build.py --package   -> also the installer: Releases/kaboom_<version>_amd64.deb (Linux),
                                   Releases/kaboom-setup-<version>.exe (Windows, needs Inno Setup)
                                   or Releases/kaboom-<version>-macos-<arch>.dmg (macOS)
    python build.py --smoke     -> starts the built game off-screen and checks it runs without error

macOS: one build per processor (arm64 = Apple Silicon, x86_64 = Intel), made on a Mac of that kind:
Qt 5 has no universal2 package. The .app is signed ad hoc (no Apple Developer account needed).

Needs the packages of requirements-build.txt. The kaboom_install scripts make a venv and run this.
"""
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLIENT = str(ROOT / "Client")
sys.path.insert(0, CLIENT)
from client_version import VERSION  # noqa: E402

OS_NAME = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")
ARCH = {"amd64": "x86_64", "aarch64": "arm64"}.get(platform.machine().lower(), platform.machine().lower())
SMOKE_SECONDS = 20


def paths(os_name: str, arch: str) -> dict[str, Path]:
    """Where the build of one system goes.
    game: the folder PyInstaller makes; shipped: what is archived and installed (Kaboom.app on macOS);
    executable: what the smoke test starts; archive / installer: the files of a release."""
    dist = ROOT / "dist" / os_name
    game = dist / "Kaboom"
    releases = ROOT / "Releases"
    if os_name == "windows":
        return {"dist": dist, "game": game, "shipped": game, "executable": game / "Kaboom.exe",
                "archive": ROOT / "dist" / f"Kaboom-{VERSION}-windows.zip",
                "installer": releases / f"kaboom-setup-{VERSION}.exe"}
    if os_name == "macos":
        app = dist / "Kaboom.app"
        return {"dist": dist, "game": game, "shipped": app, "executable": app / "Contents" / "MacOS" / "Kaboom",
                "archive": ROOT / "dist" / f"Kaboom-{VERSION}-macos-{arch}.tar.gz",
                "installer": releases / f"kaboom-{VERSION}-macos-{arch}.dmg"}
    return {"dist": dist, "game": game, "shipped": game, "executable": game / "Kaboom",
            "archive": ROOT / "dist" / f"Kaboom-{VERSION}-linux.tar.gz",
            "installer": releases / f"kaboom_{VERSION}_amd64.deb"}


def config_dir(os_name: str, home: Path) -> Path:
    """The player's folder (settings, logs, session), as in Client/client_logs.py."""
    return {"windows": home / "Kaboom",  # %APPDATA%
            "macos": home / "Library" / "Application Support" / "Kaboom"}.get(os_name, home / ".config" / "kaboom")


PATHS = paths(OS_NAME, ARCH)
DIST, GAME_DIR, SHIPPED, EXECUTABLE = PATHS["dist"], PATHS["game"], PATHS["shipped"], PATHS["executable"]


def game_files() -> list[tuple[str, str]]:
    """(file, folder in the build) for every file the game reads. Only what the game uses: no dev
    scripts, no logs, no music or sounds that client_audio.py doesn't play."""
    files = []

    def add_folder(folder: str, keep=lambda name: True):
        for root, dirs, names in os.walk(os.path.join(CLIENT, folder)):
            dirs[:] = [d for d in dirs if not d.startswith((".", "__"))]
            for name in names:
                if not name.startswith(".") and keep(name):
                    files.append((os.path.join(root, name), os.path.relpath(root, CLIENT)))

    add_folder("images", lambda name: name.endswith(".png"))
    for folder in ("styles", "fonts", "confs", "settings"):
        add_folder(folder)
    with open(os.path.join(CLIENT, "client_audio.py"), encoding="utf-8") as file:
        played = set(re.findall(r'"([\w-]+\.(?:wav|mp3))"', file.read()))
    for folder in ("audio/Sound", "audio/Music"):
        add_folder(folder, lambda name: name in played)
    return files


def run(*command, **kwargs):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True, cwd=ROOT, **kwargs)


def build():
    run(sys.executable, "-m", "PyInstaller", "Kaboom.spec", "--noconfirm", "--clean",
        "--distpath", DIST, "--workpath", ROOT / "build" / OS_NAME)
    if OS_NAME == "macos":
        # Ad hoc signature: Apple Silicon only runs signed code, and a bundle changed after
        # PyInstaller signed its files needs one signature for the whole .app.
        run("codesign", "--force", "--deep", "--sign", "-", SHIPPED)
        run("codesign", "--verify", "--deep", "--strict", SHIPPED)
    print(f"Built {SHIPPED} ({folder_size(SHIPPED) / 1e6:.0f} MB)")


def folder_size(folder: Path) -> int:
    return sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())


def archive():
    """The game folder (Kaboom.app on macOS) in one file, for CI artifacts and Steam. A .tar.gz keeps
    the executable bit and the symlinks of the .app."""
    path = PATHS["archive"]
    if OS_NAME == "windows":
        shutil.make_archive(str(path.with_suffix("")), "zip", DIST, "Kaboom")
    else:
        with tarfile.open(path, "w:gz") as tar:
            tar.add(SHIPPED, arcname=SHIPPED.name)
    print(f"Archive: {path}")


def find_iscc() -> str:
    found = shutil.which("iscc")
    if found:
        return found
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles")):
        if base and Path(base, "Inno Setup 6", "ISCC.exe").exists():
            return str(Path(base, "Inno Setup 6", "ISCC.exe"))
    sys.exit("Inno Setup (ISCC.exe) not found: install it from https://jrsoftware.org/isdl.php")


def make_dmg():
    """The macOS installer: a disk image with Kaboom.app and a link to Applications, to drag it in."""
    dmg = PATHS["installer"]
    dmg.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kaboom-dmg-") as stage:
        run("ditto", SHIPPED, Path(stage, SHIPPED.name))  # copies the .app with its symlinks and signature
        Path(stage, "Applications").symlink_to("/Applications")
        run("hdiutil", "create", "-volname", f"Kaboom {VERSION}", "-srcfolder", stage,
            "-format", "UDZO", "-ov", dmg)
    print(f"Installer: {dmg}")


def package():
    if OS_NAME == "linux":
        run("bash", "create_release_package.sh", VERSION)
    elif OS_NAME == "windows":
        run(find_iscc(), f"/DMyAppVersion={VERSION}", "kaboom_setup.iss")
    else:
        make_dmg()


def smoke():
    """Starts the built game with an empty player folder, off-screen, and without a game server.
    Fails if it stops or writes an error before SMOKE_SECONDS."""
    with tempfile.TemporaryDirectory(prefix="kaboom-smoke-") as home:
        env = {**os.environ, "HOME": home, "APPDATA": home, "QT_QPA_PLATFORM": "offscreen",
               "PULSE_SERVER": "/nonexistent", "KABOOM_SERVER_HOST": "127.0.0.1", "KABOOM_SERVER_PORT": "9"}
        config = config_dir(OS_NAME, Path(home))
        print(f"+ {EXECUTABLE} (for {SMOKE_SECONDS} s)", flush=True)
        game = subprocess.Popen([str(EXECUTABLE)], env=env, cwd=home)
        try:
            deadline = time.monotonic() + SMOKE_SECONDS
            while time.monotonic() < deadline and game.poll() is None:
                time.sleep(0.5)
            code = game.poll()
        finally:
            if game.poll() is None:
                game.kill()
            game.wait()
        errors_log = config / "logs" / "errors.log"
        errors = errors_log.read_text(encoding="utf-8", errors="replace") if errors_log.exists() else ""
        if code is not None or "Traceback" in errors:
            sys.exit(f"Smoke test failed (exit code {code}):\n{errors[-5000:]}")
        if not (config / "settings" / "user_sound_global.csv").exists():
            sys.exit(f"Smoke test failed: the game did not write its settings to {config}")
    print("Smoke test passed: the game ran without error")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archive", action="store_true", help="also make the game folder's archive")
    parser.add_argument("--package", action="store_true", help="also make the installer (.deb / setup .exe / .dmg)")
    parser.add_argument("--smoke", action="store_true", help="start the built game to check it runs")
    parser.add_argument("--skip-build", action="store_true", help="use the dist/ folder already built")
    args = parser.parse_args()
    if not args.skip_build:
        build()
    if args.smoke:
        smoke()
    if args.archive:
        archive()
    if args.package:
        package()


if __name__ == "__main__":
    main()
