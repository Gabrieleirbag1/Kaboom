from server_utils import *
import random, time, threading
from socket import socket as socket
from server_logs import ErrorLogger

ErrorLogger.setup_logging()

class Game(threading.Thread):
    """This class manages a game in its entirety
    
    Attributes:
        conn (socket): The client's connection socket
        players (dict): Dictionary containing the players' information
        creator (str): The creator's nickname
        game (bool): The game's status
        rules (list): List containing the game's rules
        game_name (str): The game's name"""
    def __init__(self, conn: socket, players: dict[str, bool, int, object], creator: str, game: bool, rules: list, game_name: str, langue: str):
        """Initialization of the Game class
        
        Args:
            conn (socket): Client connection socket
            players (dict[str, bool, int, Game]): Dictionary containing player information
            creator (str): Username of the game creator
            game (bool): Game status
            rules (list): List containing the game rules
            game_name (str): Name of the game
            langue (str): Language for the game"""
        threading.Thread.__init__(self)
        self.conn = conn
        self.players = players
        self.creator = creator
        self.game = game
        self.rules = rules
        self.game_name = game_name
        self.shared_state = {"bad_round": False}

        self.stop_compteur_lock = threading.Lock()
        self.players_conn_list = self.get_conn()
        syllabes = read_words_from_file(langue)
        self.syllabes = syllabes
        self.repetition_syllabes = []

        self.classement = []

    def run(self):
        """Run the game when the thread is started"""
        infos_logger.log_infos("[GAME STATE]", f"Game Infos : {self.players} {self.creator}")
        self.check_death_mode()
        self.send_game_started()
        self.set_ingame(start = True)
        self.set_lifes()
        self.set_game()
        self.set_syllabes_rules()
        while self.game:
            for player in self.players["Player"]:
                self.index_player = self.players["Player"].index(player)
                if not self.check_game_ended():
                    if self.players["Ready"][self.index_player] and self.players["Lifes"][self.index_player] > 0:
                        sylb = self.set_syllabe()
                        if self.shared_state["bad_round"]:
                            time.sleep(3)  # temps d'animation
                            self.shared_state["bad_round"] = False
                        self.send_syllabe(self.players_conn_list, sylb, player)
                        self.start_compteur()
                else:
                    break
        else:
            self.game_ended(self.players_conn_list)
            self.get_ready_false()
            self.reset_players()
            add_waiting_room_players(self.game_name)
            infos_logger.log_infos("[GAME STATE]", f"Game ended : {self.game_name}")

    def start_compteur(self):
        """Start the timer for the game round"""
        timerule_min = self.rules[0]
        time_rule_max = self.rules[1]

        self.stopFlag = threading.Event()
        delay = random.randint(timerule_min, time_rule_max)
        self.compteur_thread = Compteur(self.stopFlag, delay, self.players, self.index_player, self.game_name, self.shared_state, self.players_conn_list, self.classement)
        self.compteur_thread.start()
        self.compteur_thread.join()

    def set_syllabe(self):
        """Sets the syllable for the game round"""
        if not self.repetition_syllabes:
            sylb = self.syllabe()
            for i in range(self.rules[5]):
                self.repetition_syllabes.append(sylb)
        else:
            sylb = self.repetition_syllabes[-1]
            self.repetition_syllabes.pop(-1)
        return sylb
    
    def set_ingame(self, start: bool):
        """Sets the "InGame" status of the players

        Args:
            start (bool): True if the game has started, False otherwise"""
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            game_tour["InGame"][index_player] = start

    def set_syllabes_rules(self):
        """Set the syllable rules for the game"""
        delete_list = []
        for syllabe in self.syllabes:
            if len(syllabe) < self.rules[3] or len(syllabe) > self.rules[4]:
                delete_list.append(syllabe)
        for syllabe in delete_list:
            self.syllabes.remove(syllabe)

    def game_ended(self, players_conn_list: list):
        """Notify players that the game has ended

        Args:
            players_conn_list (list): List of player connection sockets"""
        time.sleep(4.5)#à ajuster en fonction du temps de l'animation
        self.get_classement()
        for conn in players_conn_list:
            send_client(conn, f"GAME_MESSAGE|GAME-ENDED|{self.game_name}|{self.classement}|")
        self.set_ingame(start=False)

    def get_classement(self):
        """Get the game ranking"""
        self.classement.reverse()

    def get_ready_false(self):
        """Updaye the "Ready" status of the players"""
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)
            self.players["Ready"][index_player] = False
    
        for player in game_tour["Player"]:
            index_player = game_tour["Player"].index(player)
            if game_tour["Game"][index_player] == self.game_name and player != self.creator:
                game_tour["InGame"][index_player] = False
                game_tour["Ready"][index_player] = False

    def reset_players(self):
        """Reset the players' status"""
        game_conn_list = {"Conn": [], "Player":[]}
        for conn in reception_list["Conn"]:
            try:
                index_conn = game_tour["Conn"].index(conn)
            except ValueError:
                ErrorLogger.log_error("[GAME ERROR]", f"Connection {conn} not found in game_tour.")
                continue
            if game_tour["Player"][index_conn] in self.players["Player"]:
                game_conn_list["Conn"].append(conn)
                game_conn_list["Player"].append(game_tour["Player"][index_conn])

        for conn in game_conn_list["Conn"]:
            try:
                game_conn_list_index = game_conn_list["Conn"].index(conn)
            except ValueError:
                ErrorLogger.log_error("[GAME ERROR]", f"Connection {conn} not found in game_conn_list.")
                continue
            player = game_conn_list["Player"][game_conn_list_index]
            conn_index = reception_list["Conn"].index(conn)
            reception = reception_list["Reception"][conn_index]
            join = self.check_if_creator(player)
            reception.reset_players(join, self.creator, self.game_name)

    def check_if_creator(self, player: str) -> bool:
        """Checks if the player is the creator of the game

        Args:
            player (str): Player's nickname

        Returns:
            bool: True if the player is the creator, False otherwise"""
        if player != self.creator:
            return True
        else:
            return False
        
    def check_death_mode(self):
        """Check if the game is in death mode"""
        self.death_mode_state = self.rules[6]
        for conn in reception_list["Conn"]:
            index_conn = reception_list["Conn"].index(conn)
            reception = reception_list["Reception"][index_conn]
            reception.death_mode = self.death_mode_state
        if self.rules[6] == 2:
            self.rules[2] = 1
            
            
    def set_game(self):
        """Set the game name for the players"""
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            game_tour["Game"][index_player] = self.game_name

    def set_lifes(self):
        """Set the number of lives for the players""" 
        for player in self.players["Player"]:
            self.index_player = self.players["Player"].index(player)
            self.players["Lifes"][self.index_player] = self.rules[2]
        self.send_lifes_rules()

    def send_game_started(self):
        """Send a message to the players that the game has started"""
        for conn in self.players_conn_list:
            send_client(conn, f"GAME_MESSAGE|GAME-STARTED|{self.game_name}|{self.death_mode_state}|")

    def send_lifes_rules(self):
        """Send the number of lives and rules to the players"""
        ready_players_list = []
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)
            if self.players["Ready"][index_player]:
                ready_players_list.append(player)
        ready_players = ",".join(ready_players_list)
        for conn in self.players_conn_list:
            send_client(conn, f"GAME_MESSAGE|LIFES-RULES|{self.rules[2]}|{ready_players}|")

    def check_game_ended(self) -> bool:
        """Check if the game has ended

        Returns:
            bool: True if the game has ended, False otherwise"""
        not_dead_players = []
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)
            if self.players["Lifes"][index_player] > 0:
                if self.players["Ready"][index_player]:
                    not_dead_players.append(player)
        if len(not_dead_players) > 1:
            return False #la game continue
        else:
            self.get_winner(not_dead_players[0])
            self.game = False
            return True
        
    def get_winner(self, winner: str):
        """Get the winner's avatar and nickname

        Args:
            winner (str): Winner's nickname"""
        for player in game_tour["Player"]:
            index_player = game_tour["Player"].index(player)
            if player == winner:
                self.classement.append([winner, game_tour["Avatar"][index_player]])
    
    def get_conn(self) -> list:
        """Get the players' connection sockets

        Returns:
            list: List of player connection sockets for the game"""
        player_conn_list = []
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            if game_tour["Game"][index_player] == self.game_name:
                conn = game_tour["Conn"][index_player]
                player_conn_list.append(conn)
        return player_conn_list

    def stop_compteur(self, game: str):
        """Stop the timer for the game round

        Args:
            game (str): Game name"""
        with self.stop_compteur_lock:
            if game == self.game_name:
                self.stopFlag.set()
                self.repetition_syllabes.clear()

    def syllabe(self):
        """Generate a random syllable"""
        return random.choice(self.syllabes)
    
    def send_syllabe(self, players_conn_list: list, sylb: str, player: str):
        """Send the syllable to the players

        Args:
            players_conn_list (list): List of player connection sockets
            sylb (str): Syllable
            player (str): Player's nickname"""
        for connexion in players_conn_list:
            send_client(connexion, f"SYLLABE_|{sylb}|{player}|{self.death_mode_state}|")

class Compteur(threading.Thread):
    """Class that manages the game round timer
    
    Attributes:
        event (threading.Event): Event to stop the timer
        delay (int): Timer delay
        players (dict): Dictionary containing player information
        index_player (int): Index of the player in the "players" dictionary
        shared_state (dict): Round status (True if the player lost, False otherwise)
        game_name (str): Name of the game
        players_conn_list (list): List of player connection sockets for the game
        classement (list): List of player rankings"""
    def __init__(self, event: threading.Event, delay: int, players: dict, index_player: int, game_name: str, shared_state: dict, players_conn_list: list, classement: list):
        """Initialization of the Compteur class
        
        Args:
            event (threading.Event): Event to stop the timer
            delay (int): Timer delay
            players (dict): Dictionary containing player information
            index_player (int): Index of the player in the "players" dictionary
            shared_state (dict): Round status (True if the player lost, False otherwise)
            game_name (str): Name of the game
            players_conn_list (list): List of player connection sockets for the game
            classement (list): List of player rankings"""
        threading.Thread.__init__(self)
        self.stopped_event = event
        self.delay = delay
        self.players = players
        self.index_player = index_player
        self.shared_state = shared_state
        self.game_name = game_name
        self.players_conn_list = players_conn_list

        self.username = self.players["Player"][self.index_player]
        self.classement = classement

    def run(self):
        """Run the timer when the thread is started"""
        while not self.stopped_event.wait(self.delay) and not self.stopped_event.is_set():
            self.time_is_up()
            self.stopped_event.set()

    def time_is_up(self):
        """Sends a message to the players when the timer runs out"""
        for conn in self.players_conn_list:
            send_client(conn, f"GAME_MESSAGE|TIME'S-UP|{self.username}|")

        self.players["Lifes"][self.index_player] -= 1
        self.shared_state["bad_round"] = True  # Update the shared state
        self.check_classement()

    def check_classement(self):
        """Add a player to the ranking if he's dead"""
        if self.players["Lifes"][self.index_player] == 0:
            self.classement.append([self.username, None])