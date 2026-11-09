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

