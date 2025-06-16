from server_utils import *
from server_game import Game
from server_mqtt import Mqtt_Sub
import random, time, threading, unidecode
from socket import socket as socket
from server_logs import ErrorLogger

ErrorLogger.setup_logging()

class Reception(threading.Thread):
    """Class that manages the reception of messages from the client.

    Attributes:
        conn (socket): The client's connection socket.
        mqtt_started (bool): Whether the MQTT client has started.
        words_list (list): The list of words.
        langue (str): The language of the game.
        death_mode (int): The death mode.
        username (str): The username of the client.
        players (dict): The players in the game.
        list_lock (threading.Lock): The lock for the list of players.
    """

    def __init__(self, conn: socket):
        """Initializes the reception thread.

        Args:
            conn (socket): The client's connection socket."""
        threading.Thread.__init__(self)
        self.conn = conn

        self.mqtt_started = False
        self.words_list = []
        self.langue = "Français"
        self.death_mode = 0
        self.username = f"Client {random.randint(1, 1000)}"
        self.players: dict[str, bool, int, Game] = \
            {"Player": [], "Ready": [], "Lifes": [], "Game": []}
        self.list_lock = threading.Lock()

    def run(self):
        """Run the reception thread which receives messages from the client."""
        self.reception(self.conn)

    def reception(self, conn: socket):
        """Receives messages from the client and processes them.
        
        Args:
            conn (socket): The client's connection socket."""
        global arret
        flag = False

        while not flag and not arret:
            try:
                msg = conn.recv(1024).decode()
                if msg:
                    infos_logger.log_infos("[RECEIVED]", msg)
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

            if not msg:
                deco_thread = threading.Thread(target=self.__deco, args=(conn,))
                deco_thread.start()
                flag = True

            elif message[0] == "MENU-STATE_":
                looking_for_games_players.remove(conn)

            elif message[0] == "CREATE-GAME_":
                self.create_game(conn, message)

            elif message[0] == "CHECK-GAME-NAME_":
                self.check_game_name(conn, message)

            elif message[0] == "NEW-WORD_":
                self.new_word(conn, message)

            elif message[0] == "READY-TO-PLAY_":
                self.ready_to_play(conn, message)
            
            elif message[0] == "READY-TO-PLAY-JOIN_":
                self.ready_to_play_join(conn, message)

            elif message[0] == "START-GAME_":
                self.start_game(conn, message)

            elif message[0] == "NEW-USER_": #Nouvel utilisateur se connecte
                self.new_user(conn, message)

            elif message[0] == "NEW-SYLLABE_":
                self.new_syllabe(conn, message, msg)

            elif message[0] == "GET-GAMES_":
                self.get_games(conn, username = message[1])

            elif message[0] == "LEAVE-GAME_":
                self.leave_game(conn, game_name=message[1], player=message[2])
            
            elif message[0] == "JOIN-GAME_":
               self.manage_join_game(conn, message)

            elif message[0] == "JOIN-GAME-AS-A-PLAYER_":
                self.manage_join_game_as_a_player(conn, message)

            elif message[0] == "LEAVE-WAITING-ROOM_":
                self.leave_waiting_room(conn)
            
            else:
                infos_logger.log_infos("[UNKNOWN]", "Last message was unknown")

    def manage_join_game(self, conn: socket, message: list):
        """Manage the request to join a game as a creator.
        
        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message."""
        try:
            if not self.check_not_ingame(game_name = message[1], player = message[3]):
                if not self.check_game_is_full(game_name = message[1]):
                    self.join_game(conn, message)
                else:
                    self.send_client(conn, f"JOIN_STATE|GAME-FULL|{message[1]}|")
            else:
                self.waiting_room(conn=conn, player=message[3], game_name = message[1])
                players_number = game_list["Players_Number"][game_list["Name"].index(message[1])]
                self.send_client(conn, f"JOIN_STATE|ALREADY-IN-GAME|{message[1]}|{players_number}|")
        except ValueError:
            infos_logger.log_infos("[HANDLED ERROR]", "ValueError, game probably does not exist anymore (Join Game)")

    def manage_join_game_as_a_player(self, conn: socket, message: list):
        """Manage the request to join a game as a player.
        
        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message."""
        if not self.check_not_ingame(game_name = message[2], player = message[1]) and not self.check_game_is_full(game_name = message[2]):
            self.join_game_as_a_player(conn, username = message[1], game_name = message[2])
            self.send_new_player(game_name = message[2])

    def check_game_is_full(self, game_name: str) -> bool:
        """Check if the game is full.

        Args:
            game_name (str): The name of the game.

        Returns:
            bool: True if the game is full, False otherwise
        """
        try:
            game_index = game_list["Name"].index(game_name)
            if game_list["Players_Number"][game_index] == max_players:
                return True
            return False
        except ValueError:
            infos_logger.log_infos("[HANDLED ERROR]", "ValueError, game probably does not exist anymore (Check Game Is Full)")
        except IndexError:
            infos_logger.log_infos("[HANDLED ERROR]", "IndexError, game probably does not exist anymore (Check Game Is Full)")

    def join_game(self, conn: socket, message: list):
        """Join a game as a creator. 
        Check if the game is private and if the password is correct.
        Send a message to all players to inform them that a new player has joined the game.

        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message."""
        password = message[2]
        username = message[3]
        game_index = game_list["Name"].index(message[1])
        game_name = game_list["Name"][game_index]
        game_creator = game_list["Creator"][game_index]
        game_password = game_list["Password"][game_index]
        game_private = game_list["Private"][game_index]
        self.langue = game_list["Langue"][game_index]
        if game_private == "True":
            if password == game_password:
                looking_for_games_players.remove(conn)
                for connexion in game_tour["Conn"]:
                    conn_index = game_tour["Conn"].index(connexion)
                    if game_tour["Game"][conn_index] == game_name:
                        self.send_client(connexion, f"JOIN_STATE|GAME-JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")
                self.send_client(conn, f"JOIN_STATE|GAME-JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")
            else:
                self.send_client(conn, "JOIN_STATE|WRONG-PASSWORD|")
        else:
            looking_for_games_players.remove(conn)
            for connexion in game_tour["Conn"]:
                conn_index = game_tour["Conn"].index(connexion)
                if game_tour["Game"][conn_index] == game_name:
                    self.send_client(connexion, f"JOIN_STATE|GAME-JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")
            self.send_client(conn, f"JOIN_STATE|GAME-JOINED|{game_name}|{game_creator}|{game_password}|{game_private}|{username}|")

    def send_new_player(self, game_name: str):
        """Send a message to all players to inform them that a new player has joined the game.

        Args:
            game_name (str): The name of the game."""
        self.add_a_player_list(game_name)
        for conn in looking_for_games_players:
            self.send_client(conn, f"JOIN_STATE|NEW-PLAYER|{game_name}|")
    
    def add_a_player_list(self, game_name: str):
        """Add a player to the list of players in the game.

        Args:
            game_name (str): The name of the game."""
        game_index = game_list["Name"].index(game_name)
        game_list["Players_Number"][game_index] += 1

    def get_game_players(self, game_name: str) -> tuple[str]:
        """Get the players in the game.

        Args:
            game_name (str): The name of the game.

        Returns:
            tuple[str]: The players in the game."""
        game_players : list[str] = []
        game_avatars : list[str]= []
        ready_players : list[str]= []
        for player in game_tour["Player"]:
            player_index = game_tour["Player"].index(player)
            if game_tour["Game"][player_index] == game_name:
                game_players.append(player)
                game_avatars.append(game_tour["Avatar"][player_index])
                if game_tour["Ready"][player_index]:
                    game_ready = True
                    ready_players.append(str(game_ready))
                else:
                    game_ready = False
                    ready_players.append(str(game_ready))
        return game_players, game_avatars, ready_players
    
    
    def check_not_ingame(self, game_name: str, player: str) -> bool:
        """Check if the player is not already in a game.

        Args:
            game_name (str): The name of the game.
            player (str): The player to check.

        Returns:
            bool: True if the player is not in the game, False otherwise."""
        game_players, game_avatars, ready_players = self.get_game_players(game_name)
        for player in game_players:
            index_player = game_tour["Player"].index(player)
            if game_tour["InGame"][index_player]:
                return True
        return False
    
    def check_player_ingame(self, player: str) -> bool:
        """Check if the player is currently playing

        Args:
            player (str): The player to check.
        
        Returns:
            bool: True if the player is playing, False otherwise
        """
        index_player = game_tour["Player"].index(player)
        return game_tour["InGame"][index_player]

    def join_game_as_a_player(self, conn: socket, username: str, game_name: str):
        """Function that associates the player with the correct game in the global game_tour list
        
        Args:
            conn (socket): The client's connection socket.
            username (str): The player's username.
            game_name (str): The name of the game.
        """
        player_index = game_tour["Player"].index(username)
        game_tour["Game"][player_index] = game_name
        game_players_list, game_avatars_list, ready_players = self.get_game_players(game_name)
        game_players = ','.join(game_players_list)
        game_avatars = ','.join(game_avatars_list)
        ready_players = ','.join(ready_players)
        for connexion in game_tour["Conn"]:
            conn_index = game_tour["Conn"].index(connexion)
            if game_tour["Game"][conn_index] == game_name:
                self.send_client(connexion, f"JOIN_STATE|GET-PLAYERS|{game_players}|{game_avatars}|{ready_players}|")

    def waiting_room(self, conn: socket, player: str, game_name: str):
        """Function that adds a player to the waiting room

        Args:
            conn (socket): The client's connection socket.
            player (str): The player's username.
            game_name (str): The name of the game.
        """
        waiting_room["Conn"].append(conn)
        waiting_room["Player"].append(player)
        waiting_room["Game"].append(game_name)

    def leave_waiting_room(self, conn: socket):
        """Function that allows a player to leave the waiting room
        
        Args:
            conn (socket): The client's connection socket
        """
        try:
            index_conn = waiting_room["Conn"].index(conn)
            waiting_room["Conn"].remove(conn)
            waiting_room["Player"].pop(index_conn)
            waiting_room["Game"].pop(index_conn)
        except ValueError:
            pass

    def new_syllabe(self, conn: socket, message: list, msg: str):
        """
        Verifies if the syllable is correct and if the word exists in the dictionary.

        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message.
            msg (str): The client's message.
        """
        word = message[2]
        sylb = self.convert_word(message[3])
        index_player = game_tour["Player"].index(message[1])
        connexion = game_tour["Conn"][index_player]
        
        if self.check_syllabe(word, sylb):
            if self.convert_word(word.lower()) in getattr(sys.modules[__name__], f"{self.langue}_dictionnaire"):
                self.right(connexion, player=message[1])
                self.words_list.append(word.lower())
            else:
                self.wrong(connexion, player=message[1])
        else:
            self.wrong(connexion, player=message[1])
    
    def convert_word(self, word: str) -> str:
        """
        Ignores special characters, accents, and uppercase letters in the dictionary.

        Args:
            word (str): Word to convert

        Returns:
            str: Converted word
        """
        word = unidecode.unidecode(word)  # Convertir les caractères spéciaux en caractères ASCII
        word = word.lower()  # Convertir les majuscules en minuscules
        return word

    def new_user(self, conn: socket, message: list[str]):
        """
        Adds a new player.

        Args:
            conn (socket): The client's connection socket.
            message (list[str]): The client's message.
        """
        if self.check_user_unique(message[1]):
            game_tour["Player"].append(message[1])
            game_tour["Conn"].append(conn)
            game_tour["Ready"].append(False)
            game_tour["InGame"].append(False)
            game_tour["Game"].append(None)
            game_tour["Avatar"].append(message[2])
            self.username = message[1]
            self.avatar = message[2]
            self.send_client(conn, "NAME_CORRECT|")

        else:
            self.send_client(conn, "NAME_ALREADY_USED|")
    
    def get_games(self, conn: socket, username: str):
        """Get the list of games
        
        Args:
            conn (socket): The client's connection socket
            username (str): The player's username"""
        looking_for_games_players.append(conn)
        for i in range(len(game_list["Name"])):
            game_name = game_list["Name"][i]
            private = game_list["Private"][i]
            players_number = game_list["Players_Number"][i]
            langue = game_list["Langue"][i]
            self.send_client(conn, f"GAME_CREATED|{game_name}|{private}|{players_number}|{langue}|")

    def get_game_name(self, player: str) -> str:
        """
        Retrieve the name of the game.

        Args:
            player (str): The player's username.

        Returns:
            str: The name of the game.
        """
        index_player = game_tour["Player"].index(player)
        return game_tour["Game"][index_player]
    
    def leave_game(self, conn: socket, game_name: str, player: str) -> None:
        """
        Allows a player to leave a game.

        Args:
            conn (socket): The client's connection socket.
            game_name (str): The name of the game.
            player (str): The player's username.
        """
        players_list = []
        number_of_players = 0

        game_index = game_tour["Player"].index(player)
        game_tour["Game"][game_index] = None
        game_tour["InGame"][game_index] = False
        game_tour["Ready"][game_index] = False
        self.send_player_leaving(game_name, player)

        for game in game_tour["Game"]:
            if game == game_name:
                number_of_players += 1
                players_list.append(game_tour["Player"][game_tour["Game"].index(game)])
        self.players = {"Player": [], "Ready": [], "Lifes": [], "Game": []}
        
        if number_of_players == 0:
            self.delete_game(conn, game_name)
            self.unsubscribe_mqtt(game_name)
        else:
            creator = game_list["Creator"][game_list["Name"].index(game_name)]
            if player == creator:
                for player in players_list:
                    if player != creator:
                        self.new_creator(game_name, player)
                        return
            add_waiting_room_players(game_name)

    def send_player_leaving(self, game_name: str, player: str) -> None:
        """
        Send a message to all players to inform them that a player has left the game.

        Args:
            game_name (str): The name of the game.
            player (str): The player's username.
        """
        game_index = game_list["Name"].index(game_name)
        game_list["Players_Number"][game_index] -= 1
        for connexion in game_tour["Conn"]:
            if game_tour["Game"][game_tour["Conn"].index(connexion)] == game_name:
                self.send_client(connexion, f"LOBBY_STATE|LEAVE-GAME|{game_name}|{player}|")
        for conne in looking_for_games_players:
            self.send_client(conne, f"JOIN_STATE|LEAVE-GAME|{game_name}|{player}|")
                
    def new_creator(self, game_name: str, player: str):
        """Change the creator of the game.
        
        Args:
            game_name (str): The name of the game.
            player (str): The username of the player.
        """
        game_index = game_list["Name"].index(game_name)
        game_list["Creator"][game_index] = player
        conn = self.get_conn(player)
        conn_index = reception_list["Conn"].index(conn)
        reception = reception_list["Reception"][conn_index]
        index_player = game_tour["Player"].index(player)
        reset_state = game_tour["Ready"][index_player]
        reception.reset_players(join = False, creator = player, game_name = game_name, reset=reset_state)
        if not reception.mqtt_started:
            reception.subscribe_mqtt(game_name = game_name)
        self.send_client(conn, f"LOBBY_STATE|NEW-CREATOR|{game_name}|{player}|")

    
    def get_conn(self, player: str) -> socket:
        """Retrieve the connection socket of the player.
        
        Args:
            player (str): The player's username.
        
        Returns:
            socket: The player's connection socket."""
        index_player = game_tour["Player"].index(player)
        return game_tour["Conn"][index_player]


    def delete_game(self, conn: socket, game_name: str):
        """
        Delete a game.

        Args:
            conn (socket): The client's connection socket.
            game_name (str): The name of the game.
        """
        game_index = game_list["Name"].index(game_name)
        game_list["Name"].pop(game_index)
        game_list["Creator"].pop(game_index)
        game_list["Password"].pop(game_index)
        game_list["Private"].pop(game_index)
        game_list["Game_Object"].pop(game_index)
        game_list["Players_Number"].pop(game_index)
        game_list["Langue"].pop(game_index)

        for connexion in looking_for_games_players:
            if connexion != conn:
                self.send_client(connexion, f"GAME_DELETED|{game_name}|")
        infos_logger.log_infos("[GAME STATE]", f"Deleted the game : {game_name}")


    def start_game(self, conn: socket, message: list):
        """
        Start a game.

        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message.
        """
        infos_logger.log_infos("[GAME STATE]", f"Game starting : {message[2]}")
        self.new_players(game_name=message[2], creator=message[1])
        rules = [int(message[3]), int(message[4]), int(message[5]), int(message[6]), int(message[7]), int(message[8]), int(message[9])]
        self.game = Game(conn, self.players, creator=message[1], game=True, rules=rules, game_name=message[2], langue=self.langue)
        game_list_index = game_list["Name"].index(message[2])
        with self.list_lock:
            game_list["Game_Object"][game_list_index] = self.game #on ajoute l'insatance de la classe pour pouvoir l'utiliser depuis d'autres threads de réception
        self.game.start()

    def ready_to_play(self, conn: socket, message: list):
        """
        Determine if the player is ready.
        
        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message.
        """
        index_player = self.players["Player"].index(message[1])

        if self.players["Ready"][index_player]:
            self.players["Ready"][index_player] = False
            ready = False
        else:
            self.players["Ready"][index_player] = True
            ready = True
        index_player = game_tour["Player"].index(message[1])
        game_tour["Ready"][index_player] = ready
        game_name = game_tour["Game"][index_player]
        self.send_ready(ready, message[1], game_name)
        
    def ready_to_play_join(self, conn: socket, message: list):
        """
        Determine if the player is ready to join.

        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message.
        """
        index_player = game_tour["Player"].index(message[1])
        if game_tour["Ready"][index_player]:
            game_tour["Ready"][index_player] = False
            ready = False
        else:
            game_tour["Ready"][index_player] = True
            ready = True
        game_name = game_tour["Game"][index_player]
        self.send_ready(ready, message[1], game_name)

    def send_ready(self, ready: bool, player: str, game_name: str):
        """
        Send a message to all players to inform them that a player is ready.

        Args:
            ready (bool): Whether the player is ready.
            player (str): The player's username.
            game_name (str): The name of the game.
        """
        for connexion in game_tour["Conn"]:
            if game_tour["Game"][game_tour["Conn"].index(connexion)] == game_name:
                self.send_client(connexion, f"LOBBY_STATE|READY|{player}|{ready}|")

    def new_word(self, conn: socket, message: list):
        """
        Add a new word.

        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message.
        """
        self.words_list.append(message[1])

    def new_players(self, game_name: str, creator: str):
        """
        Add new players to the game.

        Args:
            game_name (str): The name of the game.
            creator (str): The creator of the game.
        """
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

    def reset_players(self, join: bool, creator: str, game_name: str, reset: bool = False):
        """
        Reset the players.

        Args:
            join (bool): Whether the player is joining a game.
            creator (str): The creator of the game.
            game_name (str): The name of the game.
            reset (bool): Whether to reset the player's state.
        """
        self.players = {"Player": [], "Ready": [], "Lifes": [], "Game": []}
        if not join:
            self.players["Player"].append(creator)
            self.players["Ready"].append(reset)
            self.players["Game"].append(f"{game_name}")
            self.players["Lifes"].append(0)

    def create_game(self, conn: socket, message: list):
        """Create a game.

        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message."""
        #message = f"CREATE-GAME_|{username}|{game_name}|{password}|{private_game}"
        infos_logger.log_infos("[GAME STATE]", f"Game creation : {message[2]}")
        
        def add_game_list():
            """Add the game to the list of games."""
            game_list["Creator"].append(message[1])
            game_list["Name"].append(message[2])
            game_list["Password"].append(message[3])
            game_list["Private"].append(message[4])
            game_list["Game_Object"].append(None)
            game_list["Players_Number"].append(1)
            try:
                getattr(sys.modules[__name__], f"{message[5]}_dictionnaire")
            except AttributeError:
                message[5] = "English"
            game_list["Langue"].append(message[5])
            self.langue = message[5]

        def add_selfplayers():
            """Add the creator to the list of players."""
            self.players["Player"].append(message[1])
            self.players["Ready"].append(False)
            self.players["Game"].append(f"{message[2]}")
            self.players["Lifes"].append(0)
        
        def add_gametour():
            """Add the creator to the game tour list."""
            player_index = game_tour["Player"].index(message[1])
            game_tour["Game"][player_index] = message[2] #ici on ajoute le nom de la partie au createur de la partie

        def send_game_created():
            """Send a message to all players to inform them that a game has been created."""
            for connexion in looking_for_games_players:
                if connexion != conn:
                    self.send_client(connexion, f"GAME_CREATED|{message[2]}|{message[4]}|{1}|{message[5]}|")

        add_game_list()
        add_selfplayers()
        add_gametour()
        self.subscribe_mqtt(game_name=message[2])
        send_game_created()

    def subscribe_mqtt(self, game_name: str):
        """Subscribe to an MQTT topic.

        Args:
            game_name (str): The name of the game.
        """
        self.mqtt_sub = Mqtt_Sub(topic=game_name)
        mqtt_list["Game"].append(game_name)
        mqtt_list["Mqtt_Object"].append(self.mqtt_sub)
        self.mqtt_sub.start()
        self.mqtt_started = True

    def unsubscribe_mqtt(self, game_name: str):
        """Unsubscribe from an MQTT topic.

        Args:
            game_name (str): The name of the game.
        """
        try:
            self.mqtt_sub.stop_loop()
            mqtt_index = mqtt_list["Game"].index(game_name)
            mqtt_list["Game"].pop(mqtt_index)
            mqtt_list["Mqtt_Object"].pop(mqtt_index)
        except AttributeError:
            infos_logger.log_infos("[MQTT]", "Failed to start mqtt subscriber (too fast)")
            pass

    def check_game_name(self, conn: socket, message: list) -> bool:
        """
        Verify if the game name is correct.

        Args:
            conn (socket): The client's connection socket.
            message (list): The client's message.

        Returns:
            bool: True if the game name is correct, False otherwise.
        """
        for game in game_list["Name"]:
            if game == message[1]:
                self.send_client(conn, f"CHECK_GAME|GAME-NAME-ALREADY-USED|{message[1]}|{message[2]}|{message[3]}|")
                return False
        self.send_client(conn, f"CHECK_GAME|GAME-NAME-CORRECT|{message[1]}|{message[2]}|{message[3]}|")
        return True
    
    def __deco(self, conn: socket):
        """Disconnect a client.
        
        Args:
            conn (socket): The client's connection socket."""
        def game_tour_deco(conn: socket):
            """Remove a player from the game tour list.
            
            Args:
                conn (socket): The client's connection socket."""
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
        
        def looking_for_games_players_deco(conn: socket):
            """Remove a player from the list of players looking for games.

            Args:
                conn (socket): The client's connection socket."""
            try:
                looking_for_games_players.remove(conn)
            except ValueError:
                pass

        def reception_list_deco(conn: socket):
            """Remove a player from the reception list.
            
            Args:
                conn (socket): The client's connection socket."""
            index_conn = reception_list["Conn"].index(conn)
            reception_list["Conn"].remove(conn)
            reception_list["Reception"].pop(index_conn)
        
        def conn_list_deco(conn: socket):
            """Remove a player from the list of connections.
            
            Args:
                conn (socket): The client's connection socket."""
            conn_list.remove(conn)

        def game_deco():
            """Remove a player from the list of players in the game."""
            try:
                game_name = self.get_game_name(self.username)
                self.leave_game(conn, game_name = game_name, player = self.username)
            except ValueError:
                pass
            except AttributeError:
                pass

        def waiting_room_deco():
            """Remove a player from the waiting room."""
            try:
                index_conn = waiting_room["Conn"].index(conn)
                waiting_room["Conn"].remove(conn)
                waiting_room["Player"].pop(index_conn)
                waiting_room["Game"].pop(index_conn)
            except ValueError:
                pass
        
        def send_deco(conn: socket, player: str):
            """Send a message to all players to inform them that a player has disconnected.
            
            Args:
                conn (socket): The client's connection socket.
                player (str): The player's username."""
            try:
                for connexion in game_tour["Conn"]:
                    if connexion != conn and game_tour["Game"][game_tour["Conn"].index(connexion)] == game_tour["Game"][game_tour["Conn"].index(conn)]:
                        self.send_client(connexion, f"LOBBY_STATE|PLAYER-DECO|{player}|")
            except ValueError:
                pass

        def lists_deco(conn: socket):
            """Remove a player from the lists.
            
            Args:
                conn (socket): The client's connection socket."""
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
        
        lists_deco(conn)
        infos_logger.log_infos("[SOCKET]", f"{self.username} just disconnected - {conn}")

    def check_user_unique(self, user: str) -> bool:
        """
        Check if the player's username is unique.

        Args:
            user (str): The player's username.

        Returns:
            bool: True if the username is unique, False otherwise.
        """
        for player in game_tour["Player"]:
            if player == user:
                return False
        return True

    def wrong(self, conn: socket, player: str):
        """
        Send a message to the client indicating that they made a mistake.

        Args:
            conn (socket): The client's connection socket.
            player (str): The player's username.
        """
        self.send_client(conn, "GAME_MESSAGE|WRONG|")
        if self.death_mode != 0:
            try:
                #On vérifie si le joueur est dans une partie
                player_index = self.players["Player"].index(player)
                game = self.players["Game"][player_index]
            except ValueError:
                #Si le joueur n'est pas dans une partie on le récupère
                player_index = game_tour["Player"].index(player)
                game_name = game_tour["Game"][player_index]
                self.new_players(game_name=game_name, creator=None)
                self.game = game_list["Game_Object"][game_list["Name"].index(game_name)]
                game = game_name
            self.game.compteur_thread.time_is_up()
            self.game.stop_compteur(game)

    def right(self, conn: socket, player: str):
        """
        Send a message to the client indicating that they found a word and stop the timer.
        If the player is not in a game, retrieve them from the list of players.

        Args:
            conn (socket): The client's connection socket.
            player (str): The player's username.
        """
        self.send_client(conn, f"GAME_MESSAGE|RIGHT|{player}|")
        try:
            #On vérifie si le joueur est dans une partie
            player_index = self.players["Player"].index(player)
            game = self.players["Game"][player_index]
        except ValueError:
            #Si le joueur n'est pas dans une partie on le récupère
            player_index = game_tour["Player"].index(player)
            game_name = game_tour["Game"][player_index]
            self.new_players(game_name=game_name, creator=None)
            self.game = game_list["Game_Object"][game_list["Name"].index(game_name)]
            game = game_name
        self.game.stop_compteur(game)

    def check_syllabe(self, word: str, sylb: str) -> bool:
        """
        Check if the word contains the given syllable.

        Args:
            word (str): Word to check.
            sylb (str): Syllable to check.

        Returns:
            bool: True if the word contains the syllable, False otherwise.
        """
        if sylb in word:
            return True
        else:
            return False
        
    def send_client(self, conn: socket, message: str):
        """
        Send a message to the client.

        Args:
            conn (socket): The client's connection socket.
            message (str): The message to send.
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