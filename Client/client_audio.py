from requirements import *
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

class SoundEffect():
    """Class which allows to manage the sound effects of the game
    
    Attributes:
        settings_object (object): Object containing the settings of the game
        sounds (dict[str: list]): Dictionary containing the sound effects
        ligne_csv (int): Line of the csv file"""
    def __init__(self, settings_object: object, sounds: dict[str: list], ligne_csv: int):
        """Constructor of the SoundEffect class
        
        Args:
            settings_object (object): Object containing the settings of the game
            sounds (dict[str: list]): Dictionary containing the sound effects
            ligne_csv (int): Line of the csv file"""
        self.settings: object = settings_object
        self.sound_path = os.path.join(os.path.dirname(__file__), "audio/Sound/")
        self.sounds: dict[str: list] = sounds
        self.ligne_csv: int = ligne_csv
        self.setup_sound_effects()
        self.check_muted()
        self.change_volume(int(self.settings.sound_global_data[ligne_csv][1]))

    def setup_sound_effects(self):
        """setup_sound_effects() : Fonction qui permet de charger les effets sonores du jeu"""
        self.sound_objects : list = []
        for sound in self.sounds:
            setattr(self, self.sounds[sound][0], QSoundEffect())
            getattr(self, self.sounds[sound][0]).setSource(QUrl.fromLocalFile(f"{self.sound_path}{sound}"))
            getattr(self, self.sounds[sound][0]).setVolume(float(self.sounds[sound][1]))
            self.sound_objects.append(getattr(self, self.sounds[sound][0]))

    def play_sound(self, sound_effect: object):
        """Function that plays the sound effect
        
        Args:
            sound_effect (object): The sound effect to play"""
        if not sound_effect.isMuted():
            sound_effect.play()

    def mute_sound_effects(self):
        """Function that mutes the sound effects"""
        if self.sound_objects[0].isMuted():
            self.settings.sound_global_data[self.ligne_csv][2] = "notmuted"
            for sound in self.sound_objects:
                sound.setMuted(False)
        else:
            self.settings.sound_global_data[self.ligne_csv][2] = "muted"
            for sound in self.sound_objects:
                sound.setMuted(True)
        
        self.settings.write_settings(
            concern = self.settings.sound_global_data[self.ligne_csv][0], 
            data = self.settings.sound_global_data[self.ligne_csv][1], 
            mute = self.settings.sound_global_data[self.ligne_csv][2],
            file = "user_sound_global.csv")

    def check_muted(self):
        """Function that checks if the sound effects are muted"""
        if self.settings.sound_global_data[self.ligne_csv][2] == "muted":
            for sound in self.sounds:
                getattr(self, self.sounds[sound][0]).setMuted(True)
        else:
            for sound in self.sounds:
                getattr(self, self.sounds[sound][0]).setMuted(False)

    def change_volume(self, volume: int):
        """Function that changes the volume of the sound effects
        
        Args:
            volume (int): The volume of the sound effects"""
        for sound in self.sounds:
            getattr(self, self.sounds[sound][0]).setVolume(float(self.sounds[sound][1]) * (volume / 100))
        self.settings.sound_global_data[self.ligne_csv][1] = volume
        self.settings.write_settings(
            concern = self.settings.sound_global_data[self.ligne_csv][0], 
            data = self.settings.sound_global_data[self.ligne_csv][1], 
            mute = self.settings.sound_global_data[self.ligne_csv][2],
            file = "user_sound_global.csv")
        
class AmbianceSoundEffect():
    """AmbianceSoundEffect: Class that manages ambiance sound effects
    
    Attributes:
        sound_effects (SoundEffect): Object containing the sound effects"""
    def __init__(self, settings: object):
        """Constructor of the AmbianceSoundEffect class
        
        Args:
            settings (object): Object containing the settings of the game"""
        sounds: dict[str: list] = {
            "Victory.wav": settings.ambiance_data[0],
            "Next.wav": settings.ambiance_data[1],
            "tombe1.wav": settings.ambiance_data[2],
            "tombe2.wav": settings.ambiance_data[3],
            "tombe3.wav": settings.ambiance_data[4],
            "tombe4.wav": settings.ambiance_data[5],
        }
        self.sound_effects = SoundEffect(settings, sounds, 2)

class ButtonSoundEffect():
    """ButtonSoundEffect: Class that manages button sound effects
    
    Attributes:
        sound_effects (SoundEffect): Object containing the sound effects"""
    def __init__(self, settings: object):
        """Constructor of the ButtonSoundEffect class
        
        Args:
            settings (object): Object containing the settings of the game"""
        sounds: dict[str: list] = {
            "Select.wav": settings.sound_effects_data[0],
            "Error.wav": settings.sound_effects_data[1],
            "WindowsXP.wav": settings.sound_effects_data[2],
            "Ubuntu.wav": settings.sound_effects_data[3],
        }
        self.sound_effects = SoundEffect(settings, sounds, 3)
        
class MusicPlayer():
    """MusicPlayer: Class that manages the game's music
    
    Attributes:
        settings (object): Object containing the settings of the game"""
    def __init__(self, settings: object):
        """Constructor of the MusicPlayer class
        
        Args:
            settings (object): Object containing the settings of the game"""
        self.settings: object = settings
        self.musics: dict[str : int] = {
            "Energy_Wave.mp3": self.settings.music_data[0][1],
            "Sakura_Jazzy.mp3": self.settings.music_data[1][1],
            "jazz_funky.mp3": self.settings.music_data[2][1],
        }
        self.musics_default = copy.deepcopy(self.musics)
        self.setup_music()
        self.check_muted()
        self.change_volume(int(self.settings.sound_global_data[1][1]))

    def setup_music(self):
        """Function that sets up the music"""
        self.playlist = QMediaPlaylist()
        self.musicPath = os.path.join(os.path.dirname(__file__), "audio/Music/")
        for music in self.musics:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f"{self.musicPath}{music}")))
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        
    def choose_music(self, index: int):
        """Function that plays the music at the given index
        
        Args:
            index (int): Index of the music in the playlist"""
        self.playlist.setCurrentIndex(index)
        self.loop_music(index)
        music_file = self.playlist.media(index).canonicalUrl().fileName()
        self.player.setVolume(int(self.musics.get(music_file, 50))) #50 is the default volume
        self.player.play()

    def loop_music(self, index: int):
        """Function that sets the music at the given index to loop
        
        Args:
            index (int): Index of the music in the playlist"""
        self.playlist.setCurrentIndex(index)
        self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
    
    def play_music(self):
        """Function that plays the game's music"""
        self.player.play()

    def mute_music(self):
        """Function that mutes the game's music"""
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
        """Function that checks if the music is muted"""
        if self.settings.sound_global_data[1][2] == "muted":
            self.player.setMuted(True)
        else:
            self.player.setMuted(False)

    def change_volume(self, volume: int):
        """Function that changes the volume of the music
        
        Args:
            volume (int): Volume of the music"""
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