import sys, socket, threading, time, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from client_reception import ReceptionThread, ConnectThread
from client_utils import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QPushButton, QLabel

class Login(QMainWindow):
    """Fenêtre de login pour le client"""
    login_accepted = pyqtSignal(bool)

    def __init__(self):
        """__init__() : Initialisation de la fenêtre de login"""
        super().__init__()

        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre de login"""
        global receiver_thread
        self.setWindowTitle("Login")
        layout = QGridLayout()

        self.label = QLabel("Username:", self)
        layout.addWidget(self.label, 0, 0)

        self.username_edit = QLineEdit(self)
        layout.addWidget(self.username_edit, 0, 1)
        self.username_edit.returnPressed.connect(self.send_username)

        self.alert_label = QLabel("", self)
        self.alert_label.setStyleSheet("color: red;")
        layout.addWidget(self.alert_label, 1, 0, 1, 2)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.send_username)
        layout.addWidget(self.login_button, 2, 0, 1, 2)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)
        receiver_thread.name_correct.connect(self.show_window)

    def send_username(self):
        """send_username() : Envoie le nom d'utilisateur au serveur"""
        username = self.username_edit.text()
        client_socket.send(f"NEW_USER|{username}".encode())
        self.username_edit.clear()

    def show_window(self, name_correct):
        """show_wiindow() : Affiche la fenêtre principale si le nom d'utilisateur est correct
        
        Args:
            name_correct (bool): True si le nom d'utilisateur est correct, False sinon"""
        if name_correct:
            self.close()
            window.show()
        else:
            self.alert_label.setText("Username already used")

class ClientWindow(QMainWindow):
    """Fenêtre principale du client"""
    def __init__(self):
        """__init__() : Initialisation de la fenêtre principale"""
        super().__init__()

        self.setup()
    
    def setup(self):
        """setup() : Mise en place de la fenêtre principale"""
        self.setWindowTitle("Client")
        self.resize(500, 500)
        self.setStyleSheet(stylesheet)
        layout = QGridLayout()

        self.create_game = QPushButton("Créer une partie", self)
        self.create_game.setObjectName("create_game_pushbutton")
        layout.addWidget(self.create_game, 1, 0, Qt.AlignHCenter)

        self.join_game = QPushButton("Rejoindre une partie", self)
        self.join_game.setObjectName("join_game_pushbutton")
        layout.addWidget(self.join_game, 3, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setup_threads()
        self.create_game.clicked.connect(lambda: self.setup_game(layout))
        self.join_game.clicked.connect(lambda: self.setup_join_game(layout))


    def setup_game(self, layout):
        """setup_game(layout) : Mise en place de la fenêtre de jeu
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale"""
        layout.removeWidget(self.create_game)
        layout.removeWidget(self.join_game)

        self.player1_label = QLabel("Joueur 1", self)
        self.player2_label = QLabel("Joueur 2", self)
        self.player3_label = QLabel("Joueur 3", self)
        self.player4_label = QLabel("Joueur 4", self)
        self.player5_label = QLabel("Joueur 5", self)
        self.player6_label = QLabel("Joueur 6", self)
        self.player7_label = QLabel("Joueur 7", self)
        self.player8_label = QLabel("Joueur 8", self)

        sub_layout = QGridLayout()


        self.syllable_label = QLabel("", self)
        sub_layout.addWidget(self.syllable_label, 0, 0, Qt.AlignHCenter)

        self.text_label = QLabel("", self)
        sub_layout.addWidget(self.text_label, 1, 0, Qt.AlignHCenter)

        self.text_line_edit = QLineEdit(self)
        sub_layout.addWidget(self.text_line_edit, 2, 0, Qt.AlignHCenter)

        self.text_widget = QWidget()
        self.text_widget.setObjectName("text_widget")
        self.text_widget.setLayout(sub_layout)

        layout.addWidget(self.player1_label, 0, 0, Qt.AlignLeft)
        layout.addWidget(self.player2_label, 0, 1, Qt.AlignHCenter)
        layout.addWidget(self.player3_label, 0, 2, Qt.AlignRight)
        layout.addWidget(self.player4_label, 1, 0, Qt.AlignLeft)
        layout.addWidget(self.player5_label, 1, 2, Qt.AlignRight)
        layout.addWidget(self.player6_label, 2, 0, Qt.AlignLeft)
        layout.addWidget(self.player7_label, 2, 1, Qt.AlignCenter)
        layout.addWidget(self.player8_label, 2, 2, Qt.AlignRight)

        layout.addWidget(self.text_widget, 1, 1, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def setup_join_game(self, layout):
        layout.removeWidget(self.create_game)
        layout.removeWidget(self.join_game)

        layout = QVBoxLayout()

        # Création du QListWidget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Création des boutons
        button_layout = QVBoxLayout()
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_item)
        button_layout.addWidget(add_button)

        self.button_widget = QWidget()
        self.button_widget.setLayout(button_layout)
        layout.addWidget(self.button_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_item(self):
        """Ajoute un élément au QListWidget"""
        self.join_game_push_button = QPushButton(f"Partie n°{self.list_widget.count() + 1}")
        item = QListWidgetItem(self.list_widget)
        item_widget = QWidget()
        item_layout = QGridLayout(item_widget)
        item_layout.addWidget(self.join_game_push_button)
        item_widget.setLayout(item_layout)
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)

    def setup_threads(self):
        """setup_threads() : Mise en place des threads de réception et de connexion"""
        global receiver_thread
        self.connect_thread = ConnectThread()
        self.connect_thread.start()
        self.connect_thread.connection_established.connect(self.connect_to_server)

        receiver_thread = ReceptionThread()

    def connect_to_server(self):
        """connect_to_server() : Se connecte au serveur"""
        global receiver_thread
        receiver_thread.message_received.connect(self.display_message)
        receiver_thread.start()

    def send_message(self):
        """send_message() : Envoie un message au serveur"""
        message = message
        client_socket.send(message.encode())
        self.text_edit.clear()

    def display_message(self, message):
        """display_message(message) : affiche le message dans la fenêtre principale
        
        Args:
            message (str): message à afficher"""
        self.text_edit.append(message)


if __name__ == "__main__":
    """__maiLance l'application"""
    app = QApplication(sys.argv)
    window = ClientWindow()
    login = Login()
    login.show()
    sys.exit(app.exec_())
