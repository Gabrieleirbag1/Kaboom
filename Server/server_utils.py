import csv, os, time, random, unidecode, sys
from socket import socket as socket
from server_confs import Configurations
from server_logs import ErrorLogger, InfosLogger

ErrorLogger.setup_logging()
infos_logger = InfosLogger()
infos_logger.log_infos("[START]", "Server started")

def send_client(conn: socket, message: str) -> None:
    """
    Sends a message to the client
    Args:
        conn (socket.socket): Client connection socket
        message (str): Message to send to the client
    """
    try:
        conn.send(message.encode())
        infos_logger.log_infos("[SEND]", f"{message} - {str(conn)}")
    except BrokenPipeError:
        infos_logger.log_infos("[SOCKET]", "Client disconnected (BrokenPipeError)")
        pass
    except ConnectionResetError:
        infos_logger.log_infos("[SOCKET]", "Client disconnected (ConnectionResetError)")
        pass
    except OSError:
        infos_logger.log_infos("[SOCKET]", "Client disconnected (OSError)")
        pass

def read_words_from_file(langue: str = "Français") -> list:
    """
    Reads words from a CSV file based on the specified language.

    Args:
        langue (str): Language of the file to read. Defaults to "Français".

    Returns:
        list: List of words read from the file.
    """
    chemin_csv = os.path.join(os.path.dirname(__file__), f"../Dictionary/{langue}/Syllabes/syllabes.csv")

    if not os.path.isfile(chemin_csv):
        print(f"File not found: {chemin_csv}")
        chemin_csv = os.path.join(os.path.dirname(__file__), f"../Dictionary/English/Syllabes/syllabes.csv")
    
    with open(chemin_csv, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        words = [line.strip().replace(',', '') for line in lines]  # Supprimer les caractères d'espacement comme les sauts de ligne
    
    return words

def get_csv(csv_file_path: str) -> list:
    """
    Retrieves data from a CSV file.

    Args:
        csv_file_path (str): Path to the CSV file to read.

    Returns:
        list: List of the first column's values from the CSV file.
    """
    premiere_colonne = []

    with open(csv_file_path, 'r', newline='', encoding='utf-8') as fichier_csv:
        lecteur_csv = csv.reader(fichier_csv)
        for ligne in lecteur_csv:
            if ligne:  # Vérifier si la ligne n'est pas vide
                premiere_colonne.append(ligne[0])

    return premiere_colonne

def add_waiting_room_players(game_name: str):
    """Add players to the waiting room
    
    Args:
        game_name (str): Game name
    """
    def get_game_elements():
        """Get game elements"""
        for game in game_list["Name"]:
            if game == game_name:
                game_creator = game_list["Creator"][game_list["Name"].index(game)]
                game_password = game_list["Password"][game_list["Name"].index(game)]
                game_private = game_list["Private"][game_list["Name"].index(game)]
                return f"{game_name}|{game_creator}|{game_password}|{game_private}"
    
    def check_players_waiting() -> tuple:
        """Check the number of players waiting in the waiting room
        
        Returns:
            tuple: Number of players waiting in the waiting room, list of players waiting in the waiting room
        """
        number_of_players = max_players - game_list["Players_Number"][game_list["Name"].index(game_name)]
        game_waiting_room_list = []
        for player in waiting_room["Player"]:
            if waiting_room["Game"][waiting_room["Player"].index(player)] == game_name:
                game_waiting_room_list.append(player)
        return number_of_players, game_waiting_room_list

    def add_players_waiting():
        """Add players to the waiting room"""
        i = 0
        game_elements = get_game_elements()
        number_of_players, game_waiting_room_list = check_players_waiting()
        while i < number_of_players:
            try:
                player = game_waiting_room_list[i]
                conn = waiting_room["Conn"][waiting_room["Player"].index(player)]
                looking_for_games_players.remove(conn)
                send_client(conn, f"JOIN_STATE|GAME-JOINED|{game_elements}|{player}|")
                waiting_room_index = waiting_room["Player"].index(player)
                waiting_room["Conn"].pop(waiting_room_index)
                waiting_room["Player"].pop(waiting_room_index)
                waiting_room["Game"].pop(waiting_room_index)
                i+=1
            except IndexError:
                break
    try:
        add_players_waiting()
    except ValueError:
        infos_logger.log_infos("[HANDLED ERROR]", "ValueError, game probably does not exist anymore (Waiting Room)")

def convert_word(word: str) -> str:
    """Ignore the accents and convert the word to lowercase

    Args:
        word (str): Word to convert

    Returns:
        str: Converted word
    """
    word = unidecode.unidecode(word)  # Convertir les caractères spéciaux en caractères ASCII
    word = word.lower()  # Convertir les majuscules en minuscules
    return word

def bool_convert(boolean: str) -> bool:
    """Convert a string to a boolean

    Args:
        boolean (str): String to convert

    Returns:
        bool: Converted boolean
    """
    if boolean == "False":
        return False
    else:
        return True
#Mqtt
confs = Configurations()

confs.broker = 'localhost'
confs.port = 1883
confs.topic = "test"
confs.client_id = f'publish-{random.randint(0, 1000)}'
confs.username = 'frigiel'
confs.password = 'toto'

# Loads the dictionaries
for dossier in os.listdir(os.path.join(os.path.dirname(__file__), "../Dictionary")):
    chemin_du_fichier_csv = os.path.join(os.path.dirname(__file__), f"../Dictionary/{dossier}/Dictionary/dictionary.csv")
    dictionnaire = get_csv(chemin_du_fichier_csv)
    setattr(sys.modules[__name__], f"{dossier}_dictionnaire", set(convert_word(mot) for mot in dictionnaire))

# Vars
arret: bool = False
max_players: int = 8  # Max players in a lobby

looking_for_games_players: list[socket] = []
conn_list: list[socket] = []

reception_list: dict[socket, object] = \
    {"Conn": [], "Reception": []}
mqtt_list: dict[str, object] = \
    {"Game": [], "Mqtt_Object": []}
game_list: dict[str, str, str, bool, object, int, str] = \
    {"Creator": [], "Name": [], "Password": [], "Private": [], "Game_Object": [], "Players_Number": [], "Langue": []}
game_tour: dict[str, socket, bool, bool, str, str] = \
    {"Player": [], "Conn": [], "Ready": [], "InGame": [], "Game": [], "Avatar": []}
waiting_room: dict[socket, str, str] = \
    {"Conn": [], "Player": [], "Game": []}