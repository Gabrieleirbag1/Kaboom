from server_utils import *
import random, time, threading

syllabes = ("ai", "an", "au", "ay", "ea", "ee", "ei", "eu", "ey", "ie", "is", "oe", "oi", "oo", "ou", "oy", "ui", "uy", "y", "ch", "sh", "th", "dge", "tch", "ng", "ph", "gh", "kn", "wr", "mb", "ll", "mm", "nn", "pp", "rr", "ss", "tt", "zz", "qu", "ce", "ci", "ge", "gi", "gue", "que", "se", "si", "ze", "ssi", "s", "c", "g", "sc", "xo","cq", "bra", "bre", "bri", "bro", "bru", "dra", "dre", "dri", "dro", "dru", "fra", "fre", "fri", "fro", "fru", "gra", "gre", "gri", "gro", "gru", "pra", "pre", "pri", "pro", "pru", "tra", "tre", "tri", "tro", "tru", "bla", "ble", "bli", "blo", "blu", "cla", "cle", "cli", "clo", "dra", "dre", "dri", "dro", "dru", "fra", "fre", "fri", "fro", "fru", "gra", "gre", "gri", "gro", "gru", "pra", "pre", "pri", "pro", "pru", "tra", "tre", "tri", "tro", "tru")

game_tour = {"Player": ["Juan"], "Conn": ["conn"]}
class Game():
    """Game() : Classe qui gère le jeu"""
    def __init__(self, conn, players, creator):
        threading.Thread.__init__(self)
        self.conn = conn
        self.players = players
        self.creator = creator
        self.timer = None
        self.players = {"Player": ["Juan"], "Ready": [True], "Lifes": [3], "Game": ["Juan"]}


    def run(self):
        """run() : Fonction qui lance le jeu"""
        print(self.players["Player"])
        for player in self.players["Player"]:
            index_player = self.players["Player"].index(player)

            if self.players["Game"][index_player] == self.creator:
                if self.players["Ready"][index_player] and self.players["Lifes"][index_player] > 0:
                    conn = self.get_conn(player)
                    sylb = self.syllabe()
                    #conn.send(sylb.encode())
                    timerule_min = 3
                    time_rule_max = 3
                    compteur_thread = threading.Thread(target=self.compteur, args=[timerule_min, time_rule_max])
                    compteur_thread.start()

    def compteur(self, timerule_min, time_rule_max):
        """compteur() : Fonction qui permet de compter le temps entre chaque message
        
        Args:
            timerule_min (int): Temps minimum entre chaque message
            time_rule_max (int): Temps maximum entre chaque message"""
        time.sleep(timerule_min)
        delay = random.randint(timerule_min, time_rule_max)
        self.timer = threading.Timer(delay, self.time_is_up)
        #self.stop_compteur()
        self.timer.start()
    
    def get_conn(self, player):
        """get_conn() : Fonction qui permet de récupérer le socket de connexion du joueur
        
        Args:
            player (str): Pseudo du joueur"""
        index_player = game_tour["Player"].index(player)
        conn = game_tour["Conn"][index_player]
        return conn

    def stop_compteur(self):
        """stop_compteur() : Fonction qui permet d'arrêter le compteur"""
        print("stop_compteur")
        if self.timer is not None:
            self.timer.cancel()
            print("Timer annulé")

    def time_is_up(self):
        print(f"Signal reçu")
        for conn in conn_list:
            conn.send("Time's up".encode())

    def syllabe(self):
        """syllabe() : Fonction qui génère une syllabe aléatoire"""
        return random.choice(syllabes)
            
i = Game("conn", "players", "Juan")
i.run()