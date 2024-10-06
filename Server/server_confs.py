import os, random
from server_logs import ErrorLogger

ErrorLogger.setup_logging()

confs_file_path = os.path.join(os.path.dirname(__file__), "confs/")

class Configurations():
    """Class allowing to manage the configurations of the server"""
    def __init__(self):
        """Initializes the Configurations class"""
        self.get_settings()
        self.set_mqtt()
        self.set_socket()

    def read_settings(self, file_path: str) -> list:
        """Reads the settings from a file

        Args:
            file_path (str): The path to the file to read

        Returns:
            list: The list of settings read from the file
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as file:
            for eachLine in file:
                line = eachLine.strip().split(',')
                data.append(line)
        return data

    def get_settings(self):
        """Get the settings from the configuration files"""
        self.mqtt_data = self.read_settings(f"{confs_file_path}/mqtt.csv")
        self.socket_data = self.read_settings(f"{confs_file_path}/socket.csv")

    def set_mqtt(self):
        """Setups the MQTT settings"""
        self.broker = self.mqtt_data[0][1]
        self.port = int(self.mqtt_data[1][1])
        self.topic = self.mqtt_data[2][1]
        self.client_id = f'publish-{random.randint(0, 1000)}'
        self.username = self.mqtt_data[3][1]
        self.password = self.mqtt_data[4][1]

    def set_socket(self):
        """Setups the socket settings"""
        self.socket_host = self.socket_data[0][1]
        self.socket_port = int(self.socket_data[1][1])
