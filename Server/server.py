from server_utils import *
from server_protocol import Connection, encode
from server_tls import ServerTLS
import socket, threading, os, sys, logging
from server_reception import Reception
from server_logs import ErrorLogger

ErrorLogger.setup_logging()

def __command():
    """__command() : Thread qui gère les commandes du serveur"""
    global arret
    while not arret:
        try:
            command = input()
        except EOFError:  # no keyboard (docker run -d): no commands
            return
        if command == "/stop":
            with state_lock:
                connections = list(conn_list)
            for conn in connections:
                try:  # sent directly: the process exits right after
                    conn.sendall(encode("COMMAND_|STOP-SERVER|"))
                except OSError:
                    pass
            arret = True
            server_socket.close()
            os._exit(0)

def accept():
    """accept() : Fonction principale du programme"""
    global arret
    host = confs.socket_host
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, confs.socket_port))# Port d'écoute du serveur
    server_socket.listen(100)

    while not arret:
        raw_conn, address = server_socket.accept()
        # The TLS handshake happens in the client's own thread (Reception): a slow or silent
        # client can't hold up the others here.
        conn = Connection(raw_conn, tls.context() if tls else None, server_side=True)

        infos_logger.log_infos("[SOCKET]", f"Nouvelle connexion : {str(address)}")

        register_connection(conn)
        reception_thread = Reception(conn)
        with state_lock:
            conn_list.append(conn)
            reception_list["Conn"].append(conn)
            reception_list["Reception"].append(reception_thread)
        reception_thread.start()

def load_tls() -> ServerTLS | None:
    """The certificate for the encrypted connections (#19), None if tls is off in socket.csv."""
    if not confs.socket_tls:
        infos_logger.log_infos("[TLS]", "tls,False in confs/socket.csv: connections are NOT encrypted")
        return None
    try:
        return ServerTLS(confs.socket_certfile, confs.socket_keyfile)
    except (OSError, ValueError) as e:
        message = (f"Can't load the TLS certificate ({e}): {confs.socket_certfile} / {confs.socket_keyfile}. "
                   "Copy it there (see docs/game-server-tls.md) or set tls,False in Server/confs/socket.csv")
        print(message, file=sys.__stderr__)
        logging.error(message)
        sys.exit(1)

if __name__ == '__main__':
    tls = load_tls()  # before the threads start, so a missing certificate stops the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_thread = threading.Thread(target=__command)
    command_thread.start()
    accept()