from client_utils import *
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

class ReceptionThread(QThread):
    """Class that manages the reception of messages from the server

    Signals:
        name_correct (bool): Signal to check if the username is correct
        sylb_received (str, str, int): Signal to receive the syllabe
        game_signal (str): Signal to receive the game message
        check_game_signal (list): Signal to check the game
        game_created (str, str, int, str): Signal to create the game
        game_deleted (str): Signal to delete the game
        join_signal (str): Signal to join the game
        lobby_state_signal (str): Signal to get the lobby state"""
    name_correct = pyqtSignal(bool)
    sylb_received = pyqtSignal(str, str, int)
    game_signal = pyqtSignal(str)
    check_game_signal = pyqtSignal(list)
    game_created = pyqtSignal(str, str, int, str)
    game_deleted = pyqtSignal(str)
    join_signal = pyqtSignal(str)
    lobby_state_signal = pyqtSignal(str)

    def __init__(self):
        """Constructor of the ReceptionThread class"""
        super().__init__()

    def run(self):
        """Function that manages the reception of messages from the server"""
        global syllabe
        flag = False
        while not flag:
            response = client_socket.recv(1024).decode()
            infos_logger.log_infos("[RECEIVED]", response)
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
                    self.name_correct.emit(False)

                elif reply[0] == "NAME_CORRECT":
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
                    game_name = reply[1]
                    private_game = reply[2]
                    players_number = int(reply[3])
                    langue = reply[4]
                    self.game_created.emit(game_name, private_game, players_number, langue)

                elif reply[0] == "GAME_DELETED":
                    game_name = reply[1]
                    self.game_deleted.emit(f"{game_name}")

                elif reply[0] == "LOBBY_STATE":
                    lobby_state = f"{reply[0]}|{reply[1]}|{reply[2]}|{reply[3]}"
                    self.lobby_state_signal.emit(lobby_state)

                elif reply[0] == "JOIN_STATE":
                    self.join_signal.emit(response)

                elif reply[0] == "SYLLABE_":
                    syllabe = reply[1]
                    player = reply[2]
                    death_mode_state = int(reply[3])
                    self.sylb_received.emit(syllabe, player, death_mode_state)
                    syllabes.append(syllabe)

                else:
                    infos_logger.log_infos("[UNKNOWN]", "Last message was unknown")

    def manage_command(self, command: str):
        """Manages server commands
        
        Args:
            command (str): Command to manage"""
        if command == "STOP-SERVER":
            client_socket.close()
            os._exit(0)

        elif command == "STOP-CLIENT":
            client_socket.close()
            os._exit(0)

        else:
            infos_logger.log_infos("[UNKNOWN]", "Last command was unknown")

    def manage_response(self, response: str) -> list[str]:
        """Manages the response from the server to avoid message reception bugs
        
        Args:
            response (str): Message received from the server
            
        Returns:
            list[str]: List of messages"""
        responses = re.split(r'(?<=\|)', response)

        var_with_underscore = {"Underscore": [], "Index": []}
        for i, response in enumerate(responses):
            if "_" in response:
                var_with_underscore["Underscore"].append(response)
                var_with_underscore["Index"].append(i)

        new_rep = []
        for j in range(len(var_with_underscore["Index"])):
            message = ""
            index_start = var_with_underscore["Index"][j]
            try:
                index_fin = var_with_underscore["Index"][j + 1]
            except IndexError:
                index_fin = len(responses) - 1

            for i in range(index_start, index_fin):
                message += responses[i]
            new_rep.append(message)

        return new_rep

class ConnectThread(QThread):
    """Class that manages the connection to the server"""
    connection_established = pyqtSignal()

    def __init__(self):
        """Constructor of the ConnectThread class"""
        super().__init__()

    def connect(self):
        """Retrieves the public IP address"""
        try:
            client_socket.connect((confs.socket_server, confs.socket_port))
        except ConnectionRefusedError:
            client_socket.connect(("localhost", confs.socket_port))
        
    def run(self):
        """Connects to the server"""
        try:
            self.connect()
            infos_logger.log_infos("[SOCKET]", "Connected")
            self.connection_established.emit()
            infos_logger.log_infos("[SOCKET]", "Connection established")
        except ConnectionRefusedError:
            infos_logger.log_infos("[SOCKET]", "Connection failed (Server not found)")
            time.sleep(3)
            self.run()
        except socket.gaierror:
            infos_logger.log_infos("[SOCKET]", "Failed to resolve server address")
            time.sleep(3)
            self.run()

class CountdownTimer(QThread):
    def __init__(self, duration):
        """Initializes the CountdownTimer class
        
        Args:
            duration (int): Duration of the countdown in seconds"""
        self.duration = duration
        self.remaining_time = duration
        self.running = False
        self.thread = None

    def start(self):
        """Starts the countdown timer"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def _run(self):
        """Runs the countdown timer"""
        start_time = time.time()
        while self.running and self.remaining_time > 0:
            time.sleep(0.1)
            elapsed_time = time.time() - start_time
            self.remaining_time = max(0, self.duration - elapsed_time)
            #print(f"Time left: {self.remaining_time:.1f} seconds", end='\r')
        self.running = False

    def reset(self, duration=None):
        """Resets the countdown timer
        
        Args:
            duration (int, optional): New duration of the countdown in seconds"""
        self.running = False
        if duration is not None:
            self.duration = duration
        self.remaining_time = self.duration

    def adjust(self, new_duration):
        """Adjusts the countdown timer
        
        Args:
            new_duration (int): New duration of the countdown in seconds"""
        self.duration = new_duration
        self.remaining_time = new_duration

    def stop(self):
        """Stops the countdown timer"""
        self.running = False
        if self.thread:
            self.thread.join()

class PingThread(QThread):
    """Class that manages the server ping"""
    ping_signal = pyqtSignal(float, bool)
    
    def __init__(self, *args, **kwargs):
        """Constructor of the PingThread class"""
        super().__init__()
        self.running: bool = True
        self.ping_time: float = 0.0
        self.countdown = CountdownTimer(30)

    def run(self):
        """Pings the server"""
        self.countdown.start()
        while self.running:
            try:
                working_ping = True
                out = subprocess.check_output(["ping", "-c 1", "missclick.net"])
                output = "".join(map(chr, out))
                match = re.search(r'time=(\d+.\d+) ms', output)
                if match:
                    self.countdown.stop()
                    self.countdown.reset()
                    self.countdown.start()
                    self.ping_time = float(match.group(1))
                else:
                    if self.countdown.remaining_time == 0:
                        self.ping_time = 0.0
            except subprocess.CalledProcessError:
                if self.countdown.remaining_time == 0:
                    working_ping = False
                    infos_logger.log_infos("[NETWORK]", "Failed to reach missclick.net")
                self.ping_time = 0.0

            self.ping_signal.emit(self.ping_time, working_ping)
            time.sleep(3)