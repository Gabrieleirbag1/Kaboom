from server_utils import *
import random, time, threading

#syllabes = ("clo", "clo", "clo")

class Game(threading.Thread):
    """Game() : Classe qui gère le jeu"""
    def __init__(self, conn, players, creator, game, rules):
        threading.Thread.__init__(self)
        self.conn = conn
        self.players = players
        self.creator = creator
        self.game = game
        self.rules = rules

        syllabes = ["ai", "an", "au", "ay", "ea", "ee", "ei", "eu", "ey", "ie", "is", "oe", "oi", "oo", "ou", "oy", "ui", "uy", "y", "ch", "sh", "th", "dge", "tch", "ng", "ph", "gh", "kn", "wr", "mb", "ll", "mm", "nn", "pp", "rr", "ss", "tt", "zz", "qu", "ce", "ci", "ge", "gi", "gue", "que", "se", "si", "ze", "ssi", "s", "c", "g", "sc", "xo","cq", "bra", "bre", "bri", "bro", "bru", "dra", "dre", "dri", "dro", "dru", "fra", "fre", "fri", "fro", "fru", "gra", "gre", "gri", "gro", "gru", "pra", "pre", "pri", "pro", "pru", "tra", "tre", "tri", "tro", "tru", "bla", "ble", "bli", "blo", "blu", "cla", "cle", "cli", "clo", "dra", "dre", "dri", "dro", "dru", "fra", "fre", "fri", "fro", "fru", "gra", "gre", "gri", "gro", "gru", "pra", "pre", "pri", "pro", "pru", "tra", "tre", "tri", "tro", "tru", "erdre", "colat"]
        self.syllabes = syllabes

    def run(self):
        """run() : Fonction qui lance le jeu"""
        print("Début")
        self.set_lifes()
        self.set_game()
        self.set_syllabes_rules()
        while self.game:
            for player in self.players["Player"]:
                #print("Boucle")
                self.index_player = self.players["Player"].index(player)

                if self.players["Game"][self.index_player] == self.creator:
                    #print("Bonne partie")
                    #print(self.players)
                    if not self.check_game_ended():
                        print("Partie en cours")
                        if self.players["Ready"][self.index_player] and self.players["Lifes"][self.index_player] > 0:
                            #print(self.rules)
                            #print("Ready and lify")
                            conn = self.get_conn(player)
                            sylb = self.syllabe()
                            print(sylb)
                            time.sleep(0.5)
                            conn.send(sylb.encode())
                            
                            timerule_min = self.rules[0]
                            time_rule_max = self.rules[1]

                            self.stopFlag = threading.Event()
                            delay = random.randint(timerule_min, time_rule_max)
                            compteur_thread = Compteur(self.stopFlag, delay, self.players, self.index_player, self.creator)
                            compteur_thread.start()
                            compteur_thread.join()

        else:
            self.game_ended()
            self.get_ready_false()
            print("Partie terminée")
    
    def set_syllabes_rules(self):
        """set_syllabes_rules() : Fonction qui permet de définir la longueur des syllabes"""
        delete_list = []
        print("rules syllabes", self.rules[3], self.rules[4])
        for syllabe in self.syllabes:
            if len(syllabe) < self.rules[3] or len(syllabe) > self.rules[4]:
                delete_list.append(syllabe)
        for syllabe in delete_list:
            self.syllabes.remove(syllabe)

    def game_ended(self):
        """game_ended() : Fonction qui est appelée lorsque la partie est terminée"""
        #print("GAME ENDED WOW", self.creator)
        for conn in game_tour["Conn"]:
            index_player = game_tour["Conn"].index(conn)
            if game_tour["Game"][index_player] == self.creator:
                print("-----------------------", game_tour, self.creator)
                conn.send(f"GAME|GAME_ENDED|{self.creator}".encode())

    def get_ready_false(self):
        """get_ready_false() : Fonction qui met à jour le statut "Ready" des joueurs"""
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)
            self.players["Ready"][index_player] = False

    def set_game(self):
        """set_game() : Fonction qui initialise la partie"""
        print("Set game")
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            game_tour["Game"][index_player] = self.creator
            print(game_tour)

    def set_lifes(self):
        """set_lifes() : Fonction qui initialise les vies des joueurs"""
        print("Set lifes")
        for player in self.players["Player"]:
            self.index_player = self.players["Player"].index(player)
            self.players["Lifes"][self.index_player] = self.rules[2]
            print(self.players)

    def check_game_ended(self) -> bool:
        """check_game_ended() : Fonction qui vérifie si la partie est terminée
        
        Returns:
            bool: True si la partie est terminée, False sinon"""
        not_dead_players = []
        for player in self.players["Player"]:
            if self.players["Game"][self.index_player] == self.creator and self.players["Lifes"][self.index_player] > 0:
                not_dead_players.append(player)
        if len(not_dead_players) > 0:
            return False
        else:
            self.game = False
            return True
    
    def get_conn(self, player) -> str:
        """get_conn() : Fonction qui permet de récupérer le socket de connexion du joueur
        
        Args:
            player (str): Pseudo du joueur"""
        index_player = game_tour["Player"].index(player)
        conn = game_tour["Conn"][index_player]
        return conn

    def stop_compteur(self, game):
        """stop_compteur() : Fonction qui permet d'arrêter le compteur
        
        Args:
            game (str): Nom de la partie"""
        print("arrêt")
        if game == self.creator:
            self.stopFlag.set()
            print("Timer annulé")

    def syllabe(self):
        """syllabe() : Fonction qui génère une syllabe aléatoire"""
        return random.choice(self.syllabes)
            

class Compteur(threading.Thread):
    """Compteur(threading.Thread) : Classe qui gère le compteur"""
    def __init__(self, event, delay, players, index_player, creator):
        """__init__() : Initialisation de la classe Compteur
        
        Args:
            event (threading.Event): Event qui permet d'arrêter le compteur
            delay (int): Délai du compteur
            players (dict): Dictionnaire contenant les informations des joueurs
            index_player (int): Index du joueur dans le dictionnaire "players"""
        threading.Thread.__init__(self)
        self.stopped_event = event
        self.delay = delay
        self.players = players
        self.index_player = index_player
        self.creator = creator

        self.username = self.players["Player"][self.index_player]

    def run(self):
        """run() : Fonction qui lance le compteur"""
        while not self.stopped_event.wait(self.delay) and not self.stopped_event.is_set():
            self.time_is_up()
            self.stopped_event.set()

    def time_is_up(self):
        """time_is_up() : Fonction qui est appelée lorsque le temps est écoulé"""
        print(f"Signal reçu")
        for player in self.players["Player"]:
            index_player = game_tour["Player"].index(player)
            if game_tour["Game"][index_player] == self.creator:
                conn = game_tour["Conn"][index_player]
                conn.send(f"GAME|TIME'S_UP|{self.username}".encode())

        self.players["Lifes"][self.index_player] -= 1