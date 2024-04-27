import sys, socket, threading, time, random, os, datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

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

def center_window(object):
    """center_window(object) : Fonction qui permet de centrer une fenêtre sur l'écran"""
    qr = object.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    object.move(qr.topLeft())

# Audio
class SoundEffect():
    """Classe SoundEffect : Classe qui permet de gérer les effets sonores du jeu"""
    def __init__(self):
        """__init__() : Constructeur de la classe SoundEffect"""
        self.sound_path = os.path.join(os.path.dirname(__file__), "audio/Sound/")
        self.setup_sound_effects()

    def setup_sound_effects(self):
        """setup_sound_effects() : Fonction qui permet de charger les effets sonores du jeu"""
        self.select_sound = QSoundEffect()
        self.select_sound.setSource(QUrl.fromLocalFile(f"{self.sound_path}Select.wav"))
        self.select_sound.setVolume(1)

        self.error_sound = QSoundEffect()
        self.error_sound.setSource(QUrl.fromLocalFile(f"{self.sound_path}Error.wav"))

    def play_sound(self, sound_effect):
        """play_sound(sound_effect) : Fonction qui permet de jouer un effet sonore"""
        sound_effect.play()


class MusicPlayer():
    """Classe MusicPlayer : Classe qui permet de gérer la musique du jeu"""
    def __init__(self):
        """__init__() : Constructeur de la classe MusicPlayer"""
        self.playlist = QMediaPlaylist()
        self.musicPath = os.path.join(os.path.dirname(__file__), "audio/Music/")
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f"{self.musicPath}Energy_Wave.mp3")))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f"{self.musicPath}Sakura_Jazzy.mp3")))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f"{self.musicPath}jazz_funky.mp3")))
        # self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f"{self.musicPath}Select.mp3")))

        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        self.player.setVolume(50)
        
    def choose_music(self, index):
        """choose_music(index) : Function that plays the music at the given index"""
        self.playlist.setCurrentIndex(index)
        self.loop_music(index)
        self.player.play()

    def loop_music(self, index):
        """loop_music(index) : Function that sets the music at the given index to loop"""
        self.playlist.setCurrentIndex(index)
        self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
    
    def play_music(self):
        """play_music() : Fonction qui permet de jouer la musique du jeu"""
        self.player.play()

    def stop_music(self):
        """stop_music() : Fonction qui permet d'arrêter la musique du jeu"""
        self.player.stop()

sound = SoundEffect()
music = MusicPlayer()