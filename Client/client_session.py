"""Remembers who the player is, so they can get back to their game (#10).

After login the server gives a secret key. It is saved in the player's config folder: if the
connection drops, or if the game is closed and started again, the client sends it back
(RECONNECT_) and the server puts the player back in their seat.

KABOOM_PROFILE separates the sessions of several clients on the same computer (for testing).
"""
import json
import os

from client_logs import base_path

_profile = os.environ.get("KABOOM_PROFILE", "")
SESSION_FILE = os.path.join(base_path, f"session{'-' + _profile if _profile else ''}.json")


def save_session(username: str, token: str, avatar: str) -> None:
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as file:
            json.dump({"username": username, "token": token, "avatar": avatar}, file)
    except OSError:
        pass


def load_session() -> dict | None:
    """The saved session, or None if there is none (or the file is broken)."""
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as file:
            session = json.load(file)
        if all(isinstance(session.get(key), str) and session[key] for key in ("username", "token", "avatar")):
            return session
    except (OSError, ValueError):
        pass
    return None


def clear_session() -> None:
    try:
        os.remove(SESSION_FILE)
    except OSError:
        pass
