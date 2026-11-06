from requirements import *
from client_audio import ButtonSoundEffect, AmbianceSoundEffect, MusicPlayer
from client_settings import Settings, Configurations, LangueSettings
from client_logs import ErrorLogger, InfosLogger
from client_protocol import encode, MessageBuffer, PROTOCOL_VERSION, is_valid_text_field
from client_session import save_session, load_session, clear_session

ErrorLogger.setup_logging()

infos_logger = InfosLogger()
infos_logger.log_infos("[START]", "Client started")

# Socket
confs = Configurations()

# Vars
if os.environ.get("QT_QPA_PLATFORM"):  # platform chosen by the user or the tests (offscreen)
    app = QApplication(sys.argv)
elif sys.platform == "win32":
    app = QApplication(sys.argv + ['-platform', 'windows:darkmode=1'])
elif sys.platform == "linux":
    app = QApplication(sys.argv + ['-platform', 'xcb'])
elif sys.platform == "darwin":
    app = QApplication(sys.argv + ['-platform', 'cocoa'])
else:
    app = QApplication(sys.argv)
backslash = "\\"
screen_size = QDesktopWidget().screenGeometry()
screen_width, screen_height = screen_size.width(), screen_size.height()

# The game is designed for a 1920x1080 screen: sizes are fractions of the screen, and fonts follow
# the same scale (in pixels, so Windows display scaling at 125 % / 150 % doesn't make text overflow).
UI_SCALE = min(screen_width / 1920, screen_height / 1080)


def font_px(points: float) -> int:
    """Pixel size of a font of `points` on the 1920x1080 reference screen, for this screen."""
    return max(1, round(points * 96 / 72 * UI_SCALE))


SCALED_PROPERTIES = re.compile(r"(?<![\w-])(font-size|padding(?:-\w+)?|margin(?:-\w+)?|border(?:-\w+)*|"
                               r"(?:min-|max-)?(?:width|height))(\s*:\s*)([^;}]*)")
LENGTH = re.compile(r"(?<![#\w.])(\d+(?:\.\d+)?)(px|pt)?(?![\w.])")


def scale_stylesheet(stylesheet: str) -> str:
    """Scales a stylesheet made for 1920x1080 to this screen: font sizes, paddings, margins, borders
    and radii become pixels of this screen (colors like rgba(...) or #5c596e are left alone)."""
    def scale_length(match: re.Match) -> str:
        value = float(match.group(1))
        if value == 0:
            return match.group(0)
        if match.group(2) == "pt":
            return f"{font_px(value)}px"
        return f"{max(1, round(value * UI_SCALE))}px"

    def scale_property(match: re.Match) -> str:
        parts = re.split(r"(\([^)]*\))", match.group(3))  # keep rgba(...) / url(...) as they are
        value = "".join(part if part.startswith("(") else LENGTH.sub(scale_length, part) for part in parts)
        return match.group(1) + match.group(2) + value
    return SCALED_PROPERTIES.sub(scale_property, stylesheet)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None
syllabes = []

# Live typing (#20): the broker account the server gave for the current game (MQTT_ message).
# Set by the reception thread, taken by client_mqtt.Mqtt_Sub.
_mqtt_access: dict | None = None
_mqtt_access_lock = threading.Lock()


def set_mqtt_access(access: dict) -> None:
    global _mqtt_access
    with _mqtt_access_lock:
        _mqtt_access = access


def take_mqtt_access(game_name: str) -> dict | None:
    """The account for this game if one arrived since the last call, else None."""
    global _mqtt_access
    with _mqtt_access_lock:
        if _mqtt_access and _mqtt_access["game"] == game_name:
            access, _mqtt_access = _mqtt_access, None
            return access
    return None


TYPED_TEXT_MAX = 40  # longer than any word: a player can't flood the others' screens


def clean_typed_text(text: str) -> str:
    """Only the letters a player may type (the label shows HTML: no tags can get through)."""
    return re.sub(r'[^a-zA-ZÀ-ÿ]', '', text)


def highlight_syllable(text: str, syllabe: str) -> str:
    """The typed text in lower case, with the syllable in bold."""
    highlighted_text = text.lower()
    if not syllabe:
        return highlighted_text
    for s in [syllabe, syllabe.upper(), syllabe.lower(), syllabe.capitalize(), syllabe.upper().capitalize()]:
        if s in text or unidecode.unidecode(s) in unidecode.unidecode(text).upper():
            text = text.lower()
            highlighted_text = text.replace(s, f"<b>{s}</b>")
    return highlighted_text
rules = [7, 9, 3, 2, 3, 1, 0] # Minimum time, maximum time, lifes, minimum syllables, maximum syllables, number of repetitions, death mode code

# Paths
image_path = os.path.join(os.path.dirname(__file__), "images/")
avatar_path = os.path.join(image_path, "avatars/")
tombstone_path = os.path.join(image_path, "tombes/")

# The avatar pictures are 3000x3000 (36 MB each once decoded) but never shown bigger than the
# winner's picture (screen_width / 4): keep them at that size, and read each file only once.
AVATAR_MAX_SIDE = max(1, screen_width // 4)
_avatar_pixmaps: dict[str, QPixmap] = {}


def avatar_pixmap(avatar_name: str) -> QPixmap:
    """The picture of an avatar ("tasse-avatar", "no-avatar"...), at most AVATAR_MAX_SIDE wide.

    Args:
        avatar_name (str): The avatar's name (its file in images/avatars without ".png")

    Returns:
        QPixmap: The picture (null if the file can't be read)"""
    if avatar_name not in _avatar_pixmaps:
        image = QImageReader(f"{avatar_path}{avatar_name}.png").read()
        if max(image.width(), image.height()) > AVATAR_MAX_SIDE:
            image = image.scaled(AVATAR_MAX_SIDE, AVATAR_MAX_SIDE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        _avatar_pixmaps[avatar_name] = QPixmap.fromImage(image)
    return _avatar_pixmaps[avatar_name]

main_style_file_path = os.path.join(os.path.dirname(__file__), "styles/main.qss")
main_style_file = QFile(main_style_file_path)
main_style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
main_stylesheet = scale_stylesheet(QTextStream(main_style_file).readAll())

windows_style_file_path = os.path.join(os.path.dirname(__file__), "styles/windows.qss")
windows_style_file = QFile(windows_style_file_path)
windows_style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
windows_stylesheet = scale_stylesheet(QTextStream(windows_style_file).readAll())

# Fonts
QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Bubble Love Demo.otf"))
QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Game On_PersonalUseOnly.ttf"))
QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Chilanka-Regular.ttf"))

# Settings
settings = Settings()
langue = LangueSettings(settings.accessibility_data[1][1])

# Audio
button_sound = ButtonSoundEffect(settings)
ambiance_sound = AmbianceSoundEffect(settings)
music = MusicPlayer(settings)

def center_window(object: object):
    """Center a window on the screen"""
    qr = object.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    object.move(qr.topLeft())

_send_lock = threading.Lock()  # the window and the reception thread (PING_) both send
server_address: tuple[str, int] | None = None  # set once connected, used to reconnect
quitting = False  # True once the player quits on purpose: don't reconnect
session_taken = False  # the game was opened again and took this seat: this window must stop


def send_server(message: str | bytes):
    """Send one message to the server (a newline is added to mark its end)"""
    if isinstance(message, bytes):
        message = message.decode()
    try:
        with _send_lock:
            client_socket.sendall(encode(message))
    except OSError:  # connection lost: the reception thread is reconnecting
        infos_logger.log_infos("[SOCKET]", f"Not sent (no connection): {message}")
        return
    infos_logger.log_infos("[SEND]", message)


def new_client_socket() -> socket.socket:
    """Replace the connection by a new (not yet connected) one, to reconnect."""
    global client_socket
    with _send_lock:
        try:
            client_socket.close()
        except OSError:
            pass
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return client_socket


def quit_server(keep_seat: bool = False):
    """The game is closing.

    Args:
        keep_seat (bool): True during a running game: the server keeps the seat until the game
            ends and the session is kept, so starting the game again puts the player back (#10).
            False: nothing to come back to (the server removes the player), forget the session."""
    global quitting
    quitting = True
    if session_taken or keep_seat:  # session_taken: it now belongs to the other window
        return
    clear_session()