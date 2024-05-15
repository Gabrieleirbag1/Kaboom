from PyQt5.QtGui import QMouseEvent
from client_utils import *
from games.tetris import Tetris, Board
from client_objects import ClickButton, ToolMainWindow

def handle_username(new_username):
    """handle_username(new_username) : Gère le nouveau nom d'utilisateur"""
    global username
    username = new_username

class AvatarWindow(ToolMainWindow):
    """Fenêtre de sélection d'avatar"""
    avatar_signal = pyqtSignal(str)
    def __init__(self, parent = None):
        super(AvatarWindow, self).__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        center_window(self)
        self.setup_window()

    def setup_window(self):
        """setup_window(): Permet l'affichage de la sélection d'avatar"""
        self.setup_pixmap()

        self.reveil = ClickButton()
        self.reveil.setObjectName("reveil_button")
        self.reveil.setIcon(QIcon(self.reveil_avatar))
        self.reveil.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.cactus = ClickButton()
        self.cactus.setObjectName("cactus_button")
        self.cactus.setIcon(QIcon(self.cactus_avatar))
        self.cactus.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.serviette = ClickButton()
        self.serviette.setObjectName("serviette_button")
        self.serviette.setIcon(QIcon(self.serviette_avatar))
        self.serviette.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.robot_ninja = ClickButton()
        self.robot_ninja.setObjectName("robot_ninja_button")
        self.robot_ninja.setIcon(QIcon(self.robot_ninja_avatar))
        self.robot_ninja.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.bouteille = ClickButton()
        self.bouteille.setObjectName("bouteille_button")
        self.bouteille.setIcon(QIcon(self.bouteille_avatar))
        self.bouteille.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.panneau = ClickButton()
        self.panneau.setObjectName("panneau_button")
        self.panneau.setIcon(QIcon(self.panneau_avatar))
        self.panneau.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.television = ClickButton()
        self.television.setObjectName("television_button")
        self.television.setIcon(QIcon(self.television_avatar))
        self.television.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.pizza = ClickButton()
        self.pizza.setObjectName("pizza_button")
        self.pizza.setIcon(QIcon(self.pizza_avatar))
        self.pizza.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.gameboy = ClickButton()
        self.gameboy.setObjectName("gameboy_button")
        self.gameboy.setIcon(QIcon(self.gameboy_avatar))
        self.gameboy.setIconSize(QSize(int(screen_width//15),int(screen_width//15)))

        self.tasse = ClickButton()
        self.tasse.setObjectName("tasse_button")
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
        self.reveil_avatar = QPixmap(f"{image_path}reveil-avatar.png")
        self.cactus_avatar = QPixmap(f"{image_path}cactus-avatar.png")
        self.robot_ninja_avatar = QPixmap(f"{image_path}robot-ninja-avatar.png")
        self.bouteille_avatar = QPixmap(f"{image_path}bouteille-avatar.png")
        self.panneau_avatar = QPixmap(f"{image_path}panneau-avatar.png")
        self.television_avatar = QPixmap(f"{image_path}television-avatar.png")
        self.pizza_avatar = QPixmap(f"{image_path}pizza-avatar.png")
        self.gameboy_avatar = QPixmap(f"{image_path}gameboy-avatar.png")
        
    def set_avatar(self, avatar_name):
        """set_avatar() : Définit l'avatar"""
        self.avatar_signal.emit(avatar_name)
        self.close()
    
class RulesWindow(ToolMainWindow):
    """Fenêtre des règles du jeu"""
    def __init__(self):
        """__init__() : Initialisation de la fenêtre des règles"""
        super().__init__()
        self.setWindowTitle("Règles")
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)

        self.setup()
        self.show()

    def setup(self):
        """setup() : Mise en place de la fenêtre des règles"""
        layout = QGridLayout()

        self.timerulemin_label = QLabel("Temps minimum avant explosion :", self)
        self.timerulemin_label.setObjectName("timerulemin_label")
        layout.addWidget(self.timerulemin_label, 0, 0)

        self.timerulemin_spinbox= QSpinBox(self)
        self.timerulemin_spinbox.setObjectName("timerulemin_spinbox")
        self.timerulemin_spinbox.setMaximum(20)
        self.timerulemin_spinbox.setMinimum(2)
        self.timerulemin_spinbox.setValue(rules[0])
        self.timerulemin_spinbox.valueChanged.connect(self.check_timerulemax)
        layout.addWidget(self.timerulemin_spinbox, 1, 0)

        self.timerulemax_label = QLabel("Temps maximum après explosion :", self)
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
        layout.addWidget(self.lifes_label, 5, 0)

        self.lifes_spinbox = QSpinBox(self)
        self.lifes_spinbox.setObjectName("lifes_spinbox")
        self.lifes_spinbox.setMaximum(9)
        self.lifes_spinbox.setMinimum(1)
        self.lifes_spinbox.setValue(rules[2])
        layout.addWidget(self.lifes_spinbox, 6, 0)

        self.syllabes_label_min = QLabel("Nombre lettres par syllabes syllabes (min):", self)
        self.syllabes_label_min.setObjectName("syllabes_label_min")
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
        layout.addWidget(self.syllabes_label_max, 9, 0)

        self.syllabes_spinbox_max = QSpinBox(self)
        self.syllabes_spinbox_max.setObjectName("syllabes_spinbox_max")
        self.syllabes_spinbox_max.setMaximum(5)
        self.syllabes_spinbox_max.setMinimum(1)
        self.syllabes_spinbox_max.setValue(rules[4])
        layout.addWidget(self.syllabes_spinbox_max, 10, 0)

        self.repetition_label = QLabel("Répétition de syllabes :", self)
        self.repetition_label.setObjectName("repetition_label")
        layout.addWidget(self.repetition_label, 11, 0)

        self.repetition_spinbox = QSpinBox(self)
        self.repetition_spinbox.setObjectName("repetition_spinbox")
        self.repetition_spinbox.setMaximum(8)
        self.repetition_spinbox.setMinimum(0)
        print(rules[5], rules, "regles")
        self.repetition_spinbox.setValue(rules[5])
        layout.addWidget(self.repetition_spinbox, 12, 0)

        self.save_button = ClickButton("Enregistrer", self)
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

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return:
            self.save_rules()
        return super().keyPressEvent(event)

class GameCreationWindow(ToolMainWindow):
    """Fenêtre de création de partie"""
    create_game_signal = pyqtSignal(str, str, bool)

    def __init__(self, layout, receiverthread):
        """__init__() : Initialisation de la fenêtre de création de partie"""
        super().__init__()
        self.setWindowTitle("Créer une partie")
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)

        self.layout = layout
        self.receiverthread = receiverthread
        self.receiverthread.check_game_signal.connect(self.game_is_unique)

    def setup(self):
        """setup() : Mise en place de la fenêtre de création de partie"""
        global username
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

        self.private_button = ClickButton("🌐", self)
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

        self.show_password_button = ClickButton("🔑", self)
        self.show_password_button.setObjectName("show_password_pushbutton")
        self.show_password_button.clicked.connect(self.show_password)
        self.show_password_button.setEnabled(False)

        self.create_game_button2 = ClickButton("Créer la partie", self)
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
            button_sound.sound_effects.error_sound.play()


class JoinGameWindow(ToolMainWindow):
    """Fenêtre de création de partie"""
    def __init__(self, game_name, private_game, window):
        """__init__() : Initialisation de la fenêtre de création de partie"""
        super().__init__()
        self.game_name = game_name
        self.private_game = private_game
        self.clientWindow = window

        self.setWindowTitle("Rejoindre une partie")
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)

        window.in_game_signal.connect(self.in_game)
        
    def setup(self):
        """setup() : Mise en place de la fenêtre de création de partie"""
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

        self.show_password_button = ClickButton("🔑", self)
        self.show_password_button.setObjectName("show_password_pushbutton")
        self.show_password_button.setFixedWidth(40)
        self.show_password_button.clicked.connect(self.show_password)

        self.join_game_button = ClickButton("Rejoindre la partie", self)
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
            button_sound.sound_effects.error_sound.play()

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

class WaitingRoomWindow(ToolMainWindow):
    """Fenêtre d'attente"""
    def __init__(self, game_name, players_number, window):
        """__init__() : Initialisation de la fenêtre d'attente"""
        super().__init__()
        self.game_name = game_name
        self.players_number = players_number
        self.clientWindow = window

        self.setWindowTitle("Waiting Room")
        self.resize(int(screen_width // 6), int(screen_height // 2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)

        try:
            window.waiting_room_close_signal.connect(lambda: self.close())
            window.players_number_signal.connect(self.manage_players_number)
        except AttributeError:
            print("Ignorées pour un test")

    def setup(self):
        """setup() : Mise en place de la fenêtre d'attente"""
        layout = QVBoxLayout()
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
        self.tetris.setFixedSize(int(screen_width // 10), int(screen_height // 3))
        
        layout.addWidget(self.game_name_label)
        layout.addWidget(self.waiting_label)
        layout.addWidget(self.number_of_players_label)
        layout.addWidget(self.tetris)

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

class LeaveGameWindow(ToolMainWindow):
    """Fenêtre pour quitter la partie"""
    def __init__(self, clientObject : object, mqtt_sub : object, game_name : str):
        """__init__() : Initialisation de la fenêtre de quitter la partie"""
        super(LeaveGameWindow, self).__init__()
        self.clientObject = clientObject
        self.mqtt_sub = mqtt_sub
        self.game_name = game_name
        
        self.setWindowTitle("Quitter la partie")
        self.setStyleSheet(stylesheet_window)
        center_window(self)
        self.resize(int(screen_width // 6), int(screen_height // 7))

        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre de quitter la partie"""
        self.central_widget = QWidget()
        self.leave_game_layout = QGridLayout(self.central_widget)

        self.ok_icon = QIcon.fromTheme('dialog-ok')
        self.cancel_icon = QIcon.fromTheme('dialog-cancel')

        self.warning_label = QLabel("Êtes vous sûr de vouloir quitter la partie ?")

        self.ok_button = ClickButton('OK')
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setIcon(self.ok_icon)
        self.ok_button.setAutoDefault(True)
        self.ok_button.clicked.connect(self.ok_clicked)
        
        self.cancel_button = ClickButton('Cancel')
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setIcon(self.cancel_icon)
        self.cancel_button.setAutoDefault(True)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        self.leave_game_layout.addWidget(self.warning_label)
        self.leave_game_layout.addWidget(self.ok_button, 1, 1, Qt.AlignRight)
        self.leave_game_layout.addWidget(self.cancel_button, 1, 0, Qt.AlignLeft)

        self.setCentralWidget(self.central_widget)

        self.cancel_button.setFocus()

    def ok_clicked(self):
        self.mqtt_sub.stop_loop()
        self.clientObject.join_state()
        self.clientObject.kill_borders()
        self.clientObject.setup(join=False)
        client_socket.send(f"LEAVE_GAME|{self.game_name}|{username}".encode())
        music.choose_music(1)
        self.close()

    def cancel_clicked(self):
        self.close()

class SettingsWindow(ToolMainWindow):
    """Fenêtre des paramètres"""
    def __init__(self, parent = None):
        """__init__() : Initialisation de la fenêtre des paramètres"""
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Paramètres")
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)
        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre des paramètres"""
        self.setup_tabs()
        self.setup_sound_tab()
        self.setup_graphic_tab()
        self.setup_language_tab()
        self.check_music_muted(self.musique_button)
        self.check_sound_effects_muted(self.ambiance_button, 2)
        self.check_sound_effects_muted(self.boutons_button, 3)

        widget = QWidget()
        reset_button = ClickButton("Réinitialiser les paramètres", self)
        reset_button.setObjectName("reset_button")
        reset_button.clicked.connect(self.reset_settings)

        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabs)
        layout.addWidget(reset_button)
        self.setCentralWidget(widget)

    def setup_tabs(self):
        """setup_tabs() : Mise en place des onglets des paramètres"""
        self.tabs = QTabWidget()
        self.sound_tab = QWidget()
        self.graphic_tab = QWidget()
        self.language_tab = QWidget()
        
        self.tabs.addTab(self.sound_tab, "Son")
        self.tabs.addTab(self.graphic_tab, "Graphique")
        self.tabs.addTab(self.language_tab, "Langue")
    
    def setup_sound_tab(self):
        """setup_sound_tab() : Mise en place de l'onglet du son"""
        # Sound tab
        self.sound_layout = QGridLayout(self.sound_tab)
        self.sound_button = ClickButton("Global", self.sound_tab)
        self.sound_button.setObjectName("sound_button")
        self.sound_slider = QSlider(Qt.Horizontal, self.sound_tab)
        self.sound_slider.setObjectName("sound_slider")
        self.sound_slider.setMinimum(0)
        self.sound_slider.setMaximum(100)
        self.sound_slider.setValue(int(settings.sound_global_data[0][1]))
        # Musique
        self.musique_button = ClickButton("Musique", self)
        self.musique_button.setObjectName("musique_button")
        self.musique_button.clicked.connect(music.mute_music)
        self.musique_button.clicked.connect(lambda: self.check_music_muted(self.musique_button))
        self.musique_slider = QSlider(Qt.Horizontal, self)
        self.musique_slider.setObjectName("musique_slider")
        self.musique_slider.setMinimum(0)
        self.musique_slider.setMaximum(100)
        self.musique_slider.setValue(int(settings.sound_global_data[1][1]))
        self.musique_slider.valueChanged.connect(self.set_music_volume)
        # Ambiance
        self.ambiance_button = ClickButton("Ambiance", self)
        self.ambiance_button.setObjectName("ambiance_button")
        self.ambiance_button.clicked.connect(ambiance_sound.sound_effects.mute_sound_effects)
        self.ambiance_button.clicked.connect(lambda: self.check_sound_effects_muted(self.ambiance_button, 2))
        self.ambiance_slider = QSlider(Qt.Horizontal, self)
        self.ambiance_slider.setObjectName("ambiance_slider")
        self.ambiance_slider.setMinimum(0)
        self.ambiance_slider.setMaximum(100)
        self.ambiance_slider.setValue(int(settings.sound_global_data[2][1]))
        self.ambiance_slider.valueChanged.connect(self.set_ambiance_volume)
        # Boutons
        self.boutons_button = ClickButton("Boutons", self)
        self.boutons_button.setObjectName("boutons_button")
        self.boutons_button.clicked.connect(button_sound.sound_effects.mute_sound_effects)
        self.boutons_button.clicked.connect(lambda: self.check_sound_effects_muted(self.boutons_button, 3))
        self.boutons_slider = QSlider(Qt.Horizontal, self)
        self.boutons_slider.setObjectName("boutons_slider")
        self.boutons_slider.setMinimum(0)
        self.boutons_slider.setMaximum(100)
        self.boutons_slider.setValue(int(settings.sound_global_data[3][1]))
        self.boutons_slider.valueChanged.connect(self.set_sound_effects_volume)
        # Ajout des éléments
        self.sound_layout.addWidget(self.sound_button, 0, 0)
        self.sound_layout.addWidget(self.sound_slider, 0, 1)
        self.sound_layout.addWidget(self.musique_button, 1, 0)
        self.sound_layout.addWidget(self.musique_slider, 1, 1)
        self.sound_layout.addWidget(self.ambiance_button, 2, 0)
        self.sound_layout.addWidget(self.ambiance_slider, 2, 1)
        self.sound_layout.addWidget(self.boutons_button, 3, 0)
        self.sound_layout.addWidget(self.boutons_slider, 3, 1)
        
    def setup_graphic_tab(self):
        """setup_graphic_tab() : Mise en place de l'onglet graphique"""
        # Graphic tab
        self.graphic_layout = QGridLayout(self.graphic_tab)
        self.theme_sombre_checkbox = QCheckBox("Thème sombre", self.graphic_tab)
        self.animations_checkbox = QCheckBox("Activer les animations", self.graphic_tab)
        # Ajout des éléments
        self.graphic_layout.addWidget(self.theme_sombre_checkbox, 0, 0)
        self.graphic_layout.addWidget(self.animations_checkbox, 1, 0)
    
    def setup_language_tab(self):
        """setup_language_tab() : Mise en place de l'onglet de la langue"""
        # Language tab
        self.language_layout = QVBoxLayout(self.language_tab)
        self.language_combobox = QComboBox(self.language_tab)
        self.language_combobox.addItem("Français")
        self.language_combobox.addItem("English")
        self.language_combobox.addItem("Deutsch")
        self.language_combobox.addItem("Español")
        index_language : int = self.language_combobox.findText(settings.accessibility_data[2][1], Qt.MatchFixedString)
        self.language_combobox.setCurrentIndex(index_language)
        self.language_combobox.currentIndexChanged.connect(self.change_language)

        self.language_layout.addWidget(self.language_combobox)

    def change_language(self):
        """change_language() : Change la langue"""
        language = self.language_combobox.currentText()
        settings.accessibility.change_language(language)

    def set_music_volume(self):
        music.change_volume(self.musique_slider.value())
    
    def set_sound_effects_volume(self):
        button_sound.sound_effects.change_volume(self.boutons_slider.value())

    def set_ambiance_volume(self):
        ambiance_sound.sound_effects.change_volume(self.ambiance_slider.value())

    def check_music_muted(self, object : object):
        if music.player.isMuted():
            object.setStyleSheet("background-color: red;")
        else:
            object.setStyleSheet("background-color: green;")

    def check_sound_effects_muted(self, object : object, ligne : int):
        if settings.sound_global_data[ligne][2] == "muted":
            object.setStyleSheet("background-color: red;")
        else:
            object.setStyleSheet("background-color: green;")
    
    def reset_settings(self):
        """reset_settings() : Réinitialise les paramètres"""
        settings.reset_settings()
        music.check_muted()
        self.check_music_muted(self.musique_button)
        button_sound.sound_effects.check_muted()
        self.check_sound_effects_muted(self.boutons_button, 2)
        self.check_sound_effects_muted(self.ambiance_button, 3)
        self.sound_slider.setValue(int(settings.sound_global_data[0][1]))
        self.musique_slider.setValue(int(settings.sound_global_data[1][1]))
        self.ambiance_slider.setValue(int(settings.sound_global_data[2][1]))
        self.boutons_slider.setValue(int(settings.sound_global_data[3][1]))
        self.language_combobox.setCurrentIndex(self.language_combobox.findText(settings.accessibility_data[2][1], Qt.MatchFixedString))

class VictoryWindow(ToolMainWindow):
    """Fenêtre de victoire"""
    def __init__(self, classement : list[list[str]]):
        """__init__() : Initialisation de la fenêtre de victoire"""
        super(VictoryWindow, self).__init__()
        self.classement = classement
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        self.complete_list()
        self.setup()
        self.show()
        ambiance_sound.sound_effects.victory_sound.play()
    
    def complete_list(self):
        """complete_list() : Complète la liste des joueurs"""
        for i in range(8):
            if i >= len(self.classement):
                self.classement.append(["...", None])

    def setup(self):
        """setup() : Mise en place de la fenêtre de victoire"""
        self.setup_widgets()
        self.setup_classement()
        self.setup_layouts()
        self.setCentralWidget(self.central_widget)
        # button_sound.sound_effects.victory_sound.play()
    def setup_widgets(self):
        """setup_widgets() : Mise en place des widgets de la fenêtre de victoire"""
        self.central_widget = QWidget()
        self.central_widget.setObjectName("victory_widget")
        self.victory_layout = QVBoxLayout(self.central_widget)
        self.victory_layout.setAlignment(Qt.AlignCenter)
        
        self.winner_widget = QWidget()
        self.winner_widget.setObjectName("winner_widget")
        self.winner_layout = QVBoxLayout(self.winner_widget)

        self.score_widget = QWidget()
        self.score_widget.setObjectName("score_widget")
        self.score_layout = QHBoxLayout(self.score_widget)

        self.podium_widget = QWidget()
        self.podium_layout = QVBoxLayout(self.podium_widget)

        self.classement_widget = QWidget()
        self.classement_layout = QVBoxLayout(self.classement_widget)

    def setup_classement(self):
        """setup_classement() : Mise en place du classement de la fenêtre de victoire"""
        self.avatar_winner = QPixmap(f"{image_path}{self.classement[0][1]}.png")
        self.avatar_label = QLabel()
        self.avatar_label.setMinimumSize(screen_width//4, screen_width//4)
        self.avatar_label.setObjectName("avatar_label_victory")
        self.avatar_label.setPixmap(self.avatar_winner.scaled(self.avatar_label.size(), Qt.KeepAspectRatio))
        self.avatar_label.setAlignment(Qt.AlignCenter)

        self.winner_label = QLabel(f"{self.classement[0][0]} a gagné !")
        self.winner_label.setObjectName("winner_label")
        self.winner_label.setAlignment(Qt.AlignCenter)

        self.first_label = QLabel(f"🥇 {self.classement[0][0]}")
        self.first_label.setObjectName("podium_label")
        font = QFont()
        font.setPointSize(25)  # Set the font size to 25pt
        self.first_label.setFont(font)  # Set the font for the label
        width = self.first_label.fontMetrics().width('A'*22)  # Calculate the width of 25 characters
        self.first_label.setFixedWidth(width)  # Set the fixed width

        self.second_label = QLabel(f"🥈 {self.classement[1][0]}")
        self.second_label.setObjectName("podium_label")

        self.third_label = QLabel(f"🥉 {self.classement[2][0]}")
        self.third_label.setObjectName("podium_label")

        self.forth_label = QLabel(f"4. {self.classement[3][0]}")
        self.forth_label.setObjectName("classement_label")

        self.fifth_label = QLabel(f"5. {self.classement[4][0]}")
        self.fifth_label.setObjectName("classement_label")

        self.sixth_label = QLabel(f"6. {self.classement[5][0]}")
        self.sixth_label.setObjectName("classement_label")

        self.seventh_label = QLabel(f"7. {self.classement[6][0]}")
        self.seventh_label.setObjectName("classement_label")

        self.eighth_label = QLabel(f"8. {self.classement[7][0]}")
        self.eighth_label.setObjectName("classement_label")

    def setup_layouts(self):
        """setup_layouts() : Mise en place des layouts de la fenêtre de victoire"""
        self.victory_layout.addWidget(self.winner_widget)
        self.victory_layout.addWidget(self.score_widget)

        self.winner_layout.addWidget(self.avatar_label)
        self.winner_layout.addWidget(self.winner_label)
        
        self.score_layout.addWidget(self.podium_widget)
        self.score_layout.addWidget(self.classement_widget)

        self.podium_layout.addWidget(self.first_label)
        self.podium_layout.addWidget(self.second_label)
        self.podium_layout.addWidget(self.third_label)

        self.classement_layout.addWidget(self.forth_label)
        self.classement_layout.addWidget(self.fifth_label)
        self.classement_layout.addWidget(self.sixth_label)
        self.classement_layout.addWidget(self.seventh_label)
        self.classement_layout.addWidget(self.eighth_label)

    def mouseDoubleClickEvent(self, a0: QMouseEvent | None) -> None:
        """mouseDoubleClickEvent(a0) : Double clic de la souris pour fermer la fenêtre"""
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        """keyPressEvent(event) : Appui sur une touche du clavier
        
        Args:
            event (QKeyEvent): Événement du clavier"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Space:
            self.close()
        return super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    waiting_window = WaitingRoomWindow("azertyuiopqsdfghjkl", 0, None)
    waiting_window.show()
    waiting_window.setup()
    # settings = SettingsWindow()
    # settings.sound_layout = QGridLayout()
    # settings.show()
    # rules = RulesWindow()
    # victory = VictoryWindow([["Tom", "reveil-avatar"], 
    #                          ["i", "robot-ninja-avatar"],])
    # victory.show()
    sys.exit(app.exec_())