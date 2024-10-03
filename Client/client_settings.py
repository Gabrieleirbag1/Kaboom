import os, shutil, random, json, sys
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

# Create the base path
if sys.platform == "win32":
    base_path = os.path.join(os.getenv('APPDATA'), "Kaboom")
else:
    base_path = os.path.join(os.path.expanduser("~"), ".config", "kaboom")

# Create the settings and confs directories if they don't exist
os.makedirs(base_path, exist_ok=True)
os.makedirs(os.path.join(base_path, "settings"), exist_ok=True)
os.makedirs(os.path.join(base_path, "confs"), exist_ok=True)

# Path to the settings and confs files
settings_file_path = os.path.join(base_path, "settings")
confs_file_path = os.path.join(base_path, "confs")

# Path to the local settings and confs files
local_settings_file_path = os.path.join(os.path.dirname(__file__), "settings")
local_confs_file_path = os.path.join(os.path.dirname(__file__), "confs")

class FileManager:
    """Class to manage files"""
    def __init__(self, base_path: str, local_settings_file_path: str):
        """Initializes the FileManager class
        
        Args:
            base_path (str): Path to the base directory
            local_settings_file_path (str): Path to the local settings directory"""
        self.base_path = base_path
        self.local_settings_file_path = local_settings_file_path
        self.files_content = self.load_files_content()
        self.create_files()

    def load_files_content(self):
        """Loads the content of the files"""
        files_content = {}
        for file_name in os.listdir(self.local_settings_file_path):
            file_path = os.path.join(self.local_settings_file_path, file_name)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    files_content[file_name] = file.read()
        return files_content

    def create_files(self):
        """Creates the files if they don't exist"""
        for file_name, content in self.files_content.items():
            file_path = os.path.join(self.base_path, file_name)
            if not os.path.exists(file_path): # If the file doesn't exist
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)

# Create settings and confs files
file_manager_settings = FileManager(settings_file_path, local_settings_file_path)
confs_manager_settings = FileManager(confs_file_path, local_confs_file_path)

class Settings():
    """Settings class: Manages game settings
    
    Attributes:
        accessibility (Accessibility): Object containing the accessibility settings of the game"""
    def __init__(self):
        """Constructor of the Settings class"""
        self.accessibility = self.Accessibility(self)
        self.get_settings()

    def read_settings(self, file_path: str) -> list:
        """
        Reads a CSV file
        
        Args:
            file_path (str): Path to the CSV file

        Returns:
            list: Data from the CSV file
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as file:
            for eachLine in file:
                line = eachLine.strip().split(',')
                data.append(line)
        return data

    def get_settings(self):
        """Retrieves game settings"""
        self.sound_global_data = self.read_settings(f"{settings_file_path}/user_sound_global.csv")
        self.music_data = self.read_settings(f"{settings_file_path}/sound_music.csv")
        self.ambiance_data = self.read_settings(f"{settings_file_path}/sound_ambiance.csv")
        self.sound_effects_data = self.read_settings(f"{settings_file_path}/sound_effects.csv")
        self.accessibility_data = self.read_settings(f"{settings_file_path}/user_accessibility.csv")

    def write_settings(self, concern: str, data: int, mute: str = "NotSound", file: str = None):
        """
        Writes data to a CSV file
        
        Args:
            concern (str): Parameter to modify
            data (int): Data to write
            mute (str): Mute mode or not
            file (str): File to modify
        """
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
        """Resets game settings"""
        shutil.copyfile(f"{settings_file_path}/sound_global.csv", f"{settings_file_path}/user_sound_global.csv")
        shutil.copyfile(f"{settings_file_path}/accessibility.csv", f"{settings_file_path}/user_accessibility.csv")
        self.get_settings()

    class Accessibility():
        """Accessibility class: Manages game accessibility settings
        
        Attributes:
            settings (object): Object containing the settings of the game"""
        def __init__(self, settings_object: object):
            """Constructor of the Accessibility class
            
            Args:
                settings_object (object): Object containing the settings of the game"""
            self.settings = settings_object

        def change_langue(self, langue: str):
            """Changes the game language
            
            Args:
                langue (str): The language to use"""
            self.settings.write_settings("language", langue, file="user_accessibility.csv")
        
        def change_theme(self, color1: str, color2: str):
            """Changes the game theme
            
            Args:
                color1 (str): The first color of the theme
                color2 (str): The second color of the theme"""
            theme = f"{color1}/{color2}"
            self.settings.write_settings("theme", theme, file="user_accessibility.csv")

        def change_animations(self, state: str):
            """Changes the state of animations
            
            Args:
                state (str): The state of animations"""
            self.settings.accessibility_data[2][1] = state
            self.settings.write_settings("animations", state, file="user_accessibility.csv")

        def change_borders(self, state: str):
            """Changes the state of borders
            
            Args:
                state (str): The state of borders"""
            self.settings.accessibility_data[3][1] = state
            self.settings.write_settings("borders", state, file="user_accessibility.csv")

class Configurations():
    """Configurations class: Manages game configurations"""
    def __init__(self):
        """Constructor of the Configurations class"""
        self.get_settings()
        self.set_mqtt()
        self.set_socket()

    def read_settings(self, file_path: str) -> list:
        """
        Reads a CSV setting file
        
        Args:
            file_path (str): Path to the CSV file

        Returns:
            list: Data from the CSV file
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as file:
            for eachLine in file:
                line = eachLine.strip().split(',')
                data.append(line)
        return data

    def get_settings(self):
        """Retrieves game configurations"""
        self.mqtt_data = self.read_settings(f"{confs_file_path}/mqtt.csv")
        self.socket_data = self.read_settings(f"{confs_file_path}/socket.csv")

    def set_mqtt(self):
        """Sets MQTT parameters"""
        self.broker = self.mqtt_data[0][1]
        self.port = int(self.mqtt_data[1][1])
        self.topic = self.mqtt_data[2][1]
        self.client_id = f'publish-{random.randint(0, 1000)}'
        self.user = self.mqtt_data[3][1]
        self.password = self.mqtt_data[4][1]

    def set_socket(self):
        """Sets socket parameters"""
        self.socket_server = self.socket_data[0][1]
        self.socket_port = int(self.socket_data[1][1])

class LangueSettings():
    """LangueSettings class: Manages language settings"""
    def __init__(self, langue: str = "French"):
        """Constructor of the LangueSettings class
        
        Args:
            langue (str): The language to use (default "French")"""
        # print(langue)
        self.langue_data = self.langue_json(f"{confs_file_path}/{langue}.json")

    def langue_json(self, file_path: str) -> dict:
        """
        Reads a JSON file and returns the data
        
        Args:
            file_path (str): Path to the JSON file

        Returns:
            dict: Data from the JSON file
        """
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data