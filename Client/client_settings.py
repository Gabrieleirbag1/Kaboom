import os
import shutil

settings_file_path = os.path.join(os.path.dirname(__file__), "settings")

class Settings():
    """Classe Settings : Classe qui permet de gérer les paramètres du jeu"""
    def __init__(self):
        """__init__() : Constructeur de la classe Settings"""
        self.accessibility = self.Accessibility(self)
        self.get_settings()

    def read_settings(self, file_path: str) -> list:
        """read_settings(file_path) : Fonction qui permet de lire un fichier CSV et de retourner les données
        
        Args:
            file_path (str): Chemin du fichier CSV"""
        data = []
        with open(file_path, "r") as file:
            for eachLine in file:
                line = eachLine.strip().split(',')
                data.append(line)
        return data

    def get_settings(self):
        """get_settings() : Fonction qui permet de récupérer les paramètres du jeu"""
        self.sound_global_data = self.read_settings(f"{settings_file_path}/user_sound_global.csv")
        self.music_data = self.read_settings(f"{settings_file_path}/sound_music.csv")
        self.ambiance_data = self.read_settings(f"{settings_file_path}/sound_ambiance.csv")
        self.sound_effects_data = self.read_settings(f"{settings_file_path}/sound_effects.csv")
        self.accessibility_data = self.read_settings(f"{settings_file_path}/user_accessibility.csv")

    def write_settings(self, concern: str, data: int, mute: str = "NotSound", file: str = None):
        """write_settings(data) : Fonction qui permet d'écrire des données dans un fichier CSV
        
        Args:
            concern (str): Paramètre à modifier
            data (int): Données à écrire
            mute (str): Mode muet ou non
            file (str): Fichier à modifier"""
        path = os.path.join(settings_file_path, file)
        with open(path, "r") as file:
            lines = file.readlines()
        with open(path, "w") as file:
            for line in lines:
                line = line.strip().split(',')
                if line[0] == concern:
                    line[1] = str(data)
                    line[2] = mute
                file.write(','.join(line) + '\n')

    def reset_settings(self):
        """reset_settings() : Fonction qui permet de réinitialiser les paramètres du jeu"""
        shutil.copyfile(f"{settings_file_path}/sound_global.csv", f"{settings_file_path}/user_sound_global.csv")
        shutil.copyfile(f"{settings_file_path}/accessibility.csv", f"{settings_file_path}/user_accessibility.csv")
        self.get_settings()

    class Accessibility():
        """Classe Accessibility : Classe qui permet de gérer l'accessibilité du jeu"""
        def __init__(self, settings_object):
            """__init__() : Constructeur de la classe Accessibility"""
            self.settings = settings_object

        def change_language(self, language: str):
            """change_language() : Fonction qui permet de changer la langue du jeu"""
            self.settings.write_settings("language", language, file="user_accessibility.csv")

if __name__ == "__main__":
    settings = Settings()
    print(settings.sound_global_data)
    print(settings.music_data)
    print(settings.sound_effects_data)
    settings.write_settings("music", 50)
    settings.get_settings()
    print(settings.sound_global_data)
