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
        """Setups the MQTT settings (live typing, see server_mqtt.py).

        admin_*: how this server reaches the broker. player_*: what the players are told.
        The admin password is never in the file: it comes from KABOOM_MQTT_PASSWORD.
        KABOOM_MQTT_<KEY> overrides a key of the file (KABOOM_MQTT_ADMIN_PORT...)."""
        values = {line[0]: line[1] for line in self.mqtt_data if len(line) >= 2}

        def get(key: str) -> str:
            return os.environ.get(f"KABOOM_MQTT_{key.upper()}", values.get(key, ""))

        self.mqtt_admin_host = get("admin_host")
        self.mqtt_admin_port = int(get("admin_port") or 1883)
        self.mqtt_admin_tls = get("admin_tls") == "True"
        self.mqtt_player_host = get("player_host")
        self.mqtt_player_port = int(get("player_port") or 8883)
        self.mqtt_player_tls = get("player_tls") == "True"
        self.mqtt_admin_user = os.environ.get("KABOOM_MQTT_USER", "kaboom-admin")
        self.mqtt_admin_password = os.environ.get("KABOOM_MQTT_PASSWORD", "")

    def set_socket(self):
        """Setups the socket settings"""
        # KABOOM_SOCKET_HOST / KABOOM_SOCKET_PORT override the file (used by the tests)
        self.socket_host = os.environ.get("KABOOM_SOCKET_HOST", self.socket_data[0][1])
        self.socket_port = int(os.environ.get("KABOOM_SOCKET_PORT", self.socket_data[1][1]))
