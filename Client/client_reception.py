import ssl
import client_utils
from client_utils import *
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

PING_INTERVAL = 5    # seconds between two PING_ (the server answers PONG_)
LOST_AFTER = 15      # nothing received for this long: the connection is lost (e.g. wifi gone)
RECONNECT_FOR = 90   # keep trying to reconnect this long (the server keeps the seat while the game runs)


class ReceptionThread(QThread):
    """Class that manages the reception of messages from the server

    Signals:
        name_correct (bool): Signal to check if the username is correct
        login_refused (str): Signal sent when the server refuses the login (text key)
        sylb_received (str, str, int): Signal to receive the syllabe
        game_signal (str): Signal to receive the game message
        check_game_signal (list): Signal to check the game
        game_created (str, str, int, str): Signal to create the game
        game_deleted (str): Signal to delete the game
        join_signal (str): Signal to join the game
        lobby_state_signal (str): Signal to get the lobby state
        connection_state (bool): False when the connection is lost, True when it is back
        reconnected (str): The server gave the seat back (RECONNECTED message)
        reconnect_failed (): The seat could not be taken back
        ping_signal (float, bool): Round trip of PING_/PONG_ in ms (0 when not connected), and
            always True (the lost connection is shown by connection_state)"""
    name_correct = pyqtSignal(bool)
    login_refused = pyqtSignal(str)  # key of the error text in the language file
    sylb_received = pyqtSignal(str, str, int)
    game_signal = pyqtSignal(str)
    check_game_signal = pyqtSignal(list)
    game_created = pyqtSignal(str, str, int, str)
    game_deleted = pyqtSignal(str)
    join_signal = pyqtSignal(str)
    lobby_state_signal = pyqtSignal(str)
    connection_state = pyqtSignal(bool)
    reconnected = pyqtSignal(str)
    reconnect_failed = pyqtSignal()
    ping_signal = pyqtSignal(float, bool)

    def __init__(self):
        """Constructor of the ReceptionThread class"""
        super().__init__()
        self.session_token: str = ""  # secret key given at login, to reconnect

    def run(self):
        """Receives the messages from the server. If the connection is lost after login, reconnects
        and asks the server for the player's seat back (#10)."""
        while True:
            self.read_messages()
            self.ping_signal.emit(0.0, True)
            if client_utils.quitting or client_utils.session_taken:
                return
            session = load_session()  # None if not logged in yet: just open a new connection
            infos_logger.log_infos("[SOCKET]", "Connection lost, reconnecting")
            self.connection_state.emit(False)
            if not self.reconnect(session):
                self.reconnect_failed.emit()
                return

    def reconnect(self, session: dict | None) -> bool:
        """Opens a new connection and, if the player was logged in, sends RECONNECT_.
        Returns False if the server can't be reached in time.

        Args:
            session (dict | None): The saved session (username, token, avatar), None on the login screen"""
        # On the login screen there is no seat to lose: keep trying until the server is back.
        deadline = time.monotonic() + RECONNECT_FOR if session else float("inf")
        while time.monotonic() < deadline and not client_utils.quitting and client_utils.server_address:
            try:
                client_utils.connect_to_server(client_utils.server_address)
            except OSError as e:
                if isinstance(e, ssl.SSLCertVerificationError):
                    infos_logger.log_infos("[SOCKET]", f"The server's certificate is not valid: {e.verify_message}")
                time.sleep(2)
                continue
            if session:
                send_server(f"RECONNECT_|{session['username']}|{session['token']}|{PROTOCOL_VERSION}")
            else:
                self.connection_state.emit(True)  # nothing to restore: the player can log in
            return True
        return False

    def read_messages(self):
        """Reads and handles messages until the connection is lost."""
        global syllabe
        buffer = MessageBuffer()
        warned_old_server = False
        sock = client_utils.client_socket
        last_received = time.monotonic()
        last_ping = last_received - PING_INTERVAL  # first PING_ at once: the ping shows quickly
        ping_sent: float | None = None  # when the PING_ still waiting for its PONG_ was sent
        while True:
            now = time.monotonic()
            if now - last_ping >= PING_INTERVAL:
                send_server("PING_|")
                last_ping = now
                if ping_sent is None:
                    ping_sent = now
            if now - last_received >= LOST_AFTER:
                infos_logger.log_infos("[SOCKET]", f"Nothing received for {LOST_AFTER} s")
                return
            try:
                data = sock.recv(4096, timeout=1.0)
            except TimeoutError:
                # Data without an end of message for 2 s: the server is an old version
                # (v1.1 servers don't end messages with a newline). Tell the player.
                if buffer.pending and now - last_received >= 2 and not warned_old_server:
                    warned_old_server = True
                    infos_logger.log_infos("[SOCKET]", "The server uses an older message format")
                    self.login_refused.emit("Login__alert_label__version_error")
                continue
            except (OSError, ValueError):  # ValueError: socket already closed
                return
            if not data:
                return
            last_received = time.monotonic()

            for response in buffer.feed(data):
                if response.startswith("MQTT_|"):  # don't write the password in the log
                    infos_logger.log_infos("[RECEIVED]", "MQTT_|(live typing account)")
                elif response != "PONG_|":
                    infos_logger.log_infos("[RECEIVED]", response)
                reply = response.split("|")
                if reply[0] == "PONG_":
                    if ping_sent is not None:
                        self.ping_signal.emit((time.monotonic() - ping_sent) * 1000, True)
                        ping_sent = None

                elif reply[0] == "COMMAND_":
                    self.manage_command(reply[1])

                elif reply[0] == "NAME_ALREADY_USED":
                    self.name_correct.emit(False)

                elif reply[0] == "NAME_CORRECT":
                    self.session_token = reply[1]
                    self.name_correct.emit(True)

                elif reply[0] == "NAME_INVALID":
                    self.login_refused.emit("Login__alert_label__invalid_char_error")

                elif reply[0] == "VERSION_MISMATCH":
                    self.login_refused.emit("Login__alert_label__version_error")

                elif reply[0] == "RECONNECTED":
                    self.connection_state.emit(True)
                    self.reconnected.emit(response)

                elif reply[0] == "RECONNECT_FAILED":
                    clear_session()
                    self.reconnect_failed.emit()

                elif reply[0] == "GAME_MESSAGE":
                    self.game_signal.emit(response)
                
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

                elif reply[0] == "MQTT_":
                    # MQTT_|game|host|port|tls|topic|username|password|: live typing account (#20)
                    set_mqtt_access({"game": reply[1], "host": reply[2], "port": int(reply[3]),
                                     "tls": reply[4] == "True", "topic": reply[5],
                                     "username": reply[6], "password": reply[7]})

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
            client_utils.client_socket.close()
            os._exit(0)

        elif command == "STOP-CLIENT":
            client_utils.client_socket.close()
            os._exit(0)

        elif command == "SESSION-TAKEN":
            # The game was started again and took this seat back: this window must stop.
            client_utils.session_taken = True
            self.reconnect_failed.emit()

        else:
            infos_logger.log_infos("[UNKNOWN]", "Last command was unknown")

class ConnectThread(QThread):
    """Class that manages the connection to the server"""
    connection_established = pyqtSignal()

    def __init__(self):
        """Constructor of the ConnectThread class"""
        super().__init__()

    def connect(self):
        """Connects to the server of socket.csv (encrypted, #19), else to a local one."""
        try:
            address = (confs.socket_server, confs.socket_port)
            client_utils.connect_to_server(address)
        except ConnectionRefusedError:
            address = ("localhost", confs.socket_port)
            client_utils.connect_to_server(address)
        client_utils.server_address = address  # to reconnect later

    def run(self):
        """Connects to the server, trying again every 3 s until it works"""
        while True:
            try:
                self.connect()
            except ConnectionRefusedError:
                infos_logger.log_infos("[SOCKET]", "Connection failed (Server not found)")
            except socket.gaierror:
                infos_logger.log_infos("[SOCKET]", "Failed to resolve server address")
            except ssl.SSLCertVerificationError as e:
                infos_logger.log_infos("[SOCKET]", f"The server's certificate is not valid: {e.verify_message}")
            except OSError as e:  # timeout, server that doesn't speak TLS...
                infos_logger.log_infos("[SOCKET]", f"Connection failed ({type(e).__name__}: {e})")
            else:
                infos_logger.log_infos("[SOCKET]", "Connected")
                self.connection_established.emit()
                infos_logger.log_infos("[SOCKET]", "Connection established")
                return
            time.sleep(3)
