from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from client_utils import *
from games.tetris import Tetris, Board
import string, random, re

def handle_username(new_username):
    """handle_username(new_username) : Gère le nouveau nom d'utilisateur"""
    global username
    username = new_username

class AvatarWindow(QMainWindow):
    """Fenêtre de sélection d'avatar"""
    avatar_signal = pyqtSignal(str)
    def __init__(self, parent = None):
        super(AvatarWindow, self).__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.FramelessWindowHint)
        center_window(self)
        self.setStyleSheet(stylesheet_window)
        self.setup_window()

    def setup_window(self):
        """
        setup_window(): Permet l'affichage de la sélection d'avatar
        """
        self.setup_pixmap()

        self.reveil = QPushButton()
        self.reveil.setIcon(QIcon(self.tasse_avatar))
        self.reveil.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.cactus = QPushButton()
        self.cactus.setIcon(QIcon(self.tasse_avatar))
        self.cactus.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.serviette = QPushButton()
        self.serviette.setIcon(QIcon(self.serviette_avatar))
        self.serviette.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.robot_ninja = QPushButton()
        self.robot_ninja.setIcon(QIcon(self.tasse_avatar))
        self.robot_ninja.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.bouteille = QPushButton()
        self.bouteille.setIcon(QIcon(self.tasse_avatar))
        self.bouteille.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.panneau = QPushButton()
        self.panneau.setIcon(QIcon(self.tasse_avatar))
        self.panneau.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.television = QPushButton()
        self.television.setIcon(QIcon(self.tasse_avatar))
        self.television.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.pizza = QPushButton()
        self.pizza.setIcon(QIcon(self.tasse_avatar))
        self.pizza.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.gameboy = QPushButton()
        self.gameboy.setIcon(QIcon(self.tasse_avatar))
        self.gameboy.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.tasse = QPushButton()
        self.tasse.setIcon(QIcon(self.tasse_avatar))
        self.tasse.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        layout = QGridLayout()
        layout.addWidget(self.reveil, 0, 0)
        layout.addWidget(self.cactus, 0, 1)
        layout.addWidget(self.serviette, 0, 2)
        layout.addWidget(self.robot_ninja, 0, 3)
        layout.addWidget(self.bouteille, 0, 4)
        layout.addWidget(self.panneau, 1, 0)
        layout.addWidget(self.television, 1, 1)
        layout.addWidget(self.pizza, 1, 2)
        layout.addWidget(self.gameboy, 1, 3)
        layout.addWidget(self.tasse, 1, 4)

        self.reveil.clicked.connect(lambda: self.set_avatar("reveil-avatar"))
        self.cactus.clicked.connect(lambda: self.set_avatar("cactus-avatar"))
        self.serviette.clicked.connect(lambda: self.set_avatar("serviette-avatar"))
        self.robot_ninja.clicked.connect(lambda: self.set_avatar("robot-ninja-avatar"))
        self.bouteille.clicked.connect(lambda: self.set_avatar("bouteille-avatar"))
        self.panneau.clicked.connect(lambda: self.set_avatar("panneau-avatar"))
        self.television.clicked.connect(lambda: self.set_avatar("television-avatar"))
        self.pizza.clicked.connect(lambda: self.set_avatar("pizza-avatar"))
        self.gameboy.clicked.connect(lambda: self.set_avatar("gameboy-avatar"))
        self.tasse.clicked.connect(lambda: self.set_avatar("tasse-avatar"))
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def setup_pixmap(self):
        self.tasse_avatar = QPixmap(f"{image_path}tasse-avatar.png")
        self.serviette_avatar = QPixmap(f"{image_path}serviette-avatar.png")

    def set_avatar(self, avatar_name):
        """set_avatar() : Définit l'avatar"""
        self.avatar_signal.emit(avatar_name)
        self.close()

class RulesWindow(QMainWindow):
    """Fenêtre des règles du jeu"""
    def __init__(self):
        """__init__() : Initialisation de la fenêtre des règles"""
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setup()
        self.show()

    def setup(self):
        """setup() : Mise en place de la fenêtre des règles"""
        self.setWindowTitle("Règles")
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)
        layout = QGridLayout()

        self.timerulemin_label = QLabel("Temps minimum avant explosion :", self)
        self.timerulemin_label.setObjectName("timerulemin_label")
        self.timerulemin_label.setFixedSize(400, 50) 
        layout.addWidget(self.timerulemin_label, 0, 0)

        self.timerulemin_spinbox= QSpinBox(self)
        self.timerulemin_spinbox.setObjectName("timerulemin_spinbox")
        self.timerulemin_spinbox.setMaximum(20)
        self.timerulemin_spinbox.setMinimum(2)
        self.timerulemin_spinbox.setValue(rules[0])
        self.timerulemin_spinbox.valueChanged.connect(self.check_timerulemax)
        layout.addWidget(self.timerulemin_spinbox, 1, 0)

        self.timerulemax_label = QLabel("Temps maximum après explosion :", self)
        self.timerulemax_label.setFixedSize(400, 50) 
        self.timerulemax_label.setObjectName("timerulemax_label")
        layout.addWidget(self.timerulemax_label, 2, 0)

        self.timerulemax_spinbox = QSpinBox(self)
        self.timerulemax_spinbox.setObjectName("timerulemax_spinbox")
        self.timerulemax_spinbox.setMaximum(30)
        self.timerulemax_spinbox.setMinimum(self.timerulemin_spinbox.value() + 2)
        self.timerulemax_spinbox.setValue(rules[1])
        layout.addWidget(self.timerulemax_spinbox, 3, 0)

        self.lifes_label = QLabel("Nombre de vies :", self)
        self.lifes_label.setObjectName("lifes_label")
        self.lifes_label.setFixedSize(400, 50)
        layout.addWidget(self.lifes_label, 5, 0)

        self.lifes_spinbox = QSpinBox(self)
        self.lifes_spinbox.setObjectName("lifes_spinbox")
        self.lifes_spinbox.setMaximum(12)
        self.lifes_spinbox.setMinimum(1)
        self.lifes_spinbox.setValue(rules[2])
        layout.addWidget(self.lifes_spinbox, 6, 0)

        self.syllabes_label_min = QLabel("Nombre lettres par syllabes syllabes (min):", self)
        self.syllabes_label_min.setObjectName("syllabes_label_min")
        self.syllabes_label_min.setFixedSize(400, 50)
        layout.addWidget(self.syllabes_label_min, 7, 0)

        self.syllabes_spinbox_min = QSpinBox(self)
        self.syllabes_spinbox_min.setObjectName("syllabes_spinbox_min")
        self.syllabes_spinbox_min.setMaximum(5)
        self.syllabes_spinbox_min.setMinimum(1)
        self.syllabes_spinbox_min.setValue(rules[3])
        self.syllabes_spinbox_min.valueChanged.connect(self.check_syllabesmax)
        layout.addWidget(self.syllabes_spinbox_min, 8, 0)

        self.syllabes_label_max = QLabel("Nombre lettres par syllabes syllabes (max):", self)
        self.syllabes_label_max.setObjectName("syllabes_label_max")
        self.syllabes_label_max.setFixedSize(400, 50)
        layout.addWidget(self.syllabes_label_max, 9, 0)

        self.syllabes_spinbox_max = QSpinBox(self)
        self.syllabes_spinbox_max.setObjectName("syllabes_spinbox_max")
        self.syllabes_spinbox_max.setMaximum(5)
        self.syllabes_spinbox_max.setMinimum(1)
        self.syllabes_spinbox_max.setValue(rules[4])
        layout.addWidget(self.syllabes_spinbox_max, 10, 0)

        self.repetition_label = QLabel("Répétition de syllabes :", self)
        self.repetition_label.setObjectName("repetition_label")
        self.repetition_label.setFixedSize(400, 50)
        layout.addWidget(self.repetition_label, 11, 0)

        self.repetition_spinbox = QSpinBox(self)
        self.repetition_spinbox.setObjectName("repetition_spinbox")
        self.repetition_spinbox.setMaximum(8)
        self.repetition_spinbox.setMinimum(0)
        print(rules[5], rules, "regles")
        self.repetition_spinbox.setValue(rules[5])
        layout.addWidget(self.repetition_spinbox, 12, 0)

        self.save_button = QPushButton("Enregistrer", self)
        self.save_button.setObjectName("enregistrer_pushbutton")
        self.save_button.clicked.connect(self.save_rules)

        layout.addWidget(self.save_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def check_syllabesmax(self):
        """check_syllabesmax() : Vérifie que le nombre maximum de syllabes est supérieur au nombre minimum"""
        self.syllabes_spinbox_max.setMinimum(self.syllabes_spinbox_min.value())
        if self.syllabes_spinbox_max.value() < self.syllabes_spinbox_min.value():
            self.syllabes_spinbox_max.setValue(self.syllabes_spinbox_min.value())

    def check_timerulemax(self):
        """check_timerulemax() : Vérifie que le temps maximum est supérieur au temps minimum"""
        self.timerulemax_spinbox.setMinimum(self.timerulemin_spinbox.value() + 2)
        if self.timerulemax_spinbox.value() < self.timerulemin_spinbox.value() + 2:
            self.timerulemax_spinbox.setValue(self.timerulemin_spinbox.value() + 2)

    def save_rules(self):
        """send_rules() : Sauvegarde les règles du jeu dans la liste rules"""
        if self.timerulemax_spinbox.value() < self.timerulemin_spinbox.value() + 2:
            self.timerulemax_spinbox.setValue(self.timerulemin_spinbox.value() + 2)
        rules.clear()
        rules.extend([self.timerulemin_spinbox.value(), self.timerulemax_spinbox.value(), self.lifes_spinbox.value(), self.syllabes_spinbox_min.value(), self.syllabes_spinbox_max.value(), self.repetition_spinbox.value()])
        print(rules)
        self.close()

class GameCreationWindow(QMainWindow):
    """Fenêtre de création de partie"""
    create_game_signal = pyqtSignal(str, str, bool)

    def __init__(self, layout, receiverthread):
        """__init__() : Initialisation de la fenêtre de création de partie"""
        super().__init__()
        self.layout = layout
        self.receiverthread = receiverthread
        self.receiverthread.check_game_signal.connect(self.game_is_unique)
        self.setWindowModality(Qt.ApplicationModal)


    def setup(self):
        """setup() : Mise en place de la fenêtre de création de partie"""
        global username
        self.setWindowTitle("Créer une partie")
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)
        layout = QGridLayout()

        self.game_name_label = QLabel("Nom de la partie :", self)
        self.game_name_label.setObjectName("game_name_label")
        # self.game_name_label.setFixedSize(400, 50)

        default_game_name = f"Partie de {username}"
        self.game_name_lineedit = QLineEdit(self)
        self.game_name_lineedit.setObjectName("game_name_lineedit")
        self.game_name_lineedit.setPlaceholderText(default_game_name)
        self.game_name_lineedit.setMaxLength(20)
        self.game_name_lineedit.setText(default_game_name)
        self.game_name_lineedit.textChanged.connect(lambda: self.restricted_caracters(self.game_name_lineedit))
        self.game_name_lineedit.returnPressed.connect(lambda: self.create_game(default_game_name, self.password_lineedit.text(), self.private_button.text()))

        self.game_name_alert_button = QLabel(self)
        self.game_name_alert_button.setObjectName("game_name_alert_label")
        self.game_name_alert_button.setStyleSheet("color: red;")

        self.private_button = QPushButton("🌐", self)
        self.private_button.setObjectName("private_pushbutton")
        self.private_button.clicked.connect(self.private_game)

        self.password_label = QLabel("Mot de passe :", self)
        self.password_label.setObjectName("password_label")
        # self.password_label.setFixedSize(400, 50)

        characters = string.ascii_letters + string.digits
        random_password = "".join(random.choice(characters) for i in range(12))
        self.password_lineedit = QLineEdit(self)
        self.password_lineedit.setObjectName("password_lineedit")
        self.password_lineedit.setPlaceholderText("Définir un mot de passe")
        self.password_lineedit.setText(random_password)
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        self.password_lineedit.setEnabled(False)
        self.password_lineedit.setMaxLength(20)
        self.password_lineedit.returnPressed.connect(lambda: self.create_game(default_game_name, random_password, self.password_lineedit.text()))
        self.password_lineedit.textChanged.connect(lambda: self.restricted_caracters(self.password_lineedit))

        self.show_password_button = QPushButton("🔑", self)
        self.show_password_button.setObjectName("show_password_pushbutton")
        self.show_password_button.clicked.connect(self.show_password)
        self.show_password_button.setEnabled(False)

        self.create_game_button2 = QPushButton("Créer la partie", self)
        self.create_game_button2.setObjectName("create_game_button2")
        self.create_game_button2.clicked.connect(lambda: self.create_game(default_game_name, random_password, self.password_lineedit.text()))

        layout.addWidget(self.game_name_label, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.game_name_lineedit, 1, 0)
        layout.addWidget(self.private_button, 1, 1)
        layout.addWidget(self.game_name_alert_button, 2, 0)
        layout.addWidget(self.password_label, 3, 0, Qt.AlignHCenter)
        layout.addWidget(self.password_lineedit, 4, 0)
        layout.addWidget(self.show_password_button, 4, 1)
        layout.addWidget(self.create_game_button2, 5, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def restricted_caracters(self, lineedit : QLineEdit):
        """restricted_caracters(lineedit) : Restreint les caractères spéciaux
        
        Args:
            lineedit (QLineEdit): LineEdit"""
        text = lineedit.text()
        lineedit.setText(re.sub(r'[^a-zA-ZÀ-ÿ\s0-9]', '', text))

    def show_password(self):
        """show_password() : Affiche le mot de passe"""
        if self.password_lineedit.echoMode() == QLineEdit.Password:
            self.password_lineedit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_lineedit.setEchoMode(QLineEdit.Password)

    def private_game(self):
        """private_game() : Rend la partie privée"""
        if self.private_button.text() == "🌐":
            self.private_button.setText("🔒")
            self.password_lineedit.setEnabled(True)
            self.show_password_button.setEnabled(True)
        else:
            self.private_button.setText("🌐")
            self.password_lineedit.setEnabled(False)
            self.show_password_button.setEnabled(False)
            self.password_lineedit.setEchoMode(QLineEdit.Password)

    def create_game(self, dafault_game_name, random_password, manual_password):
        """create_game() : Crée une partie
        
        Args:
            dafault_game_name (str): Nom de la partie par défaut
            random_password (str): Mot de passe par défaut
            manual_password (str): Mot de passe manuel"""
        if self.password_lineedit.text() == random_password or self.password_lineedit.text() == "" or self.password_lineedit.text().isspace():
            password = random_password
        else:
            password = manual_password

        if self.game_name_lineedit.text() == dafault_game_name or self.game_name_lineedit.text() == "" or self.game_name_lineedit.text().isspace():
            game_name = dafault_game_name
        else:
            game_name = self.game_name_lineedit.text()

        if self.private_button.text() == "🌐":
            private_game = False
        else:
            private_game = True
        
        self.check_game_name_is_unique(game_name, password, private_game)
        # self.create_game_signal.emit(game_name, password, private_game)
        # self.close()
    
    def check_game_name_is_unique(self, game_name, password, private_game):
        client_socket.send(f"CHECK_GAME_NAME|{game_name}|{password}|{private_game}".encode())

    def game_is_unique(self, reply):
        if reply[1] == "GAME-NAME-CORRECT":
            game_name = reply[2]
            password = reply[3]
            if reply[4] == "True":
                private_game = True
            else:
                private_game = False
            self.create_game_signal.emit(game_name, password, private_game)
            self.close()
        else:
            self.game_name_alert_button.setText("Game name already taken")

class JoinGameWindow(QMainWindow):
    """Fenêtre de création de partie"""
    def __init__(self, game_name, private_game, window):
        """__init__() : Initialisation de la fenêtre de création de partie"""
        super().__init__()
        self.game_name = game_name
        self.private_game = private_game
        self.clientWindow = window

        self.setWindowModality(Qt.ApplicationModal)

        window.in_game_signal.connect(self.in_game)
        
    def setup(self):
        """setup() : Mise en place de la fenêtre de création de partie"""
        self.setWindowTitle("Rejoindre une partie")
        self.resize(200, 200)
        center_window(self)
        self.setStyleSheet(stylesheet_window)
        layout = QGridLayout()

        self.game_name_label = QLabel(f"<b>{self.game_name}<b>", self)
        self.game_name_label.setObjectName("game_name_label")
        self.game_name_label.setFixedSize(400, 50)

        self.password_label = QLabel("Mot de passe :", self)
        self.password_label.setObjectName("password_label")
        self.password_label.setFixedSize(400, 50)

        self.password_widget = QWidget()
        self.password_widget.setFixedHeight(100)
        self.password_layout = QHBoxLayout()

        self.password_lineedit = QLineEdit(self)
        self.password_lineedit.setObjectName("password_lineedit")
        self.password_lineedit.setPlaceholderText("Mot de passe")
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        self.password_lineedit.setMaxLength(30)
        self.password_lineedit.returnPressed.connect(self.join_game)
        self.password_lineedit.textChanged.connect(lambda: self.restricted_caracters(self.password_lineedit))

        self.show_password_button = QPushButton("🔑", self)
        self.show_password_button.setObjectName("show_password_pushbutton")
        self.show_password_button.setFixedWidth(40)
        self.show_password_button.clicked.connect(self.show_password)

        self.join_game_button = QPushButton("Rejoindre la partie", self)
        self.join_game_button.setObjectName("join_game_button")
        self.join_game_button.clicked.connect(self.join_game)

        self.alert_label = QLabel("", self)
        self.alert_label.setFixedSize(400, 50)
        self.alert_label.setStyleSheet("color: red;")

        self.game_name_label.setAlignment(Qt.AlignHCenter)  # Center the text horizontally
        self.alert_label.setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.game_name_label, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.password_label, 1, 0) 
        layout.addWidget(self.password_widget, 2, 0)
        layout.addWidget(self.alert_label, 3, 0, Qt.AlignHCenter)
        layout.addWidget(self.join_game_button, 4, 0, Qt.AlignHCenter)

        self.password_widget.setLayout(self.password_layout)
        self.password_layout.addWidget(self.password_lineedit)
        self.password_layout.addWidget(self.show_password_button)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.clientWindow.correct_mdp.connect(self.incorrect_mdp)

    def join_lobby(self):
        """join_lobby() : Rejoint le lobby (public)"""
        global username
        client_socket.send(f"JOIN_GAME|{self.game_name}|password|{username}".encode())

    def join_game(self):
        """join_game(game_name) : Rejoint une partie privée"""
        global username
        if self.password_lineedit.text() != "" and not self.password_lineedit.text().isspace():
            client_socket.send(f"JOIN_GAME|{self.game_name}|{self.password_lineedit.text()}|{username}".encode())

    def show_password(self):
        """show_password() : Affiche le mot de passe"""
        if self.password_lineedit.echoMode() == QLineEdit.Password:
            self.password_lineedit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_lineedit.setEchoMode(QLineEdit.Password)

    def incorrect_mdp(self, mdp : bool):
        """incorrect_mdp() : Affiche un message d'erreur
        
        Args:
            mdp (bool): Mot de passe incorrect ou non"""
        if mdp:
            self.alert_label.setText("")
            self.close()
        else:
            self.alert_label.setText("Mot de passe incorrect")

    def in_game(self, game_name, players_number):
        """in_game() : Affiche un message d'erreur"""
        self.waiting_room = WaitingRoomWindow(game_name, players_number, self.clientWindow)
        self.waiting_room.show()
        self.waiting_room.setup()
        self.close()

    def restricted_caracters(self, lineedit : QLineEdit):
        """restricted_caracters(lineedit) : Restreint les caractères spéciaux
        
        Args:
            lineedit (QLineEdit): LineEdit"""
        text = lineedit.text()
        lineedit.setText(re.sub(r'[^a-zA-ZÀ-ÿ\s0-9]', '', text))

class WaitingRoomWindow(QMainWindow):
    """Fenêtre d'attente"""
    def __init__(self, game_name, players_number, window):
        """__init__() : Initialisation de la fenêtre d'attente"""
        super().__init__()
        self.game_name = game_name
        self.players_number = players_number
        self.clientWindow = window

        # self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f"Waiting Room")
        self.resize(300, 300)
        center_window(self)
        self.setStyleSheet(stylesheet_window)

        window.waiting_room_close_signal.connect(lambda: self.close())
        window.players_number_signal.connect(self.manage_players_number)

    def setup(self):
        """setup() : Mise en place de la fenêtre d'attente"""
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignHCenter)
        self.game_name_label = QLabel(f"<b>{self.game_name}<b>", self)
        self.game_name_label.setObjectName("game_name_label")
        self.game_name_label.setAlignment(Qt.AlignHCenter)

        self.waiting_label = QLabel("👥", self)
        self.waiting_label.setObjectName("waiting_label")
        self.waiting_label.setAlignment(Qt.AlignHCenter)
        self.waiting_label.setStyleSheet("font-size: 80px;")

        self.number_of_players_label = QLabel(f"{self.players_number}/8", self)
        self.number_of_players_label.setObjectName("number_of_players_label")
        self.number_of_players_label.setAlignment(Qt.AlignHCenter)

        # eventthread = threading.Thread(target=self.__event)
        # eventthread.start()
        self.tetris = Tetris()
        self.tetris.setFixedSize(180, 380)
        
        layout.addWidget(self.game_name_label, 0, 1)
        layout.addWidget(self.waiting_label, 1, 1)
        layout.addWidget(self.number_of_players_label, 2, 1)
        layout.addWidget(self.tetris, 3, 1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def manage_players_number(self, players_number : str):
        """manage_players_number() : Gère le nombre de joueurs dans la partie"""
        self.players_number = players_number
        self.number_of_players_label.setText(players_number)

    def closeEvent(self, event):
        """closeEvent(event) : Fonction appelée lors de la fermeture de la fenêtre
        
        Args:
            event (QCloseEvent): Événement de fermeture"""
        client_socket.send(f"LEAVE_WAITING_ROOM|{self.game_name}|{username}".encode())
        event.accept()
    
    def __event(self):
        while True:
            if Board.Game_is_over:
                self.tetris.close()