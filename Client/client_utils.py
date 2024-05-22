from requirements import *
from client_audio import ButtonSoundEffect, AmbianceSoundEffect, MusicPlayer
from client_settings import Settings

# MQTT
broker = 'localhost'
port = 1883
topic = "test"
client_id = f'publish-{random.randint(0, 1000)}'
username = 'frigiel'
password = 'toto'

# Vars
app = QApplication(sys.argv)
screen_size = QDesktopWidget().screenGeometry()
screen_width, screen_height = screen_size.width(), screen_size.height()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None
syllabes = []
rules = [5, 7, 3, 2, 3, 1]

# Paths
image_path = os.path.join(os.path.dirname(__file__), "images/")

styles_file_path = os.path.join(os.path.dirname(__file__), "styles/client.qss")
style_file = QFile(styles_file_path)
style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
stylesheet_window = QTextStream(style_file).readAll()

QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Bubble Love Demo.otf"))
QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Game On_PersonalUseOnly.ttf"))

# Settings
settings = Settings()
# Audio
button_sound = ButtonSoundEffect(settings)
ambiance_sound = AmbianceSoundEffect(settings)
music = MusicPlayer(settings)

def center_window(object):
    """center_window(object) : Fonction qui permet de centrer une fenêtre sur l'écran"""
    qr = object.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    object.move(qr.topLeft())