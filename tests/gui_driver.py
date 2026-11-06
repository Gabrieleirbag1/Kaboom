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
            if hasattr(window, "turn_label"):
                st.update(turn=window.turn_label.text(), turn_glow=window.turn_label_glow.active,
                          box_glow=window.word_box_glow.active, box_focus=window.text_line_edit.hasFocus(),
                          placeholder=window.text_line_edit.placeholderText(), active=window.isActiveWindow(),
                          **turn_cues)
        except RuntimeError:  # the lobby screen is being replaced
            pass
    return st


def find(path: str):
    """A window from a dotted path: "window", "login", "window.settings_window"..."""
    root, *attributes = path.split(".")
    target = game_globals()[root]
    for attribute in attributes:
        target = getattr(target, attribute)
    return target


def rect(widget, window) -> list[int]:
    """[x, y, width, height] of `widget` in `window` coordinates."""
    top_left = widget.mapTo(window, widget.rect().topLeft())
    return [top_left.x(), top_left.y(), widget.width(), widget.height()]


def hearts_visible(hearts) -> bool:
    """True if every heart of the list is fully shown (none wrapped to a hidden second line)."""
    area = hearts.viewport().rect()
    return all(area.contains(hearts.visualItemRect(hearts.item(i))) for i in range(hearts.count()))


def layout() -> dict:
    """Where the game screen's pieces are, to check alignment and that everything fits the screen."""
    from PyQt5.QtWidgets import QApplication
    for _ in range(5):  # finish the layout work already asked for (hearts just added...)
        QApplication.processEvents()
    window = game_globals()["window"]
    screen = QApplication.primaryScreen().geometry()
    info = {"screen": [screen.width(), screen.height()], "window": [window.width(), window.height()]}
    if hasattr(window, "player_label_list"):
        info["players"] = [{"name": rect(label, window), "avatar": rect(avatar, window),
                            "hearts": rect(getattr(window, f"heart_list_widget{i + 1}"), window),
                            "hearts_count": getattr(window, f"heart_list_widget{i + 1}").count(),
                            "hearts_visible": hearts_visible(getattr(window, f"heart_list_widget{i + 1}")),
                            "border": window.player_border_size[i]}
                           for i, (label, avatar) in enumerate(zip(window.player_label_list, window.avatar_label_list))]
        info.update({name: rect(getattr(window, name), window) for name in (
            "rules_button", "ready_button", "start_button", "bomb_label", "syllabe_label", "text_line_edit",
            "home_button_game", "game_name_label")})
    return info


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


def luminance(color) -> float:
    def channel(value: int) -> float:
        value /= 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(color.red()) + 0.7152 * channel(color.green()) + 0.0722 * channel(color.blue())


def visible_share(label, background: str) -> float:
    """Draws `label` (without its glow) on a plain `background` color. Returns the share of the
    text's area drawn with a contrast of at least 3:1 against the background (WCAG's minimum for
    big text): 0 means the text can't be read on that background."""
    from PyQt5.QtGui import QColor, QImage, QPainter
    from PyQt5.QtWidgets import QWidget
    effect = label.graphicsEffect()
    if effect is not None:
        effect.setEnabled(False)
    image = QImage(label.size(), QImage.Format_ARGB32)
    image.fill(QColor(background))
    painter = QPainter(image)
    label.render(painter, flags=QWidget.DrawChildren)
    painter.end()
    if effect is not None:
        effect.setEnabled(True)
    back = luminance(QColor(background))
    text_pixels = readable = 0
    for y in range(image.height()):
        for x in range(image.width()):
            pixel = QColor(image.pixel(x, y))
            if pixel.rgb() == QColor(background).rgb():
                continue
            text_pixels += 1
            lighter, darker = sorted((luminance(pixel), back), reverse=True)
            readable += (lighter + 0.05) / (darker + 0.05) >= 3
    return readable / max(text_pixels, 1)


turn_cues = {"alerts": 0, "chimes": 0}  # see count_turn_cues()


def count_turn_cues():
    """From now on, count the taskbar flashes and the "your turn" chimes."""
    from PyQt5.QtWidgets import QApplication
    real_alert = QApplication.alert

    def alert(*args):
        turn_cues["alerts"] += 1
        return real_alert(*args)
    QApplication.alert = alert
    chime = client_utils.ambiance_sound.sound_effects.your_turn_sound
    real_play = chime.play

    def play():
        turn_cues["chimes"] += 1
        return real_play()
    chime.play = play


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


def perf() -> dict:
    """Memory and CPU used by the game so far, and the size of the style sheets it keeps."""
    from client_styles import AnimatedButton
    window = game_globals()["window"]
    with open("/proc/self/statm") as file:  # Linux: size and resident pages
        rss_mb = int(file.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 2**20
    return {"rss_mb": rss_mb, "cpu_s": time.process_time(), "window_sheet": len(window.styleSheet()),
            "button_sheets": [len(button.styleSheet()) for button in window.findChildren(AnimatedButton)]}


def sprites() -> dict:
    """{folder: [frames, biggest width, biggest height]} of the animations loaded by the game."""
    window = game_globals()["window"]
    loaded = {}
    for name, frames in vars(window).items():
        if name.endswith("_sprites") and isinstance(frames, list):
            loaded[name[:-len("_sprites")]] = [len(frames), max((f.width() for f in frames), default=0),
                                               max((f.height() for f in frames), default=0)]
    return loaded


def hover_menu_buttons(times: int):
    """The mouse goes in and out of the main menu buttons, `times` times each."""
    from PyQt5.QtCore import QEvent
    from PyQt5.QtWidgets import QApplication
    from client_styles import AnimatedButton
    for _ in range(times):
        for button in game_globals()["window"].findChildren(AnimatedButton):
            for kind in (QEvent.Enter, QEvent.Leave):
                QApplication.sendEvent(button, QEvent(kind))
                deadline = time.monotonic() + 0.3  # the hover animation lasts 250 ms
                while time.monotonic() < deadline:
                    QApplication.processEvents()
                    time.sleep(0.01)


def background_pixels(points: list) -> list[str]:
    """Colors ("#rrggbb") of the game window at these [x, y] points (as shown on screen)."""
    image = game_globals()["window"].grab().toImage()
    return [image.pixelColor(x, y).name() for x, y in points]


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
    elif name == "screenshot":  # saves a window as a PNG, e.g. of="window" (the game), "window.rules_window"
        target = find(command.get("of", "window"))
        target.grab().save(command["path"])
        return {"size": [target.width(), target.height()]}
    elif name == "call":  # calls a method of a window, e.g. target="login.avatar_window", method="show"
        getattr(find(command["target"]), command["method"])()
        target = find(command["target"])
        return {"size": [target.width(), target.height()]}
    elif name == "layout":
        return layout()
    elif name == "rules_window":  # the game rules window (the creator's "Rules" button)
        g["window"].display_rules()
        from PyQt5.QtWidgets import QApplication
        for _ in range(5):  # let it finish its layout before measuring it
            QApplication.processEvents()
        return {"size": [g["window"].rules_window.width(), g["window"].rules_window.height()]}
    elif name == "click_skull":  # the death mode button of the rules window
        rules = g["window"].rules_window
        rules.death_mode_pixmap_button.click()
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        return {"size": [rules.width(), rules.height()], "mode": rules.death_mode_state}
    elif name == "answer":  # the player types a word in the word box and presses Enter
        g["window"].text_line_edit.setText(command["word"])
        g["window"].text_line_edit.returnPressed.emit()
    elif name == "turn_visibility":  # how readable the turn text is on each background color
        return {"visible": {color: visible_share(g["window"].turn_label, color) for color in command["colors"]}}
    elif name == "count_turn_cues":
        count_turn_cues()
    elif name == "focus":  # the player clicks on the game window (or alt-tabs away from it)
        from PyQt5.QtWidgets import QApplication
        if command.get("on", True):
            g["window"].activateWindow()
        else:
            QApplication.setActiveWindow(None)
        for _ in range(5):
            QApplication.processEvents()
        return {"active": g["window"].isActiveWindow()}
    elif name == "count_sound":
        count_sound()
    elif name == "sound":
        return sound_state()
    elif name == "close_settings":
        g["window"].settings_window.close()
    elif name == "menu":  # click on the title screen: the main menu (create / join a game)
        if not g["window"].loaded_select_screen:
            g["window"].load_select_screen()
    elif name == "perf":
        return perf()
    elif name == "sprites":
        return {"sprites": sprites(), "avatars": {avatar: [pixmap.width(), pixmap.height()]
                                                  for avatar, pixmap in client_utils._avatar_pixmaps.items()}}
    elif name == "hover_menu_buttons":
        hover_menu_buttons(command.get("times", 1))
    elif name == "theme":  # settings > graphics > a background theme button
        g["window"].display_settings()
        g["window"].settings_window.set_color_theme(command["color1"], command["color2"])
        g["window"].settings_window.close()
    elif name == "background_pixels":
        return {"colors": background_pixels(command["points"])}
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
