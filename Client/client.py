import sys, socket, threading, time, random, os
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
        receiver_thread.game_signal.connect(self.game_tools)

    def game_tools(self, game_message):
        reply = game_message.split("|")
        print(reply, reply[1])
        if reply[1] == "GAME_ENDED":
            try:
                self.unsetup_game()
            except Exception as e:
                print(e)
            print("Game ended")
        elif reply[1] == "TIME'S_UP":
            if reply[2] == username:
                self.remove_heart()

        elif reply[1] == "WRONG":
            self.syllable_label.clear()
            self.syllable_label.setText("❌")
        
        elif reply[1] == "RIGHT":
            self.syllable_label.clear()
            self.syllable_label.setText("✅")
    
    def remove_heart(self):
        """remove_heart() : Enlève un coeur au joueur"""
        global username
        if username == self.player1_label.text():
            self.heart_list_widget1.takeItem(self.heart_list_widget1.count() - 1)
        elif username == self.player2_label.text():
            self.heart_list_widget2.takeItem(self.heart_list_widget2.count() - 1)
        elif username == self.player3_label.text():
            self.heart_list_widget3.takeItem(self.heart_list_widget3.count() - 1)
        elif username == self.player4_label.text():
            self.heart_list_widget4.takeItem(self.heart_list_widget4.count() - 1)
        elif username == self.player5_label.text():
            self.heart_list_widget5.takeItem(self.heart_list_widget5.count() - 1)
        elif username == self.player6_label.text():
            self.heart_list_widget6.takeItem(self.heart_list_widget6.count() - 1)
        elif username == self.player7_label.text():
            self.heart_list_widget7.takeItem(self.heart_list_widget7.count() - 1)
        elif username == self.player8_label.text():
            self.heart_list_widget8.takeItem(self.heart_list_widget8.count() - 1)

    def unsetup_game(self):
        """unsetup_game() : Reset les éléments de la partie"""
        self.start_button.setEnabled(False)
        self.ready_button.setEnabled(True)
        self.rules_button.setEnabled(True)
        try:
            self.clear_game()
        except Exception as e:
            print(e)

    def clear_game(self):
        """clear_game() : Efface les éléments de la fenêtre de jeu"""
        self.text_label.clear()
        self.syllable_label.clear()
        self.text_line_edit.clear()
        self.heart_list_widget1.clear()
        self.heart_list_widget2.clear()
        self.heart_list_widget3.clear()
        self.heart_list_widget4.clear()
        self.heart_list_widget5.clear()
        self.heart_list_widget6.clear()
        self.heart_list_widget7.clear()
        self.heart_list_widget8.clear()

    def setup_game(self, layout):
        """setup_game(layout) : Mise en place de la fenêtre de jeu
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale"""
        global username
        self.create_game()

        layout.removeWidget(self.create_game_button)
        layout.removeWidget(self.join_game)

        self.player1_label = QLabel(username, self)
        self.player2_label = QLabel("Joueur 2", self)
        self.player3_label = QLabel("Joueur 3", self)
        self.player4_label = QLabel("Joueur 4", self)
        self.player5_label = QLabel("Joueur 5", self)
        self.player6_label = QLabel("Joueur 6", self)
        self.player7_label = QLabel("Joueur 7", self)
        self.player8_label = QLabel("Joueur 8", self)

        self.setup_heart_layout()
        self.setup_hearts_widget()
        self.setup_label()

        self.heart_layout.addWidget(self.heart_list_widget1, 0, 0, Qt.AlignHCenter)
        self.heart_layout2.addWidget(self.heart_list_widget2, 0, 0, Qt.AlignHCenter)
        self.heart_layout3.addWidget(self.heart_list_widget3, 0, 0, Qt.AlignHCenter)
        self.heart_layout4.addWidget(self.heart_list_widget4, 0, 0, Qt.AlignHCenter)
        self.heart_layout5.addWidget(self.heart_list_widget5, 0, 0, Qt.AlignHCenter)
        self.heart_layout6.addWidget(self.heart_list_widget6, 0, 0, Qt.AlignHCenter)
        self.heart_layout7.addWidget(self.heart_list_widget7, 0, 0, Qt.AlignHCenter)
        self.heart_layout8.addWidget(self.heart_list_widget8, 0, 0, Qt.AlignHCenter)

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

        layout.addWidget(self.player1_widget, 1, 0, Qt.AlignLeft)
        layout.addWidget(self.player2_widget, 1, 1, Qt.AlignHCenter)
        layout.addWidget(self.player3_widget, 1, 2, Qt.AlignRight)
        layout.addWidget(self.player4_widget, 2, 0, Qt.AlignLeft)
        layout.addWidget(self.text_widget, 2, 1, Qt.AlignHCenter)
        layout.addWidget(self.player5_widget, 2, 2, Qt.AlignRight)
        layout.addWidget(self.player6_widget, 3, 0, Qt.AlignLeft)
        layout.addWidget(self.player7_widget, 3, 1, Qt.AlignCenter)
        layout.addWidget(self.player8_widget, 3, 2, Qt.AlignRight)

        self.player1_layout.addWidget(self.player1_label, 0, Qt.AlignHCenter)
        self.player2_layout.addWidget(self.player2_label, 0, Qt.AlignHCenter)
        self.player3_layout.addWidget(self.player3_label, 0, Qt.AlignHCenter)
        self.player4_layout.addWidget(self.player4_label, 0, Qt.AlignHCenter)
        self.player5_layout.addWidget(self.player5_label, 0, Qt.AlignHCenter)
        self.player6_layout.addWidget(self.player6_label, 0, Qt.AlignHCenter)
        self.player7_layout.addWidget(self.player7_label, 0, Qt.AlignHCenter)
        self.player8_layout.addWidget(self.player8_label, 0, Qt.AlignHCenter)

        self.player1_layout.addWidget(self.heart_widget_player1)
        self.player2_layout.addWidget(self.heart_widget_player2)
        self.player3_layout.addWidget(self.heart_widget_player3)
        self.player4_layout.addWidget(self.heart_widget_player4)
        self.player5_layout.addWidget(self.heart_widget_player5)
        self.player6_layout.addWidget(self.heart_widget_player6)
        self.player7_layout.addWidget(self.heart_widget_player7)
        self.player8_layout.addWidget(self.heart_widget_player8)

        self.home_button = QPushButton("Home", self)
        self.home_button.setObjectName("home_pushbutton")
        self.home_button.clicked.connect(self.delete_game)
        
        self.private_button = QPushButton("Private", self)
        self.private_button.setObjectName("private_pushbutton")

        self.password_linedit = QLineEdit(self)
        self.password_linedit.setObjectName("password_linedit")
        self.password_linedit.setPlaceholderText("Mot de passe")
        self.password_linedit.setEchoMode(QLineEdit.Password)

        self.show_password_button = QPushButton("🔑", self)
        self.show_password_button.setObjectName("show_password_pushbutton")
        self.show_password_button.clicked.connect(self.show_password)

        self.rules_button = QPushButton("Règles", self)
        self.rules_button.setObjectName("rules_pushbutton")
        self.rules_button.clicked.connect(self.display_rules)

        self.ready_button = QPushButton("Ready", self)
        self.ready_button.setObjectName("ready_pushbutton")
        self.ready_button.setEnabled(True)
        self.ready_button.clicked.connect(self.ready)

        self.start_button = QPushButton("Start", self)
        self.start_button.setObjectName("start_pushbutton")
        self.start_button.clicked.connect(self.start_game)
        self.start_button.setEnabled(False)
        
        layout.addWidget(self.home_button, 0, 0, Qt.AlignLeft)
        layout.addWidget(self.private_button, 0, 1, Qt.AlignHCenter)
        self.password_layout = QHBoxLayout()
        self.password_layout.addWidget(self.password_linedit)
        self.password_layout.addWidget(self.show_password_button)
        self.show_password_button.setFixedWidth(20)
        
        layout.addLayout(self.password_layout, 0, 2, Qt.AlignRight)
        layout.addWidget(self.rules_button, 4, 0, Qt.AlignLeft)
        layout.addWidget(self.ready_button, 4, 1)
        layout.addWidget(self.start_button, 4, 2, Qt.AlignRight)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def show_password(self):
        """show_password() : Affiche le mot de passe"""
        if self.password_linedit.echoMode() == QLineEdit.Password:
            self.password_linedit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_linedit.setEchoMode(QLineEdit.Password)

    def setup_heart_layout(self):
        """setup_heart_layout() : Mise en place des coeurs des joueurs"""
        self.coeur = QPixmap("./Client/images/coeur-resized.png")
        self.heart_layout = QGridLayout()
        self.heart_widget_player1 = QWidget()
        self.heart_widget_player1.setObjectName("heart_widget")
        self.heart_widget_player1.setLayout(self.heart_layout)

        self.heart_layout2 = QGridLayout()
        self.heart_widget_player2 = QWidget()
        self.heart_widget_player2.setObjectName("heart_widget2")
        self.heart_widget_player2.setLayout(self.heart_layout2)

        self.heart_layout3 = QGridLayout()
        self.heart_widget_player3 = QWidget()
        self.heart_widget_player3.setObjectName("heart_widget3")
        self.heart_widget_player3.setLayout(self.heart_layout3)

        self.heart_layout4 = QGridLayout()
        self.heart_widget_player4 = QWidget()
        self.heart_widget_player4.setObjectName("heart_widget4")
        self.heart_widget_player4.setLayout(self.heart_layout4)

        self.heart_layout5 = QGridLayout()
        self.heart_widget_player5 = QWidget()
        self.heart_widget_player5.setObjectName("heart_widget5")
        self.heart_widget_player5.setLayout(self.heart_layout5)

        self.heart_layout6 = QGridLayout()
        self.heart_widget_player6 = QWidget()
        self.heart_widget_player6.setObjectName("heart_widget6")
        self.heart_widget_player6.setLayout(self.heart_layout6)

        self.heart_layout7 = QGridLayout()
        self.heart_widget_player7 = QWidget()
        self.heart_widget_player7.setObjectName("heart_widget7")
        self.heart_widget_player7.setLayout(self.heart_layout7)

        self.heart_layout8 = QGridLayout()
        self.heart_widget_player8 = QWidget()
        self.heart_widget_player8.setObjectName("heart_widget8")
        self.heart_widget_player8.setLayout(self.heart_layout8)

    def setup_label(self):
        """setup_label() : Mise en place des labels des joueurs"""
        self.player1_widget = QWidget()
        self.player1_widget.setObjectName("player1_widget")
        self.player1_layout = QVBoxLayout()
        self.player1_widget.setLayout(self.player1_layout)

        self.player2_widget = QWidget()
        self.player2_widget.setObjectName("player2_widget")
        self.player2_layout = QVBoxLayout()
        self.player2_widget.setLayout(self.player2_layout)

        self.player3_widget = QWidget()
        self.player3_widget.setObjectName("player3_widget")
        self.player3_layout = QVBoxLayout()
        self.player3_widget.setLayout(self.player3_layout)

        self.player4_widget = QWidget()
        self.player4_widget.setObjectName("player4_widget")
        self.player4_layout = QVBoxLayout()
        self.player4_widget.setLayout(self.player4_layout)

        self.player5_widget = QWidget()
        self.player5_widget.setObjectName("player5_widget")
        self.player5_layout = QVBoxLayout()
        self.player5_widget.setLayout(self.player5_layout)

        self.player6_widget = QWidget()
        self.player6_widget.setObjectName("player6_widget")
        self.player6_layout = QVBoxLayout()
        self.player6_widget.setLayout(self.player6_layout)

        self.player7_widget = QWidget()
        self.player7_widget.setObjectName("player7_widget")
        self.player7_layout = QVBoxLayout()
        self.player7_widget.setLayout(self.player7_layout)

        self.player8_widget = QWidget()
        self.player8_widget.setObjectName("player8_widget")
        self.player8_layout = QVBoxLayout()
        self.player8_widget.setLayout(self.player8_layout)

    def setup_hearts_widget(self):
        """setup_hearts_widget() : Mise en place des coeurs des joueurs"""
        self.heart_list_widget1 = QListWidget()
        self.heart_list_widget1.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget1.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget1.setSpacing(5)
        self.heart_list_widget1.setFixedSize(103, 20)
        self.heart_list_widget1.setObjectName("heart_list_widget1")
        self.heart_list_widget1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget2 = QListWidget()
        self.heart_list_widget2.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget2.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget2.setSpacing(5)
        self.heart_list_widget2.setFixedSize(103, 20)
        self.heart_list_widget2.setObjectName("heart_list_widget2")
        self.heart_list_widget2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget3 = QListWidget()
        self.heart_list_widget3.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget3.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget3.setSpacing(5)
        self.heart_list_widget3.setFixedSize(103, 20)
        self.heart_list_widget3.setObjectName("heart_list_widget3")
        self.heart_list_widget3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget3.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget4 = QListWidget()
        self.heart_list_widget4.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget4.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget4.setSpacing(5)
        self.heart_list_widget4.setFixedSize(103, 20)
        self.heart_list_widget4.setObjectName("heart_list_widget4")
        self.heart_list_widget4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget4.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget5 = QListWidget()
        self.heart_list_widget5.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget5.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget5.setSpacing(5)
        self.heart_list_widget5.setFixedSize(103, 20)
        self.heart_list_widget5.setObjectName("heart_list_widget5")
        self.heart_list_widget5.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget5.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget6 = QListWidget()
        self.heart_list_widget6.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget6.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget6.setSpacing(5)
        self.heart_list_widget6.setFixedSize(103, 20)
        self.heart_list_widget6.setObjectName("heart_list_widget6")
        self.heart_list_widget6.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget6.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget7 = QListWidget()
        self.heart_list_widget7.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget7.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget7.setSpacing(5)
        self.heart_list_widget7.setFixedSize(103, 20)
        self.heart_list_widget7.setObjectName("heart_list_widget7")
        self.heart_list_widget7.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget7.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget8 = QListWidget()
        self.heart_list_widget8.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget8.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget8.setSpacing(5)
        self.heart_list_widget8.setFixedSize(103, 20)
        self.heart_list_widget8.setObjectName("heart_list_widget8")
        self.heart_list_widget8.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget8.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setup_hearts_rules(self):
        for i in range(0, rules[2]):
            self.heart_label1 = QLabel()
            self.heart_label1.setPixmap(self.coeur)
            item1 = QListWidgetItem()
            item1.setSizeHint(self.heart_label1.sizeHint())
            self.heart_list_widget1.addItem(item1)
            self.heart_list_widget1.setItemWidget(item1, self.heart_label1)
        for i in range(0, rules[2]):
            self.heart_label2 = QLabel()
            self.heart_label2.setPixmap(self.coeur)
            item2 = QListWidgetItem()
            item2.setSizeHint(self.heart_label2.sizeHint())
            self.heart_list_widget2.addItem(item2)
            self.heart_list_widget2.setItemWidget(item2, self.heart_label2)
        for i in range(0, rules[2]):
            self.heart_label3 = QLabel()
            self.heart_label3.setPixmap(self.coeur)
            item3 = QListWidgetItem()
            item3.setSizeHint(self.heart_label3.sizeHint())
            self.heart_list_widget3.addItem(item3)
            self.heart_list_widget3.setItemWidget(item3, self.heart_label3)
        for i in range(0, rules[2]):
            self.heart_label4 = QLabel()
            self.heart_label4.setPixmap(self.coeur)
            item4 = QListWidgetItem()
            item4.setSizeHint(self.heart_label4.sizeHint())
            self.heart_list_widget4.addItem(item4)
            self.heart_list_widget4.setItemWidget(item4, self.heart_label4)
        for i in range(0, rules[2]):
            self.heart_label5 = QLabel()
            self.heart_label5.setPixmap(self.coeur)
            item5 = QListWidgetItem()
            item5.setSizeHint(self.heart_label5.sizeHint())
            self.heart_list_widget5.addItem(item5)
            self.heart_list_widget5.setItemWidget(item5, self.heart_label5)
        for i in range(0, rules[2]):
            self.heart_label6 = QLabel()
            self.heart_label6.setPixmap(self.coeur)
            item6 = QListWidgetItem()
            item6.setSizeHint(self.heart_label6.sizeHint())
            self.heart_list_widget6.addItem(item6)
            self.heart_list_widget6.setItemWidget(item6, self.heart_label6)
        for i in range(0, rules[2]):
            self.heart_label7 = QLabel()
            self.heart_label7.setPixmap(self.coeur)
            item7 = QListWidgetItem()
            item7.setSizeHint(self.heart_label7.sizeHint())
            self.heart_list_widget7.addItem(item7)
            self.heart_list_widget7.setItemWidget(item7, self.heart_label7)
        for i in range(0, rules[2]):
            self.heart_label8 = QLabel()
            self.heart_label8.setPixmap(self.coeur)
            item8 = QListWidgetItem()
            item8.setSizeHint(self.heart_label8.sizeHint())
            self.heart_list_widget8.addItem(item8)
            self.heart_list_widget8.setItemWidget(item8, self.heart_label8)

    def delete_game(self):
        """delete_game() : Supprime la partie"""
        error = QMessageBox(self)
        error.setWindowTitle("Quitter la partie")
        content = f"Êtes vous sûr de vouloir supprime votre partie ?"
        error.setText(content)
        ok_button = error.addButton(QMessageBox.Ok)
        ok_button.clicked.connect(lambda: self.setup(start=False))
        ok_button.clicked.connect(lambda: client_socket.send(f"DELETE_GAME|{username}".encode()))
        cancel_button = error.addButton(QMessageBox.Cancel)
        error.setIcon(QMessageBox.Warning)
        error.exec()

    def create_game(self):
        """create_game() : Crée une partie"""
        global username
        message = f"CREATE_GAME|{username}"
        client_socket.send(message.encode())

    def start_game(self):
        """start_game() : Lance la partie"""
        global username
        self.start_button.setEnabled(False)
        self.ready_button.setEnabled(False)
        self.rules_button.setEnabled(False)
        message = f"START_GAME|{username}|{rules[0]}|{rules[1]}|{rules[2]}|{rules[3]}"
        client_socket.send(message.encode())

        self.setup_hearts_rules()

    def ready(self):
        """ready() : Indique au serveur que le joueur est prêt"""
        global username
        if self.start_button.isEnabled():
            self.start_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)

        if self.rules_button.isEnabled():
            self.rules_button.setEnabled(False)
        else:
            self.rules_button.setEnabled(True)
        message = f"READY_TO_PLAY|{username}"
        client_socket.send(message.encode())

    def setup_join_game(self, layout):
        """setup_join_game(layout) : Mise en place de la fenêtre de jeu
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale"""
        layout.removeWidget(self.create_game_button)
        layout.removeWidget(self.join_game)

        layout = QVBoxLayout()

        self.home_button = QPushButton("Home", self)
        self.home_button.setObjectName("home_pushbutton")
        self.home_button.clicked.connect(lambda: self.setup(start=False))
        layout.addWidget(self.home_button)
        # Création du QListWidget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        receiver_thread.game_created.connect(self.add_item)
        receiver_thread.game_deleted.connect(self.delete_item)
        client_socket.send(f"GET_GAMES|{username}".encode())


    def display_sylb(self, sylb):
        """display_sylb(sylb) : Affiche la syllabe dans la fenêtre principale
        
        Args:
            sylb (str): Syllabe à afficher"""
        self.syllable_label.setText(sylb)

    def add_item(self, creator):
        """Ajoute un élément au QListWidget"""
        print("add item", creator)
        
        # Vérifier si l'objet existe déjà
        if not self.list_widget.findChild(QPushButton, creator):        
            self.join_game_pushbutton = QPushButton(f"Partie de {creator}")
            self.join_game_pushbutton.setObjectName(creator)
            item = QListWidgetItem(self.list_widget)
            item_widget = QWidget()
            item_layout = QGridLayout(item_widget)
            item_layout.addWidget(self.join_game_pushbutton)
            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)
        else:
            return
        
    def delete_item(self, creator):
        """delete_item(creator) : Supprime un élément du QListWidget
        
        Args:
            creator (str): Créateur de la partie"""
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            button = self.list_widget.itemWidget(item).findChild(QPushButton)
            if button.objectName() == creator:
                row = self.list_widget.row(item)
                self.list_widget.takeItem(row)
                break
        del item

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

    # def resizeEvent(self, event):
    #     """resizeEvent(event) : Redimensionne les éléments de la fenêtre principale"""
    #     font_size = min(self.width(), self.height()) // 30
    #     font = QFont("Arial", font_size)

    #     try:
    #         self.player1_label.setFont(font)
    #         self.player2_label.setFont(font)
    #         self.player3_label.setFont(font)
    #         self.player4_label.setFont(font)
    #         self.player5_label.setFont(font)
    #         self.player6_label.setFont(font)
    #         self.player7_label.setFont(font)
    #         self.player8_label.setFont(font)
    #         self.text_label.setFont(font)
    #         self.syllable_label.setFont(font)
    #     except AttributeError:
    #         pass

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
        self.timerulemin_spinbox.setMinimum(2)
        self.timerulemin_spinbox.setValue(rules[0])
        self.timerulemin_spinbox.valueChanged.connect(self.check_timerulemax)
        layout.addWidget(self.timerulemin_spinbox, 1, 0)

        self.timerulemax_label = QLabel("Temps maximum après explosion :", self)
        self.timerulemax_label.setFixedSize(300, 20) 
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
        self.lifes_label.setFixedSize(300, 20)
        layout.addWidget(self.lifes_label, 5, 0)

        self.lifes_spinbox = QSpinBox(self)
        self.lifes_spinbox.setObjectName("lifes_spinbox")
        self.lifes_spinbox.setMaximum(12)
        self.lifes_spinbox.setMinimum(1)
        self.lifes_spinbox.setValue(rules[2])
        layout.addWidget(self.lifes_spinbox, 6, 0)

        self.syllabes_spinbox = QSpinBox(self)
        self.syllabes_spinbox.setObjectName("syllabes_spinbox")
        self.syllabes_spinbox.setMaximum(5)
        self.syllabes_spinbox.setMinimum(1)
        self.syllabes_spinbox.setValue(rules[3])
        layout.addWidget(self.syllabes_spinbox, 7, 0)

        self.save_button = QPushButton("Enregistrer", self)
        self.save_button.setObjectName("enregistrer_pushbutton")
        self.save_button.clicked.connect(self.save_rules)

        layout.addWidget(self.save_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def check_timerulemax(self):
        """check_timerulemax() : Vérifie que le temps maximum est supérieur au temps minimum"""
        self.timerulemax_spinbox.setMinimum(self.timerulemin_spinbox.value() + 2)
        if self.timerulemax_spinbox.value() < self.timerulemin_spinbox.value() + 2:
            self.timerulemax_spinbox.setValue(self.timerulemin_spinbox.value() + 2)

    def save_rules(self):
        """send_rules() : Envoie les règles au serveur"""
        if self.timerulemax_spinbox.value() < self.timerulemin_spinbox.value() + 2:
            self.timerulemax_spinbox.setValue(self.timerulemin_spinbox.value() + 2)
        rules.clear()
        rules.extend([self.timerulemin_spinbox.value(), self.timerulemax_spinbox.value(), self.lifes_spinbox.value(), self.syllabes_spinbox.value()])
        print(rules)
        self.close()

if __name__ == "__main__":
    """__main__() : Lance l'application"""
    app = QApplication(sys.argv)
    window = ClientWindow(start = True)
    login = Login()
    login.show()
    sys.exit(app.exec_())
