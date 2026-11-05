from requirements import *
from client_audio import ButtonSoundEffect, AmbianceSoundEffect, MusicPlayer
from client_settings import Settings, Configurations, LangueSettings
from client_logs import ErrorLogger, InfosLogger
from client_protocol import encode, MessageBuffer, PROTOCOL_VERSION, is_valid_text_field
from client_session import save_session, load_session, clear_session

ErrorLogger.setup_logging()

infos_logger = InfosLogger()
infos_logger.log_infos("[START]", "Client started")

# MQTT & Socket
confs = Configurations()

# Vars
if sys.platform == "win32":
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
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None
syllabes = []
rules = [7, 9, 3, 2, 3, 1, 0] # Minimum time, maximum time, lifes, minimum syllables, maximum syllables, number of repetitions, death mode code

# Paths
image_path = os.path.join(os.path.dirname(__file__), "images/")
avatar_path = os.path.join(image_path, "avatars/")
tombstone_path = os.path.join(image_path, "tombes/")

main_style_file_path = os.path.join(os.path.dirname(__file__), "styles/main.qss")
main_style_file = QFile(main_style_file_path)
main_style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
main_stylesheet = QTextStream(main_style_file).readAll()

windows_style_file_path = os.path.join(os.path.dirname(__file__), "styles/windows.qss")
windows_style_file = QFile(windows_style_file_path)
windows_style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
windows_stylesheet = QTextStream(windows_style_file).readAll()

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


def quit_server():
    """The player quits on purpose: tell the server to free the seat now, and forget the session."""
    global quitting
    quitting = True
    if session_taken:  # the session now belongs to the other window: keep it
        return
    send_server("QUIT_|")
    clear_session()