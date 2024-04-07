import sys, socket, threading, time, random, re, requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from client_utils import *

class ReceptionThread(QThread):
    """ReceptionThread(QThread) : Classe qui gère la réception des messages du serveur
    
    Args:
        QThread (class): Classe mère de ReceptionThread
    
    Signals:
        name_correct (bool): Signal qui permet de vérifier si le nom d'utilisateur est correct
        sylb_received (str): Signal qui permet de recevoir une syllabe
        game_signal (str): Signal qui permet de recevoir un message de jeu
        game_created (str, str): Signal qui permet de recevoir un message de création de jeu
        game_deleted (str): Signal qui permet de recevoir un message de suppression de jeu
        join_signal (str): Signal qui permet de recevoir un message de connexion à un jeu
        lobby_state_signal (str): Signal qui permet de recevoir un message d'état du lobby"""
    name_correct = pyqtSignal(bool)
    sylb_received = pyqtSignal(str, str)
    game_signal = pyqtSignal(str)
    check_game_signal = pyqtSignal(list)
    game_created = pyqtSignal(str, str, int)
    game_deleted = pyqtSignal(str)
    join_signal = pyqtSignal(str)
    lobby_state_signal = pyqtSignal(str)

    def __init__(self):
        """__init__() : Constructeur de la classe ReceptionThread"""
        super().__init__()

    def run(self):
        """run() : Fonction qui permet de recevoir des messages du serveur"""
        global syllabe
        flag = False
        while not flag:
            response = client_socket.recv(1024).decode()
            print(response)
            try:
                reply = response.split("|")
            except:
                reply = response
            if not response:
                flag = True
                break

            responses = self.manage_response(response)
            
            for response in responses:
                try:
                    reply = response.split("|")
                except:
                    reply = response
                if reply[0] == "COMMAND_":
                    self.manage_command(reply[1])

                elif reply[0] == "NAME_ALREADY_USED":
                    #print("Username already used")
                    self.name_correct.emit(False)

                elif reply[0] == "NAME_CORRECT":
                    #print("Username correct")
                    self.name_correct.emit(True)
                
                elif reply[0] == "GAME_MESSAGE":
                    try:
                        game_message = f"{reply[0]}|{reply[1]}|{reply[2]}|{reply[3]}"
                    except IndexError:
                        game_message = f"{reply[0]}|{reply[1]}|{reply[2]}"
                    print(datetime.datetime.now(), "its riggght")
                    self.game_signal.emit(game_message)
                
                elif reply[0] == "CHECK_GAME":
                    self.check_game_signal.emit(reply)

                elif reply[0] == "GAME_CREATED":
                    # print("Game created")
                    game_name = reply[1]
                    private_game = reply[2]
                    players_number = int(reply[3])
                    self.game_created.emit(game_name, private_game, players_number)

                elif reply[0] == "GAME_DELETED":
                    # print("Game deleted")
                    game_name = reply[1]
                    self.game_deleted.emit(f"{game_name}")

                elif reply[0] == "LOBBY_STATE":
                    print("LOBBY STATE")
                    lobby_state = f"{reply[0]}|{reply[1]}|{reply[2]}|{reply[3]}"
                    self.lobby_state_signal.emit(lobby_state)

                elif reply[0] == "JOIN_STATE":
                    print("Join")
                    self.join_signal.emit(response)

                elif reply[0] == "SYLLABE_":
                    syllabe = reply[1]
                    player = reply[2]
                    self.sylb_received.emit(syllabe, player)
                    syllabes.append(syllabe)

                else:
                    print("Unknown message", response)

    def manage_command(self, command : str):
        """manage_command(command) : Fonction qui permet de gérer les commandes du serveur
        
        Args:
            command (str): Commande à gérer"""
        if command == "STOP-SERVER":
            print("Server stopped")
            client_socket.close()
            os._exit(0)

        elif command == "STOP-CLIENT":
            print("Client stopped")
            client_socket.close()
            os._exit(0)

        else:
            print("Unknown command", command)

    def manage_response(self, response : str) -> list[str]:
        """check_content(response) : Fonction qui permet d'éviter le bug de réception de messages en vérifiant le contenu du message
        
        Args:
            response (str): Message reçu du serveur"""
        responses = re.split(r'(?<=\|)', response)

        var_with_underscore = {"Underscore":[], "Index":[]}
        for i, response in enumerate(responses):
            if "_" in response:
                var_with_underscore["Underscore"].append(response)
                var_with_underscore["Index"].append(i)

        new_rep = []
        for j in range (len(var_with_underscore["Index"])):
            message = ""
            index_start = var_with_underscore["Index"][j]
            try:
                index_fin = var_with_underscore["Index"][j+1]
            except IndexError:
                index_fin = len(responses)-1

            for i in range(index_start, index_fin):
                message += responses[i]
            new_rep.append(message)

        return new_rep

class ConnectThread(QThread):
    """ConnectThread(QThread) : Classe qui gère la connexion au serveur"""
    connection_established = pyqtSignal()

    def __init__(self):
        """__init__() : Constructeur de la classe ConnectThread"""
        super().__init__()

    def get_public_address(self):
        """get_public_address() : Fonction qui permet de récupérer l'adresse IP publique"""
        # try:
        #     public_address = requests.get("http://ip.42.pl/raw").text
        #     print(public_address)
        #     return public_address
        # except:
        #     return "localhost"
        return "localhost"
        
    def run(self):
        """run() : Fonction qui permet de se connecter au serveur"""
        try:
            public_address = self.get_public_address()
            client_socket.connect((public_address, 22222))
            self.connection_established.emit()
            print("Connection established")
        except ConnectionRefusedError:
            print("Connection failed (Server not found)")
            time.sleep(3)
            self.run()
        except socket.gaierror:
            print("Connection failed (DNS resolution failed)")
            time.sleep(3)
            self.run()
            self.connection_established.emit()
            print("Connection established")