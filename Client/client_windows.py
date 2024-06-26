from PyQt5.QtGui import QMouseEvent
from client_utils import *
from external.tetris import Tetris, Board
from external.rating_widget import RatingWidget
from client_objects import ClickButton, ToolMainWindow, DialogMainWindow, HoverPixmapButton
from client_styles import StyledButton

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
        self.setWindowTitle(langue.langue_data["RulesWindow__title"])
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        self.setStyleSheet(stylesheet_window)

        self.lifes_value = rules[2]
        self.setup()
        self.show()
        center_window(self)

    def setup(self):
        """setup() : Mise en place de la fenêtre des règles"""
        layout = QGridLayout()
        layout.setSpacing(20)

        #TIME RULES
        self.timerules_widget = QWidget()
        self.timerules_layout = QVBoxLayout(self.timerules_widget)

        self.timerulesmin_widget = QWidget()
        self.timerulesmin_layout = QHBoxLayout(self.timerulesmin_widget)

        self.timerulesmax_widget = QWidget()
        self.timerulesmax_layout = QHBoxLayout(self.timerulesmax_widget)

        self.timeruleslabel = QLabel(langue.langue_data["RulesWindow__timeruleslabel__text"], self)
        self.timeruleslabel.setObjectName("timeruleslabel")
        self.timeruleslabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.timerulemin_spinbox= QSpinBox(self)
        self.timerulemin_spinbox.setObjectName("timerulemin_spinbox")
        self.timerulemin_spinbox.setMaximum(20)
        self.timerulemin_spinbox.setMinimum(2)
        self.timerulemin_spinbox.setValue(rules[0])
        self.timerulemin_spinbox.setFixedWidth(self.timerulemin_spinbox.sizeHint().width() * 2)
        self.timerulemin_spinbox.valueChanged.connect(self.check_timerulemax)

        self.timerulemin_label = QLabel(langue.langue_data["RulesWindow__timeruleminlabel__text"], self)
        self.timerulemin_label.setObjectName("timerulemax_label")

        self.timerulemax_spinbox = QSpinBox(self)
        self.timerulemax_spinbox.setObjectName("timerulemax_spinbox")
        self.timerulemax_spinbox.setMaximum(30)
        self.timerulemax_spinbox.setMinimum(self.timerulemin_spinbox.value() + 2)
        self.timerulemax_spinbox.setValue(rules[1])        
        self.timerulemax_spinbox.setFixedWidth(self.timerulemax_spinbox.sizeHint().width() * 2)
        
        self.timerulemax_label = QLabel(langue.langue_data["RulesWindow__timerulmaxlabel__text"], self)
        self.timerulemax_label.setObjectName("timerulemax_label")

        #SYLLABES RULES
        self.syllabes_widget = QWidget()
        self.syllabes_layout = QVBoxLayout(self.syllabes_widget)

        self.syllabes_sub_widget = QWidget()
        self.syllabes_sub_layout = QHBoxLayout(self.syllabes_sub_widget)

        self.syllabes_label = QLabel(langue.langue_data["RulesWindow__syllabes_label__text"], self)
        self.syllabes_label.setObjectName("syllabes_label")
        self.syllabes_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.syllabes_spinbox_min = QSpinBox(self)
        self.syllabes_spinbox_min.setObjectName("syllabes_spinbox_min")
        self.syllabes_spinbox_min.setMaximum(5)
        self.syllabes_spinbox_min.setMinimum(1)
        self.syllabes_spinbox_min.setValue(rules[3])
        self.syllabes_spinbox_min.setFixedWidth(self.syllabes_spinbox_min.sizeHint().width() * 2)
        self.syllabes_spinbox_min.valueChanged.connect(self.check_syllabesmax)

        self.syllabes_label_min = QLabel(langue.langue_data["RulesWindow__syllabes_label_min__text"], self)
        self.syllabes_label_min.setObjectName("syllabes_label_min")

        self.syllabes_spinbox_max = QSpinBox(self)
        self.syllabes_spinbox_max.setObjectName("syllabes_spinbox_max")
        self.syllabes_spinbox_max.setMaximum(5)
        self.syllabes_spinbox_max.setMinimum(1)
        self.syllabes_spinbox_max.setValue(rules[4])   
        self.syllabes_spinbox_max.setFixedWidth(self.syllabes_spinbox_max.sizeHint().width() * 2)
        
        self.syllabes_label_max = QLabel(langue.langue_data["RulesWindow__syllabes_label_max__text"], self)
        self.syllabes_label_max.setObjectName("syllabes_label_max")

        #REPETITION RULES
        self.repetition_label = QLabel(langue.langue_data["RulesWindow__repetition_label__text"], self)
        self.repetition_label.setObjectName("repetition_label")

        self.repetition_spinbox = QSpinBox(self)
        self.repetition_spinbox.setObjectName("repetition_spinbox")
        self.repetition_spinbox.setMaximum(8)
        self.repetition_spinbox.setMinimum(0)
        self.repetition_spinbox.setValue(rules[5])
        self.repetition_spinbox.setFixedWidth(self.repetition_spinbox.sizeHint().width() * 2)

        #DEATH MODE RULES
        self.death_mode_widget = QWidget()
        self.death_mode_layout = QVBoxLayout(self.death_mode_widget)

        self.death_mode_sub_widget = QWidget()
        self.death_mode_sub_layout = QHBoxLayout(self.death_mode_sub_widget)

        self.death_mode_label = QLabel(langue.langue_data["RulesWindow__death_mode_label__text"], self)
        self.death_mode_label.setObjectName("death_mode_label")
        self.death_mode_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.skull_pixmap = QPixmap(f"{image_path}skull.png")
        self.skull_pixmap_hover = QPixmap(f"{image_path}skull-hover.png")
        self.skull_red_pixmap = QPixmap(f"{image_path}skull-red.png")
        self.skull_red_pixmap_hover = QPixmap(f"{image_path}skull-red-hover.png")
        self.skull_green_pixmap = QPixmap(f"{image_path}skull-green.png")
        self.skull_green_pixmap_hover = QPixmap(f"{image_path}skull-green-hover.png")

        self.death_mode_pixmap_button = HoverPixmapButton(self.skull_pixmap, self.skull_pixmap_hover)
        self.death_mode_pixmap_button.setObjectName("other_buttons")
        self.death_mode_pixmap_button.setIcon(QIcon(self.skull_pixmap))
        self.death_mode_pixmap_button.setIconSize(QSize(int(screen_width//14), int(screen_width//14)))
        self.death_mode_pixmap_button.clicked.connect(self.set_death_mode)
        self.death_mode_state = rules[6]
        
        self.death_mode_explained_label = QLabel(langue.langue_data["RulesWindow__death_mode_explained_label__text"], self)
        self.death_mode_explained_label.setObjectName("death_mode_explained_label")
        self.death_mode_explained_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #LIFES RULES
        self.lifes_widget = QWidget()
        self.lifes_layout = QVBoxLayout(self.lifes_widget)
        
        self.lifes_label = QLabel(langue.langue_data["RulesWindow__lifes_label__text"], self)
        self.lifes_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.lifes_rating_widget = RatingWidget(rule_value=rules[2])
        self.lifes_rating_widget.value_updated.connect(self.set_life_value)

        #SAVE BUTTON
        self.save_button = StyledButton(langue.langue_data["RulesWindow__save_button__text"], self)
        self.save_button.setObjectName("enregistrer_pushbutton")
        self.save_button.clicked.connect(self.save_rules)

        #LAYOUT
        self.timerulesmin_layout.addWidget(self.timerulemin_spinbox)
        self.timerulesmin_layout.addWidget(self.timerulemin_label)

        self.timerulesmax_layout.addWidget(self.timerulemax_spinbox)
        self.timerulesmax_layout.addWidget(self.timerulemax_label)

        self.timerules_layout.addWidget(self.timeruleslabel, Qt.AlignmentFlag.AlignHCenter)
        self.timerules_layout.addWidget(self.timerulesmin_widget)
        self.timerules_layout.addWidget(self.timerulesmax_widget)

        self.syllabes_layout.addWidget(self.syllabes_label, Qt.AlignmentFlag.AlignHCenter)
        self.syllabes_layout.addWidget(self.syllabes_sub_widget)

        self.syllabes_sub_layout.addWidget(self.syllabes_spinbox_min)
        self.syllabes_sub_layout.addWidget(self.syllabes_label_min)
        self.syllabes_sub_layout.addWidget(self.syllabes_spinbox_max)
        self.syllabes_sub_layout.addWidget(self.syllabes_label_max)
        self.syllabes_sub_layout.addWidget(self.repetition_spinbox)
        self.syllabes_sub_layout.addWidget(self.repetition_label)

        self.lifes_layout.addWidget(self.lifes_label, Qt.AlignmentFlag.AlignHCenter)
        self.lifes_layout.addWidget(self.lifes_rating_widget, Qt.AlignmentFlag.AlignHCenter)

        self.death_mode_sub_layout.addWidget(self.death_mode_pixmap_button)
        self.death_mode_sub_layout.addWidget(self.death_mode_explained_label)
        self.death_mode_layout.addWidget(self.death_mode_label, Qt.AlignmentFlag.AlignHCenter)
        self.death_mode_layout.addWidget(self.death_mode_sub_widget, Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self.timerules_widget)
        layout.addWidget(self.syllabes_widget)
        layout.addWidget(self.lifes_widget)
        layout.addWidget(self.death_mode_widget)
        layout.addWidget(self.save_button, 4, 0, Qt.AlignmentFlag.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def set_life_value(self, value : int):
        """set_life_value(value) : Définit la valeur de la vie"""
        self.lifes_value = value

    def set_death_mode(self):
        """set_death_mode() : Définit le mode de mort"""
        self.death_mode_state = (self.death_mode_state + 1) % 3
        if self.death_mode_state == 2:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_red_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_red_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_red_pixmap_hover
        elif self.death_mode_state == 1:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_green_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_green_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_green_pixmap_hover
        else:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_pixmap_hover

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
        rules.extend([self.timerulemin_spinbox.value(), 
                      self.timerulemax_spinbox.value(), 
                      self.lifes_value, 
                      self.syllabes_spinbox_min.value(), 
                      self.syllabes_spinbox_max.value(), 
                      self.repetition_spinbox.value(), 
                      self.death_mode_state])
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
        self.setWindowTitle(langue.langue_data["GameCreationWindow__text"])
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(stylesheet_window)

        self.old_layout = layout
        self.receiverthread = receiverthread
        self.receiverthread.check_game_signal.connect(self.game_is_unique)

    def setup(self):
        """setup() : Mise en place de la fenêtre de création de partie"""
        global username
        layout = QGridLayout()

        self.game_name_label = QLabel(langue.langue_data["GameCreationWindow__game_name_label__text"], self)
        self.game_name_label.setObjectName("game_name_label")
        # self.game_name_label.setFixedSize(400, 50)

        default_game_name = f"{langue.langue_data["GameCreationWindow__game_name_label__default_text"]}{username}"
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

        self.password_label = QLabel(langue.langue_data["GameCreationWindow__password_label__text"], self)
        self.password_label.setObjectName("password_label")
        # self.password_label.setFixedSize(400, 50)

        characters = string.ascii_letters + string.digits
        random_password = "".join(random.choice(characters) for i in range(12))
        self.password_lineedit = QLineEdit(self)
        self.password_lineedit.setObjectName("password_lineedit")
        self.password_lineedit.setPlaceholderText(langue.langue_data["GameCreationWindow__password_lineedit__placeholder"])
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

        self.select_langue_combobox = QComboBox(self)
        self.select_langue_combobox.setObjectName("select_langue_button")
        self.select_langue_combobox.addItems(["Français", "English"])
        index_language : int = self.select_langue_combobox.findText(settings.accessibility_data[2][1], Qt.MatchFixedString)
        self.select_langue_combobox.setCurrentIndex(index_language)

        self.create_game_button2 = StyledButton(langue.langue_data["GameCreationWindow__create_game_button2__text"], self)
        self.create_game_button2.setObjectName("create_game_button2")
        self.create_game_button2.clicked.connect(lambda: self.create_game(default_game_name, random_password, self.password_lineedit.text()))

        layout.addWidget(self.game_name_label, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.game_name_lineedit, 1, 0)
        layout.addWidget(self.private_button, 1, 1)
        layout.addWidget(self.game_name_alert_button, 2, 0)
        layout.addWidget(self.password_label, 3, 0, Qt.AlignHCenter)
        layout.addWidget(self.password_lineedit, 4, 0)
        layout.addWidget(self.show_password_button, 4, 1)
        layout.addWidget(self.select_langue_combobox, 5, 0, Qt.AlignHCenter)
        layout.addWidget(self.create_game_button2, 6, 0, Qt.AlignHCenter)

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
        client_socket.send(f"CHECK_GAME_NAME|{game_name}|{password}|{private_game}|".encode())

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
            self.game_name_alert_button.setText(langue.langue_data["GameCreationWindow__game_name_alert_button__already_taken_error"])
            button_sound.sound_effects.error_sound.play()


class JoinGameWindow(ToolMainWindow):
    """Fenêtre de création de partie"""
    def __init__(self, game_name, private_game, window):
        """__init__() : Initialisation de la fenêtre de création de partie"""
        super().__init__()
        self.game_name = game_name
        self.private_game = private_game
        self.clientWindow = window

        self.setWindowTitle(langue.langue_data["JoinGameWindow__text"])
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

        self.password_label = QLabel(langue.langue_data["JoinGameWindow__password_label__text"], self)
        self.password_label.setObjectName("password_label")
        self.password_label.setFixedSize(400, 50)

        self.password_widget = QWidget()
        self.password_widget.setFixedHeight(100)
        self.password_layout = QHBoxLayout()

        self.password_lineedit = QLineEdit(self)
        self.password_lineedit.setObjectName("password_lineedit")
        self.password_lineedit.setPlaceholderText(langue.langue_data["JoinGameWindow__password_lineedit__placeholder"])
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        self.password_lineedit.setMaxLength(30)
        self.password_lineedit.returnPressed.connect(self.join_game)
        self.password_lineedit.textChanged.connect(lambda: self.restricted_caracters(self.password_lineedit))

        self.show_password_button = ClickButton("🔑", self)
        self.show_password_button.setObjectName("show_password_pushbutton")
        self.show_password_button.setFixedWidth(40)
        self.show_password_button.clicked.connect(self.show_password)

        self.join_game_button = StyledButton(langue.langue_data["JoinGameWindow__join_game_button__text"], self)
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
            self.alert_label.setText(langue.langue_data["JoinGameWindow__alert_label__incorrect_password_error"])
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

        self.setWindowTitle(langue.langue_data["WaitingRoomWindow__text"])
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

class LeaveGameWindow(DialogMainWindow):
    """Fenêtre pour quitter la partie"""
    def __init__(self, clientObject : object, mqtt_sub : object, game_name : str):
        """__init__() : Initialisation de la fenêtre de quitter la partie"""
        super(LeaveGameWindow, self).__init__()
        self.clientObject = clientObject
        self.mqtt_sub = mqtt_sub
        self.game_name = game_name
        self.setWindowTitle(langue.langue_data["LeaveGameWindow__text"])
        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre de quitter la partie"""
        self.central_widget = QWidget()
        self.leave_game_layout = QGridLayout(self.central_widget)

        self.ok_icon = QIcon.fromTheme('dialog-ok')
        self.cancel_icon = QIcon.fromTheme('dialog-cancel')

        self.warning_label = QLabel(langue.langue_data["LeaveGameWindow__warning_label__text"])

        self.ok_button = ClickButton(langue.langue_data["LeaveGameWindow__ok_button__text"])
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setIcon(self.ok_icon)
        self.ok_button.setAutoDefault(True)
        self.ok_button.clicked.connect(self.ok_clicked)
        
        self.cancel_button = ClickButton(langue.langue_data["LeaveGameWindow__cancel_button__text"])
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

class ConnexionInfoWindow(DialogMainWindow):
    """Fenêtre d'informations de connexion"""
    def __init__(self, clientObject : object):
        """__init__() : Initialisation de la fenêtre d'informations de connexion"""
        super(ConnexionInfoWindow, self).__init__()
        self.clientObject = clientObject
        self.setWindowTitle(langue.langue_data["ConnexionInfoWindow__text"])
        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre d'informations de connexion"""
        self.central_widget = QWidget()
        self.connexion_info_layout = QGridLayout(self.central_widget)

        self.error_icon = QIcon.fromTheme('dialog-error')

        self.warning_label = QLabel(langue.langue_data["ConnexionInfoWindow__warning_label__lost_connection_error"])
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.quitter_button = ClickButton(langue.langue_data["ConnexionInfoWindow__quitter_button__text"], self)
        self.quitter_button.setObjectName("quitter_button")
        self.quitter_button.setIcon(self.error_icon)
        self.quitter_button.setAutoDefault(True)
        self.quitter_button.clicked.connect(self.close_windows)

        self.connexion_info_layout.addWidget(self.warning_label)
        self.connexion_info_layout.addWidget(self.quitter_button, 1, 0, Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(self.central_widget)

        self.quitter_button.setFocus()

    def ok_clicked(self):
        self.close()

    def close_windows(self):
        self.clientObject.close()
        self.close()

    def closeEvent(self, event = QEvent) -> None:
        self.clientObject.connexion_info_window = None
        self.close_windows()
        event.accept()

class GameIsFullWindow(DialogMainWindow):
    def __init__(self, clientObject : object):
        """__init__() : Initialisation de la fenêtre d'informations de connexion"""
        super(GameIsFullWindow, self).__init__()
        self.clientObject = clientObject
        self.setWindowTitle(langue.langue_data["GameIsFullWindow__text"])
        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre d'informations de connexion"""
        self.central_widget = QWidget()
        self.connexion_info_layout = QGridLayout(self.central_widget)

        self.ok_icon = QIcon.fromTheme('dialog-ok')

        self.warning_label = QLabel(langue.langue_data["GameIsFullWindow__warning_label__game_full_error"])
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ok_button = ClickButton(langue.langue_data["GameIsFullWindow__ok_button__text"], self)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setIcon(self.ok_icon)
        self.ok_button.setAutoDefault(True)
        self.ok_button.clicked.connect(self.ok_clicked)

        self.connexion_info_layout.addWidget(self.warning_label)
        self.connexion_info_layout.addWidget(self.ok_button, 1, 0, Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(self.central_widget)

        self.ok_button.setFocus()

    def ok_clicked(self):
        self.close()

class RestartWindow(DialogMainWindow):
    """Fenêtre de redémarrage"""
    def __init__(self, clientObject : object):
        """__init__() : Initialisation de la fenêtre de redémarrage"""
        super(RestartWindow, self).__init__()
        self.clientObject = clientObject
        self.setWindowTitle(langue.langue_data["RestartWindow__text"])
        self.setup()

    def setup(self):
        """setup() : Mise en place de la fenêtre de redémarrage"""
        self.central_widget = QWidget()
        self.restart_layout = QGridLayout(self.central_widget)

        self.warning_label = QLabel(langue.langue_data["RestartWindow__warning_label__text"])
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ok_icon = QIcon.fromTheme('dialog-ok')
        self.cancel_icon = QIcon.fromTheme('dialog-cancel')

        self.ok_button = ClickButton(langue.langue_data["RestartWindow__ok_button__text"], self)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setIcon(self.ok_icon)
        self.ok_button.setAutoDefault(True)
        self.ok_button.clicked.connect(self.ok_clicked)

        self.cancel_button = ClickButton(langue.langue_data["RestartWindow__cancel_button__text"], self)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setIcon(self.cancel_icon)
        self.cancel_button.setAutoDefault(True)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        self.restart_layout.addWidget(self.warning_label)
        self.restart_layout.addWidget(self.ok_button, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.restart_layout.addWidget(self.cancel_button, 1, 0, Qt.AlignmentFlag.AlignLeft)

        self.setCentralWidget(self.central_widget)

        self.cancel_button.setFocus()

    def ok_clicked(self):
        self.close()
        self.clientObject.close()

    def cancel_clicked(self):
        self.close()

class SettingsWindow(ToolMainWindow):
    """Fenêtre des paramètres"""
    def __init__(self, parent = None):
        """__init__() : Initialisation de la fenêtre des paramètres"""
        super(SettingsWindow, self).__init__(parent)
        self.clientObject = parent
        self.setWindowTitle(langue.langue_data["SettingsWindow__text"])
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
        self.check_sound_effects_muted(self.sound_button, 0)
        self.check_sound_effects_muted(self.ambiance_button, 2)
        self.check_sound_effects_muted(self.boutons_button, 3)

        widget = QWidget()
        reset_button = ClickButton(langue.langue_data["SettingsWindow__reset_button__text"], self)
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
        
        self.tabs.addTab(self.sound_tab, langue.langue_data["SettingsWindow__sound_tab__added_tab_title"])
        self.tabs.addTab(self.graphic_tab, langue.langue_data["SettingsWindow__graphic_tab__added_tab_title"])
        self.tabs.addTab(self.language_tab, langue.langue_data["SettingsWindow__langue_tab__added_tab_title"])
    
    def setup_sound_tab(self):
        """setup_sound_tab() : Mise en place de l'onglet du son"""
        # Sound tab
        self.sound_layout = QGridLayout(self.sound_tab)
        self.sound_button = ClickButton(langue.langue_data["SettingsWindow__sound_button__text"], self.sound_tab)
        self.sound_button.setObjectName("sound_button")
        self.sound_button.clicked.connect(self.global_mute)
        self.sound_slider = QSlider(Qt.Horizontal, self.sound_tab)
        self.sound_slider.setObjectName("sound_slider")
        self.sound_slider.setMinimum(0)
        self.sound_slider.setMaximum(100)
        self.sound_slider.setValue(int(settings.sound_global_data[0][1]))
        self.sound_slider.valueChanged.connect(self.set_global_volume)
        # Musique
        self.musique_button = ClickButton(langue.langue_data["SettingsWindow__musique_button__text"], self)
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
        self.ambiance_button = ClickButton(langue.langue_data["SettingsWindow__ambiance_button__text"], self)
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
        self.boutons_button = ClickButton(langue.langue_data["SettingsWindow__boutons_button__text"], self)
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
        self.graphic_layout = QVBoxLayout(self.graphic_tab)
        #thème
        self.theme_label = QLabel(langue.langue_data["SettingsWindow__theme_label__text"], self.graphic_tab)
        self.theme_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.theme_sombre_checkbox = QCheckBox("Thème sombre", self.graphic_tab)
        #animations
        self.animations_label = QLabel(langue.langue_data["SettingsWindow__animations_label__text"], self.graphic_tab)
        self.animations_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.deactivate_button = ClickButton(langue.langue_data["SettingsWindow__deactivate_button__text"], self.graphic_tab)
        self.animations_checkbox = QCheckBox(langue.langue_data["SettingsWindow__animations_checkbox__text"], self.graphic_tab)
        self.border_checkbox = QCheckBox(langue.langue_data["SettingsWindow__border_checkbox__text"], self.graphic_tab)
        self.background_checkbox = QCheckBox(langue.langue_data["SettingsWindow__background_checkbox__text"], self.graphic_tab)
        # Ajout des éléments
        self.graphic_layout.addWidget(self.theme_label, Qt.AlignmentFlag.AlignCenter)
        self.graphic_layout.addWidget(self.theme_sombre_checkbox)
        self.graphic_layout.addWidget(self.animations_label, Qt.AlignmentFlag.AlignCenter)
        self.graphic_layout.addWidget(self.animations_checkbox)
        self.graphic_layout.addWidget(self.border_checkbox)
        self.graphic_layout.addWidget(self.background_checkbox)
        self.graphic_layout.addWidget(self.deactivate_button)
    
    def setup_language_tab(self):
        """setup_language_tab() : Mise en place de l'onglet de la langue"""
        # Language tab
        self.language_layout = QVBoxLayout(self.language_tab)
        self.language_combobox = QComboBox(self.language_tab)
        self.language_combobox.addItems(["Français", "English", "Deutch", "Español"])
        index_language : int = self.language_combobox.findText(settings.accessibility_data[2][1], Qt.MatchFixedString)
        self.language_combobox.setCurrentIndex(index_language)
        self.language_combobox.currentIndexChanged.connect(self.change_language)

        self.language_layout.addWidget(self.language_combobox)

    def change_language(self):
        """change_language() : Change la langue"""
        language = self.language_combobox.currentText()
        settings.accessibility.change_langue(language)
        self.restart_window = RestartWindow(self.clientObject)
        self.restart_window.show()

    def global_mute(self):
        """global_mute() : Mute le son global"""
        music.mute_music()
        if settings.sound_global_data[0][2] == "notmuted":
            settings.sound_global_data[0][2] = "muted"
        else:
            settings.sound_global_data[0][2] = "notmuted"
        settings.write_settings(
            concern = settings.sound_global_data[0][0], 
            data = settings.sound_global_data[0][1], 
            mute = settings.sound_global_data[0][2],
            file = "user_sound_global.csv")
        button_sound.sound_effects.mute_sound_effects()
        ambiance_sound.sound_effects.mute_sound_effects()
        self.check_music_muted(self.musique_button)
        print(settings.sound_global_data[0][2])
        self.check_sound_effects_muted(self.sound_button, 0)
        self.check_sound_effects_muted(self.ambiance_button, 2)
        self.check_sound_effects_muted(self.boutons_button, 3)

    def set_global_volume(self):
        settings.sound_global_data[0][1] = self.sound_slider.value()
        self.musique_slider.setValue(self.sound_slider.value())
        self.ambiance_slider.setValue(self.sound_slider.value())
        self.boutons_slider.setValue(self.sound_slider.value())
        settings.write_settings(
            concern = settings.sound_global_data[0][0], 
            data = settings.sound_global_data[0][1], 
            mute = settings.sound_global_data[0][2],
            file = "user_sound_global.csv")
        
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
        ambiance_sound.sound_effects.check_muted()
        self.check_sound_effects_muted(self.sound_button, 0)
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

        self.winner_label = QLabel(f"{self.classement[0][0]}{langue.langue_data["VictoryWindow__winner_label__text"]}")
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
    # waiting_window = WaitingRoomWindow("azertyuiopqsdfghjkl", 0, None)
    # waiting_window.show()
    # waiting_window.setup()

    # settings = SettingsWindow()
    # settings.sound_layout = QGridLayout()
    # settings.show()
    ruleswindow = RulesWindow()
    # game = GameIsFullWindow(GameIsFullWindow)
    # game.show()
    # victory = VictoryWindow([["Tom", "reveil-avatar"], 
    #                          ["i", "robot-ninja-avatar"],])
    # victory.show()
    sys.exit(app.exec_())