from requirements import *
from client_audio import ButtonSoundEffect, AmbianceSoundEffect, MusicPlayer
from client_settings import Settings, Configurations, LangueSettings
from client_logs import ErrorLogger, InfosLogger

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

def send_server(message: str):
    """Send a socket message to the server"""
    client_socket.send(message)
    infos_logger.log_infos("[SEND]", message.decode())