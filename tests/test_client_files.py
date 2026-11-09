"""Issue #29: the player's settings files after an update of the game.

The game copies its files (Client/settings, Client/confs) to the player's folder once. After an
update, the old copies stayed: a new setting was missing and the game crashed, unless the player
deleted the folder (and lost their settings). Now, at each start:
- the game's own files (languages, sound lists, defaults) are replaced by the new version;
- the player's files keep the player's values; a new setting is added with its default value,
  a removed one is dropped;
- files the game doesn't ship any more are deleted.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("client_files", ROOT / "Client" / "client_files.py")
client_files = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(client_files)


def rows(text: str) -> list[list[str]]:
    return client_files.read_rows(text)


# --- Merging one file -----------------------------------------------------------------------

def test_merge_keeps_the_players_values():
    default = rows("theme,#fec2ff/#7bf8fc,NotSound\nlanguage,English,NotSound\n")
    player = rows("theme,#000000/#ffffff,NotSound\nlanguage,Français,NotSound\n")
    assert client_files.merge_rows(player, default) == player


def test_merge_adds_new_settings_and_drops_removed_ones():
    default = rows("theme,a,NotSound\nlanguage,English,NotSound\nborders,yes,NotSound\n")
    player = rows("language,Français,NotSound\nold_option,1,NotSound\ntheme,b,NotSound\n")
    assert client_files.merge_rows(player, default) == rows(
        "theme,b,NotSound\nlanguage,Français,NotSound\nborders,yes,NotSound\n")  # the game's order


def test_merge_fills_a_new_column_with_its_default():
    default = rows("global,100,notmuted\n")
    assert client_files.merge_rows(rows("global,40\n"), default) == rows("global,40,notmuted\n")
    assert client_files.merge_rows(rows("global,40,muted,extra\n"), default) == rows("global,40,muted\n")


def test_merge_ignores_empty_lines_and_keeps_the_first_duplicate():
    default = rows("host,missclick.net\nport,22222\n")
    player = rows("\nhost,my.server\n\nhost,other\nport,1234\n\n")
    assert client_files.merge_rows(player, default) == rows("host,my.server\nport,1234\n")


# --- A whole folder -------------------------------------------------------------------------

def write(folder: Path, files: dict[str, str]):
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (folder / name).write_text(text, encoding="utf-8")


def test_sync_folder(tmp_path):
    game, player = tmp_path / "game", tmp_path / "player"
    write(game, {"user_settings.csv": "a,1\nb,2\nnew,3\n",
                 "sounds.csv": "boom,1\nnew_sound,0.5\n",
                 "English.json": '{"hello": "Hello", "new": "New"}'})
    write(player, {"user_settings.csv": "a,10\nb,20\ngone,0\n",
                   "sounds.csv": "boom,1\n",
                   "English.json": '{"hello": "Hello"}',
                   "mqtt.csv": "password,secret\n",
                   "user_settings.csv.tmp": "half written"})
    client_files.sync_folder(player, game, player_files=("user_settings.csv",))

    assert (player / "user_settings.csv").read_text() == "a,10\nb,20\nnew,3\n"
    assert (player / "sounds.csv").read_text() == "boom,1\nnew_sound,0.5\n"
    assert json.loads((player / "English.json").read_text()) == {"hello": "Hello", "new": "New"}
    assert sorted(p.name for p in player.iterdir()) == ["English.json", "sounds.csv", "user_settings.csv"]


def test_sync_folder_creates_missing_files_and_leaves_unchanged_ones_alone(tmp_path):
    game, player = tmp_path / "game", tmp_path / "player"
    write(game, {"user_settings.csv": "a,1\n", "sounds.csv": "boom,1\n"})
    client_files.sync_folder(player, game, player_files=("user_settings.csv",))
    assert (player / "user_settings.csv").read_text() == "a,1\n"
    before = {p.name: p.stat().st_mtime_ns for p in player.iterdir()}
    client_files.sync_folder(player, game, player_files=("user_settings.csv",))
    assert {p.name: p.stat().st_mtime_ns for p in player.iterdir()} == before  # nothing rewritten


def test_unreadable_player_file_goes_back_to_the_default(tmp_path):
    game, player = tmp_path / "game", tmp_path / "player"
    write(game, {"user_settings.csv": "a,1\n"})
    player.mkdir()
    (player / "user_settings.csv").write_bytes(b"\xff\xfe\x00garbage")
    client_files.sync_folder(player, game, player_files=("user_settings.csv",))
    assert (player / "user_settings.csv").read_text() == "a,1\n"


# --- The real game, started on the files of an older version ---------------------------------

def older_version_files(config: Path):
    """What a player of an older version has: their own choices, files of that version."""
    shipped = json.loads((ROOT / "Client" / "confs" / "Français.json").read_text(encoding="utf-8"))
    old_french = {key: value for key, value in shipped.items() if key != "Login__alert_label__connection_error"}
    write(config / "settings", {
        # "borders" didn't exist yet, "old_option" doesn't exist any more
        "user_accessibility.csv": "theme,#123456/#abcdef,NotSound\nlanguage,Français,NotSound\n"
                                  "animations,no,NotSound\nold_option,1,NotSound\n",
        "user_sound_global.csv": "global,40,notmuted\nmusic,30,muted\nambiance,20,notmuted\nbouton,10,notmuted\n",
        "sound_ambiance.csv": "victory_sound,1\nnext_sound,0.25\n",  # sounds were added since
    })
    write(config / "confs", {
        "Français.json": json.dumps(old_french, ensure_ascii=False),
        "socket.csv": "host,my.server.example\nport,22222",
        "mqtt.csv": "broker,missclick.net\nport,1883\nuser,siphano\npassword,old\n",
    })


@pytest.mark.gui
def test_game_starts_on_the_files_of_an_older_version(server, make_gui, tmp_path):
    home = tmp_path / "home"
    config = home / ".config" / "kaboom"
    older_version_files(config)

    gui = make_gui(home=home)
    gui.wait_for(lambda st: st["login_visible"], timeout=60)
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    gui.call("open_settings")
    assert gui.errors() == ""

    settings = config / "settings"
    assert (settings / "user_accessibility.csv").read_text(encoding="utf-8") == (
        "theme,#123456/#abcdef,NotSound\nlanguage,Français,NotSound\nanimations,no,NotSound\nborders,yes,NotSound\n")
    assert (settings / "user_sound_global.csv").read_text(encoding="utf-8") == (
        "global,40,notmuted\nmusic,30,muted\nambiance,20,notmuted\nbouton,10,notmuted\n")
    for name in ("sound_ambiance.csv", "sound_music.csv"):
        assert (settings / name).read_text(encoding="utf-8") == (ROOT / "Client" / "settings" / name).read_text(encoding="utf-8")
    confs = config / "confs"
    assert (confs / "Français.json").read_text(encoding="utf-8") == (ROOT / "Client" / "confs" / "Français.json").read_text(encoding="utf-8")
    assert (confs / "socket.csv").read_text(encoding="utf-8").startswith("host,my.server.example\nport,22222\n")
    assert not (confs / "mqtt.csv").exists()
