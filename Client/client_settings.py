import os, shutil, random, json, sys, logging
from client_logs import ErrorLogger, base_path

#ErrorLogger.setup_logging()

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
    def __init__(self, base_path: str, local_settings_file_path: str, always_update: tuple[str, ...] = ()):
        """Initializes the FileManager class
        
        Args:
            base_path (str): Path to the base directory
            local_settings_file_path (str): Path to the local settings directory
            always_update (tuple[str, ...]): File extensions to overwrite when the game's own copy
                changed (e.g. language files after an update). Other files are only created once,
                so the player's changes are kept."""
        self.base_path = base_path
        self.local_settings_file_path = local_settings_file_path
        self.always_update = always_update
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
            if os.path.exists(file_path):
                if not (self.always_update and file_name.endswith(self.always_update)):
                    continue  # keep the player's copy
                with open(file_path, "r", encoding="utf-8") as file:
                    if file.read() == content:
                        continue
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

# Create settings and confs files. The sound lists (sound_*.csv) belong to the game, not the player:
# refreshed after an update (a new sound). The player's choices are in the user_*.csv files.
file_manager_settings = FileManager(settings_file_path, local_settings_file_path,
                                    always_update=("sound_ambiance.csv", "sound_effects.csv", "sound_music.csv"))
# Language files (.json) are refreshed after an update; socket.csv keeps the player's values
confs_manager_settings = FileManager(confs_file_path, local_confs_file_path, always_update=(".json",))
# Older versions kept a shared broker password in confs/mqtt.csv. The server now gives each player
# their own account for live typing (#20), so remove the old file.
try:
    os.remove(os.path.join(confs_file_path, "mqtt.csv"))
except FileNotFoundError:
    pass

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
        if not self.valid_sound_settings(self.sound_global_data):
            # Broken file (e.g. the game was closed while writing it): start again from the defaults
            logging.warning("user_sound_global.csv is broken, using the default volumes")
            shutil.copyfile(f"{settings_file_path}/sound_global.csv", f"{settings_file_path}/user_sound_global.csv")
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
        rows = []
        for row in self.read_settings(path):
            if row[0] == concern:
                row[1:3] = [str(data), mute]
            rows.append(row)
        self.write_rows(path, rows)

    def save_sound_settings(self):
        """Writes every volume and mute state (sound_global_data) to user_sound_global.csv at once"""
        self.write_rows(os.path.join(settings_file_path, "user_sound_global.csv"), self.sound_global_data)

    def write_rows(self, path: str, rows: list):
        """
        Writes CSV rows safely: the file is either the old one or the new one, never half written.
        A file locked by another program (antivirus...) is logged and written at the next save.

        Args:
            path (str): Path to the CSV file
            rows (list): Rows to write
        """
        temp_path = f"{path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                file.writelines(','.join(str(value) for value in row) + '\n' for row in rows)
            os.replace(temp_path, path)
        except OSError:
            logging.exception(f"Could not save the settings in {path}")

    @staticmethod
    def valid_sound_settings(rows: list) -> bool:
        """True if the rows read from user_sound_global.csv are usable (4 lines: name,volume,mute)"""
        try:
            return len(rows) >= 4 and all(len(row) >= 3 and 0 <= int(row[1]) <= 100 for row in rows[:4])
        except ValueError:
            return False

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
        self.socket_data = self.read_settings(f"{confs_file_path}/socket.csv")

    def set_socket(self):
        """Sets socket parameters.

        socket.csv: host, port and tls (encrypted connection, #19: True unless the file says
        tls,False, so the files of older versions stay encrypted). KABOOM_SERVER_HOST / _PORT /
        _TLS override the file, KABOOM_SERVER_CAFILE replaces the trusted certificates (tests)."""
        values = {line[0]: line[1] for line in self.socket_data if len(line) >= 2}
        host = values.get("host") or values.get("server") or self.socket_data[0][1]
        port = values.get("port") or self.socket_data[1][1]
        self.socket_server = os.environ.get("KABOOM_SERVER_HOST", host)
        self.socket_port = int(os.environ.get("KABOOM_SERVER_PORT", port))
        self.socket_tls = os.environ.get("KABOOM_SERVER_TLS", values.get("tls", "True")) != "False"
        self.socket_cafile = os.environ.get("KABOOM_SERVER_CAFILE")  # None: the usual (certifi)

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