from PyQt5.QtGui import QMouseEvent
from client_utils import *
from tetris import Tetris, Board
from rating_widget import RatingWidget
from client_objects import ClickButton, ToolMainWindow, DialogMainWindow, HoverPixmapButton, UnderlineLineEdit, CustomTabWidget, ClickedSlider, ClickedCheckbox
from client_styles import StyledButton, LinearGradiantLabel
from client_logs import ErrorLogger

ErrorLogger.setup_logging()


def handle_username(new_username: str):
    """Handle the username"""
    global username
    username = new_username

class AvatarWindow(ToolMainWindow):
    """Class to create an avatar window
    
    Signals:
        avatar_signal (str): Signal to send the avatar name"""
    avatar_signal = pyqtSignal(str)
    def __init__(self, parent: object = None):
        """Initialize the AvatarWindow class"""
        super(AvatarWindow, self).__init__(parent)
        self.setObjectName("avatar_window")
        self.setWindowFlag(Qt.FramelessWindowHint)
        center_window(self)
        self.setup_window()

    def setup_window(self):
        """Setup the avatar window"""
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
        """Setup the pixmap for the avatars"""
        self.tasse_avatar = QPixmap(f"{avatar_path}tasse-avatar.png")
        self.serviette_avatar = QPixmap(f"{avatar_path}serviette-avatar.png")
        self.reveil_avatar = QPixmap(f"{avatar_path}reveil-avatar.png")
        self.cactus_avatar = QPixmap(f"{avatar_path}cactus-avatar.png")
        self.robot_ninja_avatar = QPixmap(f"{avatar_path}robot-ninja-avatar.png")
        self.bouteille_avatar = QPixmap(f"{avatar_path}bouteille-avatar.png")
        self.panneau_avatar = QPixmap(f"{avatar_path}panneau-avatar.png")
        self.television_avatar = QPixmap(f"{avatar_path}television-avatar.png")
        self.pizza_avatar = QPixmap(f"{avatar_path}pizza-avatar.png")
        self.gameboy_avatar = QPixmap(f"{avatar_path}gameboy-avatar.png")
        
    def set_avatar(self, avatar_name: str):
        """Define the avatar name"""
        self.avatar_signal.emit(avatar_name)
        self.close()
    
class RulesWindow(ToolMainWindow):
    """Class to create a rules window"""
    def __init__(self):
        """Initialize the RulesWindow class"""
        super().__init__()
        self.setObjectName("rules_window")
        self.setWindowTitle(langue.langue_data["RulesWindow__title"])
        self.resize(int(screen_width // 2.5), int(screen_height // 2.5))
        self.setStyleSheet(windows_stylesheet)

        self.lifes_value = rules[2]
        self.setup()
        self.show()
        self.activateWindow()
        center_window(self)

    def setup(self):
        """Setup the rules window"""
        layout = QGridLayout()
        layout.setSpacing(20)
        if sys.platform == "win32":
            spinbox_stylesheet = f'''
                QSpinBox#rules_spinboxes::up-button{{
                    image: url({os.path.join(image_path, "plus.png").replace("\\", "/")});}} 
                QSpinBox#rules_spinboxes::down-button{{
                    image: url({os.path.join(image_path, "moins.png").replace("\\", "/")});}}'''
        else:
            spinbox_stylesheet = f'''
                QSpinBox#rules_spinboxes::up-button{{
                    image: url({os.path.join(image_path, "plus.png")});}} 
                QSpinBox#rules_spinboxes::down-button{{
                    image: url({os.path.join(image_path, "moins.png")});}}'''
        

        #TIME RULES
        self.timerules_widget = QWidget()
        self.timerules_layout = QVBoxLayout(self.timerules_widget)

        self.timerulesmin_widget = QWidget()
        self.timerulesmin_layout = QHBoxLayout(self.timerulesmin_widget)

        self.timerulesmax_widget = QWidget()
        self.timerulesmax_layout = QHBoxLayout(self.timerulesmax_widget)

        self.timeruleslabel = LinearGradiantLabel(langue.langue_data["RulesWindow__timeruleslabel__text"], color1=QColor(45,120,191), color2=QColor(210,45,98))
        self.timeruleslabel.setObjectName("rules_title_labels")
        self.timeruleslabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.timerulemin_spinbox= QSpinBox(self)
        self.timerulemin_spinbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.timerulemin_spinbox.setObjectName("rules_spinboxes")
        self.timerulemin_spinbox.setStyleSheet(spinbox_stylesheet)
        self.timerulemin_spinbox.setMaximum(20)
        self.timerulemin_spinbox.setMinimum(2)
        self.timerulemin_spinbox.setValue(rules[0])
        self.timerulemin_spinbox.setFixedWidth(self.timerulemin_spinbox.sizeHint().width() // 4)
        self.timerulemin_spinbox.valueChanged.connect(self.check_timerulemax)

        self.timerulemin_label = QLabel(langue.langue_data["RulesWindow__timeruleminlabel__text"], self)
        self.timerulemin_label.setObjectName("timerulemin_label")

        self.timerulemax_spinbox = QSpinBox(self)
        self.timerulemax_spinbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.timerulemax_spinbox.setObjectName("rules_spinboxes")
        self.timerulemax_spinbox.setStyleSheet(spinbox_stylesheet)
        self.timerulemax_spinbox.setMaximum(30)
        self.timerulemax_spinbox.setMinimum(self.timerulemin_spinbox.value() + 2)
        self.timerulemax_spinbox.setValue(rules[1])        
        self.timerulemax_spinbox.setFixedWidth(self.timerulemax_spinbox.sizeHint().width() // 4)
        
        self.timerulemax_label = QLabel(langue.langue_data["RulesWindow__timerulmaxlabel__text"], self)
        self.timerulemax_label.setObjectName("timerulemax_label")

        #SYLLABES RULES
        self.syllabes_widget = QWidget()
        self.syllabes_layout = QVBoxLayout(self.syllabes_widget)

        self.syllabes_sub_widget = QWidget()
        self.syllabes_sub_layout = QHBoxLayout(self.syllabes_sub_widget)

        self.syllabes_label = LinearGradiantLabel(langue.langue_data["RulesWindow__syllabes_label__text"], color1=QColor(45,120,191), color2=QColor(210,45,98))
        self.syllabes_label.setObjectName("rules_title_labels")
        self.syllabes_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.syllabes_spinbox_min = QSpinBox(self)
        self.syllabes_spinbox_min.setCursor(QCursor(Qt.PointingHandCursor))
        self.syllabes_spinbox_min.setObjectName("rules_spinboxes")
        self.syllabes_spinbox_min.setStyleSheet(spinbox_stylesheet)
        self.syllabes_spinbox_min.setMaximum(5)
        self.syllabes_spinbox_min.setMinimum(1)
        self.syllabes_spinbox_min.setValue(rules[3])
        self.syllabes_spinbox_min.setFixedWidth(self.syllabes_spinbox_min.sizeHint().width() // 4)
        self.syllabes_spinbox_min.valueChanged.connect(self.check_syllabesmax)

        self.syllabes_label_min = QLabel(langue.langue_data["RulesWindow__syllabes_label_min__text"], self)
        self.syllabes_label_min.setObjectName("syllabes_label_min")

        self.syllabes_spinbox_max = QSpinBox(self)
        self.syllabes_spinbox_max.setCursor(QCursor(Qt.PointingHandCursor))
        self.syllabes_spinbox_max.setObjectName("rules_spinboxes")
        self.syllabes_spinbox_max.setStyleSheet(spinbox_stylesheet)
        self.syllabes_spinbox_max.setMaximum(5)
        self.syllabes_spinbox_max.setMinimum(1)
        self.syllabes_spinbox_max.setValue(rules[4])   
        self.syllabes_spinbox_max.setFixedWidth(self.syllabes_spinbox_max.sizeHint().width() // 4)
        
        self.syllabes_label_max = QLabel(langue.langue_data["RulesWindow__syllabes_label_max__text"], self)
        self.syllabes_label_max.setObjectName("syllabes_label_max")

        #REPETITION RULES
        self.repetition_label = QLabel(langue.langue_data["RulesWindow__repetition_label__text"], self)
        self.repetition_label.setObjectName("repetition_label")

        self.repetition_spinbox = QSpinBox(self)
        self.repetition_spinbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.repetition_spinbox.setObjectName("rules_spinboxes")
        self.repetition_spinbox.setStyleSheet(spinbox_stylesheet)
        self.repetition_spinbox.setMaximum(8)
        self.repetition_spinbox.setMinimum(0)
        self.repetition_spinbox.setValue(rules[5])
        self.repetition_spinbox.setFixedWidth(self.repetition_spinbox.sizeHint().width() // 4)

        #DEATH MODE RULES
        self.death_mode_widget = QWidget()
        self.death_mode_layout = QVBoxLayout(self.death_mode_widget)

        self.death_mode_sub_widget = QWidget()
        self.death_mode_sub_layout = QHBoxLayout(self.death_mode_sub_widget)

        self.death_mode_label = LinearGradiantLabel(langue.langue_data["RulesWindow__death_mode_label__text"], color1=QColor(45,120,191), color2=QColor(210,45,98))
        self.death_mode_label.setObjectName("rules_title_labels")
        self.death_mode_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.skull_pixmap = QPixmap(f"{image_path}skull.png")
        self.skull_pixmap_hover = QPixmap(f"{image_path}skull-hover.png")
        self.skull_red_pixmap = QPixmap(f"{image_path}skull-red.png")
        self.skull_red_pixmap_hover = QPixmap(f"{image_path}skull-red-hover.png")
        self.skull_green_pixmap = QPixmap(f"{image_path}skull-green.png")
        self.skull_green_pixmap_hover = QPixmap(f"{image_path}skull-green-hover.png")

        self.death_mode_pixmap_button = HoverPixmapButton(self.skull_pixmap, self.skull_pixmap_hover)
        self.death_mode_pixmap_button.setObjectName("other_buttons")
        self.set_death_mode_image()
        self.death_mode_pixmap_button.setIconSize(QSize(int(screen_width//14), int(screen_width//14)))
        self.death_mode_pixmap_button.clicked.connect(self.set_death_mode)
        self.death_mode_state = rules[6]
        
        self.death_mode_explained_label = QLabel(langue.langue_data["RulesWindow__death_mode_explained_label__text1"], self)
        self.death_mode_explained_label.setObjectName("death_mode_explained_label")
        self.death_mode_explained_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #LIFES RULES
        self.lifes_widget = QWidget()
        self.lifes_layout = QVBoxLayout(self.lifes_widget)
        
        self.lifes_label = LinearGradiantLabel(langue.langue_data["RulesWindow__lifes_label__text"], color1=QColor(45,120,191), color2=QColor(210,45,98))
        self.lifes_label.setObjectName("rules_title_labels")
        self.lifes_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.lifes_rating_widget = RatingWidget(rule_value=rules[2])
        self.lifes_rating_widget.value_updated.connect(self.set_life_value)

        #SAVE BUTTON
        self.save_button = StyledButton(langue.langue_data["RulesWindow__save_button__text"], self, color1="#6f85e2", color2="#d26d9e")
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
        """Set the life value"""
        self.lifes_value = value

    def set_death_mode_image(self):
        """Set the death mode image corresponding to the level"""
        if rules[6] == 2:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_red_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_red_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_red_pixmap_hover
        elif rules[6] == 1:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_green_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_green_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_green_pixmap_hover
        else:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_pixmap_hover

    def set_death_mode(self):
        """Set the death mode level"""
        self.death_mode_state = (self.death_mode_state + 1) % 3
        if self.death_mode_state == 2:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_red_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_red_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_red_pixmap_hover
            self.death_mode_explained_label.setText(langue.langue_data["RulesWindow__death_mode_explained_label__text3"])
        elif self.death_mode_state == 1:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_green_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_green_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_green_pixmap_hover
            self.death_mode_explained_label.setText(langue.langue_data["RulesWindow__death_mode_explained_label__text2"])
        else:
            self.death_mode_pixmap_button.setIcon(QIcon(self.skull_pixmap_hover))
            self.death_mode_pixmap_button.image = self.skull_pixmap
            self.death_mode_pixmap_button.image_hover = self.skull_pixmap_hover
            self.death_mode_explained_label.setText(langue.langue_data["RulesWindow__death_mode_explained_label__text1"])

    def check_syllabesmax(self):
        """Check the maximum syllabes"""
        self.syllabes_spinbox_max.setMinimum(self.syllabes_spinbox_min.value())
        if self.syllabes_spinbox_max.value() < self.syllabes_spinbox_min.value():
            self.syllabes_spinbox_max.setValue(self.syllabes_spinbox_min.value())

    def check_timerulemax(self):
        """Check the maximum time rule"""
        self.timerulemax_spinbox.setMinimum(self.timerulemin_spinbox.value() + 2)
        if self.timerulemax_spinbox.value() < self.timerulemin_spinbox.value() + 2:
            self.timerulemax_spinbox.setValue(self.timerulemin_spinbox.value() + 2)

    def save_rules(self):
        """Save the rules"""
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
        self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Manage the key press event
        
        Args:
            event (QKeyEvent): The key event
            
        Returns:
            None"""
        if event.key() == Qt.Key_Return:
            self.save_rules()
        return super().keyPressEvent(event)

class GameCreationWindow(ToolMainWindow):
    """Class to create a game creation window
    
    Attributes:
        old_layout (QGridLayout): The old layout
        receiverthread (object): The receiver thread
        
    Signals:
        create_game_signal (str, str, bool): Signal to create a game"""
    create_game_signal = pyqtSignal(str, str, bool)

    def __init__(self, layout: QGridLayout, receiverthread: object):
        """Initialize the GameCreationWindow class"""
        super().__init__()
        self.setObjectName("game_creation_window")
        self.setWindowTitle(langue.langue_data["GameCreationWindow__text"])
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(windows_stylesheet)

        self.old_layout = layout
        self.receiverthread = receiverthread
        self.receiverthread.check_game_signal.connect(self.game_is_unique)

    def setup(self):
        """Setup the game creation window"""
        global username
        layout = QGridLayout()

        self.cadenas_icon = QPixmap(f"{image_path}cadenas.png")
        self.cadenas_hover_icon = QPixmap(f"{image_path}cadenas-hover.png")
        self.globe_icon = QPixmap(f"{image_path}globe.png")
        self.globe_hover_icon = QPixmap(f"{image_path}globe-hover.png")
        self.key_icon = QPixmap(f"{image_path}key.png")
        self.key_hover_icon = QPixmap(f"{image_path}key-hover.png")
        
        self.game_name_label = LinearGradiantLabel(langue.langue_data["GameCreationWindow__game_name_label__text"], color1=QColor(219,85,149), color2=QColor(22,49,215))
        self.game_name_label.setObjectName("gamecreation_label")
        self.game_name_label.setFixedWidth(screen_width//5)

        default_game_name = f"{langue.langue_data["GameCreationWindow__game_name_label__default_text"]}{username}"

        game_name_widget = QWidget()
        game_name_layout = QHBoxLayout(game_name_widget)
        self.game_name_lineedit = UnderlineLineEdit()
        self.game_name_lineedit.setObjectName("gamecreation_lineedit")
        self.game_name_lineedit.setPlaceholderText(default_game_name)
        self.game_name_lineedit.setMaxLength(20)
        self.game_name_lineedit.setText(default_game_name)
        self.game_name_lineedit.setFixedWidth(self.game_name_lineedit.sizeHint().width() * 3)
        self.game_name_lineedit.textChanged.connect(lambda: self.restricted_caracters(self.game_name_lineedit))
        self.game_name_lineedit.returnPressed.connect(lambda: self.create_game(default_game_name, self.password_lineedit.text(), self.private_button.text()))

        self.game_name_alert_button = QLabel(self)
        self.game_name_alert_button.setObjectName("game_name_alert_label")
        self.game_name_alert_button.setStyleSheet("color: red;")

        self.private_button = HoverPixmapButton(self.globe_icon, self.globe_hover_icon, self)
        self.private_button.setFixedSize(screen_width//40, screen_width//40)
        self.private_button.setIcon(QIcon(self.globe_icon))
        self.private_button.setIconSize(self.private_button.size())
        self.private_button.setObjectName("hover_buttons")
        self.private_state = False
        self.private_button.clicked.connect(self.private_game)

        self.password_label = LinearGradiantLabel(langue.langue_data["GameCreationWindow__password_label__text"], color1=QColor(219,85,149), color2=QColor(22,49,215))
        self.password_label.setObjectName("gamecreation_label")
        self.password_label.setFixedWidth(screen_width//5)

        password_wiget = QWidget()
        password_layout = QHBoxLayout(password_wiget)

        characters = string.ascii_letters + string.digits
        random_password = "".join(random.choice(characters) for i in range(12))
        self.password_lineedit = UnderlineLineEdit()
        self.password_lineedit.setObjectName("gamecreation_lineedit")
        self.password_lineedit.setPlaceholderText(langue.langue_data["GameCreationWindow__password_lineedit__placeholder"])
        self.password_lineedit.setText(random_password)
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        self.password_lineedit.setEnabled(False)
        self.password_lineedit.setMaxLength(20)
        self.password_lineedit.setFixedWidth(self.password_lineedit.sizeHint().width() * 3)
        self.password_lineedit.returnPressed.connect(lambda: self.create_game(default_game_name, random_password, self.password_lineedit.text()))
        self.password_lineedit.textChanged.connect(lambda: self.restricted_caracters(self.password_lineedit))

        self.show_password_button = HoverPixmapButton(self.key_icon, self.key_hover_icon, self)
        self.show_password_button.setObjectName("hover_buttons")
        self.show_password_button.setFixedSize(screen_width//40, screen_width//40)
        self.show_password_button.setIcon(QIcon(self.key_icon))
        self.show_password_button.setIconSize(self.show_password_button.size())
        self.show_password_button.clicked.connect(self.show_password)
        self.show_password_button.setEnabled(False)

        self.select_langue_combobox = QComboBox(self)
        self.select_langue_combobox.setCursor(Qt.PointingHandCursor)
        self.select_langue_combobox.setObjectName("select_langue_combobox")
        langues = ["Français", "English"]
        self.select_langue_combobox.addItems(langues)
        if settings.accessibility_data[1][1] in langues:
            index_language: int = self.select_langue_combobox.findText(settings.accessibility_data[1][1], Qt.MatchFixedString)
        else:
            index_language: int = self.select_langue_combobox.findText("English", Qt.MatchFixedString)
        self.select_langue_combobox.setCurrentIndex(index_language)
        if sys.platform == "win32":
            self.select_langue_combobox.setStyleSheet(f'''QComboBox#select_langue_combobox::down-arrow{{border-image: url({os.path.join(image_path, "arrow.png").replace("\\", "/")}); width: 20; height: 20; margin-right: 10;}}''')
        else:
            self.select_langue_combobox.setStyleSheet(f'''QComboBox#select_langue_combobox::down-arrow{{border-image: url({os.path.join(image_path, "arrow.png")}); width: 20; height: 20; margin-right: 10;}}''')

        self.create_game_button2 = StyledButton(langue.langue_data["GameCreationWindow__create_game_button2__text"], self, button_width=0.4, color1="#6f85e2")
        self.create_game_button2.setObjectName("create_game_button2")
        self.create_game_button2.clicked.connect(lambda: self.create_game(default_game_name, random_password, self.password_lineedit.text()))

        game_name_layout.addWidget(self.game_name_lineedit)
        game_name_layout.addWidget(self.private_button)

        password_layout.addWidget(self.password_lineedit)
        password_layout.addWidget(self.show_password_button)

        layout.addWidget(self.game_name_label, 0, 0, Qt.AlignHCenter)
        layout.addWidget(game_name_widget, 1, 0, Qt.AlignHCenter)
        layout.addWidget(self.game_name_alert_button, 2, 0)
        layout.addWidget(self.password_label, 3, 0, Qt.AlignHCenter)
        layout.addWidget(password_wiget, 4, 0, Qt.AlignHCenter)
        layout.addWidget(self.select_langue_combobox, 5, 0, Qt.AlignHCenter)
        layout.addWidget(self.create_game_button2, 6, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def restricted_caracters(self, lineedit: QLineEdit):
        """Restricts special characters
        
        Args:
            lineedit (QLineEdit): LineEdit"""
        text = lineedit.text()
        lineedit.setText(re.sub(r'[^a-zA-ZÀ-ÿ\s0-9]', '', text))

    def show_password(self):
        """Show or hide the password"""
        if self.password_lineedit.echoMode() == QLineEdit.Password:
            self.password_lineedit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_lineedit.setEchoMode(QLineEdit.Password)

    def private_game(self):
        """Makes the game private or not"""
        if self.private_state:
            self.private_state = False
            self.private_button.image = self.globe_icon
            self.private_button.image_hover = self.globe_hover_icon
            self.private_button.setIcon(QIcon(self.globe_hover_icon))
            self.password_lineedit.setEnabled(False)
            self.show_password_button.setEnabled(False)
            self.password_lineedit.setEchoMode(QLineEdit.Password)
        else:
            self.private_state = True
            self.private_button.image = self.cadenas_icon
            self.private_button.image_hover = self.cadenas_hover_icon
            self.private_button.setIcon(QIcon(self.cadenas_hover_icon))
            self.password_lineedit.setEnabled(True)
            self.show_password_button.setEnabled(True)

    def create_game(self, dafault_game_name: str, random_password: str, manual_password: str):
        """Creates a game
        
        Args:
            default_game_name (str): Default game name
            random_password (str): Default password
            manual_password (str): Manual password"""
        if self.password_lineedit.text() == random_password or self.password_lineedit.text() == "" or self.password_lineedit.text().isspace():
            password = random_password
        else:
            password = manual_password

        if self.game_name_lineedit.text() == dafault_game_name or self.game_name_lineedit.text() == "" or self.game_name_lineedit.text().isspace():
            game_name = dafault_game_name
        else:
            game_name = self.game_name_lineedit.text()

        if not self.private_state:
            private_game = False
        else:
            private_game = True
        
        self.check_game_name_is_unique(game_name, password, private_game)
        # self.create_game_signal.emit(game_name, password, private_game)
        # self.close()
    
    def check_game_name_is_unique(self, game_name: str, password: str, private_game: bool):
        """Check if the game name is unique
        
        Args:
            game_name (str): The game name
            password (str): The password
            private_game (bool): Is the game private or not"""
        send_server(f"CHECK-GAME-NAME_|{game_name}|{password}|{private_game}|".encode())

    def game_is_unique(self, reply: list):
        """Check if the game name is unique
        
        Args:
            reply (list): The reply from the server"""
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
    """Window to join a private game
    
    Attributes:
        game_name (str): The game name
        private_game (bool): Is the game private or not
        clientWindow (QWidget): The parent window"""
    def __init__(self, game_name: str, private_game: bool, clientWindow: QWidget):
        """Initialize the joig game window
        
        Args:
            game_name (str): The game name
            private_game (bool): Is the game private or not
            clientWindow (QWidget): The parent window"""
        super().__init__()
        self.game_name = game_name
        self.private_game = private_game
        self.clientWindow = clientWindow

        self.setObjectName("joingame_window")
        self.setWindowTitle(langue.langue_data["JoinGameWindow__text"])
        self.resize(int(screen_width // 2.8), int(screen_height // 2.5))
        center_window(self)
        self.setStyleSheet(windows_stylesheet)

        clientWindow.in_game_signal.connect(self.in_game)
        clientWindow.join_window_close_signal.connect(self.check_to_close)
        
    def setup(self):
        """Setup the join game window"""
        layout = QGridLayout()

        self.key_icon = QPixmap(f"{image_path}key.png")
        self.key_hover_icon = QPixmap(f"{image_path}key-hover.png")

        self.game_name_label = QLabel(f"<b>{self.game_name}<b>", self)
        self.game_name_label.setObjectName("joingame_name_label")

        self.password_label = LinearGradiantLabel(langue.langue_data["JoinGameWindow__password_label__text"], color1=QColor(219,85,149), color2=QColor(22,49,215))
        self.password_label.setObjectName("joingame_password_label")

        self.password_widget = QWidget()
        self.password_layout = QHBoxLayout()

        self.password_lineedit = UnderlineLineEdit()
        self.password_lineedit.setObjectName("underline_password_lineedit")
        self.password_lineedit.setPlaceholderText(langue.langue_data["JoinGameWindow__password_lineedit__placeholder"])
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        self.password_lineedit.setMaxLength(30)
        self.password_lineedit.returnPressed.connect(self.join_game)
        self.password_lineedit.textChanged.connect(lambda: self.restricted_caracters(self.password_lineedit))

        self.show_password_button = HoverPixmapButton(self.key_icon, self.key_hover_icon, self)
        self.show_password_button.setObjectName("hover_buttons")
        self.show_password_button.setFixedSize(screen_width//40, screen_width//40)
        self.show_password_button.setIcon(QIcon(self.key_icon))
        self.show_password_button.setIconSize(self.show_password_button.size())
        self.show_password_button.clicked.connect(self.show_password)

        self.join_game_button = StyledButton(langue.langue_data["JoinGameWindow__join_game_button__text"], self, color1="#6f85e2", color2="#d26d9e")
        self.join_game_button.setObjectName("join_game_button")
        self.join_game_button.clicked.connect(self.join_game)

        self.alert_label = QLabel(parent=self)
        self.alert_label.setStyleSheet("color: red;")
        self.alert_label.setFixedHeight(int(self.alert_label.sizeHint().height() * 2))

        self.game_name_label.setAlignment(Qt.AlignHCenter)
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
        """Join the lobby (public)"""
        global username
        send_server(f"JOIN-GAME_|{self.game_name}|password|{username}".encode())

    def join_game(self):
        """Join the lobby (private)"""
        global username
        if self.password_lineedit.text() != "" and not self.password_lineedit.text().isspace():
            send_server(f"JOIN-GAME_|{self.game_name}|{self.password_lineedit.text()}|{username}".encode())

    def show_password(self):
        """Show or hide the password"""
        if self.password_lineedit.echoMode() == QLineEdit.Password:
            self.password_lineedit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_lineedit.setEchoMode(QLineEdit.Password)

    def incorrect_mdp(self, mdp: bool):
        """Shows an alert if the password is incorrect
        
        Args:
            mdp (bool): Is the password correct"""
        if mdp:
            self.alert_label.setText("")
            self.close()
        else:
            self.alert_label.setText(langue.langue_data["JoinGameWindow__alert_label__incorrect_password_error"])
            button_sound.sound_effects.error_sound.play()

    def check_to_close(self, game_name: str):
        """Check if the game name is the same
        
        Args:
            game_name (str): The game name"""
        if game_name == self.game_name:
            self.close()

    def in_game(self, game_name: str, players_number: int):
        """Show the waiting room window with Tetris
        
        Args:
            game_name (str): The game name
            players_number (int): The number of players"""
        self.waiting_room = WaitingRoomWindow(game_name, players_number, self.clientWindow)
        self.waiting_room.show()
        self.waiting_room.activateWindow()
        self.waiting_room.setup()
        self.close()

    def restricted_caracters(self, lineedit: QLineEdit):
        """Restrict special characters
        
        Args:
            lineedit (QLineEdit): LineEdit"""
        text = lineedit.text()
        lineedit.setText(re.sub(r'[^a-zA-ZÀ-ÿ\s0-9]', '', text))

class WaitingRoomWindow(ToolMainWindow):
    """Waiting room window
    
    Attributes:
        game_name (str): The game name
        players_number (int): The number of players
        clientWindow (object): The parent object"""
    def __init__(self, game_name: str, players_number: int, clientWindow: object):
        """Initialize the waiting room window
        
        Args:
            game_name (str): The game name
            players_number (int): The number of players
            window (object): The parent object"""
        super().__init__()
        self.game_name = game_name
        self.players_number = players_number
        self.clientWindow = clientWindow

        self.setObjectName("waiting_room_window")
        self.setWindowTitle(langue.langue_data["WaitingRoomWindow__text"])
        self.resize(int(screen_width // 6), int(screen_height // 2))
        center_window(self)
        self.setStyleSheet(windows_stylesheet)

        self.clientWindow.waiting_room_close_signal.connect(self.close)

    def setup(self):
        """Setup the waiting room window"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        self.game_name_label = QLabel(f"<b>{self.game_name}<b>", self)
        self.game_name_label.setObjectName("game_name_label")
        self.game_name_label.setAlignment(Qt.AlignHCenter)
        self.game_name_label.setWordWrap(True)

        self.waiting_label = QLabel("👥", self)
        self.waiting_label.setObjectName("waiting_label")
        self.waiting_label.setAlignment(Qt.AlignHCenter)
        self.waiting_label.setStyleSheet("font-size: 80px;")

        self.number_of_players_label = QLabel(f"{self.players_number}/8", self)
        self.number_of_players_label.setObjectName("number_of_players_label")
        self.number_of_players_label.setAlignment(Qt.AlignHCenter)

        self.tetris = Tetris()
        self.tetris.setFixedSize(int(screen_width // 10), int(screen_height // 3))
        self.tetris.statusbar.setObjectName("waiting_room_statusbar")
        
        layout.addWidget(self.game_name_label)
        layout.addWidget(self.waiting_label)
        layout.addWidget(self.number_of_players_label)
        layout.addWidget(self.tetris)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def manage_players_number(self, players_number: str):
        """Manage the number of players"""
        self.players_number = players_number
        self.number_of_players_label.setText(players_number)

    def closeEvent(self, event: QEvent):
        """Close the waiting room window
        
        Args:
            event (QEvent): The event"""
        send_server(f"LEAVE-WAITING-ROOM_|{self.game_name}|{username}".encode())
        event.accept()

class LeaveGameWindow(DialogMainWindow):
    """Fenêtre pour quitter la partie
    
    Attributes:
        clientObject (object): Objet parent
        mqtt_sub (object): Objet mqtt
        game_name (str): Nom de la partie"""
    def __init__(self, clientObject: object, mqtt_sub: object, game_name: str):
        """Initilalize the leave game window
        
        Args:
            clientObject (object): The parent object
            mqtt_sub (object): The mqtt object
            game_name (str): The game name"""
        super(LeaveGameWindow, self).__init__()
        self.clientObject = clientObject
        self.mqtt_sub = mqtt_sub
        self.game_name = game_name
        self.setWindowTitle(langue.langue_data["LeaveGameWindow__text"])
        self.setup()

    def setup(self):
        """Setup the leave game window"""
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
        """Unset the game to return to menu"""
        self.mqtt_sub.stop_loop()
        self.clientObject.join_state()
        self.clientObject.kill_borders()
        self.clientObject.setup(join=False)
        send_server(f"LEAVE-GAME_|{self.game_name}|{username}".encode())
        music.choose_music(1)
        self.close()

    def cancel_clicked(self):
        """Close the window"""
        self.close()

class ExitGameWindow(DialogMainWindow):
    """Class for the exit game window
    
    Attributes:
        clientObject (object): The parent object"""
    def __init__(self, clientObject: object):
        """Initialize the exit game window
        
        Args:
            clientObject (object): The parent object"""
        super(ExitGameWindow, self).__init__()
        self.clientObject = clientObject
        self.setWindowTitle(langue.langue_data["ExitGameWindow__text"])
        self.setup()

    def setup(self):
        """Setup the exit game window"""
        self.central_widget = QWidget()
        self.exit_game_layout = QVBoxLayout(self.central_widget)

        self.buttons_widget = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_widget)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setColumnStretch(0, 1)  # Left column stretches
        self.buttons_layout.setColumnStretch(1, 1)  # Right column stretches
        
        self.ok_icon = QIcon.fromTheme('dialog-ok')
        self.cancel_icon = QIcon.fromTheme('dialog-cancel')

        self.warning_label = QLabel(langue.langue_data["ExitGameWindow__warning_label__text"])
        self.warning_label.setWordWrap(True)
        
        self.ok_button = ClickButton(langue.langue_data["ExitGameWindow__ok_button__text"], self)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setIcon(self.ok_icon)
        self.ok_button.setAutoDefault(True)
        self.ok_button.clicked.connect(self.ok_clicked)

        self.cancel_button = ClickButton(langue.langue_data["ExitGameWindow__cancel_button__text"], self)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setIcon(self.cancel_icon)
        self.cancel_button.setAutoDefault(True)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        self.buttons_layout.addWidget(self.cancel_button, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.buttons_layout.addWidget(self.ok_button, 0, 1, Qt.AlignmentFlag.AlignRight)

        self.exit_game_layout.addWidget(self.warning_label, Qt.AlignmentFlag.AlignHCenter)
        self.exit_game_layout.addWidget(self.buttons_widget)
        
        self.setCentralWidget(self.central_widget)
        self.cancel_button.setFocus()
        
    def ok_clicked(self):
        """Close the window and exit the game"""
        try:
            self.clientObject.mqtt_sub.stop_loop()
        except AttributeError:
            pass
        self.close()
        QApplication.quit()

    def cancel_clicked(self):
        """Close the window"""
        self.close()

class ConnexionInfoWindow(DialogMainWindow):
    """Class for the connection information window

    Attributes:
        clientObject (object): The parent object"""
    def __init__(self, clientObject : object):
        """Initialize the connection information window
        
        Args:
            clientObject (object): The parent object"""
        super(ConnexionInfoWindow, self).__init__()
        self.clientObject = clientObject
        self.setWindowTitle(langue.langue_data["ConnexionInfoWindow__text"])
        self.setup()

    def setup(self):
        """Setup the connection information window"""
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
        """Close the window"""
        self.close()

    def close_windows(self):
        """Close the window"""
        self.close()
        QApplication.quit()

    def closeEvent(self, event: QEvent = QEvent) -> None:
        """Close the window
        
        Args:
            event (QEvent, optional): The event. Defaults to QEvent.
        
        Returns:
            None"""
        self.clientObject.connexion_info_window = None
        self.close_windows()
        event.accept()

class GameIsFullWindow(DialogMainWindow):
    """Class for the game window which check if the game il full
    
    Attributes:
        clientObject (object): The parent object"""
    def __init__(self, clientObject: object):
        """Initialize the game window which check if the game il full
        
        Args:
            clientObject (object): The parent object"""
        super(GameIsFullWindow, self).__init__()
        self.clientObject = clientObject
        self.setWindowTitle(langue.langue_data["GameIsFullWindow__text"])
        self.setup()

    def setup(self):
        """Setup the game window which check if the game il full"""
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
        """Close the window"""
        self.close()

class RestartWindow(DialogMainWindow):
    """Class for the restart window
    
    Attributes:
        clientObject (object): The parent object"""
    def __init__(self, clientObject: object):
        """Initialize the restart window
        
        Args:
            clientObject (object): The parent object"""
        super(RestartWindow, self).__init__()
        self.clientObject = clientObject
        self.setWindowTitle(langue.langue_data["RestartWindow__text"])
        self.setup()

    def setup(self):
        """Setup the restart window"""
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

        self.restart_layout.addWidget(self.warning_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.restart_layout.addWidget(self.ok_button, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.restart_layout.addWidget(self.cancel_button, 1, 0, Qt.AlignmentFlag.AlignLeft)

        self.setCentralWidget(self.central_widget)

        self.cancel_button.setFocus()

    def ok_clicked(self):
        """Restart the game"""
        self.close()
        QApplication.quit()

    def cancel_clicked(self):
        """Close the window"""
        self.close()

class SettingsWindow(ToolMainWindow):
    """Fenêtre des paramètres
    
    Attributes:
        clientObject (object): Objet client"""
    def __init__(self, clientObject: object = None):
        """
        Initialize the settings window.

        Args:
            clientObject (object, optional): The parent object. Defaults to None.
        """
        super(SettingsWindow, self).__init__(clientObject)
        self.clientObject = clientObject
        self.setObjectName("settings_window")
        self.setWindowTitle(langue.langue_data["SettingsWindow__text"])
        self.resize(int(screen_width // 2.5), int(screen_height // 2.2))
        center_window(self)
        self.setStyleSheet(windows_stylesheet)
        self.setup()

    def setup(self):
        """Setup the settings window"""
        self.setup_tabs()
        self.setup_sound_tab()
        self.setup_graphic_tab()
        self.setup_language_tab()
        self.setup_credits_tab()
        self.check_music_muted(self.musique_button)
        self.check_sound_effects_muted(self.sound_button, 0)
        self.check_sound_effects_muted(self.ambiance_button, 2)
        self.check_sound_effects_muted(self.boutons_button, 3)
        self.check_effects()

        widget = QWidget()
        reset_button = ClickButton(langue.langue_data["SettingsWindow__reset_button__text"], self)
        reset_button.setObjectName("reset_button")
        reset_button.clicked.connect(self.reset_settings)

        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabs)
        layout.addWidget(reset_button)
        self.setCentralWidget(widget)

    def setup_tabs(self):
        """Setup the tabs for the settings window"""
        self.tabs = CustomTabWidget()
        self.tabs.setObjectName("settings_tabwidget")
       
        self.sound_tab = QWidget()
        self.sound_tab.setObjectName("settings_tabs")
        self.graphic_tab = QWidget()
        self.graphic_tab.setObjectName("settings_tabs")
        self.language_tab = QWidget()
        self.language_tab.setObjectName("settings_tabs")
        self.credits_tab = QWidget()
        self.credits_tab.setObjectName("settings_tabs")
        
        self.tabs.addTab(self.sound_tab, langue.langue_data["SettingsWindow__sound_tab__added_tab_title"])
        self.tabs.addTab(self.graphic_tab, langue.langue_data["SettingsWindow__graphic_tab__added_tab_title"])
        self.tabs.addTab(self.language_tab, langue.langue_data["SettingsWindow__langue_tab__added_tab_title"])
        self.tabs.addTab(self.credits_tab, langue.langue_data["SettingsWindow__credits_tab__added_tab_title"])
    
    def setup_sound_tab(self):
        """Setup the sound tab"""
        # Sound tab
        self.sound_layout = QGridLayout(self.sound_tab)
        self.sound_button = ClickButton(langue.langue_data["SettingsWindow__sound_button__text"], self.sound_tab)
        self.sound_button.setObjectName("sound_button")
        self.sound_button.clicked.connect(self.global_mute)
        self.sound_slider = ClickedSlider(Qt.Horizontal, self.sound_tab)
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
        self.musique_slider = ClickedSlider(Qt.Horizontal, self)
        self.musique_slider.setObjectName("sound_slider")
        self.musique_slider.setMinimum(0)
        self.musique_slider.setMaximum(100)
        self.musique_slider.setValue(int(settings.sound_global_data[1][1]))
        self.musique_slider.valueChanged.connect(self.set_music_volume)
        # Ambiance
        self.ambiance_button = ClickButton(langue.langue_data["SettingsWindow__ambiance_button__text"], self)
        self.ambiance_button.setObjectName("ambiance_button")
        self.ambiance_button.clicked.connect(ambiance_sound.sound_effects.mute_sound_effects)
        self.ambiance_button.clicked.connect(lambda: self.check_sound_effects_muted(self.ambiance_button, 2))
        self.ambiance_slider = ClickedSlider(Qt.Horizontal, self)
        self.ambiance_slider.setObjectName("sound_slider")
        self.ambiance_slider.setMinimum(0)
        self.ambiance_slider.setMaximum(100)
        self.ambiance_slider.setValue(int(settings.sound_global_data[2][1]))
        self.ambiance_slider.valueChanged.connect(self.set_ambiance_volume)
        # Boutons
        self.boutons_button = ClickButton(langue.langue_data["SettingsWindow__boutons_button__text"], self)
        self.boutons_button.setObjectName("boutons_button")
        self.boutons_button.clicked.connect(button_sound.sound_effects.mute_sound_effects)
        self.boutons_button.clicked.connect(lambda: self.check_sound_effects_muted(self.boutons_button, 3))
        self.boutons_slider = ClickedSlider(Qt.Horizontal, self)
        self.boutons_slider.setObjectName("sound_slider")
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
        """
        Set up the graphic tab.
        """
        self.graphic_layout = QVBoxLayout(self.graphic_tab)
        
        self.theme_widget1 = QWidget()
        self.theme_layout1 = QHBoxLayout(self.theme_widget1)

        self.theme_widget2 = QWidget()
        self.theme_layout2 = QHBoxLayout(self.theme_widget2)

        self.theme_label = QLabel(langue.langue_data["SettingsWindow__theme_label__text"], self.graphic_tab)
        self.theme_label.setObjectName("settings_title_labels")
        self.theme_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.theme_paradis_button = ClickButton(langue.langue_data["Settings_theme_paradis_button__text"], self.graphic_tab)
        self.theme_paradis_button.setObjectName("theme_paradis_button")
        self.theme_paradis_button.clicked.connect(lambda: self.set_color_theme("#fec2ff", "#7bf8fc"))

        self.theme_aurore_button = ClickButton(langue.langue_data["Settings_theme_aurore_button__text"], self.graphic_tab)
        self.theme_aurore_button.setObjectName("theme_aurore_button")
        self.theme_aurore_button.clicked.connect(lambda: self.set_color_theme("#b7ffc7", "#8ccaff"))

        self.theme_crepuscule_button = ClickButton(langue.langue_data["Settings_theme_crepuscule_button__text"], self.graphic_tab)
        self.theme_crepuscule_button.setObjectName("theme_crepuscule_button")
        self.theme_crepuscule_button.clicked.connect(lambda: self.set_color_theme("#ffcb9e", "#e4b7ff"))

        self.theme_magma_button = ClickButton(langue.langue_data["Settings_theme_magma_button__text"], self.graphic_tab)
        self.theme_magma_button.setObjectName("theme_magma_button")
        self.theme_magma_button.clicked.connect(lambda: self.set_color_theme("#ff9898", "#ffde8f"))

        self.theme_canard_button = ClickButton(langue.langue_data["Settings_theme_canard_button__text"], self.graphic_tab)
        self.theme_canard_button.setObjectName("theme_canard_button")
        self.theme_canard_button.clicked.connect(lambda: self.set_color_theme("#22c1c3", "#fdbb2d"))

        self.theme_nuage_button = ClickButton(langue.langue_data["Settings_theme_nuage_button__text"], self.graphic_tab)
        self.theme_nuage_button.setObjectName("theme_nuage_button")
        self.theme_nuage_button.clicked.connect(lambda: self.set_color_theme("#a8a8e7", "#c6eefe"))

        self.theme_vacances_button = ClickButton(langue.langue_data["Settings_theme_vacances_button__text"], self.graphic_tab)
        self.theme_vacances_button.setObjectName("theme_vacances_button")
        self.theme_vacances_button.clicked.connect(lambda: self.set_color_theme("#fcffd7", "#abffed"))

        self.theme_toutou_button = ClickButton(langue.langue_data["Settings_theme_toutou_button__text"], self.graphic_tab)
        self.theme_toutou_button.setObjectName("theme_toutou_button")
        self.theme_toutou_button.clicked.connect(lambda: self.set_color_theme("#a7a5ff", "#ffd1da"))

        self.animations_label = QLabel(langue.langue_data["SettingsWindow__animations_label__text"], self.graphic_tab)
        self.animations_label.setObjectName("settings_title_labels")
        self.animations_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.deactivate_widget = QWidget()
        self.deactivate_layout = QGridLayout(self.deactivate_widget)
        self.deactivate_button = StyledButton(langue.langue_data["SettingsWindow__deactivate_button__text"], self, button_width=0.6, color1="#7fc0df")
        self.deactivate_button.setObjectName("deactivate_button")
        self.deactivate_button.clicked.connect(self.deactivate_effects)

        self.animations_checkbox = ClickedCheckbox(langue.langue_data["SettingsWindow__animations_checkbox__text"], self.graphic_tab)
        self.animations_checkbox.setObjectName("effects_checkboxes") 
        if sys.platform == "win32":
            self.animations_checkbox.setStyleSheet(f'''QCheckBox#effects_checkboxes::indicator:checked{{border-image: url({os.path.join(image_path, "ready.png").replace("\\", "/")}); background-color: rgba(255, 255, 255, 72)}}''')
        else:
            self.animations_checkbox.setStyleSheet(f'''QCheckBox#effects_checkboxes::indicator:checked{{border-image: url({os.path.join(image_path, "ready.png")}); background-color: rgba(255, 255, 255, 72)}}''')
        self.animations_checkbox.clicked.connect(self.set_animations)
        self.border_checkbox = ClickedCheckbox(langue.langue_data["SettingsWindow__border_checkbox__text"], self.graphic_tab)
        self.border_checkbox.setObjectName("effects_checkboxes")
        if sys.platform == "win32":
            self.border_checkbox.setStyleSheet(f'''QCheckBox#effects_checkboxes::indicator:checked{{border-image: url({os.path.join(image_path, "ready.png").replace("\\", "/")}); background-color: rgba(255, 255, 255, 72)}}''')
        else:
            self.border_checkbox.setStyleSheet(f'''QCheckBox#effects_checkboxes::indicator:checked{{border-image: url({os.path.join(image_path, "ready.png")}); background-color: rgba(255, 255, 255, 72)}}''')
        self.border_checkbox.clicked.connect(self.set_borders)

        self.theme_layout1.addWidget(self.theme_paradis_button)
        self.theme_layout1.addWidget(self.theme_aurore_button)
        self.theme_layout1.addWidget(self.theme_crepuscule_button)
        self.theme_layout1.addWidget(self.theme_magma_button)
        self.theme_layout2.addWidget(self.theme_canard_button)
        self.theme_layout2.addWidget(self.theme_nuage_button)
        self.theme_layout2.addWidget(self.theme_vacances_button)
        self.theme_layout2.addWidget(self.theme_toutou_button)

        self.deactivate_layout.addWidget(self.deactivate_button, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        self.graphic_layout.addWidget(self.theme_label, Qt.AlignmentFlag.AlignCenter)
        self.graphic_layout.addWidget(self.theme_widget1)
        self.graphic_layout.addWidget(self.theme_widget2)
        self.graphic_layout.addWidget(self.animations_label, Qt.AlignmentFlag.AlignCenter)
        self.graphic_layout.addWidget(self.animations_checkbox)
        self.graphic_layout.addWidget(self.border_checkbox)
        self.graphic_layout.addWidget(self.deactivate_widget)
    
    def setup_language_tab(self):
        """
        Set up the language tab.
        """
        self.language_layout = QVBoxLayout(self.language_tab)

        self.language_label = QLabel(langue.langue_data["SettingsWindow__language_label__text"], self.language_tab)
        self.language_label.setObjectName("settings_title_labels")
        self.language_label.setFixedHeight(int(self.height() // 4))
        self.language_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.language_combobox = QComboBox(self.language_tab)
        self.language_combobox.setCursor(Qt.PointingHandCursor)
        self.language_combobox.setObjectName("language_combobox")
        self.language_combobox.addItems(["Français", "English", "Deutsch", "Español"])
        index_language: int = self.language_combobox.findText(settings.accessibility_data[1][1], Qt.MatchFixedString)
        self.language_combobox.setCurrentIndex(index_language)
        if sys.platform == "win32":
            self.language_combobox.setStyleSheet(f'''QComboBox#language_combobox::down-arrow{{border-image: url({os.path.join(image_path, "arrow.png").replace("\\", "/")}); width: 25; height: 25; margin-right: 15;}}''')
        else:
            self.language_combobox.setStyleSheet(f'''QComboBox#language_combobox::down-arrow{{border-image: url({os.path.join(image_path, "arrow.png")}); width: 25; height: 25; margin-right: 15;}}''')
        self.language_combobox.currentIndexChanged.connect(self.change_language)

        self.language_help_label = QLabel(langue.langue_data["SettingsWindow__language_help_label__text"], self.language_tab)
        self.language_help_label.setObjectName("settings_help_label")
        self.language_help_label.setOpenExternalLinks(True)
        self.language_help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.language_layout.addWidget(self.language_label)
        self.language_layout.addWidget(self.language_combobox)
        self.language_layout.addWidget(self.language_help_label)

    def setup_credits_tab(self):
        """
        Set up the credits tab.
        """
        self.credits_layout = QVBoxLayout(self.credits_tab)
        
        self.credits_developer_label = QLabel(langue.langue_data["SettingsWindow__credits_developer_label__text"], self.credits_tab)
        self.credits_developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.credits_dev_link_label = QLabel(self.credits_tab)
        self.credits_dev_link_label.setObjectName("link_label")
        self.credits_dev_link_label.setText(f"<a href='https://missclick.net'>{langue.langue_data["SettingsWindow__credits_developer_link_label__text"]}</a><br>")
        self.credits_dev_link_label.setOpenExternalLinks(True)
        self.credits_dev_link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.credits_graphic_designer_label = QLabel(langue.langue_data["SettingsWindow__credits_graphic_designer_label__text"], self.credits_tab)
        self.credits_graphic_designer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        self.credits_gra_link_label = QLabel(self.credits_tab)
        self.credits_gra_link_label.setObjectName("link_label")
        self.credits_gra_link_label.setText(f"<a href='https://linktr.ee/Jellyfishyu'>{langue.langue_data['SettingsWindow__credits_graphic_designer_link_label__text']}</a><br>")
        self.credits_gra_link_label.setOpenExternalLinks(True)
        self.credits_gra_link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.credits_remerciments_label = QLabel(langue.langue_data["SettingsWindow__credits_remerciments_label__text"], self.credits_tab)
        self.credits_remerciments_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.credits_music_widget = QWidget()
        self.credits_music_layout = QHBoxLayout(self.credits_music_widget)

        self.credits_music_title_label1 = QLabel(langue.langue_data["SettingsWindow__credits_music_title_label1__text"], self.credits_tab)
        self.credits_music_title_label1.setOpenExternalLinks(True)
        self.credits_music_title_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.credits_music_title_label2 = QLabel(langue.langue_data["SettingsWindow__credits_music_title_label2__text"], self.credits_tab)
        self.credits_music_title_label2.setOpenExternalLinks(True)
        self.credits_music_title_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.credits_music_title_label3 = QLabel(langue.langue_data["SettingsWindow__credits_music_title_label3__text"], self.credits_tab)
        self.credits_music_title_label3.setOpenExternalLinks(True)
        self.credits_music_title_label3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.credits_music_layout.addWidget(self.credits_music_title_label1)
        self.credits_music_layout.addWidget(self.credits_music_title_label2)
        self.credits_music_layout.addWidget(self.credits_music_title_label3)

        self.credits_layout.addWidget(self.credits_developer_label)
        self.credits_layout.addWidget(self.credits_dev_link_label)
        self.credits_layout.addWidget(self.credits_graphic_designer_label)
        self.credits_layout.addWidget(self.credits_gra_link_label)
        self.credits_layout.addWidget(self.credits_remerciments_label)
        self.credits_layout.addWidget(self.credits_music_widget)

    def change_language(self):
        """
        Change the language.
        """
        language = self.language_combobox.currentText()
        settings.accessibility.change_langue(language)
        self.setup_restart_window()

    def global_mute(self):
        """
        Mute the global sound.
        """
        music.mute_music()
        if settings.sound_global_data[0][2] == "notmuted":
            settings.sound_global_data[0][2] = "muted"
        else:
            settings.sound_global_data[0][2] = "notmuted"
        settings.write_settings(
            concern=settings.sound_global_data[0][0], 
            data=settings.sound_global_data[0][1], 
            mute=settings.sound_global_data[0][2],
            file="user_sound_global.csv"
        )
        button_sound.sound_effects.mute_sound_effects()
        ambiance_sound.sound_effects.mute_sound_effects()
        self.check_music_muted(self.musique_button)
        self.check_sound_effects_muted(self.sound_button, 0)
        self.check_sound_effects_muted(self.ambiance_button, 2)
        self.check_sound_effects_muted(self.boutons_button, 3)

    def set_global_volume(self):
        """
        Set the global volume.
        """
        settings.sound_global_data[0][1] = self.sound_slider.value()
        self.musique_slider.setValue(self.sound_slider.value())
        self.ambiance_slider.setValue(self.sound_slider.value())
        self.boutons_slider.setValue(self.sound_slider.value())
        settings.write_settings(
            concern=settings.sound_global_data[0][0], 
            data=settings.sound_global_data[0][1], 
            mute=settings.sound_global_data[0][2],
            file="user_sound_global.csv"
        )
        
    def set_music_volume(self):
        """
        Set the music volume.
        """
        music.change_volume(self.musique_slider.value())
    
    def set_sound_effects_volume(self):
        """
        Set the sound effects volume.
        """
        button_sound.sound_effects.change_volume(self.boutons_slider.value())

    def set_ambiance_volume(self):
        """
        Set the ambiance volume.
        """
        ambiance_sound.sound_effects.change_volume(self.ambiance_slider.value())

    def check_music_muted(self, object: object):
        """
        Check if the music is muted.

        Args:
            object (object): The object to check.
        """
        if music.player.isMuted():
            object.setStyleSheet("background-color: red;")
        else:
            object.setStyleSheet("background-color: green;")

    def check_sound_effects_muted(self, object: object, ligne: int):
        """
        Check if the sound effects are muted.

        Args:
            object (object): The object to check.
            ligne (int): The line number to check.
        """
        if settings.sound_global_data[ligne][2] == "muted":
            object.setStyleSheet("background-color: red;")
        else:
            object.setStyleSheet("background-color: green;")

    def set_color_theme(self, color1: str, color2: str):
        """
        Change the color theme.

        Args:
            color1 (str): The primary color of the theme.
            color2 (str): The secondary color of the theme.
        """
        settings.accessibility.change_theme(color1, color2)
        
        self.clientObject.color1 = QColor(*self.clientObject.hex_to_rgb(color1))
        self.clientObject.color2 = QColor(*self.clientObject.hex_to_rgb(color2))

    def deactivate_effects(self):
        """
        Deactivate the effects.
        """
        settings.accessibility.change_animations("no")
        self.animations_checkbox.setChecked(True)
        settings.accessibility.change_borders("no")
        self.border_checkbox.setChecked(True)
        self.deactivate_button.setEnabled(False)

    def set_animations(self):
        """
        Enable or disable animations.
        """
        if self.animations_checkbox.isChecked():
            settings.accessibility.change_animations("no")
        else:
            settings.accessibility.change_animations("yes")
        self.deactivate_button.setEnabled(True)
    
    def set_borders(self):
        """
        Enable or disable borders.
        """
        if self.border_checkbox.isChecked():
            settings.accessibility.change_borders("no")
        else:
            settings.accessibility.change_borders("yes")
        self.deactivate_button.setEnabled(True)

    def check_effects(self):
        """
        Check the effects.
        """
        if settings.accessibility_data[2][1] == "no":
            self.animations_checkbox.setChecked(True)
        else:
            self.animations_checkbox.setChecked(False)
        if settings.accessibility_data[3][1] == "no":
            self.border_checkbox.setChecked(True)
        else:
            self.border_checkbox.setChecked(False)
        if settings.accessibility_data[2][1] == "no" and settings.accessibility_data[3][1] == "no":
            self.deactivate_button.setEnabled(False)
        else:
            self.deactivate_button.setEnabled(True)
    
    def reset_settings(self):
        """
        Reset the settings.
        """
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
        self.check_effects()
        self.set_color_theme("#fec2ff", "#7bf8fc")
        self.language_combobox.setCurrentIndex(self.language_combobox.findText(settings.accessibility_data[1][1], Qt.MatchFixedString))

    def setup_restart_window(self):
        """
        Set up the restart window.
        """
        self.restart_window = RestartWindow(self.clientObject)
        self.restart_window.show()
        self.restart_window.activateWindow()

class VictoryWindow(ToolMainWindow):
    """Victory Window"""
    
    def __init__(self, parent: object, classement: list[list[str]]):
        """
        Initialize the victory window.

        Args:
            parent (object): The parent object.
            classement (list[list[str]]): The ranking list.
        """
        super(VictoryWindow, self).__init__()
        self.client_object = parent
        self.classement = classement
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        self.complete_list()
        self.setup()
        self.show()
        ambiance_sound.sound_effects.victory_sound.play()
    
    def complete_list(self):
        """
        Complete the player list.
        """
        for i in range(8):
            if i >= len(self.classement):
                self.classement.append(["...", None])

    def setup(self):
        """
        Set up the victory window.
        """
        self.setup_widgets()
        self.setup_classement()
        self.setup_layouts()
        self.setCentralWidget(self.central_widget)

    def setup_widgets(self):
        """
        Set up the widgets for the victory window.
        """
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
        """
        Set up the ranking for the victory window.
        """
        self.avatar_winner = QPixmap(f"{avatar_path}{self.classement[0][1]}.png")
        self.avatar_label = QLabel()
        self.avatar_label.setMinimumSize(screen_width // 4, screen_width // 4)
        self.avatar_label.setObjectName("avatar_label_victory")
        self.avatar_label.setPixmap(self.avatar_winner.scaled(self.avatar_label.size(), Qt.KeepAspectRatio))
        self.avatar_label.setAlignment(Qt.AlignCenter)

        self.winner_label = QLabel(f"{self.classement[0][0]}{langue.langue_data['VictoryWindow__winner_label__text']}")
        self.winner_label.setObjectName("winner_label")
        self.winner_label.setAlignment(Qt.AlignCenter)

        self.first_label = QLabel(f"🥇 {self.classement[0][0]}")
        self.first_label.setObjectName("podium_label")
        font = QFont()
        font.setPointSize(25)  # Set the font size to 25pt
        self.first_label.setFont(font)  # Set the font for the label
        width = self.first_label.fontMetrics().width('A' * 22)  # Calculate the width of 25 characters
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
        """
        Set up the layouts for the victory window.
        """
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
        """
        Handle double-click event to close the window.

        Args:
            a0 (QMouseEvent | None): The mouse event.
        """
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press event to close the window.

        Args:
            event (QKeyEvent): The key event.
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Space:
            self.close()
        return super().keyPressEvent(event)
    
    def closeEvent(self, event: QEvent) -> None:
        """
        Handle the window close event.

        Args:
            event (QEvent): The close event.
        """
        self.client_object.reset_avatars()
        event.accept()

class FilterWindow(ToolMainWindow):
    """Filter Window
    
    Attributes:
        client_object (object): The parent object."""
    def __init__(self, client_object: object):
        """
        Initialize the filter window.

        Args:
            client_object (object): The parent object.
        """
        super(FilterWindow, self).__init__()
        self.client_object = client_object
        self.setWindowTitle(langue.langue_data["FilterWindow__text"])
        self.setObjectName("filter_window")
        self.resize(int(screen_width // 3.5), int(screen_height // 3.5))
        center_window(self)
        self.setStyleSheet(windows_stylesheet)
        self.setup()

    def setup(self):
        """
        Set up the filter window.
        """
        self.central_widget = QWidget()
        self.central_widget.setObjectName("filter_widget")
        self.filter_layout = QVBoxLayout(self.central_widget)

        self.filter_label = LinearGradiantLabel(langue.langue_data["FilterWindow__filter_label__text"], color1=QColor(84,58,180,255), color2=QColor(253,89,29,255))
        self.filter_label.setObjectName("filter_label")
        self.filter_label.setAlignment(Qt.AlignCenter)

        self.filter_widget = QWidget()
        self.filter_widget_layout = QHBoxLayout(self.filter_widget)

        self.filter_line = UnderlineLineEdit()
        self.filter_line.setObjectName("filter_lineedit")
        self.filter_line.setMaxLength(20)
        self.filter_line.setFixedWidth(self.filter_line.sizeHint().width() * 3)
        if self.client_object.filter and self.client_object.filter != "" and not self.client_object.filter.isspace():
            self.filter_line.setText(self.client_object.filter)
        self.filter_line.setPlaceholderText(langue.langue_data["FilterWindow__filter_lineedit__placeholder"])
        self.filter_line.returnPressed.connect(self.filter)

        self.remove_icon = QPixmap(f"{image_path}remove.png")
        self.remove_icon_hover = QPixmap(f"{image_path}remove-hover.png")
        self.remove_filter_button = HoverPixmapButton(self.remove_icon, self.remove_icon_hover)
        self.remove_filter_button.setFixedSize(self.filter_line.sizeHint().height(), self.filter_line.sizeHint().height())
        self.remove_filter_button.setObjectName("other_buttons")
        self.remove_filter_button.setIcon(QIcon(self.remove_icon))
        self.remove_filter_button.setIconSize(self.remove_filter_button.size())
        self.remove_filter_button.clicked.connect(lambda: self.filter_line.clear())

        self.filter_button = StyledButton(langue.langue_data["FilterWindow__filter_button__text"], self, button_height=0.25, color1="#6f85e2", color2="#d26d9e")
        self.filter_button.setObjectName("filter_button")
        self.filter_button.clicked.connect(self.filter)

        # Add the line edit and remove button to the horizontal layout
        self.filter_widget_layout.addWidget(self.filter_line)
        self.filter_widget_layout.addWidget(self.remove_filter_button)
        self.filter_widget_layout.setStretch(0, 1)  # The line edit takes the most space
        self.filter_widget_layout.setStretch(1, 0)  # The button takes the least space

        self.filter_layout.addWidget(self.filter_label)
        self.filter_layout.addWidget(self.filter_widget)
        self.filter_layout.addWidget(self.filter_button, alignment=Qt.AlignCenter)
        self.setCentralWidget(self.central_widget)

    def filter(self):
        """
        Filter the games.
        """
        self.client_object.filter = self.filter_line.text()
        self.client_object.filter_games(self.filter_line.text())
        self.close()