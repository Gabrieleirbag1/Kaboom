from client_utils import *
from client_styles import AvatarBorderBox, AnimatedButton, AnimatedWindow, AnimatedGameWidget, ButtonBorderBox, LinearGradiantLabel, StyledBorderButton, DrawStyledButton
from client_reception import ReceptionThread, ConnectThread, PingThread
from client_windows import RulesWindow, GameCreationWindow, JoinGameWindow, AvatarWindow, LeaveGameWindow, ConnexionInfoWindow, GameIsFullWindow, SettingsWindow, VictoryWindow, handle_username
from client_mqtt import Mqtt_Sub
from client_objects import ClickButton, UnderlineWidget, UnderlineLineEdit, HoverPixmapButton
from client_animations import LoadSprites, AvatarAnimatedLabel, LoopAnimatedLabel
import log_config

log_config.setup_logging()

class Login(QMainWindow):
    """Fenêtre de login pour le client"""
    login_accepted = pyqtSignal(bool)

    def __init__(self, avatar_name : str = "no-avatar"):
        """__init__() : Initialisationavatar de la fenêtre de login"""
        super().__init__()
        self.avatar_name = avatar_name
        self.avatar_tuple = ("tasse-avatar", "serviette-avatar", "reveil-avatar", "cactus-avatar", "robot-ninja-avatar", "bouteille-avatar", "television-avatar", "panneau-avatar", "pizza-avatar", "gameboy-avatar")
        self.avatar_window = AvatarWindow()
        self.avatar_window.avatar_signal.connect(self.set_new_avatar)

        self.setWindowTitle("KABOOM")
        self.setWindowIcon(QIcon(f"{image_path}/bombe-icon.png"))
        self.setObjectName("login_window")
        self.setup()
        self.username_edit.setFocus()

    def setup(self):
        """setup() : Mise en place de la fenêtre de login"""
        self.resize(int(screen_width // 3), int(screen_height // 3))
        center_window(self)
        self.setStyleSheet(windows_stylesheet)
        
        layout = QGridLayout()
        username_layout = QVBoxLayout()
        avatar_layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        username_widget = QWidget()
        username_widget.setLayout(username_layout)
        avatar_widget = QWidget()
        avatar_widget.setLayout(avatar_layout)

        self.kaboom_logo = QPixmap(f"{image_path}kaboom-logo.png")
        self.logo_label = QLabel()
        self.logo_label.setObjectName("logo_label")
        self.logo_label.setFixedSize(int(screen_width // 6), int(screen_height // 6))
        self.logo_label.setPixmap(self.kaboom_logo.scaled(self.logo_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

        self.label = QLabel(langue.langue_data["Login__username_label__text"])
        self.label.setObjectName("username_label")
        self.label.setAlignment(Qt.AlignCenter)

        self.username_edit = UnderlineLineEdit()
        self.username_edit.setObjectName("username_edit")
        self.username_edit.setMaxLength(20)
        self.username_edit.setPlaceholderText(langue.langue_data["Login__username_label__placeholder"])
        self.username_edit.textChanged.connect(self.restricted_caracters)
        self.username_edit.returnPressed.connect(self.send_username)

        self.alert_label = QLabel("", self)
        self.alert_label.setObjectName("alert_label")
        self.alert_label.setStyleSheet("color: red;")
        self.alert_label.setAlignment(Qt.AlignCenter)

        self.avatar_button = ClickButton()
        self.avatar_button.setObjectName("avatar_button")
        self.avatar_button.setIcon(QIcon(f"{image_path}{self.avatar_name}.png"))
        self.avatar_button.setIconSize(QSize(int(screen_width / 8), int(screen_width / 8)))
        self.avatar_button.clicked.connect(self.show_avatar_window)

        self.login_button = ClickButton(langue.langue_data["Login__login_button__text"], self)
        self.login_button.setObjectName("login_pushbutton")
        self.login_button.clicked.connect(self.send_username)

        layout.addWidget(self.logo_label, 0, 0, 1, 2, Qt.AlignHCenter)
        layout.addWidget(username_widget, 1, 0, Qt.AlignHCenter)
        layout.addWidget(avatar_widget, 1, 1, Qt.AlignHCenter)
        layout.addWidget(self.alert_label, 2, 0, 1, 2, Qt.AlignHCenter)
        layout.addWidget(self.login_button, 4, 0, 1, 2, Qt.AlignHCenter)        
        
        username_layout.addWidget(self.label, Qt.AlignHCenter)
        username_layout.addWidget(self.username_edit, Qt.AlignHCenter)
        username_layout.addWidget(self.alert_label, Qt.AlignHCenter)

        avatar_layout.addWidget(self.avatar_button)

        self.setCentralWidget(widget)

        self.setup_threads()

        receiver_thread.name_correct.connect(self.show_window)
    
    def restricted_caracters(self):
        """restricted_caracters() : Empêche l'utilisateur d'entrer des caractères spéciaux"""
        text = self.username_edit.text()
        text = re.sub(r'[^a-zA-ZÀ-ÿ0-9]', '', text)
        self.username_edit.setText(text)

    def setup_threads(self):
        """setup_threads() : Mise en place des threads de réception et de connexion"""
        self.connect_thread = ConnectThread()
        self.connect_thread.start()
        self.connect_thread.connection_established.connect(self.connect_to_server)

    def connect_to_server(self):
        """connect_to_server() : Se connecte au serveur"""
        receiver_thread.start()

    def send_username(self):
        """send_username() : Envoie le nom d'utilisateur au serveur"""
        global username
        username = self.username_edit.text()
        try:
            if username != "" and not username.isspace():
                handle_username(username)
                if self.avatar_name == "no-avatar":
                    self.avatar_name = random.choice(self.avatar_tuple)
                client_socket.send(f"NEW_USER|{username}|{self.avatar_name}".encode())
            else:
                self.alert_label.setText(langue.langue_data["Login__alert_label__empty_error"])
                button_sound.sound_effects.error_sound.play()
        except BrokenPipeError:
            self.alert_label.setText(langue.langue_data["Login__alert_label__connection_error"])
            button_sound.sound_effects.error_sound.play()
        except OSError:
            self.alert_label.setText(langue.langue_data["Login__alert_label__connection_error"])
            button_sound.sound_effects.error_sound.play()

    def set_new_avatar(self, avatar_name : str):
        """set_new_avatar(avatar_name) : Change l'avatar de l'utilisateur
        
        Args:
            avatar_name (str): Nom de l'avatar"""
        self.avatar_name = avatar_name
        self.avatar_button.setIcon(QIcon(f"{image_path}{avatar_name}.png"))

    def show_window(self, name_correct : bool):
        """show_wiindow() : Affiche la fenêtre principale si le nom d'utilisateur est correct
        
        Args:
            name_correct (bool): True si le nom d'utilisateur est correct, False sinon"""
        if name_correct:
            self.close()
            window.set_avatar(self.avatar_name)
            window.start_setup(join = False)
        else:
            self.alert_label.setText(langue.langue_data["Login__alert_label__already_used_error"])
            button_sound.sound_effects.error_sound.play()

    def show_avatar_window(self):
        """show_avatar_window() : Affiche la fenêtre des avatars"""
        self.avatar_window.show()

class ClientWindow(AnimatedWindow):
    """Fenêtre principale du client qui hérite de AnimatedWindow
    
    Attributes:
        correct_mdp (pyqtSignal): Signal pour le mot de passe correct
        in_game_signal (pyqtSignal): Signal pour la game
        waiting_room_close_signal (pyqtSignal): Signal pour fermer la salle d'attente
        players_number_signal (pyqtSignal): Signal pour le nombre de joueurs"""
    correct_mdp = pyqtSignal(bool)
    in_game_signal = pyqtSignal(str, int)
    waiting_room_close_signal = pyqtSignal()
    players_number_signal = pyqtSignal(str)

    def __init__(self, join : bool = False):
        """__init__() : Initialisation de la fenêtre principale
        
        Args:
            join (bool): True si le joueur a rejoint une partie, False sinon"""
        super().__init__()
        self.join = join
        self.ingame = False
        self.previous_player : str  | None = None
        self.should_draw = True

        self.connexion_info_window : ConnexionInfoWindow | None = None
        self.loaded_select_screen = False

        load_sprites = LoadSprites(self)
        self.setWindowIcon(QIcon(f"{image_path}/bombe-icon.png"))

        self.ping(0, True)
        self.setup_creation_game()
        self.setup_animation_instances()
        self.setObjectName("client_mainwindow")

        ping_thread.ping_signal.connect(self.ping)
        receiver_thread.sylb_received.connect(self.display_sylb)
        receiver_thread.game_signal.connect(self.game_tools)
        receiver_thread.join_signal.connect(self.join_tools)
        receiver_thread.lobby_state_signal.connect(self.lobby_state_tools)

    def setup_creation_game(self):
        """setup_creation_game() : Mise en place de la fenêtre de création de partie"""
        layout = QGridLayout()
        self.creation_game = GameCreationWindow(layout, receiver_thread)
        self.creation_game.create_game_signal.connect(lambda game_name, password, private_game: self.setup_game(layout, game_name, password, private_game))
        
    def setup_animation_instances(self):
        """setup_animation_instances() : Mise en place des instances d'animations"""
        self.avatarBorderBox = AvatarBorderBox()
        self.avatars_colors_dico = self.avatarBorderBox.setup_colors(self)
        self.label_loaded = False
        self.buttonBorderBox = ButtonBorderBox()
        self.buttonBorderBox.setup_colors(self)
        self.button_loaded = False

    def set_avatar(self, avatar_name : str):
        """set_avatar(avatar_name) : Déclare la variable de l'avatar de l'utilisateur
        
        Args:
            avatar_name (str): Nom de l'avatar"""
        self.avatar_name = avatar_name
        # print(avatar_name, "AVATAR NAME")

    def start_setup(self, join = False):
        """start_setup() : Mise en place de la fenêtre principale"""
        self.setup_title_screen(join)
        #self.setup(join)
        
    def setup_title_screen(self, join : bool):
        """setup_title_screen(join) : Mise en place de la fenêtre principale

        Args:
            join (bool): True si le joueur a rejoint une partie, False sinon"""
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.title_screen_label = LoopAnimatedLabel(frame_rate=24, ratio=Qt.AspectRatioMode.IgnoreAspectRatio)
        self.title_screen_label.setup(self, "title_screen")
        self.title_screen_label.start_loop_animation()
        music.choose_music(0)
 
        widget = QWidget(self)
        self.setCentralWidget(widget)
 
        layout = QVBoxLayout()
        layout.addWidget(self.title_screen_label)
        layout.setContentsMargins(0, 0, 0, 0)
 
        widget.setLayout(layout)

    def setup(self, join : bool) -> QGridLayout:
        """setup() : Mise en place de la fenêtre principale
        
        Args:
            join (bool): True si le joueur a rejoint une partie, False sinon"""
        self.set_rules()
        self.setWindowTitle("KABOOM")
        self.setStyleSheet(main_stylesheet)
        layout = QGridLayout()
        
        self.create_game_button = AnimatedButton("create_game_pushbutton", QColor(164,255,174,1), QColor(187,186,255,1))
        self.create_game_button.setObjectName("create_game_pushbutton")
        self.create_game_button.setText(langue.langue_data["ClientWindow__create_game_button__text"])
        layout.addWidget(self.create_game_button, 1, 0, Qt.AlignHCenter)

        self.join_game = AnimatedButton("join_game_pushbutton", QColor(211,133,214,1), QColor(253,212,145,1))
        self.join_game.setObjectName("join_game_pushbutton")
        self.join_game.setText(langue.langue_data["ClientWindow__join_game__text"])
        layout.addWidget(self.join_game, 3, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.create_game_button.clicked.connect(self.create_game_widget)
        self.set_buttonBorder_properties()
    
        self.join_game.clicked.connect(lambda: self.setup_join_game(layout))

    def create_game_widget(self):
        """create_game_widget(layout) : Mise en place de la fenêtre de création de partie"""
        self.creation_game.show()
        self.creation_game.setup()

    def set_rules(self):
        rules.clear()
        rules.extend([5, 7, 3, 2, 3, 1, 0])

    def join_tools(self, response : str):
        """join_tools(response) : Gère les messages de la partie
        
        Args:
            response (str): Message de la partie"""
        reply = response.split("|")
        if reply[1] == "GAME-JOINED":
            if reply[6] == username:
                self.correct_mdp.emit(True)
                game_name = reply[2]
                game_creator = reply[3]
                password = reply[4]
                private_game = reply[5]
                self.join = True
                private_game = self.bool_convert(private_game)
                layout = QGridLayout()
                self.setup_game(layout, game_name, password, private_game)
                self.waiting_room_close_signal.emit()
            else:
                print("Other player joined")

        elif reply[1] == "WRONG-PASSWORD":
            self.correct_mdp.emit(False)
            print("Wrong password")
        
        elif reply[1] == "GET-PLAYERS":
            print("Get players")
            self.get_players(players = reply[2], avatars = reply[3], ready_players = reply[4])
            print("Players", reply[2])

        elif reply[1] == "ALREADY-IN-GAME":
            print("Already in game")
            game_name = reply[2]
            players_number = int(reply[3])
            self.in_game_signal.emit(game_name, players_number)

        elif reply[1] == "NEW-PLAYER":
            self.players_number(game_name = reply[2], leave = False)

        elif reply[1] == "LEAVE-GAME":
            if "GAME-DELETED" in reply[3]:
                game_name = reply[4]
                print(game_name, "GAME_DELETED")
                self.delete_item(game_name)
            else:
                game_name = reply[2]
            self.players_number(game_name = game_name, leave = True)

        elif reply[1] == "GAME-FULL":
            self.show_game_is_full_window()

    def game_tools(self, game_message : str):
        """game_tools(game_message) : Gère les messages de la partie

        Args:
            game_message (str): Message de la partie"""
        reply = game_message.split("|")        
        if reply[1] == "RIGHT":
            player = reply[2]
            self.text_label.clear()
            self.text_label.setText("✅")
            if player == username:
                self.text_line_edit.setEnabled(False)

        elif reply[1] == "WRONG":
            button_sound.sound_effects.error_sound.play()
            self.text_label.clear()
            self.text_label.setText("❌")        
        
        elif reply[1] == "TIME'S-UP":
            player = reply[2]
            self.bomb_label.stop_loop_animation()
            self.remove_heart(player)
            if reply[2] == username:
                self.text_line_edit.setEnabled(False)
                self.text_line_edit.clear()
                self.text_label.clear()
                self.text_label.setText("⏰")
        
        elif reply[1] == "GAME-STARTED":
            self.ingame = True
            death_mode_state : int = int(reply[3])
            if death_mode_state == 0:
                self.bomb_label.setup(self, "bombe")
            elif death_mode_state == 1:
                self.bomb_label.setup(self, "bombe_bleue")
            elif death_mode_state == 2:
                self.bomb_label.setup(self, "bombe_rose")

        elif reply[1] == "GAME-ENDED":
            self.ingame = False
            self.unsetup_game()
            self.victory_window = VictoryWindow(eval(reply[3]))
            self.victory_window.show()
            self.bomb_label.setPixmap(self.bomb.scaled(self.bomb_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

        elif reply[1] == "LIFES-RULES":
            self.ready_button.setEnabled(False)
            self.setup_hearts_rules(lifes = int(reply[2]), ready_players = reply[3])

    def lobby_state_tools(self, lobby_state : str):
        """lobby_state_tools(lobby_state) : Gère les messages du lobby
        
        Args:
            lobby_state (str): Message du lobby"""
        reply = lobby_state.split("|")

        if reply[1] == "NEW-CREATOR":
            self.new_creator(game_name = reply[2], creator = reply[3])

        elif reply[1] == "LEAVE-GAME":
            self.remove_a_player(game_name = reply[2], player = reply[3])

        elif reply[1] == "PLAYER-DECO":
            self.deco_a_player(player = reply[2])

        elif reply[1] == "READY":
            self.user_ready(player = reply[2], ready =self.bool_convert(reply[3]))

    def set_mqtt(self, game_name : str, username : str):
        """set_mqtt(game_name) : Mise en place des clients MQTT

        Args:
            game_name (str): Nom de la partie
            username (str): Nom de l'utilisateur"""
        #Mise en place du client MQTT pour recevoir des messages
        self.mqtt_sub = Mqtt_Sub(topic = game_name, label = self.text_label, user=username)
        self.mqtt_sub.start()
        #Mise en place du client MQTT pour envoyer des messages

    def get_players(self, players : list, avatars : list, ready_players : list):
        """get_players(players) : Récupère les joueurs de la partie
        
        Args:
            players (list): Joueurs de la partie
            avatars (list): Avatars des joueurs
            ready_players (list): Joueurs prêts à jouer"""
        players = players.split(",")
        avatars = avatars.split(",")
        ready_players = ready_players.split(",")
        for player, avatar, ready in zip(players, avatars, ready_players):
            print(avatar, "Avatar", avatars)
            if player != "":
                 for i, (label, avatar_label) in enumerate(zip(self.player_label_list, self.avatar_label_list)):
                    print(label.text(), player,"LABEL TEXT")
                    if player == label.text() or f"<font color='green'>{player}</font>" == label.text():
                        print(1)
                        break
                    else:
                        if label.text() == langue.langue_data["ClientWindow__player_label__en_attente_state_text"]:
                            if not self.bool_convert(ready):
                                label.setText(player)
                            else:
                                label.setText(f"<font color='green'>{player}</font>")
                            new_avatar = QPixmap(f"{image_path}{avatar}.png")
                            avatar_label.setPixmap(new_avatar.scaled(avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                            getattr(self, f"player{i+1}_border_color").setRgb(*self.avatars_colors_dico[avatar][0])
                            getattr(self, f"player{i+1}_border_color2").setRgb(*self.avatars_colors_dico[avatar][1])

                            avatar_label.setup(self, avatar.replace("-avatar", ""))
                            break
                        else:
                            continue
                    # player_label_list[players.index(player)].setText(player)

    def players_number(self, game_name : str, leave : bool):
        """players_number(game_name) : Ajoute un joueur à la partie dans le menu pour rejoindre des parties
        
        Args:
            game_name (str): Nom de la partie
            leave (bool): True si le joueur quitte la partie, False sinon"""
        try:
            for index in range(self.game_list_widget.count()):
                item = self.game_list_widget.item(index)
                button = self.game_list_widget.itemWidget(item).findChild(QPushButton)
                label = self.game_list_widget.itemWidget(item).findChild(QLabel, "people_label")
                #print(label.objectName())
                if button.objectName() == game_name:
                    label_number = int(label.text().split("/")[0])
                    if leave:
                        label.setText(f"{label_number - 1}/8")
                    else:
                        label.setText(f"{label_number + 1}/8")
                self.players_number_signal.emit(label.text())
        except AttributeError:
            pass
        except RuntimeError:
            pass

    def change_player(self, player: str, avatar_size: float, border_size: int):
        """previous_player(player) : Mets à jour l'interface pour le joueur précédent
        
        Args:
            player (str): Joueur suivant
            avatar_size (float): Taille de l'avatar
            border_size (int): Taille de la bordure de l'avatar"""
        try:
            for i, (label, avatar_label) in enumerate(zip(self.player_label_list, self.avatar_label_list)):
                if label.text() == player or label.text() == f"<i><font color='red'>{player}</font></i>" or label.text() == f"<font color='green'>{player}</font>": #pourra évoluer
                    avatar_label.setFixedSize(int(screen_width / avatar_size), int(screen_height / avatar_size))
                    avatar_label.setPixmap(avatar_label.pixmap().scaled(avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                    self.player_border_size[i] = border_size
                    if player != self.previous_player:
                        avatar_label.play_animation()
                    break
        except IndexError:
            pass

    def remove_a_player(self, game_name: str, player: str):
        """remove_a_player(game_name, player) : Enlève un joueur de la partie
        
        Args:
            game_name (str): Nom de la partie
            player (str): Joueur à enlever"""
        try:
            for label, avatar_label in zip(self.player_label_list, self.avatar_label_list):
                if label.text() == player or label.text() == f"<i><font color='red'>{player}</font></i>" or label.text() == f"<font color='green'>{player}</font>": #pourra évoluer
                    label.setText(langue.langue_data["ClientWindow__player_label__en_attente_state_text"])
                    avatar = QPixmap(f"{image_path}no-avatar.png")
                    avatar_label.setPixmap(avatar.scaled(avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                    avatar_label.setup(self, "no-avatar")
                    break
        except IndexError:
            pass
              
    def deco_a_player(self, player : str):
        """deco_a_player(player) : Enlève un joueur de la partie
        
        Args:
            player (str): Joueur à enlever"""
        try:
            for label in self.player_label_list:
                if label.text() == player or label.text() == f"<font color='green'>{player}</font>":
                    label.setText(f"<i><font color='red'>{player}</font></i>")
                    break
        except IndexError:
            pass
        except RuntimeError:
            pass

    def remove_heart(self, player : str):
        """remove_heart() : Enlève un coeur au joueur"""
        if player == self.player1_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player1_label.text() or f"<font color='green'>{player}</font>" == self.player1_label.text():
            self.heart_list_widget1.takeItem(self.heart_list_widget1.count() - 1)
        elif player == self.player2_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player2_label.text() or f"<font color='green'>{player}</font>" == self.player2_label.text():
            self.heart_list_widget2.takeItem(self.heart_list_widget2.count() - 1)
        elif player == self.player3_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player3_label.text() or f"<font color='green'>{player}</font>" == self.player3_label.text():
            self.heart_list_widget3.takeItem(self.heart_list_widget3.count() - 1)
        elif player == self.player4_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player4_label.text() or f"<font color='green'>{player}</font>" == self.player4_label.text():
            self.heart_list_widget4.takeItem(self.heart_list_widget4.count() - 1)
        elif player == self.player5_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player5_label.text() or f"<font color='green'>{player}</font>" == self.player5_label.text():
            self.heart_list_widget5.takeItem(self.heart_list_widget5.count() - 1)
        elif player == self.player6_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player6_label.text() or f"<font color='green'>{player}</font>" == self.player6_label.text():
            self.heart_list_widget6.takeItem(self.heart_list_widget6.count() - 1)
        elif player == self.player7_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player7_label.text() or f"<font color='green'>{player}</font>" == self.player7_label.text():
            self.heart_list_widget7.takeItem(self.heart_list_widget7.count() - 1)
        elif player == self.player8_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player8_label.text() or f"<font color='green'>{player}</font>" == self.player8_label.text():
            self.heart_list_widget8.takeItem(self.heart_list_widget8.count() - 1)

    def unsetup_game(self):
        """unsetup_game() : Reset les éléments de la partie"""

        self.start_button.setEnabled(False)
        self.ready_button.setEnabled(True)
        if not self.join:
            self.rules_button.setEnabled(True)
        self.ready_button.setText(langue.langue_data["ClientWindow__ready_button__not_ready_state_text"])
        self.text_line_edit.setEnabled(False)

        self.change_player(self.previous_player, 6, 12)
        self.clear_game()
        self.reset_ready_user()

    def clear_game(self):
        """clear_game() : Efface les éléments de la fenêtre de jeu"""
        self.previous_player = None
        self.text_label.clear()
        self.syllabe_label.clear()
        self.text_line_edit.clear()
        self.heart_list_widget1.clear()
        self.heart_list_widget2.clear()
        self.heart_list_widget3.clear()
        self.heart_list_widget4.clear()
        self.heart_list_widget5.clear()
        self.heart_list_widget6.clear()
        self.heart_list_widget7.clear()
        self.heart_list_widget8.clear()

    def new_creator(self, game_name : str, creator : str):
        """new_creator(creator) : Met à jour le créateur de la partie
        
        Args:
            game_name (str): Nom de la partie
            creator (str): Créateur de la partie"""
        self.join = False
        self.rules_button.setEnabled(True)
        self.show_password_button.setEnabled(True)
        if self.ready_button.text() == langue.langue_data["ClientWindow__ready_button__ready_state_text"]:
            self.start_button.setEnabled(True)

    def setup_game(self, layout : QGridLayout, game_name : str, password : str, private_game : bool):
        """setup_game(layout) : Mise en place de la fenêtre de jeu
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale
            game_name (str): Nom de la partie
            password (str): Mot de passe de la partie
            private_game (bool): True si la partie est privée, False sinon"""
        global username
        self.join_menu_loaded = False
        self.kill_button_animation_timer()
        self.check_setup(layout, game_name, password, private_game)

        layout = QGridLayout()

        self.player1_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player2_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player3_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player4_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player5_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player6_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player7_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player8_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)

        self.player_label_list = [self.player1_label, self.player2_label, self.player3_label, self.player4_label, self.player5_label, self.player6_label, self.player7_label, self.player8_label]
        
        self.setup_player_layout()
        self.setup_avatar_label()
        self.setup_heart_layout()
        self.setup_hearts_widget()

        self.heart_layout.addWidget(self.heart_list_widget1, 0, 0, Qt.AlignHCenter)
        self.heart_layout2.addWidget(self.heart_list_widget2, 0, 0, Qt.AlignHCenter)
        self.heart_layout3.addWidget(self.heart_list_widget3, 0, 0, Qt.AlignHCenter)
        self.heart_layout4.addWidget(self.heart_list_widget4, 0, 0, Qt.AlignHCenter)
        self.heart_layout5.addWidget(self.heart_list_widget5, 0, 0, Qt.AlignHCenter)
        self.heart_layout6.addWidget(self.heart_list_widget6, 0, 0, Qt.AlignHCenter)
        self.heart_layout7.addWidget(self.heart_list_widget7, 0, 0, Qt.AlignHCenter)
        self.heart_layout8.addWidget(self.heart_list_widget8, 0, 0, Qt.AlignHCenter)

        self.text_widget = QWidget()
        self.text_widget.setObjectName("text_widget")
        text_widget_width = self.text_widget.width()
        text_widget_height = self.text_widget.height()
        sub_layout = QGridLayout()

        self.bomb = QPixmap(f"{image_path}bombe.png")
        self.bomb_label = LoopAnimatedLabel()
        self.bomb_label.setObjectName("bomb_label")
        self.bomb_label.setStyleSheet("border: 2px solid black;")
        self.bomb_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.bomb_label.setAlignment(Qt.AlignHCenter)
        self.bomb_label.setPixmap(self.bomb.scaled(self.bomb_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

        self.syllabe_label = QLabel("", self)
        self.syllabe_label.setObjectName("syllabe_label")

        self.text_label = QLabel("", self)
        self.text_label.setObjectName("text_label")

        self.text_line_edit = QLineEdit(self)
        self.text_line_edit.setObjectName("text_line_edit")

        self.text_line_edit.setPlaceholderText(langue.langue_data["ClientWindow__text_line_edit__placeholder"])
        self.text_line_edit.setEnabled(False)
        self.text_line_edit.returnPressed.connect(self.send_message)
        self.text_line_edit.textChanged.connect(self.display_text)

        sub_layout.addWidget(self.bomb_label, 0, 0, Qt.AlignHCenter)
        sub_layout.addWidget(self.syllabe_label, 1, 0, Qt.AlignHCenter)
        sub_layout.addWidget(self.text_label, 2, 0, Qt.AlignHCenter)
        sub_layout.addWidget(self.text_line_edit, 3, 0, Qt.AlignHCenter)

        self.text_widget.setLayout(sub_layout)

        layout.addWidget(self.player1_widget, 1, 0, Qt.AlignLeft)
        layout.addWidget(self.player2_widget, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.player3_widget, 1, 2, Qt.AlignRight)
        layout.addWidget(self.player4_widget, 2, 0, Qt.AlignLeft)
        layout.addWidget(self.text_widget, 2, 1, Qt.AlignCenter)
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

        self.player1_layout.addWidget(self.player1_avatar_label, 1, Qt.AlignHCenter)
        self.player2_layout.addWidget(self.player2_avatar_label, 1, Qt.AlignHCenter)
        self.player3_layout.addWidget(self.player3_avatar_label, 1, Qt.AlignHCenter)
        self.player4_layout.addWidget(self.player4_avatar_label, 1, Qt.AlignHCenter)
        self.player5_layout.addWidget(self.player5_avatar_label, 1, Qt.AlignHCenter)
        self.player6_layout.addWidget(self.player6_avatar_label, 1, Qt.AlignHCenter)
        self.player7_layout.addWidget(self.player7_avatar_label, 1, Qt.AlignHCenter)
        self.player8_layout.addWidget(self.player8_avatar_label, 1, Qt.AlignHCenter)

        self.player1_layout.addWidget(self.heart_widget_player1)
        self.player2_layout.addWidget(self.heart_widget_player2)
        self.player3_layout.addWidget(self.heart_widget_player3)
        self.player4_layout.addWidget(self.heart_widget_player4)
        self.player5_layout.addWidget(self.heart_widget_player5)
        self.player6_layout.addWidget(self.heart_widget_player6)
        self.player7_layout.addWidget(self.heart_widget_player7)
        self.player8_layout.addWidget(self.heart_widget_player8)

        self.home_logo = QPixmap(f"{image_path}home.png")
        self.home_logo_hover = QPixmap(f"{image_path}home-hover.png")
        self.home_button_game = HoverPixmapButton(self.home_logo, self.home_logo_hover)
        self.home_button_game.setEnabled(True)
        self.home_button_game.setFixedSize(screen_width//40, screen_width//40)
        self.home_button_game.setObjectName("other_buttons")
        self.home_button_game.setIcon(QIcon(self.home_logo))
        self.home_button_game.setIconSize(self.home_button_game.size())
        self.home_button_game.clicked.connect(self.leave_game)

        self.settings_logo = QPixmap(f"{image_path}settings.png")
        self.settings_logo_hover = QPixmap(f"{image_path}settings-hover.png")
        self.settings = HoverPixmapButton(self.settings_logo, self.settings_logo_hover)
        self.settings.setFixedSize(screen_width//40, screen_width//40)
        self.settings.setObjectName("other_buttons")
        self.settings.setIcon(QIcon(self.settings_logo))
        self.settings.setIconSize(self.settings.size())
        self.settings.clicked.connect(self.display_settings)

        self.wifi_label = QLabel(parent=self)
        self.wifi_label.setObjectName("wifi_label")
        self.wifi_label.setFixedSize(screen_width//40, screen_width//40)
        self.wifi_label.setPixmap(self.wifi_logo.scaled(self.wifi_label.width(), self.wifi_label.height(), Qt.KeepAspectRatio))

        self.key_icon = QPixmap(f"{image_path}key.png")
        self.key_hover_icon = QPixmap(f"{image_path}key-hover.png")

        self.show_password_button = ClickButton(parent=self)
        self.show_password_button = HoverPixmapButton(self.key_icon, self.key_hover_icon, self)
        self.show_password_button.setObjectName("hover_buttons")
        self.show_password_button.setFixedSize(screen_width//40, screen_width//40)
        self.show_password_button.setIcon(QIcon(self.key_icon))
        self.show_password_button.setIconSize(self.show_password_button.size())
        self.show_password_button.clicked.connect(self.show_password)
        self.show_password_button.setEnabled(False)

        self.password_linedit = UnderlineLineEdit()
        self.password_linedit.setObjectName("underline_password_lineedit")
        self.password_linedit.setEchoMode(QLineEdit.Password)
        self.password_linedit.setText(password)
        self.password_linedit.setMaxLength(30)
        self.password_linedit.setFixedWidth(self.player1_avatar_label.width() - self.show_password_button.width())
        self.password_linedit.setReadOnly(True)

        self.rules_button = StyledBorderButton(langue.langue_data["ClientWindow__rules_button__text"], self, "rules_button", QColor(215, 179, 245), QColor(241, 206, 112))
        self.rules_button.setObjectName("rules_pushbutton")
        self.rules_button.clicked.connect(self.display_rules)
        self.draw_rules_button = DrawStyledButton(self.rules_button, self)

        self.ready_button = StyledBorderButton(langue.langue_data["ClientWindow__ready_button__not_ready_state_text"], self, "ready_button", QColor(4,245, 130), QColor(243,108,108))
        self.ready_button.setObjectName("ready_pushbutton")
        self.ready_button.setEnabled(True)
        self.ready_button.clicked.connect(self.ready)
        self.draw_ready_button = DrawStyledButton(self.ready_button, self)

        self.start_button = StyledBorderButton(langue.langue_data["ClientWindow__start_button__text"], self, "start_button", QColor(215, 179, 245), QColor(241, 206, 112))
        self.start_button.setObjectName("start_pushbutton")
        self.start_button.clicked.connect(lambda: self.start_game(game_name))
        self.start_button.setEnabled(False)
        self.draw_start_button = DrawStyledButton(self.start_button, self)

        self.draw_buttons_list = [self.draw_rules_button, self.draw_ready_button, self.draw_start_button]

        self.game_name_label = LinearGradiantLabel(game_name)
        self.game_name_label.setObjectName("game_name_label")
        self.game_name_label.setFixedWidth(screen_width//3)
        
        if self.join: # Si le joueur a rejoint une partie
            self.show_password_button.setEnabled(False)
            self.rules_button.setEnabled(False)
        else:
            self.show_password_button.setEnabled(True)
            self.player1_label.setText(username)
            self.player1_border_color.setRgb(*self.avatars_colors_dico[self.avatar_name][0])
            self.player1_border_color2.setRgb(*self.avatars_colors_dico[self.avatar_name][1])

        button_widget = QWidget()
        button_widget.setFixedWidth(self.player1_avatar_label.width())
        button_layout = QGridLayout(button_widget)
        button_layout.addWidget(self.home_button_game, 0, 0, Qt.AlignLeft)
        button_layout.addWidget(self.settings, 0, 1, Qt.AlignLeft)
        button_layout.addWidget(self.wifi_label, 0, 2, Qt.AlignLeft)

        password_widget = QWidget()
        password_layout = QHBoxLayout(password_widget)
        if private_game:
            password_layout.addWidget(self.password_linedit)
            password_layout.addWidget(self.show_password_button)

        layout.addWidget(button_widget, 0, 0, Qt.AlignLeft)
        layout.addWidget(self.game_name_label, 0, 1, Qt.AlignHCenter)
        layout.addWidget(password_widget, 0, 2, Qt.AlignRight)
        layout.addWidget(self.rules_button, 4, 0, Qt.AlignLeft)
        layout.addWidget(self.ready_button, 4, 1, Qt.AlignHCenter)
        layout.addWidget(self.start_button, 4, 2, Qt.AlignRight)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        music.choose_music(2)

        self.set_avatarBorder_properties()

        self.set_mqtt(game_name, username)

    def check_setup(self, layout, game_name, password, private_game):
        """check_setup(layout, game_name, password, private_game) : Gère des éléments en fonction du type de partie
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale
            game_name (str): Nom de la partie
            password (str): Mot de passe de la partie
            private_game (bool): True si la partie est privée, False sinon"""
        if not self.join:
            self.create_game(game_name, password, private_game)
        else:
            self.game_name = game_name
            self.join_game_as_a_player(username, game_name)
        try:
            layout.removeWidget(self.create_game_button)
            layout.removeWidget(self.join_game)
        except:
            pass

    def show_password(self):
        """show_password() : Affiche le mot de passe"""
        if self.password_linedit.echoMode() == QLineEdit.Password:
            self.password_linedit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_linedit.setEchoMode(QLineEdit.Password)


    def setup_heart_layout(self):
        """setup_heart_layout() : Mise en place des coeurs des joueurs"""
        self.coeur = QPixmap(f"{image_path}coeur.png")
        
        self.heart_layout = QGridLayout()
        self.heart_widget_player1 = QWidget()
        self.heart_widget_player1.setObjectName("heart_widget")
        self.heart_widget_player1.setLayout(self.heart_layout)

        self.heart_layout2 = QGridLayout()
        self.heart_widget_player2 = QWidget()
        self.heart_widget_player2.setObjectName("heart_widget")
        self.heart_widget_player2.setLayout(self.heart_layout2)

        self.heart_layout3 = QGridLayout()
        self.heart_widget_player3 = QWidget()
        self.heart_widget_player3.setObjectName("heart_widget")
        self.heart_widget_player3.setLayout(self.heart_layout3)

        self.heart_layout4 = QGridLayout()
        self.heart_widget_player4 = QWidget()
        self.heart_widget_player4.setObjectName("heart_widget")
        self.heart_widget_player4.setLayout(self.heart_layout4)

        self.heart_layout5 = QGridLayout()
        self.heart_widget_player5 = QWidget()
        self.heart_widget_player5.setObjectName("heart_widget")
        self.heart_widget_player5.setLayout(self.heart_layout5)

        self.heart_layout6 = QGridLayout()
        self.heart_widget_player6 = QWidget()
        self.heart_widget_player6.setObjectName("heart_widget")
        self.heart_widget_player6.setLayout(self.heart_layout6)

        self.heart_layout7 = QGridLayout()
        self.heart_widget_player7 = QWidget()
        self.heart_widget_player7.setObjectName("heart_widget")
        self.heart_widget_player7.setLayout(self.heart_layout7)

        self.heart_layout8 = QGridLayout()
        self.heart_widget_player8 = QWidget()
        self.heart_widget_player8.setObjectName("heart_widget")
        self.heart_widget_player8.setLayout(self.heart_layout8)

    def setup_player_layout(self):
        """setup_player_layout() : Mise en place des layouts des joueurs"""
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

    def setup_avatar_label(self):
        self.no_avatar = QPixmap(f"{image_path}no-avatar.png")
        self.avatar = QPixmap(f"{image_path}{self.avatar_name}.png")
        
        self.player1_avatar_label = AvatarAnimatedLabel()
        self.player1_avatar_label.setObjectName("player1_avatar_label")
        self.player1_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player1_avatar_label.setPixmap(self.avatar.scaled(self.player1_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player1_avatar_label.setup(self, self.avatar_name.replace("-avatar", ""))
        self.player1_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player2_avatar_label = AvatarAnimatedLabel()
        self.player2_avatar_label.setObjectName("player2_avatar_label")
        self.player2_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player2_avatar_label.setPixmap(self.no_avatar.scaled(self.player2_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player2_avatar_label.setup(self, "no-avatar")
        self.player2_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player3_avatar_label = AvatarAnimatedLabel()
        self.player3_avatar_label.setObjectName("player3_avatar_label")
        self.player3_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player3_avatar_label.setPixmap(self.no_avatar.scaled(self.player3_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player3_avatar_label.setup(self, "no-avatar")
        self.player3_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player4_avatar_label = AvatarAnimatedLabel()
        self.player4_avatar_label.setObjectName("player4_avatar_label")
        self.player4_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player4_avatar_label.setPixmap(self.no_avatar.scaled(self.player4_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player4_avatar_label.setup(self, "no-avatar")
        self.player4_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player5_avatar_label = AvatarAnimatedLabel()
        self.player5_avatar_label.setObjectName("player5_avatar_label")
        self.player5_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player5_avatar_label.setPixmap(self.no_avatar.scaled(self.player5_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player5_avatar_label.setup(self, "no-avatar")
        self.player5_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player6_avatar_label = AvatarAnimatedLabel()
        self.player6_avatar_label.setObjectName("player6_avatar_label")
        self.player6_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player6_avatar_label.setPixmap(self.no_avatar.scaled(self.player6_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player6_avatar_label.setup(self, "no-avatar")
        self.player6_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player7_avatar_label = AvatarAnimatedLabel()
        self.player7_avatar_label.setObjectName("player7_avatar_label")
        self.player7_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player7_avatar_label.setPixmap(self.no_avatar.scaled(self.player7_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player7_avatar_label.setup(self, "no-avatar")
        self.player7_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player8_avatar_label = AvatarAnimatedLabel()
        self.player8_avatar_label.setObjectName("player8_avatar_label")
        self.player8_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player8_avatar_label.setPixmap(self.no_avatar.scaled(self.player8_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player8_avatar_label.setup(self, "no-avatar")
        self.player8_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.avatar_label_list = [self.player1_avatar_label, self.player2_avatar_label, self.player3_avatar_label, self.player4_avatar_label, self.player5_avatar_label, self.player6_avatar_label, self.player7_avatar_label, self.player8_avatar_label]

    def setup_hearts_widget(self):
        """setup_hearts_widget() : Mise en place des coeurs des joueurs"""
        player_avatar_width = self.player1_avatar_label.width()
        player_avatar_height = self.player1_avatar_label.height()
        
        self.heart_list_widget1 = QListWidget()
        self.heart_list_widget1.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget1.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget1.setSpacing(5)
        self.heart_list_widget1.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget1.setObjectName("heart_list_widget")
        self.heart_list_widget1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget1.setItemAlignment(Qt.AlignCenter)

        self.heart_list_widget2 = QListWidget()
        self.heart_list_widget2.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget2.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget2.setSpacing(5)
        self.heart_list_widget2.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget2.setObjectName("heart_list_widget")
        self.heart_list_widget2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget3 = QListWidget()
        self.heart_list_widget3.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget3.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget3.setSpacing(5)
        self.heart_list_widget3.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget3.setObjectName("heart_list_widget")
        self.heart_list_widget3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget3.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget4 = QListWidget()
        self.heart_list_widget4.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget4.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget4.setSpacing(5)
        self.heart_list_widget4.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget4.setObjectName("heart_list_widget")
        self.heart_list_widget4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget4.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget5 = QListWidget()
        self.heart_list_widget5.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget5.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget5.setSpacing(5)
        self.heart_list_widget5.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget5.setObjectName("heart_list_widget")
        self.heart_list_widget5.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget5.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget6 = QListWidget()
        self.heart_list_widget6.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget6.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget6.setSpacing(5)
        self.heart_list_widget6.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget6.setObjectName("heart_list_widget")
        self.heart_list_widget6.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget6.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget7 = QListWidget()
        self.heart_list_widget7.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget7.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget7.setSpacing(5)
        self.heart_list_widget7.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget7.setObjectName("heart_list_widget")
        self.heart_list_widget7.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget7.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget8 = QListWidget()
        self.heart_list_widget8.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget8.setWrapping(True) # Permet de faire passer les coeurs à la ligne
        self.heart_list_widget8.setSpacing(5)
        self.heart_list_widget8.setFixedSize(player_avatar_width, player_avatar_height//7)
        self.heart_list_widget8.setObjectName("heart_list_widget")
        self.heart_list_widget8.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget8.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setup_hearts_rules(self, lifes : int, ready_players : str):
        """setup_hearts_rules() : Mise en place des coeurs en fonction des règles de la partie"""
        ready_players : str = ready_players.split(",")
        total_spacing = 10 * self.heart_list_widget1.spacing()  # Total spacing is 10 times the size of the spacing
        size = (self.heart_list_widget1.width() - total_spacing) // 10  # Subtract the total spacing from the width before dividing by 10
        size = QSize(size, size)
        print(self.player1_label.text())
        player = re.search(r"<font color='green'>(.*?)</font>", self.player1_label.text()).group(1)
        print(player)
        self.coeur = self.coeur.scaled(size, Qt.AspectRatioMode.KeepAspectRatio)

        player_text = self.player1_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label1 = QLabel()
                    self.heart_label1.setObjectName("heart_label")
                    self.heart_label1.setPixmap(self.coeur)
                    item1 = QListWidgetItem()
                    item1.setSizeHint(self.heart_label1.sizeHint())
                    self.heart_list_widget1.addItem(item1)
                    self.heart_list_widget1.setItemWidget(item1, self.heart_label1)

        player_text = self.player2_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label2 = QLabel()
                    self.heart_label2.setObjectName("heart_label")
                    self.heart_label2.setPixmap(self.coeur)
                    item2 = QListWidgetItem()
                    item2.setSizeHint(self.heart_label2.sizeHint())
                    self.heart_list_widget2.addItem(item2)
                    self.heart_list_widget2.setItemWidget(item2, self.heart_label2)
        
        player_text = self.player3_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label3 = QLabel()
                    self.heart_label3.setObjectName("heart_label")
                    self.heart_label3.setPixmap(self.coeur)
                    item3 = QListWidgetItem()
                    item3.setSizeHint(self.heart_label3.sizeHint())
                    self.heart_list_widget3.addItem(item3)
                    self.heart_list_widget3.setItemWidget(item3, self.heart_label3)
        
        player_text = self.player4_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label4 = QLabel()
                    self.heart_label4.setObjectName("heart_label")
                    self.heart_label4.setPixmap(self.coeur)
                    item4 = QListWidgetItem()
                    item4.setSizeHint(self.heart_label4.sizeHint())
                    self.heart_list_widget4.addItem(item4)
                    self.heart_list_widget4.setItemWidget(item4, self.heart_label4)
        
        player_text = self.player5_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label5 = QLabel()
                    self.heart_label5.setObjectName("heart_label")
                    self.heart_label5.setPixmap(self.coeur)
                    item5 = QListWidgetItem()
                    item5.setSizeHint(self.heart_label5.sizeHint())
                    self.heart_list_widget5.addItem(item5)
                    self.heart_list_widget5.setItemWidget(item5, self.heart_label5)
        
        player_text = self.player6_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label6 = QLabel()
                    self.heart_label6.setObjectName("heart_label")
                    self.heart_label6.setPixmap(self.coeur)
                    item6 = QListWidgetItem()
                    item6.setSizeHint(self.heart_label6.sizeHint())
                    self.heart_list_widget6.addItem(item6)
                    self.heart_list_widget6.setItemWidget(item6, self.heart_label6)
        
        player_text = self.player7_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label7 = QLabel()
                    self.heart_label7.setObjectName("heart_label")
                    self.heart_label7.setPixmap(self.coeur)
                    item7 = QListWidgetItem()
                    item7.setSizeHint(self.heart_label7.sizeHint())
                    self.heart_list_widget7.addItem(item7)
                    self.heart_list_widget7.setItemWidget(item7, self.heart_label7)
        
        player_text = self.player8_label.text()
        match = re.search(r"<font color='green'>(.*?)</font>", player_text)
        if match:
            if player_text in ready_players or match.group(1) in ready_players:
                for i in range(0, lifes):
                    self.heart_label8 = QLabel()
                    self.heart_label8.setObjectName("heart_label")
                    self.heart_label8.setPixmap(self.coeur)
                    item8 = QListWidgetItem()
                    item8.setSizeHint(self.heart_label8.sizeHint())
                    self.heart_list_widget8.addItem(item8)
                    self.heart_list_widget8.setItemWidget(item8, self.heart_label8)

    def leave_game(self) -> None:
        """leave_game() : Ouvre une fenêtre "QMainWindow pour supprimer la partie"""
        if not self.ingame:
            self.leave_game_window = LeaveGameWindow(self, self.mqtt_sub, self.game_name)
            self.leave_game_window.show()
        else:
            return

    def leave_join_menu(self):
        """leave_join_menu() : Quitte la fenêtre de jeu pour revenir au menu principal"""
        self.join_state()
        self.setup(join=False)
        client_socket.send("MENU_STATE|".encode())

    def join_state(self):
        """join_state() : Modifie l'état du joueur en fonction de s'il a rejoint une partie ou non"""
        self.join = False
        self.join_menu_loaded = False
        print(self.join_menu_loaded)

    def kill_borders(self):
        try:
            self.avatarBorderBox.kill_timer(self)
        except AttributeError:
            pass
        self.label_loaded = False

    def create_game(self, game_name : str, password : str, private_game: bool):
        """create_game() : Crée une partie
        
        Args:
            game_name (str): Nom de la partie
            password (str): Mot de passe de la partie
            private_game (bool): True si la partie est privée, False sinon"""
        global username
        message = f"CREATE_GAME|{username}|{game_name}|{password}|{private_game}|{self.creation_game.select_langue_combobox.currentText()}|"
        self.game_name = game_name
        client_socket.send(message.encode())

    def join_game_as_a_player(self, username : str, game_name : str):
        """join_game_as_a_player(username, game_name) : Rejoint une partie en tant que joueur
        
        Args:
            username (str): Nom d'utilisateur
            game_name (str): Nom de la partie"""
        message = f"JOIN_GAME_AS_A_PLAYER|{username}|{game_name}|{self.avatar_name}"
        print("join game as a player")
        client_socket.send(message.encode())

    def start_game(self, game_name : str):
        """start_game() : Lance la partie
        
        Args:
            game_name (str): Nom de la partie"""
        global username
        if self.not_alone():
            self.start_button.setEnabled(False)
            self.ready_button.setEnabled(False)
            self.rules_button.setEnabled(False)
            message = f"START_GAME|{username}|{game_name}|{rules[0]}|{rules[1]}|{rules[2]}|{rules[3]}|{rules[4]}|{rules[5]}|{rules[6]}|"
            client_socket.send(message.encode())
    
    def not_alone(self):
        """not_alone() : Vérifie si le joueur n'est pas seul dans la partie"""
        players = 0
        for label in self.player_label_list:
            if "color='green'" in label.text():
                players +=1
        #On vérifie si le joueur n'est pas seul
        if players > 1:
            return True
        else:
            return False

    def ready(self):
        """ready() : Indique au serveur que le joueur est prêt"""
        global username
        if not self.join:
            if self.start_button.isEnabled():
                self.start_button.setEnabled(False)
            else:
                self.start_button.setEnabled(True)

            if self.rules_button.isEnabled():
                self.rules_button.setEnabled(False)
            else:
                self.rules_button.setEnabled(True)
            message = f"READY_TO_PLAY|{username}"
        else:
            message = f"READY_TO_PLAY_JOIN|{username}"
        client_socket.send(message.encode())

        if self.ready_button.text() == langue.langue_data["ClientWindow__ready_button__ready_state_text"]:
            self.ready_button.setText(langue.langue_data["ClientWindow__ready_button__not_ready_state_text"])
        else:
            self.ready_button.setText(langue.langue_data["ClientWindow__ready_button__ready_state_text"])
        
    def user_ready(self, player : str, ready : bool):
        """user_ready() : Indique que le joueur est prêt en mettant son pseudo en vert
        
        Args:
            player (str): Pseudo du joueur"""
        try:
            for label in self.player_label_list:
                if label.text() == player or label.text() == f"<font color='green'>{player}</font>":
                    if ready:
                        label.setText(f"<font color='green'>{player}</font>")
                    else:
                        label.setText(player)
        except IndexError:
            pass
        except AttributeError:
            pass

    def reset_ready_user(self):
        """reset_ready_user() : Réinitialise les joueurs prêts"""
        for label in self.player_label_list:
            match = re.search(r"<font color='green'>(.*?)</font>", label.text())
            if match:
                label.setText(match.group(1))                    

    def setup_join_game(self, layout : QGridLayout):
        """setup_join_game(layout) : Mise en place de la fenêtre pour rejoindre une partie
        
        Args:
            layout (QGridLayout): Layout de la fenêtre principale"""
        self.join_menu_loaded = True
        self.kill_button_animation_timer()
        layout.removeWidget(self.create_game_button)
        layout.removeWidget(self.join_game)

        layout = QVBoxLayout()
        sub_layout = QGridLayout()
        button_layout = QHBoxLayout()

        central_widget = QWidget()
        sub_widget = UnderlineWidget()
        button_widget = QWidget()

        self.home_logo = QPixmap(f"{image_path}home.png")
        self.home_logo_hover = QPixmap(f"{image_path}home-hover.png")
        self.home_button = HoverPixmapButton(self.home_logo, self.home_logo_hover)
        self.home_button.setFixedSize(screen_width//15, screen_width//15)
        self.home_button.setObjectName("other_buttons")
        self.home_button.setIcon(QIcon(self.home_logo))
        self.home_button.setIconSize(self.home_button.size())
        self.home_button.clicked.connect(self.leave_join_menu)

        self.settings_logo = QPixmap(f"{image_path}settings.png")
        self.settings_logo_hover = QPixmap(f"{image_path}settings-hover.png")
        self.settings = HoverPixmapButton(self.settings_logo, self.settings_logo_hover)
        self.settings.setFixedSize(screen_width//15, screen_width//15)
        self.settings.setObjectName("other_buttons")
        self.settings.setIcon(QIcon(self.settings_logo))
        self.settings.setIconSize(self.settings.size())
        self.settings.clicked.connect(self.display_settings)

        self.wifi_label = QLabel("WIFI", self)
        self.wifi_label.setObjectName("wifi_label")
        self.wifi_label.setFixedSize(screen_width//15, screen_width//15)
        self.wifi_label.setPixmap(self.wifi_logo.scaled(self.wifi_label.width(), self.wifi_label.height(), Qt.KeepAspectRatio))

        self.join_label = LinearGradiantLabel(langue.langue_data["ClientWindow__join_label__text"], color1=QColor(84,58,180,255), color2=QColor(253,89,29,255))
        self.join_label.setObjectName("join_label")
        self.join_label.setAlignment(Qt.AlignCenter)
        self.join_label.setFixedWidth(screen_width//2)
        # Création du QListWidget
        self.game_list_widget = QListWidget()
        self.game_list_widget.setObjectName("game_list_widget")
        self.game_list_widget.setSpacing(15)
        self.game_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.game_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(sub_widget)
        layout.addWidget(self.game_list_widget)

        sub_layout.addWidget(button_widget, 0, 0, Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(self.join_label, 0, 1, Qt.AlignmentFlag.AlignCenter)
        sub_layout.addWidget(self.wifi_label, 0, 2, Qt.AlignmentFlag.AlignRight)

        button_layout.addWidget(self.home_button)
        button_layout.addWidget(self.settings)

        central_widget.setLayout(layout)
        sub_widget.setLayout(sub_layout)
        button_widget.setLayout(button_layout)
        self.setCentralWidget(central_widget)

        receiver_thread.game_created.connect(self.add_item)
        receiver_thread.game_deleted.connect(self.delete_item)
        client_socket.send(f"GET_GAMES|{username}".encode())

    def display_sylb(self, sylb : str, player : str | None):
        """display_sylb(sylb) : Affiche la syllabe dans la fenêtre principale
        
        Args:
            sylb (str): Syllabe à afficher
            player (str: Pseudo du joueur)"""
        self.syllabe_label.setText(sylb)
        if self.previous_player:
            self.change_player(self.previous_player, 6, 12)
        self.change_player(player, 5.25, 20)
        self.previous_player = player
        ambiance_sound.sound_effects.next_sound.play()
        self.bomb_label.start_loop_animation()
        if player == username:
            self.text_line_edit.setEnabled(True)
            self.text_line_edit.setFocus()

    def add_item(self, game_name : str, private_game : bool, players_number : int, langue : str) -> None:
        """Ajoute un élément au QListWidget
        
        Args:
            game_name (str): Nom de la partie
            private_game (bool): True si la partie est privée, False sinon
            players_number (int): Nombre de joueurs dans la partie"""
        cadenas_icon = QPixmap(f"{image_path}cadenas.png")
        globe_icon = QPixmap(f"{image_path}globe.png")
        try:
            if not self.game_list_widget.findChild(QPushButton, game_name):     
                self.private_game_label = QLabel()
                size = self.private_game_label.fontMetrics().width('A'*4)
                if private_game == "False":
                    color1, color2 = QColor(100,198,129,1), QColor(197,186,255,1)
                    self.private_game_label.setPixmap(globe_icon.scaled(size, size, Qt.KeepAspectRatio))
                else:
                    color1, color2 = QColor(211,133,214,1), QColor(253,212,145,1)
                    self.private_game_label.setPixmap(cadenas_icon.scaled(size, size, Qt.KeepAspectRatio))
                self.private_game_label.setAlignment(Qt.AlignCenter)  # Set alignment to center

                info_game_widget = QWidget()
                info_game_layout = QHBoxLayout(info_game_widget)
                self.langue_label = QLabel(langue[:2].upper(), self)
                self.langue_label.setObjectName("langue_label")
                self.join_game_pushbutton = QPushButton(f"{game_name}")
                self.join_game_pushbutton.setObjectName(game_name)
                self.join_game_pushbutton.setStyleSheet("background-color: transparent; border: None")
                info_game_widget.setFixedHeight(int(self.join_game_pushbutton.sizeHint().height()*3.4))

                self.people_label = QLabel(f"{players_number}/8")
                self.people_label.setObjectName("people_label")
                
                item = QListWidgetItem(self.game_list_widget)
                item_widget = QWidget()
                item_widget.setStyleSheet("font-size: 25pt;")
                converted_game_name = game_name.replace(" ", "_")
                item_widget.setObjectName(converted_game_name)
                game_widget = AnimatedGameWidget(converted_game_name, color1, color2)
                
                info_game_layout.addWidget(self.join_game_pushbutton)
                info_game_layout.addWidget(self.langue_label)
                info_game_layout.setStretchFactor(self.join_game_pushbutton, 2)
                info_game_layout.setContentsMargins(0, 0, 0, 0)

                item_layout = QVBoxLayout(item_widget)
                item_layout.setStretch(0, 2)
                item_layout.setContentsMargins(0, 0, 0, 0)
                game_layout = QHBoxLayout(game_widget)
                item_layout.addWidget(game_widget)

                game_layout.addWidget(self.private_game_label)
                game_layout.addWidget(self.people_label)
                game_layout.addWidget(info_game_widget)
                game_layout.setStretch(2, 1)
                item_widget.setLayout(item_layout)

                item.setSizeHint(item_widget.sizeHint())
                self.game_list_widget.addItem(item)
                self.game_list_widget.setItemWidget(item, item_widget)
                
                game_widget.click_widget_signal.connect(lambda: self.show_join_window(game_name, private_game))
                self.join_game_pushbutton.clicked.connect(lambda: self.show_join_window(game_name, private_game))
            else:
                return
        except RuntimeError:
            pass

    def delete_item(self, creator : str):
        """delete_item(creator) : Supprime un élément du QListWidget
        
        Args:
            creator (str): Créateur de la partie"""
        try:
            for index in range(self.game_list_widget.count()):
                item = self.game_list_widget.item(index)
                button = self.game_list_widget.itemWidget(item).findChild(QPushButton)
                if button.objectName() == creator:
                    row = self.game_list_widget.row(item)
                    self.game_list_widget.takeItem(row)
                    break
        except RuntimeError:
            pass

    def show_join_window(self, game_name : str, private_game : str):
        """show_join_window(game_name) : Affiche la fenêtre de mot de passe
        
        Args:
            game_name (str): Nom de la partie
            private_game (str): À convertir en bool, True si la partie est privée, False sinon"""
        private_game = self.bool_convert(private_game)
        self.join_window = JoinGameWindow(game_name, private_game, window)
        if private_game:
            self.join_window.show()
            self.join_window.setup()
        else:
            try:
                self.join_window.join_lobby()
            except Exception as e:
                print(e, "join lobby")

    def bool_convert(self, boolean : str) -> bool:
        """bool_convert(boolean) : Convertit un str en bool"""
        if boolean == "False":
            return False
        else:
            return True

    def send_message(self):
        """send_message() : Envoie un message au serveur"""
        global username
        syllabe = syllabes[-1]
        message = f"NEW_SYLLABE|{username}|{self.text_line_edit.text()}|{syllabe}"
        client_socket.send(message.encode())
        self.text_line_edit.clear()

    def display_text(self):
        """display_text() : Affiche le texte dans le label de la fenêtre principale"""
        global username
        text = self.text_line_edit.text()
        syllabe = syllabes[-1]
        text = re.sub(r'[^a-zA-ZÀ-ÿ]', '', text)
        self.text_line_edit.setText(text)
        highlighted_text = text.lower()        
        for s in [syllabe, syllabe.upper(), syllabe.lower(), syllabe.capitalize(), syllabe.upper().capitalize()]:
            if s in text or unidecode.unidecode(s) in unidecode.unidecode(text).upper():
                text = text.lower()
                highlighted_text = text.replace(s, f"<b>{s}</b>")
        self.text_label.setText(highlighted_text)
        self.mqtt_sub.publish(f"{username}|{highlighted_text}")

    def display_rules(self):
        """display_rules() : Affiche les règles du jeu"""
        self.rules_window = RulesWindow()

    def display_settings(self):
        """display_settings() : Affiche les paramètres"""
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def show_game_is_full_window(self):
        """message_box_dialog() : Affiche la fenêtre qui informe que la partie est pleine"""
        self.game_is_full_window = GameIsFullWindow(self)
        self.game_is_full_window.show()

    def set_avatarBorder_properties(self):
        """set_avatarBorder_properties() : Mise en place des bordures animées"""
        self.labels = [self.player1_avatar_label, self.player2_avatar_label, self.player3_avatar_label, self.player4_avatar_label, self.player5_avatar_label, self.player6_avatar_label, self.player7_avatar_label, self.player8_avatar_label]
        self.avatarBorderBox.setup_timer(self)
        self.label_loaded = True
    
    def set_buttonBorder_properties(self):
        """set_buttonBorder_properties() : Mise en place des bordures animées"""
        self.buttons = [self.create_game_button, self.join_game]
        self.buttonBorderBox.setup_timer(self)
        self.button_loaded = True

    def kill_button_animation_timer(self):
        """kill_button_animation_timer() : Arrête les bordures animées"""
        self.button_loaded = False
        try:
            self.buttonBorderBox.kill_timer(self)
        except AttributeError:
            pass

    def draw_styled_button(self):
        """draw_styled_button() : Dessine les bordures animées des boutons"""
        if isinstance(self.draw_rules_button, DrawStyledButton):
            if self.should_draw_rules_button:
                self.draw_rules_button.draw_border(7, self.rules_button.color1)
            else:
                self.draw_rules_button.draw_border(0, self.rules_button.color2)

        if isinstance(self.draw_ready_button, DrawStyledButton):
            if self.should_draw_ready_button:
                self.draw_ready_button.draw_border(7, self.ready_button.color1)
            else:
                self.draw_ready_button.draw_border(0, self.ready_button.color2)

        if isinstance(self.draw_start_button, DrawStyledButton):
            if self.should_draw_start_button:
                self.draw_start_button.draw_border(7, self.start_button.color1)
            else:
                self.draw_start_button.draw_border(0, self.start_button.color2)

    def paintEvent(self, event : QPaintEvent):
        """paintEvent(event) : Dessine les bordures animées"""
        if self.label_loaded:
            self.avatarBorderBox.border(self, self.labels)
            self.draw_styled_button()
        if self.button_loaded:
            self.buttonBorderBox.border(self, self.buttons)
        return super().paintEvent(event)
        
    def mouseDoubleClickEvent(self, event: QMouseEvent | None):
        """mouseDoubleClickEvent(event) : Double clic de la souris
        
        Args:
            event (QMouseEvent): Événement de la souris"""
        self.load_select_screen()

    def keyPressEvent(self, event: QKeyEvent):
        """keyPressEvent(event) : Appui sur une touche du clavier
        
        Args:
            event (QKeyEvent): Événement du clavier"""
        if not self.button_loaded and not self.label_loaded and not self.join_menu_loaded:
            self.load_select_screen()
        elif self.join_menu_loaded:
            if event.key() == Qt.Key_Escape:
                self.leave_join_menu()
        elif self.button_loaded:
            if event.key() == Qt.Key_Escape:
                for button in self.buttons:
                    button.clearFocus()
                self.display_settings()
        elif self.label_loaded:
            if event.key() == Qt.Key_Escape:
                self.leave_game()        

    def closeEvent(self, event: QEvent) -> None:
        """closeEvent(event) : Ferme la fenêtre et coupe les thread mqtt
        
        Args:
            event(QEvent): Événement de fermeture"""
        try:
            self.mqtt_sub.stop_loop()
        except AttributeError:
            pass
        ping_thread.running = False
        event.accept()
    
    def load_select_screen(self):
        """load_select_screen() : Charge la fenêtre de sélection de l'avatar"""
        self.title_screen_label.stop_loop_animation()
        music.choose_music(1)
        self.setup(join = False)
        self.loaded_select_screen = True
        self.set_animated_properties()
        self.mouseDoubleClickEvent = self.emptyFunction

    def ping(self, ping : float, working_ping : bool):
        """ping() : Modifie l'image du label de connexion
        
        Args:
            ping (float): Ping de la connexion"""
        wifi_logo_green = QPixmap(f"{image_path}wifi-green.png")
        wifi_logo_orange = QPixmap(f"{image_path}wifi-jaune.png")
        wifi_logo_red = QPixmap(f"{image_path}wifi-red.png")
        wifi_logo_black = QPixmap(f"{image_path}wifi.png")
        if ping <= 60 and ping > 0:
            self.wifi_logo = wifi_logo_green
        elif ping > 60 and ping <= 150:
            self.wifi_logo = wifi_logo_orange
        elif ping > 150:
            self.wifi_logo = wifi_logo_red
        else:
            self.wifi_logo = wifi_logo_black
            self.manage_conexion_info_window(working_ping)
        try:
            self.wifi_label.setPixmap(self.wifi_logo.scaled(self.wifi_label.width(), self.wifi_label.height(), Qt.KeepAspectRatio))
        except AttributeError:
            pass
        except RuntimeError:
            pass
        
    def manage_conexion_info_window(self, working_ping):
        """manage_conexion_info_window(working_ping) : Gère la fenêtre d'information de connexion
        
        Args:
            working_ping (bool): True si le ping est correct, False sinon"""
        if not working_ping:
            if not isinstance(self.connexion_info_window, ConnexionInfoWindow) and self.loaded_select_screen:
                self.connexion_info_window = ConnexionInfoWindow(self)
                self.connexion_info_window.show()

if __name__ == "__main__":
    """__main__() : Lance l'application"""
    
    receiver_thread = ReceptionThread()
    ping_thread = PingThread()
    ping_thread.start()
    window = ClientWindow()
    login = Login() 
    login.show()
    sys.exit(app.exec_())