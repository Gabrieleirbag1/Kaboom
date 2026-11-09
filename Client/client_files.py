"""The player's copy of the game's settings files (#29).

The game ships its files in Client/settings and Client/confs, and works on a copy in the player's
folder (~/.config/kaboom, %APPDATA%\\Kaboom...). At each start, so that an update never needs the
player to delete that folder:
- the game's own files (languages, sound lists, default settings) are replaced by the new version;
- the player's files (PLAYER_FILES) keep the player's values: a setting the update adds gets its
  default value, a setting it removes is dropped, rows follow the new file's order;
- files the game doesn't ship any more are deleted.
"""
import logging
import os

# Files the player changes (from the settings menu, or by hand for socket.csv)
PLAYER_FILES = ("user_accessibility.csv", "user_sound_global.csv", "socket.csv")


def read_rows(text: str) -> list[list[str]]:
    """CSV rows (key,value,...) of a settings file, without empty lines."""
    return [line.strip().split(",") for line in text.splitlines() if line.strip()]


def rows_text(rows: list[list[str]]) -> str:
    return "".join(",".join(row) + "\n" for row in rows)


def merge_rows(player_rows: list[list[str]], default_rows: list[list[str]]) -> list[list[str]]:
    """The default rows (the new version's keys, in its order) with the player's values.
    A row keeps the player's columns; columns the new version added get their default."""
    player: dict[str, list[str]] = {}
    for row in player_rows:
        player.setdefault(row[0], row)
    merged = []
    for default in default_rows:
        mine = player.get(default[0])
        merged.append(default if mine is None else mine[:len(default)] + default[len(mine):])
    return merged


def _read(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError):
        logging.exception(f"Could not read {path}, using the game's version")
        return None


def _write(path: str, text: str):
    """Either the old file or the new one, never half written."""
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            file.write(text)
        os.replace(temp_path, path)
    except OSError:
        logging.exception(f"Could not update {path}")


def sync_folder(player_dir: str, game_dir: str, player_files: tuple[str, ...] = PLAYER_FILES):
    """Bring the player's folder up to date with the game's (see the top of this file)."""
    player_dir, game_dir = os.fspath(player_dir), os.fspath(game_dir)
    if os.path.realpath(player_dir) == os.path.realpath(game_dir):
        return
    os.makedirs(player_dir, exist_ok=True)
    shipped = {name for name in os.listdir(game_dir) if os.path.isfile(os.path.join(game_dir, name))}
    for name in sorted(shipped):
        default = _read(os.path.join(game_dir, name))
        if default is None:
            continue
        path = os.path.join(player_dir, name)
        current = _read(path)
        wanted = default
        if name in player_files:
            wanted = rows_text(merge_rows(read_rows(current or ""), read_rows(default)))
        if wanted != current:
            _write(path, wanted)
    for name in os.listdir(player_dir):
        path = os.path.join(player_dir, name)
        if name not in shipped and os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                logging.exception(f"Could not delete {path}")
