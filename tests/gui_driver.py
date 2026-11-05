"""Runs the real game client (Client/client.py) so a test can drive it (see GuiClient in harness.py).

Commands arrive on stdin as JSON lines ({"id": 1, "cmd": "state"}), answers are printed on stdout
as lines starting with "GUI " followed by JSON. Commands run in the Qt main thread.
"""
import json
import os
import runpy
import socket
import sys
import threading
import traceback

CLIENT_DIR = sys.argv[1]
sys.path.insert(0, CLIENT_DIR)
os.chdir(CLIENT_DIR)

import client_utils  # noqa: E402  (creates the QApplication)
from PyQt5.QtCore import QObject, pyqtSignal  # noqa: E402


def game_globals() -> dict:
    """Globals of client.py while it runs (window, login, receiver_thread...)."""
    return sys.modules["__main__"].__dict__


def state() -> dict:
    g = game_globals()
    window, login = g.get("window"), g.get("login")
    if window is None or login is None:
        return {"started": False}
    st = {"started": True, "login_visible": login.isVisible(), "login_text": login.alert_label.text(),
          "window_visible": window.isVisible(), "ingame": window.ingame}
    if hasattr(window, "player_label_list"):
        try:
            st.update(labels=[label.text() for label in window.player_label_list],
                      hearts=[getattr(window, f"heart_list_widget{i}").count() for i in range(1, 9)],
                      avatars=[avatar.pixmap_name for avatar in window.avatar_label_list],
                      syllabe=window.syllabe_label.text(), my_turn=window.text_line_edit.isEnabled())
        except RuntimeError:  # the lobby screen is being replaced
            pass
    return st


def run(command: dict) -> dict:
    g = game_globals()
    name = command["cmd"]
    if name == "state":
        return state()
    if name == "ready":
        g["window"].ready()
    elif name == "login":
        g["login"].username_edit.setText(command["name"])
        g["login"].send_username()
    elif name == "join":  # open the "join a game" menu and pick a public game, like a player
        if not g["window"].loaded_select_screen:
            g["window"].load_select_screen()
        client_utils.send_server(f"GET-GAMES_|{command['player']}|")
        client_utils.send_server(f"JOIN-GAME_|{command['game']}|password|{command['player']}")
    elif name == "drop_connection":  # like a wifi cut
        client_utils.client_socket.shutdown(socket.SHUT_RDWR)
    elif name == "quit":  # Alt+F4 then "OK" in the exit window
        g["window"].display_exit_game_window()
        g["window"].exit_window.ok_clicked()
    elif name == "exit":
        os._exit(0)
    return {}


class Bridge(QObject):
    command = pyqtSignal(str)

    def handle(self, line: str):
        command = json.loads(line)
        try:
            reply = run(command)
        except Exception:
            reply = {"error": traceback.format_exc()}
        print("GUI " + json.dumps({"id": command.get("id"), **reply}, ensure_ascii=False), flush=True)


bridge = Bridge()
bridge.command.connect(bridge.handle)  # queued: runs in the main (Qt) thread


def read_commands():
    for line in sys.stdin:
        bridge.command.emit(line)
    os._exit(0)  # the test ended


threading.Thread(target=read_commands, daemon=True).start()
sys.argv = [os.path.join(CLIENT_DIR, "client.py")]
runpy.run_path(sys.argv[0], run_name="__main__")
