import socket, threading, time
from server_utils import *
from server_reception import Reception

def envoi(conn):
    """envoi() : Fonction qui permet d'envoyer des messages au client
    Args:
        conn (socket): Socket de connexion du client"""
    flag = False
    global arret
    while not flag:
        reply = input(">")
        conn.send(reply.encode())

        if reply == "arret" or reply == "bye":
            flag = True
            if reply == "arret":
                arret = True

    print("Arret de la Thread envoi")


def accept():
    """accept() : Fonction principale du programme"""
    host = '0.0.0.0'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    server_socket.close()

if __name__ == '__main__':
    accept()
