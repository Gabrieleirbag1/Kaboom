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
import time
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


def drag_slider(slider, moves: int, gap: float = 0) -> float:
    """Press the mouse on the handle of `slider`, move it back and forth `moves` times (one move
    every `gap` seconds) and release. Returns how long it took."""
    from PyQt5.QtCore import QEvent, QPoint, Qt
    from PyQt5.QtGui import QMouseEvent
    from PyQt5.QtWidgets import QApplication

    def mouse(kind, x, buttons):
        event = QMouseEvent(kind, QPoint(x, slider.height() // 2), Qt.LeftButton, buttons, Qt.NoModifier)
        QApplication.sendEvent(slider, event)
        QApplication.processEvents()  # timers run between the moves, like with a real mouse
        if gap:
            time.sleep(gap)

    start, width = time.monotonic(), max(slider.width() - 1, 1)
    handle = slider.style().sliderPositionFromValue(slider.minimum(), slider.maximum(), slider.value(), width)
    mouse(QEvent.MouseButtonPress, handle, Qt.LeftButton)
    for i in range(moves):
        mouse(QEvent.MouseMove, (i * 37) % width, Qt.LeftButton)
    mouse(QEvent.MouseButtonRelease, (moves * 37) % width, Qt.NoButton)
    return time.monotonic() - start


SOUND_FILE = "user_sound_global.csv"
counts = {"saves": 0, "audio": 0}  # see count_sound()


def count_sound():
    """From now on, count the writes of the volume file and the volume changes given to Qt's audio
    objects (whatever code does them)."""
    import builtins
    real_open = builtins.open

    def counting_open(file, mode="r", *args, **kwargs):
        if any(m in mode for m in "wax") and SOUND_FILE in str(file):
            counts["saves"] += 1
        return real_open(file, mode, *args, **kwargs)
    builtins.open = counting_open

    def counting(set_volume):
        def wrapper(value):
            counts["audio"] += 1
            return set_volume(value)
        return wrapper
    for effects in (client_utils.button_sound.sound_effects, client_utils.ambiance_sound.sound_effects):
        for sound in effects.sound_objects:
            sound.setVolume = counting(sound.setVolume)
    client_utils.music.player.setVolume = counting(client_utils.music.player.setVolume)


def sound_state() -> dict:
    """The volumes saved on disk, and the real volume of every audio object."""
    import client_settings
    with open(os.path.join(client_settings.settings_file_path, SOUND_FILE), encoding="utf-8") as file:
        saved = {row[0]: row[1] for row in (line.strip().split(",") for line in file) if len(row) > 1}
    music = client_utils.music
    track = music.playlist.currentMedia().canonicalUrl().fileName()
    effects = {name: [[sound.volume(), float(default[1])]
                      for default, sound in zip(fx.sounds.values(), fx.sound_objects)]
               for name, fx in (("ambiance", client_utils.ambiance_sound.sound_effects),
                                ("bouton", client_utils.button_sound.sound_effects))}
    return {"saved": saved, "music": [music.player.volume(), int(music.musics_default[track])],
            "effects": effects, **counts}


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
    elif name == "open_settings":
        g["window"].display_settings()
    elif name == "drag_slider":  # the mouse drags a volume slider back and forth very fast
        slider = getattr(g["window"].settings_window, command["slider"])
        seconds = drag_slider(slider, command["moves"], command.get("gap", 0))
        return {"value": slider.value(), "seconds": seconds}
    elif name == "set_slider":  # keyboard arrows or mouse wheel: the value changes, no release
        getattr(g["window"].settings_window, command["slider"]).setValue(command["value"])
    elif name == "count_sound":
        count_sound()
    elif name == "sound":
        return sound_state()
    elif name == "close_settings":
        g["window"].settings_window.close()
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
