"""Builds the compiled game (#21): Python, Qt and the game's files in one folder, nothing to install.

    python build.py             -> dist/<os>/Kaboom/ (the Steam build)
    python build.py --archive   -> also dist/Kaboom-<version>-<os>.zip (Windows) / .tar.gz (Linux)
    python build.py --package   -> also the installer: Releases/kaboom_<version>_amd64.deb (Linux)
                                   or Releases/kaboom-setup-<version>.exe (Windows, needs Inno Setup)
    python build.py --smoke     -> starts the built game off-screen and checks it runs without error

Needs the packages of requirements-build.txt. The kaboom_install scripts make a venv and run this.
"""
import argparse
import os
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
DIST = ROOT / "dist" / OS_NAME
GAME_DIR = DIST / "Kaboom"
EXECUTABLE = GAME_DIR / ("Kaboom.exe" if OS_NAME == "windows" else "Kaboom")
SMOKE_SECONDS = 20


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
    print(f"Built {GAME_DIR} ({folder_size(GAME_DIR) / 1e6:.0f} MB)")


def folder_size(folder: Path) -> int:
    return sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())


def archive():
    """The game folder in one file, for CI artifacts and Steam (a .tar.gz keeps Linux's
    executable bit)."""
    if OS_NAME == "windows":
        path = shutil.make_archive(str(ROOT / "dist" / f"Kaboom-{VERSION}-{OS_NAME}"), "zip", DIST, "Kaboom")
    else:
        path = ROOT / "dist" / f"Kaboom-{VERSION}-{OS_NAME}.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            tar.add(GAME_DIR, arcname="Kaboom")
    print(f"Archive: {path}")


def find_iscc() -> str:
    found = shutil.which("iscc")
    if found:
        return found
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles")):
        if base and Path(base, "Inno Setup 6", "ISCC.exe").exists():
            return str(Path(base, "Inno Setup 6", "ISCC.exe"))
    sys.exit("Inno Setup (ISCC.exe) not found: install it from https://jrsoftware.org/isdl.php")


def package():
    if OS_NAME == "linux":
        run("bash", "create_release_package.sh", VERSION)
    elif OS_NAME == "windows":
        run(find_iscc(), f"/DMyAppVersion={VERSION}", "kaboom_setup.iss")
    else:
        sys.exit("No installer for this system")


def smoke():
    """Starts the built game with an empty player folder, off-screen, and without a game server.
    Fails if it stops or writes an error before SMOKE_SECONDS."""
    with tempfile.TemporaryDirectory(prefix="kaboom-smoke-") as home:
        env = {**os.environ, "HOME": home, "APPDATA": home, "QT_QPA_PLATFORM": "offscreen",
               "PULSE_SERVER": "/nonexistent", "KABOOM_SERVER_HOST": "127.0.0.1", "KABOOM_SERVER_PORT": "9"}
        config = Path(home, "Kaboom") if OS_NAME == "windows" else Path(home, ".config", "kaboom")
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
    parser.add_argument("--package", action="store_true", help="also make the installer (.deb / setup .exe)")
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
