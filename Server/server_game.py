from server_utils import *
import random, time, threading
from socket import socket as socket
#syllabes = ("clo", "clo", "clo")

class Game(threading.Thread):
    """Game() : Classe qui gère le jeu"""
    def __init__(self, conn : socket, players : dict, creator : str, game : bool, rules : list, game_name : str):
        """__init__() : Initialisation de la classe Game
        
        Args:
            conn (socket): Socket de connexion du client
            players (dict): Dictionnaire contenant les informations des joueurs
            creator (str): Pseudo du créateur de la partie
            game (bool): Statut de la partie
            rules (list): Liste contenant les règles de la partie
            game_name (str): Nom de la partie"""
        threading.Thread.__init__(self)
        self.conn = conn
        self.players = players
        self.creator = creator
        self.game = game
        self.rules = rules
        self.game_name = game_name

        self.stop_compteur_lock = threading.Lock()
        self.players_conn_list = self.get_conn()
        syllabes = read_words_from_file()
        self.syllabes = syllabes
        self.repetition_syllabes = []

    def run(self):
        """run() : Fonction qui lance le jeu"""
        print("Début", self.creator, self.players)
        self.set_ingame(start = True)
        self.set_lifes()
        self.set_game()
        self.set_syllabes_rules()
        while self.game:
            for player in self.players["Player"]:
                print("Boucle")
                print(self.players)
                self.index_player = self.players["Player"].index(player)
                if not self.check_game_ended():
                    print("Partie en cours")
                    if self.players["Ready"][self.index_player] and self.players["Lifes"][self.index_player] > 0:
                        #print(self.rules)
                        print("Ready and lify", player)
                        sylb = self.set_syllabe()
                        time.sleep(0.5) #temps d'animation
                        self.send_syllabe(self.players_conn_list, sylb, player)
                        self.start_compteur()
                else:
                    break
        else:
            self.game_ended(self.players_conn_list)
            self.get_ready_false()
            self.reset_players()
            add_waiting_room_players(self.game_name)
            print("Partie terminée")

    def start_compteur(self):
        timerule_min = self.rules[0]
        time_rule_max = self.rules[1]

        self.stopFlag = threading.Event()
        delay = random.randint(timerule_min, time_rule_max)
        compteur_thread = Compteur(self.stopFlag, delay, self.players, self.index_player, self.game_name, self.players_conn_list)
        compteur_thread.start()
        compteur_thread.join()

    def set_syllabe(self):
        if not self.repetition_syllabes:
            sylb = self.syllabe()
            for i in range(self.rules[5]):
                self.repetition_syllabes.append(sylb)
        else:
            sylb = self.repetition_syllabes[-1]
            self.repetition_syllabes.pop(-1)
        return sylb
    
    def set_ingame(self, start : bool):
        """set_ingame() : Fonction qui met à jour le statut "InGame" des joueurs
        
        Args:
            start (bool): True si la partie commence, False sinon"""
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            game_tour["InGame"][index_player] = start
        # print(game_tour, "set_ingame")

    def set_syllabes_rules(self):
        """set_syllabes_rules() : Fonction qui permet de définir la longueur des syllabes"""
        delete_list = []
        #print("rules syllabes", self.rules[3], self.rules[4])
        for syllabe in self.syllabes:
            if len(syllabe) < self.rules[3] or len(syllabe) > self.rules[4]:
                delete_list.append(syllabe)
        for syllabe in delete_list:
            self.syllabes.remove(syllabe)

    def game_ended(self, players_conn_list : list):
        """game_ended() : Fonction qui est appelée lorsque la partie est terminée
        
        Args:
            players_conn_list (list): Liste des sockets de connexion des joueurs"""
        time.sleep(1)#à ajuster en fonction du temps de l'animation
        for conn in players_conn_list:
            envoi(conn, f"GAME_MESSAGE|GAME-ENDED|{self.game_name}|")
        self.set_ingame(start = False)

    def get_ready_false(self):
        """get_ready_false() : Fonction qui met à jour le statut "Ready" des joueurs"""
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)
            self.players["Ready"][index_player] = False
    
        for player in game_tour["Player"]:
            index_player = game_tour["Player"].index(player)
            if game_tour["Game"][index_player] == self.game_name and player != self.creator:
                game_tour["InGame"][index_player] = False
                game_tour["Ready"][index_player] = False

    def reset_players(self):
        """reset_players() : Fonction qui supprime les joueurs de la partie"""
        game_conn_list = {"Conn": [], "Player":[]}
        for conn in reception_list["Conn"]:
            index_conn = game_tour["Conn"].index(conn)
            if game_tour["Player"][index_conn] in self.players["Player"]:
                game_conn_list["Conn"].append(conn)
                game_conn_list["Player"].append(game_tour["Player"][index_conn])

        for conn in game_conn_list["Conn"]:
            game_conn_list_index = game_conn_list["Conn"].index(conn)
            player = game_conn_list["Player"][game_conn_list_index]
            conn_index = reception_list["Conn"].index(conn)
            reception = reception_list["Reception"][conn_index]
            join = self.check_if_creator(player)
            print("reset players", join, self.creator,)
            reception.reset_players(join, self.creator, self.game_name)

    def check_if_creator(self, player) -> bool:
        """check_is_creator() : Fonction qui vérifie si le joueur est le créateur de la partie
        
        Args:
            player (str): Pseudo du joueur
        Returns:
            bool: True si le joueur n'est pas le créateur, False sinon"""
        if player != self.creator:
            return True
        else:
            return False

    def set_game(self):
        """set_game() : Fonction qui initialise la partie"""
        print("Set game")
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            game_tour["Game"][index_player] = self.game_name
            # print(game_tour)

    def set_lifes(self):
        """set_lifes() : Fonction qui initialise les vies des joueurs"""
        print("Set lifes")
        for player in self.players["Player"]:
            self.index_player = self.players["Player"].index(player)
            self.players["Lifes"][self.index_player] = self.rules[2]
        self.send_lifes_rules()

    def send_lifes_rules(self):
        """send_lifes_rules() : Fonction qui envoie les règles de la partie"""
        ready_players_list = []
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)
            if self.players["Ready"][index_player]:
                ready_players_list.append(player)
        ready_players = ",".join(ready_players_list)
        for conn in self.players_conn_list:
            envoi(conn, f"GAME_MESSAGE|LIFES-RULES|{self.rules[2]}|{ready_players}|")

    def check_game_ended(self) -> bool:
        """check_game_ended() : Fonction qui vérifie si la partie est terminée
        
        Returns:
            bool: True si la partie est terminée, False sinon"""
        not_dead_players = []
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)
            if self.players["Lifes"][index_player] > 0:
                if self.players["Ready"][index_player]:
                    not_dead_players.append(player)
        print(not_dead_players, len(not_dead_players), "not dead")
        if len(not_dead_players) > 1:
            return False #la game continue
        else:
            self.game = False
            return True
    
    def get_conn(self) -> list:
        """get_conn() : Fonction qui permet de récupérer le socket de connexion du joueur
        
        Args:
            player (str): Pseudo du joueu
        
        Returns:
            list: Liste des sockets de connexion des joueurs de la partie"""
        player_conn_list = []
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            if game_tour["Game"][index_player] == self.game_name:
                conn = game_tour["Conn"][index_player]
                player_conn_list.append(conn)
        return player_conn_list

    def stop_compteur(self, game):
        """stop_compteur() : Fonction qui permet d'arrêter le compteur
        
        Args:
            game (str): Nom de la partie"""
        print("arrêt")
        with self.stop_compteur_lock:
            if game == self.game_name:
                self.stopFlag.set()
                self.repetition_syllabes.clear()
                print("Timer annulé")

    def syllabe(self):
        """syllabe() : Fonction qui génère une syllabe aléatoire"""
        return random.choice(self.syllabes)
    
    def send_syllabe(self, players_conn_list : list, sylb : str, player : str):
        """send_syllabe() : Fonction qui envoie une syllabe à tous les joueurs

        Args:
            players_conn_list (list): Liste des sockets de connexion des joueurs"""
        for connexion in players_conn_list:
            envoi(connexion, f"SYLLABE_|{sylb}|{player}|")

class Compteur(threading.Thread):
    """Compteur(threading.Thread) : Classe qui gère le compteur"""
    def __init__(self, event, delay, players, index_player, game_name, players_conn_list):
        """__init__() : Initialisation de la classe Compteur
        
        Args:
            event (threading.Event): Event qui permet d'arrêter le compteur
            delay (int): Délai du compteur
            players (dict): Dictionnaire contenant les informations des joueurs
            index_player (int): Index du joueur dans le dictionnaire "players"
            game_name (str): Nom de la partie
            players_conn_list (list): Liste des sockets de connexion des joueurs de la partie"""
        threading.Thread.__init__(self)
        self.stopped_event = event
        self.delay = delay
        self.players = players
        self.index_player = index_player
        self.game_name = game_name
        self.players_conn_list = players_conn_list

        self.username = self.players["Player"][self.index_player]

    def run(self):
        """run() : Fonction qui lance le compteur"""
        while not self.stopped_event.wait(self.delay) and not self.stopped_event.is_set():
            self.time_is_up()
            self.stopped_event.set()

    def time_is_up(self):
        """time_is_up() : Fonction qui est appelée lorsque le temps est écoulé"""
        print(f"Signal reçu")

        for conn in self.players_conn_list:
            envoi(conn, f"GAME_MESSAGE|TIME'S-UP|{self.username}|")

        self.players["Lifes"][self.index_player] -= 1