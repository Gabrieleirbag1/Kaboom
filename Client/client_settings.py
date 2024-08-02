import os, shutil, random, json
import log_config

log_config.setup_logging()

settings_file_path = os.path.join(os.path.dirname(__file__), "settings")
confs_file_path = os.path.join(os.path.dirname(__file__), "confs/")

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
        with open(file_path, "r", encoding="utf-8") as file:
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
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open(path, "w", encoding="utf-8") as file:
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

        def change_langue(self, langue: str):
            """change_langue() : Fonction qui permet de changer la langue du jeu"""
            self.settings.write_settings("language", langue, file="user_accessibility.csv")
        
        def change_theme(self, color1: str, color2):
            """change_theme() : Fonction qui permet de changer le thème du jeu"""
            theme = f"{color1}/{color2}"
            self.settings.write_settings("theme", theme, file="user_accessibility.csv")

        def change_animations(self, state: str):
            """change_animations() : Fonction qui permet de changer l'état des animations"""
            self.settings.accessibility_data[2][1] = state
            self.settings.write_settings("animations", state, file="user_accessibility.csv")

        def change_borders(self, state: str):
            """change_borders() : Fonction qui permet de changer l'état des bordures"""
            self.settings.accessibility_data[3][1] = state
            self.settings.write_settings("borders", state, file="user_accessibility.csv")

class Configurations():
    """Classe Configurations : Classe qui permet de gérer les configurations du jeu"""
    def __init__(self):
        """__init__() : Constructeur de la classe Configurations"""
        self.get_settings()
        self.set_mqtt()
        self.set_socket()

    def read_settings(self, file_path: str) -> list:
        """read_settings(file_path) : Fonction qui permet de lire un fichier CSV et de retourner les données
        
        Args:
            file_path (str): Chemin du fichier CSV"""
        data = []
        with open(file_path, "r", encoding="utf-8") as file:
            for eachLine in file:
                line = eachLine.strip().split(',')
                data.append(line)
        return data

    def get_settings(self):
        """get_settings() : Fonction qui permet de récupérer les paramètres du jeu"""
        self.mqtt_data = self.read_settings(f"{confs_file_path}/mqtt.csv")
        self.socket_data = self.read_settings(f"{confs_file_path}/socket.csv")

    def set_mqtt(self):
        """set_mqtt() : Fonction qui permet de mettre en place les paramètres MQTT"""
        self.broker = self.mqtt_data[0][1]
        self.port = int(self.mqtt_data[1][1])
        self.topic = self.mqtt_data[2][1]
        self.client_id = f'publish-{random.randint(0, 1000)}'
        self.user = self.mqtt_data[3][1]
        self.password = self.mqtt_data[4][1]

    def set_socket(self):
        """set_socket() : Fonction qui permet de mettre en place les paramètres de socket"""
        self.socket_server = self.socket_data[0][1]
        self.socket_port = int(self.socket_data[1][1])

class LangueSettings():
    """Classe LangueSettings : Classe qui permet de gérer les paramètres de langue"""
    def __init__(self, langue: str = "Français"):
        """__init__() : Constructeur de la classe LangueSettings"""
        print(langue)
        self.langue_data = self.langue_json(f"{confs_file_path}/{langue}.json")

    def langue_json(self, file_path: str) -> dict:
        """langue_json(file_path) : Fonction qui permet de lire un fichier JSON et de retourner les données
        
        Args:
            file_path (str): Chemin du fichier JSON"""
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

if __name__ == "__main__":
    # settings = Settings()
    # print(settings.sound_global_data)
    # print(settings.music_data)
    # print(settings.sound_effects_data)
    # settings.write_settings("music", 50)
    # settings.get_settings()
    # print(settings.sound_global_data)
    conf = Configurations()
    print(conf.mqtt_data)
    print(conf.socket_data)
