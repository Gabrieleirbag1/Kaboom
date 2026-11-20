"""Issue #21: the compiled game (build.py / Kaboom.spec) packs every file the game reads, and only
those (no unused music, dev scripts or logs)."""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

CLIENT = ROOT / "Client"


def packed() -> dict[str, str]:
    """{path in the build: source file}"""
    return {os.path.join(folder, os.path.basename(src)).replace(os.sep, "/"): src for src, folder in build.game_files()}


def test_every_sound_the_game_plays_is_packed():
    files = packed()
    played = re.findall(r'"([\w-]+\.(?:wav|mp3))"', (CLIENT / "client_audio.py").read_text(encoding="utf-8"))
    assert played
    for name in played:
        folder = "audio/Music" if name.endswith(".mp3") else "audio/Sound"
        assert (CLIENT / folder / name).exists(), f"{name} is played but missing from Client/{folder}"
        assert f"{folder}/{name}" in files


def test_no_unused_music_scripts_or_logs():
    files = packed()
    assert not [f for f in files if f.endswith((".py", ".sh", ".bash"))]
    assert not [f for f in files if f.startswith(("logs/", "videos/", "external/")) or "/." in f or "__pycache__" in f]
    music = [f for f in files if f.startswith("audio/Music/")]
    assert len(music) == 3 and all(f.endswith(".mp3") for f in music)


def test_every_image_and_setting_is_packed():
    """Animations count the files of their sprite folder: every frame must be there."""
    files = packed()
    for folder in ("images", "settings", "confs", "fonts", "styles"):
        for path in (CLIENT / folder).rglob("*"):
            if path.is_file() and path.suffix not in (".py", ".bash", ".icns", ".ico") and not path.name.startswith("."):
                assert path.relative_to(CLIENT).as_posix() in files


def test_version_is_set_once():
    assert re.fullmatch(r"\d+\.\d+(\.\d+)?", build.VERSION)
    iss = (ROOT / "kaboom_setup.iss").read_text(encoding="utf-8")
    assert "MyAppVersion" in iss and "IsPythonInstalled" not in iss


def test_macos_build_is_an_app_bundle_per_processor():
    """macOS: one Kaboom.app per processor (Qt 5 has no universal2 package), shipped as a .dmg and
    a .tar.gz for Steam; the smoke test starts the executable inside the bundle."""
    for arch in ("arm64", "x86_64"):
        paths = build.paths("macos", arch)
        assert paths["shipped"].name == "Kaboom.app"
        assert paths["executable"] == paths["shipped"] / "Contents" / "MacOS" / "Kaboom"
        assert paths["installer"].name == f"kaboom-{build.VERSION}-macos-{arch}.dmg"
        assert paths["archive"].name == f"Kaboom-{build.VERSION}-macos-{arch}.tar.gz"
    assert build.config_dir("macos", Path("/h")) == Path("/h/Library/Application Support/Kaboom")


def test_windows_and_linux_build_paths_did_not_change():
    windows, linux = build.paths("windows", "x86_64"), build.paths("linux", "x86_64")
    assert windows["executable"] == windows["game"] / "Kaboom.exe" and windows["shipped"] == windows["game"]
    assert linux["executable"] == linux["game"] / "Kaboom" and linux["shipped"] == linux["game"]
    assert windows["archive"].name == f"Kaboom-{build.VERSION}-windows.zip"
    assert linux["archive"].name == f"Kaboom-{build.VERSION}-linux.tar.gz"
    assert linux["installer"].name == f"kaboom_{build.VERSION}_amd64.deb"


def test_player_folder_matches_the_game():
    """The smoke test and the tests look for the settings where the game writes them."""
    client_logs = (CLIENT / "client_logs.py").read_text(encoding="utf-8")
    assert '"Library", "Application Support", "Kaboom"' in client_logs
    assert '".config", "kaboom"' in client_logs


def test_macos_bundle_has_its_icon():
    spec = (ROOT / "Kaboom.spec").read_text(encoding="utf-8")
    assert (CLIENT / "images" / "bombe-icon.icns").exists()
    assert "bombe-icon.icns" in spec and "BUNDLE(" in spec and "Kaboom.app" in spec
