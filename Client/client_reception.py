from client_utils import *
import log_config

log_config.setup_logging()

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
    sylb_received = pyqtSignal(str, str, int)
    game_signal = pyqtSignal(str)
    check_game_signal = pyqtSignal(list)
    game_created = pyqtSignal(str, str, int, str)
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
                    self.game_signal.emit(game_message)
                
                elif reply[0] == "CHECK_GAME":
                    self.check_game_signal.emit(reply)

                elif reply[0] == "GAME_CREATED":
                    # print("Game created")
                    game_name = reply[1]
                    private_game = reply[2]
                    players_number = int(reply[3])
                    langue = reply[4]
                    self.game_created.emit(game_name, private_game, players_number, langue)

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
                    death_mode_state = int(reply[3])
                    self.sylb_received.emit(syllabe, player, death_mode_state)
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

    def connect(self):
        """get_public_address() : Fonction qui permet de récupérer l'adresse IP publique"""
        try:
            client_socket.connect((confs.socket_server, confs.socket_port))
        except ConnectionRefusedError:
            client_socket.connect(("localhost", confs.socket_port))
        
    def run(self):
        """run() : Fonction qui permet de se connecter au serveur"""
        try:
            self.connect()
            print("Connected")
            self.connection_established.emit()
            print("Connection established")
        except ConnectionRefusedError:
            print("Connection failed (Server not found)")
            time.sleep(3)
            self.run()
        except socket.gaierror:
            print("Failed to resolve server address")
            time.sleep(3)
            self.run()

class PingThread(QThread):
    """PingThread(threading.Thread) : Classe qui gère le ping du serveur"""
    ping_signal = pyqtSignal(float, bool)
    def __init__(self, *args, **kwargs):
        """__init__() : Constructeur de la classe PingThread"""
        super().__init__()
        self.running : bool = True
        self.ping_time : float = 0.0

    def run(self):
        """ping_server() : Function to ping the server"""
        while self.running:
            try:
                out = subprocess.check_output(["ping", "-c 1", "google.fr"])
                output = "".join(map(chr, out))
                match = re.search(r'time=(\d+.\d+) ms', output)
                working_ping = True
                if match:
                    self.ping_time = float(match.group(1))
                else:
                    self.ping_time = 0.0
            except subprocess.CalledProcessError:
                self.ping_time = 0.0
                working_ping = False
                print("Failed to reach missclick.net")
            self.ping_signal.emit(self.ping_time, working_ping)
            time.sleep(3)