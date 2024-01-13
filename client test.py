import socket
import threading

def handle_server_response(client_socket):
    while True:
        response = client_socket.recv(1024).decode()
        print("\nServer response:", response)

        if not response:
            break
def main():
    # Création du socket client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Adresse IP et port du serveur
    server_ip = "127.0.0.1"
    server_port = 22222

    # Connexion au serveur
    client_socket.connect((server_ip, server_port))
    print("Connected to server")

    # Création d'un thread pour gérer les réponses du serveur
    response_thread = threading.Thread(target=handle_server_response, args=(client_socket,))
    response_thread.start()

    while True:
        # Lecture de l'entrée utilisateur
        message = input()

        # Envoi du message au serveur
        client_socket.send(message.encode())

        # Condition de sortie
        if message == "exit":
            break

    # Fermeture du socket client
    client_socket.close()

if __name__ == "__main__":
    main()
