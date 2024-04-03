from server_utils import *
from server_game import Game
import random, time, threading, unidecode
from socket import socket as socket


class Reception(threading.Thread):
    """Reception() : Classe qui permet de gérer la réception des messages du client
    
    Args:
        threading (Thread): Classe qui permet de créer des Threads"""

    def __init__(self, conn : socket):
        """__init__() : Fonction qui permet d'initialiser la classe Reception
        
        Args:
            conn (socket): Socket de connexion du client"""
        threading.Thread.__init__(self)
        self.conn = conn
        self.words_list = []
        self.username = f"Client {random.randint(1, 1000)}"
        self.players = {"Player": [], "Ready": [], "Lifes": [], "Game": []}
        self.list_lock = threading.Lock()

    def run(self):
        """run() : Fonction qui permet de lancer la Thread reception"""
        self.reception(self.conn)

    def reception(self, conn):
        """reception() : Fonction qui permet de recevoir les messages du client
        
        Args:
            conn (socket): Socket de connexion du client"""
        global arret
        flag = False

        while not flag and not arret:
            try:
                msg = conn.recv(1024).decode()
                print(msg)
                #print(self.players, "FOR THE PLAYER")
            except ConnectionResetError:
                deco_thread = threading.Thread(target=self.__deco, args=(conn,))
                deco_thread.start()
                flag = True
                break
            except ConnectionAbortedError:
                deco_thread = threading.Thread(target=self.__deco, args=(conn,))
                deco_thread.start()
                flag = True
                break
            except OSError:
                deco_thread = threading.Thread(target=self.__deco, args=(conn,))
                deco_thread.start()
                flag = True
                break

            try:
                message = msg.split("|")
            except:
                message = msg

            if msg == "arret" or message == "bye":
                print("Arret du serveur")
                flag = True
                if message == "arret":
                    arret = True

            elif not msg:
                deco_thread = threading.Thread(target=self.__deco, args=(conn,))
                deco_thread.start()
                flag = True

            elif message[0] == "MENU_STATE":
                looking_for_games_players.remove(conn)

            elif message[0] == "CREATE_GAME":
                self.create_game(conn, message)

            elif message[0] == "NEW_WORD":
                self.new_word(conn, message)

            elif message[0] == "READY_TO_PLAY":
                self.ready_to_play(conn, message)
            
            elif message[0] == "READY_TO_PLAY_JOIN":
                self.ready_to_play_join(conn, message)

            elif message[0] == "START_GAME":
                self.start_game(conn, message)

            elif message[0] == "NEW_USER": #Nouvel utilisateur se connecte
                self.new_user(conn, message)

            elif message[0] == "NEW_SYLLABE":
                self.new_syllabe(conn, message, msg)

            elif message[0] == "GET_GAMES":
                self.get_games(conn, username = message[1])

            elif message[0] == "LEAVE_GAME":
                self.leave_game(conn, game_name=message[1], player=message[2])
            
            elif message[0] == "JOIN_GAME":
               self.manage_join_game(conn, message)

            elif message[0] == "JOIN_GAME_AS_A_PLAYER":
                self.manage_join_game_as_a_player(conn, message)

            elif message[0] == "LEAVE_WAITING_ROOM":
                self.leave_waiting_room(conn)

        print("Arret de la Thread reception")

    def manage_join_game(self, conn : socket, message : list):
        """manage_join_game() : Fonction qui permet de gérer la demande de rejoindre une partie
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        print("JOIN GAME")
        if not self.check_not_ingame(game_name = message[1], player = message[3]):
            if not self.check_game_is_full(game_name = message[1]):
                self.join_game(conn, message)
            else:
                self.envoi(conn, f"JOIN|GAME_FULL|{message[1]}|")
        else:
            self.waiting_room(conn=conn, player=message[3], game_name = message[1])
            players_number = game_list["Players_Number"][game_list["Name"].index(message[1])]
            self.envoi(conn, f"JOIN|ALREADY_IN_GAME|{message[1]}|{players_number}|")

    def manage_join_game_as_a_player(self, conn : socket, message : list):
        """manage_join_game_as_a_player() : Fonction qui permet de gérer la demande de rejoindre une partie en tant que joueur
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        print("JOIN GAME AS A PLAYER")
        if not self.check_not_ingame(game_name = message[2], player = message[1]) and not self.check_game_is_full(game_name = message[2]):
            self.join_game_as_a_player(conn, username = message[1], game_name = message[2])
            self.send_new_player(game_name = message[2])

    def check_game_is_full(self, game_name : str) -> bool:
        """check_game_is_full() : Fonction qui permet de vérifier si la partie est pleine
        
        Args:
            game_name (str): Nom de la partie
        
        Returns:
            bool: True si la partie est pleine, False sinon"""
        game_index = game_list["Name"].index(game_name)
        if game_list["Players_Number"][game_index] == max_players:
            return True
        return False

    def join_game(self, conn : socket, message : list):
        """join_game() : Fonction qui permet de vérifier si le joueur peut accéder à la partie via le mdp, et si oui, le connecte à alle en envoyant un message
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        print("Rejoindre une partie")
        looking_for_games_players.remove(conn)
        password = message[2]
        username = message[3]
        game_index = game_list["Name"].index(message[1])
        game_name = game_list["Name"][game_index]
        game_creator = game_list["Creator"][game_index]
        game_password = game_list["Password"][game_index]
        game_private = game_list["Private"][game_index]
        #print(game_name, game_creator, game_password, game_private, password, username)
        print("MOT DE PASSE", game_password, password)
        if game_private == "True":
            if password == game_password:
                for connexion in game_tour["Conn"]:
                    conn_index = game_tour["Conn"].index(connexion)
                    #print(game_tour["Game"][conn_index], game_creator, game_name, username)
                    if game_tour["Game"][conn_index] == game_name:
                        self.envoi(connexion, f"JOIN|GAME_JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")
                self.envoi(conn, f"JOIN|GAME_JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")
            else:
                self.envoi(conn, "JOIN|WRONG_PASSWORD|")
        else:
            for connexion in game_tour["Conn"]:
                conn_index = game_tour["Conn"].index(connexion)
                #print(game_tour["Game"][conn_index], game_creator, game_name, username)
                if game_tour["Game"][conn_index] == game_name:
                    self.envoi(connexion, f"JOIN|GAME_JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")
            self.envoi(conn, f"JOIN|GAME_JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")

    def send_new_player(self, game_name : str):
        """send_new_player() : Fonction qui permet d'envoyer un message à tous les joueurs pour les informer qu'un joueur a une partie dans l'onglet rejoindre
        
        Args:
            game_name (str): Nom de la partie"""
        self.add_a_player_list(game_name)
        for conn in looking_for_games_players:
            self.envoi(conn, f"JOIN|NEW_PLAYER|{game_name}|")
    
    def add_a_player_list(self, game_name : str):
        """add_a_player_list() : Fonction qui permet d'ajouter un joueur à la liste des joueurs
        
        Args:
            game_name (str): Nom de la partie"""
        game_index = game_list["Name"].index(game_name)
        game_list["Players_Number"][game_index] += 1

    def get_game_players(self, game_name : str) -> tuple[str]:
        """get_game_players() : Fonction qui permet de récupérer les joueurs d'une partie
        
        Args:
            game_name (str): Nom de la partie"""
        game_players = []
        game_avatars = []
        for player in game_tour["Player"]:
            player_index = game_tour["Player"].index(player)
            if game_tour["Game"][player_index] == game_name:
                game_players.append(player)
                game_avatars.append(game_tour["Avatar"][player_index])
        return game_players, game_avatars
    
    
    def check_not_ingame(self, game_name : str, player : str) -> bool:
        """check_not_ingame() : Fonction qui permet de vérifier si le joueur n'est pas déjà dans une partie
        
        Args:
            game_name (str): Nom de la partie
        
        Returns:
            bool: True si le joueur est déjà dans une partie, False sinon"""
        game_players, game_avatars = self.get_game_players(game_name)
        # print(game_tour, "GAME PLAYERS")
        for player in game_players:
            index_player = game_tour["Player"].index(player)
            if game_tour["InGame"][index_player]:
                # print(game_tour["InGame"][index_player], "GAME PLAYERS")
                return True
        return False
    
    def check_player_ingame(self, player : str) -> bool:
        """check_player_ingame() : Fonction qui permet de vérifier si le joueur est déjà dans une partie
        
        Args:
            player (str): Pseudo du joueur
        
        Returns:
            bool: True si le joueur est déjà dans une partie, False sinon"""
        index_player = game_tour["Player"].index(player)
        print(game_tour["InGame"][index_player], "GAME PLAYERS")
        return game_tour["InGame"][index_player]

    def join_game_as_a_player(self, conn, username, game_name):
        """join_game_as_a_player() : Fonction qui permet d'associer le joueur à la bonne partie dans la liste globale game_tour
        
        Args:
            username (str): Pseudo du joueur
            game_name (str): Nom de la partie"""
        player_index = game_tour["Player"].index(username)
        game_tour["Game"][player_index] = game_name
        game_players_list, game_avatars_list = self.get_game_players(game_name)
        game_players = ','.join(game_players_list)
        game_avatars = ','.join(game_avatars_list)
        for connexion in game_tour["Conn"]:
            conn_index = game_tour["Conn"].index(connexion)
            if game_tour["Game"][conn_index] == game_name:
                self.envoi(connexion, f"JOIN|GET_PLAYERS|{game_players}|{game_avatars}")

    def waiting_room(self, conn, player, game_name):
        """waiting_room() : Fonction qui permet d'ajouter un joueur à la salle d'attente

        Args:
            conn (socket): Socket de connexion du client
            player (str): Pseudo du joueur
            game_name (str): Nom de la partie"""
        waiting_room["Conn"].append(conn)
        waiting_room["Player"].append(player)
        waiting_room["Game"].append(game_name)

    def leave_waiting_room(self, conn):
        """leave_waiting_room() : Fonction qui permet de quitter la salle d'attente
        
        Args:
            conn (socket): Socket de connexion du client"""
        try:
            index_conn = waiting_room["Conn"].index(conn)
            waiting_room["Conn"].remove(conn)
            waiting_room["Player"].pop(index_conn)
            waiting_room["Game"].pop(index_conn)
        except ValueError:
            pass

    def new_syllabe(self, conn, message, msg):
        """new_syllabe() : Fonction qui permet de créer une nouvelle syllabe
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client
            msg (str): Message du client"""
        print(f'User : {msg} {message}\n')
        word = self.convert_word(message[2])
        sylb = self.convert_word(message[3])
        print("CONVERTED", sylb)
        print(game_tour)
        index_player = game_tour["Player"].index(message[1])
        connexion = game_tour["Conn"][index_player]

        if self.check_syllabe(word, sylb):
            print("if")
            if any(self.convert_word(word.lower()) == self.convert_word(mot.lower()) for mot in dictionnaire):
                self.right(connexion, player=message[1])
                self.words_list.append(word.lower())
            else:
                self.wrong(connexion, player=message[1])
        else:
            self.wrong(connexion, player=message[1])
    
    def convert_word(self, word) -> str:
        """convert_word() : Permet d'ignorer les caractères spéciaux, les accents et les majuscules du dictionnaire
        
        Args:
            word (str): Mot à convertir
        
        Returns:
            str: Mot converti"""
        word = unidecode.unidecode(word)  # Convertir les caractères spéciaux en caractères ASCII
        word = word.lower()  # Convertir les majuscules en minuscules
        return word

    def new_user(self, conn, message):
        """new_user() : Fonction qui permet d'ajouter un nouveau joueur
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        if self.check_user_unique(message[1]):
            game_tour["Player"].append(message[1])
            game_tour["Conn"].append(conn)
            game_tour["Ready"].append(False)
            game_tour["InGame"].append(False)
            game_tour["Game"].append(None)
            game_tour["Avatar"].append(message[2])
            self.username = message[1]
            self.avatar = message[2]
            self.envoi(conn, "NAME_CORRECT|")
        else:
            self.envoi(conn, "NAME_ALREADY_USED|")
    
    def get_games(self, conn : socket, username : str):
        """get_games() : Fonction qui permet de récupérer la liste des parties
        
        Args:
            username (str): Pseudo du joueur"""
        looking_for_games_players.append(conn)
        for i in range(len(game_list["Name"])):
            game_name = game_list["Name"][i]
            private = game_list["Private"][i]
            players_number = game_list["Players_Number"][i]
            self.envoi(conn, f"GAME_CREATED|{game_name}|{private}|{players_number}|")
            time.sleep(0.1)

    def get_game_name(self, player : str) -> str:
        """get_game_name() : Fonction qui permet de récupérer le nom de la partie
        
        Args:
            player (str): Pseudo du joueur
        
        Returns:
            str: Nom de la partie"""
        index_player = game_tour["Player"].index(player)
        return game_tour["Game"][index_player]
    
    def leave_game(self, conn, game_name, player) -> None:
        """leave_game() : Fonction qui permet de quitter une partie

        Args:
            conn (socket): Socket de connexion du client
            game_name (str): Nom de la partie
            player (str): Pseudo du joueur"""
        players_list = []
        number_of_players = 0

        game_index = game_tour["Player"].index(player)
        game_tour["Game"][game_index] = None
        game_tour["InGame"][game_index] = False
        game_tour["Ready"][game_index] = False
        # print("Quitter une partie", game_tour)
        self.send_player_leaving(game_name, player)

        for game in game_tour["Game"]:
            if game == game_name:
                number_of_players += 1
                players_list.append(game_tour["Player"][game_tour["Game"].index(game)])
        print(players_list, number_of_players, "PLAYERS LIST")
        self.players = {"Player": [], "Ready": [], "Lifes": [], "Game": []}
        
        if number_of_players == 0:
            print("DELETE GAME WALLAH")
            self.delete_game(conn, game_name)
        else:
            creator = game_list["Creator"][game_list["Name"].index(game_name)]
            if player == creator:
                for player in players_list:
                    if player != creator:
                        self.new_creator(game_name, player)
                        return
            add_waiting_room_players(game_name)

    def send_player_leaving(self, game_name : str, player : str):
        """send_player_leaving() : Fonction qui permet d'envoyer un message à tous les joueurs pour les informer qu'un joueur a quitté la partie
        
        Args:
            game_name (str): Nom de la partie"""
        game_index = game_list["Name"].index(game_name)
        game_list["Players_Number"][game_index] -= 1
        for connexion in game_tour["Conn"]:
            if game_tour["Game"][game_tour["Conn"].index(connexion)] == game_name:
                self.envoi(connexion, f"LOBBY_STATE|LEAVE_GAME|{game_name}|{player}|")
        for conne in looking_for_games_players:
            self.envoi(conne, f"JOIN|LEAVE_GAME|{game_name}|{player}|")
                
    def new_creator(self, game_name, player):
        """new_creator() : Fonction qui permet de changer le créateur de la partie
        
        Args:
            game_name (str): Nom de la partie
            player (str): Pseudo du joueur"""
        time.sleep(0.5)
        game_index = game_list["Name"].index(game_name)
        game_list["Creator"][game_index] = player
        print("Nouveau créateur", game_list["Creator"][game_index], game_list["Name"][game_index], player)
        conn = self.get_conn(player)
        conn_index = reception_list["Conn"].index(conn)
        reception = reception_list["Reception"][conn_index]
        reception.reset_players(join = False, creator = player, game_name = game_name)
        self.envoi(conn, f"LOBBY_STATE|NEW_CREATOR|{game_name}|{player}|")

    
    def get_conn(self, player : str) -> socket:
        """get_conn() : Fonction qui permet de récupérer le socket de connexion du joueur
        
        Args:
            player (str): Pseudo du joueur
        
        Returns:
            socket: Socket de connexion du joueur"""
        index_player = game_tour["Player"].index(player)
        return game_tour["Conn"][index_player]


    def delete_game(self, conn : socket, game_name : str):
        """delete_game() : Fonction qui permet de supprimer une partie
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        game_index = game_list["Name"].index(game_name)
        game_list["Name"].pop(game_index)
        game_list["Creator"].pop(game_index)
        game_list["Password"].pop(game_index)
        game_list["Private"].pop(game_index)
        game_list["Game_Object"].pop(game_index)
        game_list["Players_Number"].pop(game_index)

        for connexion in looking_for_games_players:
            if connexion != conn:
                self.envoi(connexion, f"GAME_DELETED|{game_name}|")
        print("Suppression d'une partie", game_list)


    def start_game(self, conn, message):
        """start_game() : Fonction qui permet de lancer une partie
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        print("Lancement de la partie")
        self.new_players(game_name=message[2], creator=message[1])
        rules = [int(message[3]), int(message[4]), int(message[5]), int(message[6]), int(message[7]), int(message[8])]
        #print("Règles", rules)
        self.game = Game(conn, self.players, creator=message[1], game = True, rules = rules, game_name=message[2])
        game_list_index = game_list["Name"].index(message[2])
        with self.list_lock:
            game_list["Game_Object"][game_list_index] = self.game #on ajoute l'insatance de la classe pour pouvoir l'utiliser depuis d'autres threads de réception
        self.game.start()

    def ready_to_play(self, conn, message):
        """ready_to_play() : Fonction qui permet de savoir si le joueur est prêt
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        print("Le joueur est prêt")
        index_player = self.players["Player"].index(message[1])

        if self.players["Ready"][index_player]:
            self.players["Ready"][index_player] = False
        else:
            self.players["Ready"][index_player] = True
        #print(self.players["Ready"][index_player])
        index_player = game_tour["Player"].index(message[1])
        game_tour["Ready"][index_player] = None
        
    def ready_to_play_join(self, conn, message):
        """ready_to_play_join() : Fonction qui permet de savoir si le joueur est prêt
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        index_player = game_tour["Player"].index(message[1])
        if game_tour["Ready"][index_player]:
            game_tour["Ready"][index_player] = False
        else:
            game_tour["Ready"][index_player] = True
        #print(game_tour["Ready"][index_player])

    def new_word(self, conn, message):
        """new_word() : Fonction qui permet d'ajouter un nouveau mot
        
        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        print("Nouveau mot")
        self.words_list.append(message[1])

    def new_players(self, game_name, creator):
        """new_player() : Fonction qui permet d'ajouter un nouveau joueur
        
        Args:
            game_name (str): Nom de la partie
            creator (str): Créateur de la partie"""
        for player in game_tour["Player"]:
            player_index = game_tour["Player"].index(player)
            if game_tour["Game"][player_index] == game_name and player != creator:
                self.players["Player"].append(player)
                self.players["Game"].append(game_name)
                self.players["Lifes"].append(0)
                if game_tour["Ready"][player_index]:
                    self.players["Ready"].append(True)
                else:
                    self.players["Ready"].append(False)

        #print(self.players, "PLAYERS", game_tour, game_name)

    def reset_players(self, join, creator, game_name):
        """reset_players() : Fonction qui permet de réinitialiser les joueurs
        
        Args:
            join (bool): Si le joueur rejoint une partie
            creator (str): Créateur de la partie
            game_name (str): Nom de la partie"""
        print("Reset Players")
        print(self.username)
        self.players = {"Player": [], "Ready": [], "Lifes": [], "Game": []}
        if not join:
            self.players["Player"].append(creator)
            self.players["Ready"].append(False)
            self.players["Game"].append(f"{game_name}")
            self.players["Lifes"].append(0)

    def create_game(self, conn, message):
        """create_game() : Fonction qui permet de créer une partie

        Args:
            conn (socket): Socket de connexion du client
            message (list): Message du client"""
        #message = f"CREATE_GAME|{username}|{game_name}|{password}|{private_game}"
        print("Création d'une partie")
        game_list["Creator"].append(message[1])
        game_list["Name"].append(message[2])
        game_list["Password"].append(message[3])
        game_list["Private"].append(message[4])
        game_list["Game_Object"].append(None)
        game_list["Players_Number"].append(1)
        print(game_list, "GAME LIST")
        self.players["Player"].append(message[1])
        self.players["Ready"].append(False)
        self.players["Game"].append(f"{message[2]}")
        self.players["Lifes"].append(0)
        
        player_index = game_tour["Player"].index(message[1])
        game_tour["Game"][player_index] = message[2] #ici on ajoute le nom de la partie au createur de la partie

        for connexion in looking_for_games_players:
            if connexion != conn:
                self.envoi(connexion, f"GAME_CREATED|{message[2]}|{message[4]}|{1}|")
        
    def __deco(self, conn):
        """__deco() : Fonction qui permet de déconnecter un client
        
        Args:
            conn (socket): Socket de connexion du client"""
        def game_tour_deco(conn):
            index_player = game_tour["Conn"].index(conn)
            game_tour["Conn"].remove(conn)
            game_tour["Player"].pop(index_player)
            game_tour["Ready"].pop(index_player)
            game_tour["Avatar"].pop(index_player)
            try:
                game_tour["InGame"].pop(index_player)
                game_tour["Game"].pop(index_player)
            except ValueError and IndexError:
                pass
        
        def looking_for_games_players_deco(conn):
            try:
                looking_for_games_players.remove(conn)
            except ValueError:
                pass

        def reception_list_deco(conn):
            # print(reception_list, "RECEPTION LIST")
            index_conn = reception_list["Conn"].index(conn)
            reception_list["Conn"].remove(conn)
            reception_list["Reception"].pop(index_conn)
        
        def conn_list_deco(conn):
            conn_list.remove(conn)

        def game_deco():
            try:
                game_name = self.get_game_name(self.username)
                self.leave_game(conn, game_name = game_name, player = self.username)
            except ValueError:
                pass
            except AttributeError:
                pass

        def waiting_room_deco():
            try:
                index_conn = waiting_room["Conn"].index(conn)
                waiting_room["Conn"].remove(conn)
                waiting_room["Player"].pop(index_conn)
                waiting_room["Game"].pop(index_conn)
            except ValueError:
                pass
        
        def send_deco(conn, player):
            try:
                for connexion in game_tour["Conn"]:
                    if connexion != conn and game_tour["Game"][game_tour["Conn"].index(connexion)] == game_tour["Game"][game_tour["Conn"].index(conn)]:
                        self.envoi(connexion, f"LOBBY_STATE|PLAYER_DECO|{player}|")
            except ValueError:
                pass

        def lists_deco(conn):
            send_deco(conn, self.username)
            while True:
                try:
                    if not self.check_player_ingame(self.username):
                        looking_for_games_players_deco(conn)
                        waiting_room_deco()
                        game_deco()
                        game_tour_deco(conn)
                        reception_list_deco(conn)
                        conn_list_deco(conn)
                        break
                    else:
                        time.sleep(5)
                except AttributeError: #le user ne s'est pas log
                    reception_list_deco(conn)
                    conn_list_deco(conn)
                    break
                except ValueError:
                    reception_list_deco(conn)
                    conn_list_deco(conn)
                    break
            conn.close()
        
        time.sleep(1)
        lists_deco(conn)
        print(f"{self.username} vient de se déconnecter...")

    def check_user_unique(self, user) -> bool:
        """check_user_unique() : Fonction qui vérifie si le pseudo du joueur est unique
        
        Args:
            user (str): Pseudo du joueur"""
        for player in game_tour["Player"]:
            if player == user:
                print("Pseudo déjà utilisé")
                return False
        return True

    def wrong(self, conn, player):
        """wrong() : Fonction qui génère un mot aléatoire
        
        Args:
            conn (socket): Socket de connexion du client
            player (str): Pseudo du joueur"""
        self.envoi(conn, "GAME|WRONG|")

    def right(self, conn, player):
        """right() : Fonction qui génère un mot aléatoire
        
        Args:
            conn (socket): Socket de connexion du client
            player (str): Pseudo du joueur"""
        self.envoi(conn, f"GAME|RIGHT|{player}|")
        try:
            player_index = self.players["Player"].index(player)
            game = self.players["Game"][player_index]
        except ValueError:
            print("Player not in the list")
            player_index = game_tour["Player"].index(player)
            game_name = game_tour["Game"][player_index]
            self.new_players(game_name=game_name, creator=None)
            self.game = game_list["Game_Object"][game_list["Name"].index(game_name)]
            game = game_name
        self.game.stop_compteur(game)

    def check_syllabe(self, mot, sylb) -> bool:
        """check_syllabe() : Fonction qui vérifie si le mot passé en paramètre contient une syllabe
        
        Args:
            mot (str): Mot à vérifier
            sylb (str): Syllabe à vérifier

        Returns:
            bool: True si le mot contient la syllabe, False sinon"""
        if sylb in mot:
            return True
        else:
            return False
        
    def envoi(self, conn, message):
        """self.envoi() : Fonction qui permet d'envoyer des messages au client
        Args:
            conn (socket): Socket de connexion du client"""
        try:
            conn.send(message.encode())
        except BrokenPipeError:
            pass

        
            
