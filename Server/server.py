from server_utils import *
from server_protocol import encode
import socket, threading, os
from server_reception import Reception
from server_logs import ErrorLogger

ErrorLogger.setup_logging()

def __command():
    """__command() : Thread qui gère les commandes du serveur"""
    global arret
    while not arret:
        command = input()
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
        conn, address = server_socket.accept()

        infos_logger.log_infos("[SOCKET]", f"Nouvelle connexion : {str(address)}")

        register_connection(conn)
        reception_thread = Reception(conn)
        with state_lock:
            conn_list.append(conn)
            reception_list["Conn"].append(conn)
            reception_list["Reception"].append(reception_thread)
        reception_thread.start()

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_thread = threading.Thread(target=__command)
    command_thread.start()
    accept()