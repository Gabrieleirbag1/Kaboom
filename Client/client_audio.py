from requirements import *

class SoundEffect():
    """Classe SoundEffect : Classe qui permet de gérer les effets sonores du jeu"""
    def __init__(self, settings_object):
        """__init__() : Constructeur de la classe SoundEffect"""
        self.settings : object = settings_object
        self.sound_path = os.path.join(os.path.dirname(__file__), "audio/Sound/")
        self.sounds : dict[str : list] = {
            "Select.wav": self.settings.sound_effects_data[0],
            "Error.wav": self.settings.sound_effects_data[1],
            "WindowsXP.wav": self.settings.sound_effects_data[2],
            "Ubuntu.wav": self.settings.sound_effects_data[3],
        }
        self.setup_sound_effects()
        self.check_muted()
        self.change_volume(int(self.settings.sound_global_data[3][1]))

    def setup_sound_effects(self):
        """setup_sound_effects() : Fonction qui permet de charger les effets sonores du jeu"""
        self.sound_objects : list = []
        for sound in self.sounds:
            setattr(self, self.sounds[sound][0], QSoundEffect())
            getattr(self, self.sounds[sound][0]).setSource(QUrl.fromLocalFile(f"{self.sound_path}{sound}"))
            getattr(self, self.sounds[sound][0]).setVolume(float(self.sounds[sound][1]))
            self.sound_objects.append(getattr(self, self.sounds[sound][0]))

    def play_sound(self, sound_effect):
        """play_sound(sound_effect) : Fonction qui permet de jouer un effet sonore
        
        Args:
            sound_effect (QSoundEffect): Effet sonore à jouer"""
        if not sound_effect.isMuted():
            sound_effect.play()

    def mute_sound_effects(self):
        """mute_sound() : Fonction qui permet de mettre en mode muet les effets sonores"""
        if getattr(self, self.sounds["Select.wav"][0]).isMuted():
            self.settings.sound_global_data[3][2] = "notmuted"
            for sound in self.sound_objects:
                sound.setMuted(False)
        else:
            self.settings.sound_global_data[3][2] = "muted"
            for sound in self.sound_objects:
                sound.setMuted(True)
        
        self.settings.write_settings(
        concern = self.settings.sound_global_data[3][0], 
        data = self.settings.sound_global_data[3][1], 
        mute = self.settings.sound_global_data[3][2],
        file = "user_sound_global.csv")

    def check_muted(self):
        """check_muted() : Fonction qui permet de vérifier si les effets sonores sont en mode muet"""
        if self.settings.sound_global_data[3][2] == "muted":
            for sound in self.sounds:
                getattr(self, self.sounds[sound][0]).setMuted(True)
        else:
            for sound in self.sounds:
                getattr(self, self.sounds[sound][0]).setMuted(False)

    def change_volume(self, volume : int):
        """change_volume(volume) : Fonction qui permet de changer le volume des effets sonores
        
        Args:
            volume (int): Volume des effets sonores"""
        for sound in self.sounds:
            getattr(self, self.sounds[sound][0]).setVolume(float(self.sounds[sound][1]) * (volume / 100))
        self.settings.sound_global_data[3][1] = volume
        self.settings.write_settings(
            concern = self.settings.sound_global_data[3][0], 
            data = self.settings.sound_global_data[3][1], 
            mute = self.settings.sound_global_data[3][2],
            file = "user_sound_global.csv")

class MusicPlayer():
    """Classe MusicPlayer : Classe qui permet de gérer la musique du jeu"""
    def __init__(self, settings):
        """__init__() : Constructeur de la classe MusicPlayer"""
        self.settings : object = settings
        self.musics : dict[str : int] = {
        "Energy_Wave.mp3": self.settings.music_data[0][1],
        "Sakura_Jazzy.mp3": self.settings.music_data[1][1],
        "jazz_funky.mp3": self.settings.music_data[2][1],
        }
        self.musics_default = copy.deepcopy(self.musics)
        self.setup_music()
        self.check_muted()
        self.change_volume(int(self.settings.sound_global_data[1][1]))

    def setup_music(self):
        self.playlist = QMediaPlaylist()
        self.musicPath = os.path.join(os.path.dirname(__file__), "audio/Music/")
        for music in self.musics:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f"{self.musicPath}{music}")))
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        
    def choose_music(self, index):
        """choose_music(index) : Function that plays the music at the given index
        
        Args:
            index (int): Index of the music in the playlist"""
        self.playlist.setCurrentIndex(index)
        self.loop_music(index)
        music_file = self.playlist.media(index).canonicalUrl().fileName()
        self.player.setVolume(int(self.musics.get(music_file, 50))) #50 is the default volume
        self.player.play()

    def loop_music(self, index):
        """loop_music(index) : Function that sets the music at the given index to loop
        
        Args:
            index (int): Index of the music in the playlist"""
        self.playlist.setCurrentIndex(index)
        self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
    
    def play_music(self):
        """play_music() : Fonction qui permet de jouer la musique du jeu"""
        self.player.play()

    def mute_music(self):
        """mute_music() : Fonction qui permet d'arrêter la musique du jeu"""
        if self.player.isMuted():
            self.settings.sound_global_data[1][2] = "notmuted"
            self.player.setMuted(False)
        else:
            self.settings.sound_global_data[1][2] = "muted"
            self.player.setMuted(True)
        self.settings.write_settings(
            concern = self.settings.sound_global_data[1][0], 
            data = self.settings.sound_global_data[1][1], 
            mute = self.settings.sound_global_data[1][2],
            file = "user_sound_global.csv")

    def check_muted(self):
        """check_muted() : Fonction qui permet de vérifier si la musique est en mode muet"""
        if self.settings.sound_global_data[1][2] == "muted":
            self.player.setMuted(True)
        else:
            self.player.setMuted(False)

    def change_volume(self, volume : int):
        """change_volume(volume) : Fonction qui permet de changer le volume de la musique
        
        Args:
            volume (int): Volume de la musique"""
        for music, music_default in zip(self.musics, self.musics_default):
            self.musics[music] = int(self.musics_default[music_default]) * (volume / 100)
            if music == self.playlist.currentMedia().canonicalUrl().fileName():
                self.player.setVolume(int(self.musics[music]))
        self.settings.sound_global_data[1][1] = volume
        self.settings.write_settings(
            concern = self.settings.sound_global_data[1][0], 
            data = self.settings.sound_global_data[1][1], 
            mute = self.settings.sound_global_data[1][2],
            file = "user_sound_global.csv")