from requirements import *
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
        self.select_sound.setVolume(0.5)

        self.error_sound = QSoundEffect()
        self.error_sound.setSource(QUrl.fromLocalFile(f"{self.sound_path}Error.wav"))
        self.error_sound.setVolume(1)

        self.windows_sound = QSoundEffect()
        self.windows_sound.setSource(QUrl.fromLocalFile(f"{self.sound_path}WindowsXP.wav"))
        self.windows_sound.setVolume(0.5)

        self.ubuntu_sound = QSoundEffect()
        self.ubuntu_sound.setSource(QUrl.fromLocalFile(f"{self.sound_path}Ubuntu.wav"))
        self.ubuntu_sound.setVolume(1)

    def play_sound(self, sound_effect):
        """play_sound(sound_effect) : Fonction qui permet de jouer un effet sonore"""
        sound_effect.play()


class MusicPlayer():
    """Classe MusicPlayer : Classe qui permet de gérer la musique du jeu"""
    def __init__(self):
        """__init__() : Constructeur de la classe MusicPlayer"""
        self.musics = {
        "Energy_Wave.mp3": 70,
        "Sakura_Jazzy.mp3": 40,
        "jazz_funky.mp3": 20,
        }
        self.setup_music()

    def setup_music(self):
        self.playlist = QMediaPlaylist()
        self.musicPath = os.path.join(os.path.dirname(__file__), "audio/Music/")
        for music in self.musics:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f"{self.musicPath}{music}")))

        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        self.player.setVolume(50)
        
    def choose_music(self, index):
        """choose_music(index) : Function that plays the music at the given index"""
        self.playlist.setCurrentIndex(index)
        self.loop_music(index)
        music_file = self.playlist.media(index).canonicalUrl().fileName()
        self.player.setVolume(self.musics.get(music_file, 50))
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