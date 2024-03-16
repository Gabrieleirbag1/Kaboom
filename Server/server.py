import socket, threading, subprocess, os
from server_utils import *
from server_reception import Reception

def __command():
    """__command() : Thread qui gère les commandes du serveur"""
    global arret
    while not arret:
        command = input()
        if command == "/stop":
            for conn in conn_list:
                envoi(conn, "COMMAND|STOP_SERVER")
            arret = True
            server_socket.close()
            os._exit(0)

def accept():
    """accept() : Fonction principale du programme"""
    global arret
    host = '0.0.0.0'
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, 22222))# 22222 est le port d'écoute du serveur
    server_socket.listen(100)

    while not arret:
        conn, address = server_socket.accept()

        print("Connected")

        reception_thread = Reception(conn)
        reception_thread.start()

        conn_list.append(conn)
        reception_list["Conn"].append(conn)
        reception_list["Reception"].append(reception_thread)

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_thread = threading.Thread(target=__command)
    command_thread.start()
    accept()