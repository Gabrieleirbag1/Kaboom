import sys, socket, threading, time, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from client_reception import ReceptionThread, ConnectThread
from client_utils import *

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
        global username
        username = self.username_edit.text()
        try:
            client_socket.send(f"NEW_USER|{username}".encode())
            self.username_edit.clear()
        except BrokenPipeError:
            self.alert_label.setText("Connection failed")

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
    def __init__(self, start : bool):
        """__init__() : Initialisation de la fenêtre principale"""
        super().__init__()
        self.start = start
        self.setup(start)
    
    def setup(self, start):
        """setup() : Mise en place de la fenêtre principale"""
        global receiver_thread

        self.setWindowTitle("Client")
        self.resize(500, 500)
        self.setStyleSheet(stylesheet)
        layout = QGridLayout()

        self.create_game_button = QPushButton("Créer une partie", self)
        self.create_game_button.setObjectName("create_game_pushbutton")
        layout.addWidget(self.create_game_button, 1, 0, Qt.AlignHCenter)

        self.join_game = QPushButton("Rejoindre une partie", self)
        self.join_game.setObjectName("join_game_pushbutton")
        layout.addWidget(self.join_game, 3, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.create_game_button.clicked.connect(lambda: self.setup_game(layout))
        self.join_game.clicked.connect(lambda: self.setup_join_game(layout))

        if start:
            self.setup_threads()

        receiver_thread.sylb_received.connect(self.display_sylb)



    def setup_game(self, layout):
        """setup_game(layout) : Mise en place de la fenêtre de jeu
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale"""
        
        self.create_game()
      
        layout.removeWidget(self.create_game_button)
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
        self.text_line_edit.returnPressed.connect(self.send_message)

        self.text_widget = QWidget()
        self.text_widget.setObjectName("text_widget")
        self.text_widget.setLayout(sub_layout)

        layout.addWidget(self.player1_label, 1, 0, Qt.AlignLeft)
        layout.addWidget(self.player2_label, 1, 1, Qt.AlignHCenter)
        layout.addWidget(self.player3_label, 1, 2, Qt.AlignRight)
        layout.addWidget(self.player4_label, 2, 0, Qt.AlignLeft)
        layout.addWidget(self.player5_label, 2, 2, Qt.AlignRight)
        layout.addWidget(self.player6_label, 3, 0, Qt.AlignLeft)
        layout.addWidget(self.player7_label, 3, 1, Qt.AlignCenter)
        layout.addWidget(self.player8_label, 3, 2, Qt.AlignRight)

        layout.addWidget(self.text_widget, 2, 1, Qt.AlignHCenter)

        self.home_button = QPushButton("Home", self)
        self.home_button.setObjectName("home_pushbutton")
        self.home_button.clicked.connect(lambda: self.setup(start=False))

        self.rules_button = QPushButton("Règles", self)
        self.rules_button.setObjectName("rules_pushbutton")
        self.rules_button.clicked.connect(self.display_rules)

        self.ready_button = QPushButton("Ready", self)
        self.ready_button.setObjectName("ready_pushbutton")
        self.ready_button.setEnabled(True)
        self.ready_button.clicked.connect(self.ready)

        self.start_button = QPushButton("Start", self)
        self.start_button.setObjectName("start_pushbutton")
        self.start_button.setEnabled(True)
        self.start_button.clicked.connect(self.start_game)

        layout.addWidget(self.home_button, 0, 0, Qt.AlignLeft)
        layout.addWidget(self.rules_button, 4, 0, Qt.AlignLeft)
        layout.addWidget(self.ready_button, 4, 1)
        layout.addWidget(self.start_button, 4, 2, Qt.AlignRight)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_game(self):
        """create_game() : Crée une partie"""
        global username
        message = f"CREATE_GAME|{username}"
        client_socket.send(message.encode())

    def start_game(self):
        """start_game() : Lance la partie"""
        global username
        self.start_button.setEnabled(False)
        try:
            message = f"START_GAME|{username}|{rules[0]}|{rules[1]}|{rules[2]}"
        except IndexError:
            rules.extend([5, 7, 3])
            message = f"START_GAME|{username}|{rules[0]}|{rules[1]}|{rules[2]}"
        
        client_socket.send(message.encode())

    def ready(self):
        """ready() : Indique au serveur que le joueur est prêt"""
        global username
        self.ready_button.setEnabled(False)
        message = f"READY_TO_PLAY|{username}"
        client_socket.send(message.encode())

    def setup_join_game(self, layout):
        """setup_join_game(layout) : Mise en place de la fenêtre de jeu
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale"""
        layout.removeWidget(self.create_game_button)
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

    def display_sylb(self, sylb):
        """display_sylb(sylb) : Affiche la syllabe dans la fenêtre principale
        
        Args:
            sylb (str): Syllabe à afficher"""
        self.syllable_label.setText(sylb)

    def add_item(self):
        """Ajoute un élément au QListWidget"""
        self.join_game_pushbutton = QPushButton(f"Partie n°{self.list_widget.count() + 1}")
        item = QListWidgetItem(self.list_widget)
        item_widget = QWidget()
        item_layout = QGridLayout(item_widget)
        item_layout.addWidget(self.join_game_pushbutton)
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
        global username
        syllabe = syllabes[-1]
        message = f"NEW_SYLLABE|{username}|{self.text_line_edit.text()}|{syllabe}"
        client_socket.send(message.encode())
        self.text_line_edit.clear()

    def display_message(self, message):
        """display_message(message) : affiche le message dans la fenêtre principale
        
        Args:
            message (str): message à afficher"""
        self.text_label.setText(message)

    def display_rules(self):
        """display_rules() : Affiche les règles du jeu"""
        self.rules_window = RulesWindow()
        self.rules_window.show()

class RulesWindow(QMainWindow):
    """Fenêtre des règles du jeu"""
    def __init__(self):
        """__init__() : Initialisation de la fenêtre des règles"""
        super().__init__()
        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre des règles"""
        self.setWindowTitle("Règles")
        self.resize(200, 200)
        self.setStyleSheet(stylesheet)
        layout = QGridLayout()

        self.timerulemin_label = QLabel("Temps minimum avant explosion :", self)
        self.timerulemin_label.setObjectName("timerulemin_label")
        self.timerulemin_label.setFixedSize(300, 20) 
        layout.addWidget(self.timerulemin_label, 0, 0)

        self.timerulemin_spinbox= QSpinBox(self)
        self.timerulemin_spinbox.setObjectName("timerulemin_spinbox")
        self.timerulemin_spinbox.setMaximum(20)
        self.timerulemin_spinbox.setMinimum(3)
        layout.addWidget(self.timerulemin_spinbox, 1, 0)

        self.timerulemax_label = QLabel("Temps maximum après explosion :", self)
        self.timerulemax_label.setFixedSize(300, 20) 
        self.timerulemax_label.setObjectName("timerulemax_label")
        layout.addWidget(self.timerulemax_label, 2, 0)

        self.timerulemax_spinbox = QSpinBox(self)
        self.timerulemax_spinbox.setObjectName("timerulemax_spinbox")
        self.timerulemax_spinbox.setMaximum(30)
        self.timerulemax_spinbox.setMinimum(5)
        layout.addWidget(self.timerulemax_spinbox, 3, 0)

        self.lifes_label = QLabel("Nombre de vies :", self)
        self.lifes_label.setObjectName("lifes_label")
        self.lifes_label.setFixedSize(300, 20)
        layout.addWidget(self.lifes_label, 5, 0)

        self.lifes_spinbox = QSpinBox(self)
        self.lifes_spinbox.setObjectName("lifes_spinbox")
        self.lifes_spinbox.setMaximum(12)
        self.lifes_spinbox.setMinimum(1)
        layout.addWidget(self.lifes_spinbox, 6, 0)

        self.home_button = QPushButton("Enregistrer", self)
        self.home_button.setObjectName("enregistrer_pushbutton")
        self.home_button.clicked.connect(self.save_rules)

        layout.addWidget(self.home_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def save_rules(self):
        """send_rules() : Envoie les règles au serveur"""
        rules.extend([self.timerulemin_spinbox.value(), self.timerulemax_spinbox.value(), self.lifes_spinbox.value()])
        print(rules)
        self.close()

if __name__ == "__main__":
    """__main__() : Lance l'application"""
    app = QApplication(sys.argv)
    window = ClientWindow(start = True)
    login = Login()
    login.show()
    sys.exit(app.exec_())
