import csv, os, time, random, unidecode
from server_confs import Configurations

def envoi(conn, message):
    """envoi() : Fonction qui permet d'envoyer des messages au client
    Args:
        conn (socket): Socket de connexion du client"""
    try:
        conn.send(message.encode())
    except BrokenPipeError:
        print("Client déconnecté")
        pass
    except ConnectionResetError:
        print("Client déconnecté")
        pass
    except OSError:
        print("Client déconnecté")
        pass

def read_words_from_file():
    """read_words_from_file() : Fonction qui permet de lire les mots d'un fichier texte
    
    Args:
        input_file (str): Chemin du fichier texte à lire"""
    chemin_csv = os.path.join(os.path.dirname(__file__), "../Dictionary/French/Syllabes/syllabes.csv")
    with open(chemin_csv, 'r') as file:
        lines = file.readlines()
        words = [line.strip().replace(',', '') for line in lines]  # Supprimer les caractères d'espacement comme les sauts de ligne
    
    return words

def get_csv(chemin_du_fichier_csv):
    """get_csv() : Fonction qui permet de récupérer les données d'un fichier csv
    
    Args:
        chemin_du_fichier_csv (str): Chemin du fichier csv à lire"""
    premiere_colonne = []

    with open(chemin_du_fichier_csv, 'r', newline='', encoding='utf-8') as fichier_csv:
        lecteur_csv = csv.reader(fichier_csv)
        for ligne in lecteur_csv:
            if ligne:  # Vérifier si la ligne n'est pas vide
                premiere_colonne.append(ligne[0])

    return premiere_colonne

def add_waiting_room_players(game_name):
    """add_waiting_room_players() : Fonction qui ajoute les joueurs dans la salle d'attente"""
    def get_game_elements():
        for game in game_list["Name"]:
            if game == game_name:
                game_creator = game_list["Creator"][game_list["Name"].index(game)]
                game_password = game_list["Password"][game_list["Name"].index(game)]
                game_private = game_list["Private"][game_list["Name"].index(game)]
                return f"{game_name}|{game_creator}|{game_password}|{game_private}"
    
    def check_players_waiting() -> tuple:
        number_of_players = max_players - game_list["Players_Number"][game_list["Name"].index(game_name)]
        game_waiting_room_list = []
        for player in waiting_room["Player"]:
            if waiting_room["Game"][waiting_room["Player"].index(player)] == game_name:
                game_waiting_room_list.append(player)
        return number_of_players, game_waiting_room_list

    def add_players_waiting():
        i = 0
        game_elements = get_game_elements()
        number_of_players, game_waiting_room_list = check_players_waiting()
        while i < number_of_players:
            try:
                player = game_waiting_room_list[i]
                conn = waiting_room["Conn"][waiting_room["Player"].index(player)]
                looking_for_games_players.remove(conn)
                envoi(conn, f"JOIN_STATE|GAME-JOINED|{game_elements}|{player}|")
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
        print("La partie a été supprimée")

def convert_word(word) -> str:
    """convert_word() : Permet d'ignorer les caractères spéciaux, les accents et les majuscules du dictionnaire
    
    Args:
        word (str): Mot à convertir
    
    Returns:
        str: Mot converti"""
    word = unidecode.unidecode(word)  # Convertir les caractères spéciaux en caractères ASCII
    word = word.lower()  # Convertir les majuscules en minuscules
    return word

#Mqtt
confs = Configurations()

confs.broker = 'localhost'
confs.port = 1883
confs.topic = "test"
confs.client_id = f'publish-{random.randint(0, 1000)}'
confs.username = 'frigiel'
confs.password = 'toto'

chemin_du_fichier_csv = os.path.join(os.path.dirname(__file__), "../Dictionary/French/Dictionary/dictionary.csv")
dictionnaire = get_csv(chemin_du_fichier_csv)
dictionnaire_converted = set(convert_word(mot) for mot in dictionnaire)

arret = False
max_players = 8  #nombre de joueur max dans un lobby
looking_for_games_players = [] #socket
conn_list = [] #socket
reception_list = {"Conn": [], "Reception": []} #socket, Reception
mqtt_list = {"Game": [], "Mqtt_Object": []} #str, Mqtt_Sub
game_list = {"Creator": [], "Name": [], "Password": [], "Private": [], "Game_Object": [], "Players_Number": []} #str, str, str, bool, Game, int
game_tour = {"Player": [], "Conn": [], "Ready": [], "InGame": [], "Game": [], "Avatar": []} #str, socket, bool, bool, str, str
waiting_room = {"Conn": [], "Player": [], "Game": []} #socket, str, str