import os
import random

confs_file_path = os.path.join(os.path.dirname(__file__), "confs/")

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
        self.username = self.mqtt_data[3][1]
        self.password = self.mqtt_data[4][1]

    def set_socket(self):
        """set_socket() : Fonction qui permet de mettre en place les paramètres de socket"""
        self.socket_host = self.socket_data[0][1]
        self.socket_port = int(self.socket_data[1][1])

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
