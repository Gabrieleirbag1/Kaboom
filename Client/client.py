from client_utils import *
from client_styles import AvatarBorderBox, AnimatedButton, AnimatedWindow, AnimatedGameWidget, ButtonBorderBox, LinearGradiantLabel, StyledBorderButton, DrawStyledButton
from client_reception import ReceptionThread, ConnectThread, PingThread
from client_windows import RulesWindow, GameCreationWindow, JoinGameWindow, AvatarWindow, LeaveGameWindow, ConnexionInfoWindow, GameIsFullWindow, SettingsWindow, VictoryWindow, FilterWindow, handle_username
from client_mqtt import Mqtt_Sub
from client_objects import ClickButton, UnderlineWidget, UnderlineLineEdit, HoverPixmapButton
from client_animations import LoadSprites, AvatarAnimatedLabel, LoopAnimatedLabel
from client_logs import ErrorLogger

ErrorLogger.setup_logging()


class Login(QMainWindow):
    """Login window for the client
    
    Attributes:
        avatar_name (str): Name of the avatar
        avatar_tuple (tuple): Tuple of avatars
        avatar_window (AvatarWindow): The avatar window
    """
    login_accepted = pyqtSignal(bool)

    def __init__(self, avatar_name: str = "no-avatar"):
        """
        Initializes the login window.

        Args:
            avatar_name (str): Name of the avatar.
        """
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
        """
        Sets up the login window.
        """
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
        self.logo_label.resize(int(screen_width // 4), int(screen_height // 4))
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
        self.avatar_button.setIcon(QIcon(f"{avatar_path}{self.avatar_name}.png"))
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
        """
        Prevents the user from entering special characters.
        """
        text = self.username_edit.text()
        text = re.sub(r'[^a-zA-ZÀ-ÿ0-9]', '', text)
        self.username_edit.setText(text)

    def setup_threads(self):
        """
        Sets up the reception and connection threads.
        """
        self.connect_thread = ConnectThread()
        self.connect_thread.start()
        self.connect_thread.connection_established.connect(self.connect_to_server)

    def connect_to_server(self):
        """
        Connects to the server.
        """
        receiver_thread.start()

    def send_username(self):
        """
        Sends the username to the server.
        """
        global username
        username = self.username_edit.text()
        try:
            if username != "" and not username.isspace():
                handle_username(username)
                if self.avatar_name == "no-avatar":
                    self.avatar_name = random.choice(self.avatar_tuple)
                send_server(f"NEW_USER|{username}|{self.avatar_name}".encode())
            else:
                self.alert_label.setText(langue.langue_data["Login__alert_label__empty_error"])
                button_sound.sound_effects.error_sound.play()
        except BrokenPipeError:
            self.alert_label.setText(langue.langue_data["Login__alert_label__connection_error"])
            button_sound.sound_effects.error_sound.play()
        except OSError:
            self.alert_label.setText(langue.langue_data["Login__alert_label__connection_error"])
            button_sound.sound_effects.error_sound.play()

    def set_new_avatar(self, avatar_name: str):
        """
        Changes the user's avatar.

        Args:
            avatar_name (str): Name of the avatar.
        """
        self.avatar_name = avatar_name
        self.avatar_button.setIcon(QIcon(f"{avatar_path}{avatar_name}.png"))

    def show_window(self, name_correct: bool):
        """
        Displays the main window if the username is correct.

        Args:
            name_correct (bool): True if the username is correct, False otherwise.
        """
        if name_correct:
            self.close()
            window.set_avatar(self.avatar_name)
            window.start_setup(join=False)
        else:
            self.alert_label.setText(langue.langue_data["Login__alert_label__already_used_error"])
            button_sound.sound_effects.error_sound.play()

    def show_avatar_window(self):
        """
        Displays the avatar selection window.
        """
        self.avatar_window.show()
        self.avatar_window.activateWindow()

class ClientWindow(AnimatedWindow):
    """Main client window that inherits from AnimatedWindow
    
    Attributes:
        join (bool): True if the player has joined a game, False otherwise
        ingame (bool): True if the player is in a game, False otherwise
        filter (str): The filter for the game
        previous_player (str): The previous player
        should_draw (bool): True if the player should draw, False otherwise
        connexion_info_window (ConnexionInfoWindow): The connexion info window
        loaded_select_screen (bool): True if the select screen is loaded, False otherwise
        death_mode_state (int): The death mode state
        player(str): The player name

    Signals:
        correct_mdp (pyqtSignal): Signal for correct password
        in_game_signal (pyqtSignal): Signal for the game
        waiting_room_close_signal (pyqtSignal): Signal to close the waiting room
        join_window_close_signal (pyqtSignal): Signal to close the join game window
        players_number_signal (pyqtSignal): Signal for the number of players"""
    correct_mdp = pyqtSignal(bool)
    in_game_signal = pyqtSignal(str, int)
    waiting_room_close_signal = pyqtSignal()
    join_window_close_signal = pyqtSignal(str)
    players_number_signal = pyqtSignal(str)

    def __init__(self, join: bool = False):
        """ Constructor of the ClientWindow class

        Args:
            join (bool): True if the player has joined a game, False otherwise"""
        super().__init__()
        self.join = join
        
        self.ingame: bool = False
        self.filter = None
        self.previous_player: str  | None = None
        self.should_draw: bool = True
        self.connexion_info_window: ConnexionInfoWindow | None = None
        self.loaded_select_screen: bool = False
        self.death_mode_state: int = 0
        self.player: str = ""

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
        """
        Sets up the game creation window.

        Attributes:
            creation_game (GameCreationWindow): The game creation window instance.
        """
        layout = QGridLayout()
        self.creation_game = GameCreationWindow(layout, receiver_thread)
        self.creation_game.create_game_signal.connect(lambda game_name, password, private_game: self.setup_game(layout, game_name, password, private_game))
        
    def setup_animation_instances(self):
        """
        Sets up the animation instances.
        """
        self.avatarBorderBox = AvatarBorderBox()
        self.avatars_colors_dico = self.avatarBorderBox.setup_colors(self)
        self.label_loaded = False
        self.buttonBorderBox = ButtonBorderBox()
        self.buttonBorderBox.setup_colors(self)
        self.button_loaded = False

    def set_avatar(self, avatar_name: str):
        """
        Sets the user's avatar.

        Args:
            avatar_name (str): Name of the avatar.
        """
        self.avatar_name = avatar_name

    def start_setup(self, join: bool = False):
        """
        Sets up the main window.

        Args:
            join (bool): True if the player has joined a game, False otherwise.
        """
        self.setup_title_screen(join)

    def setup_title_screen(self, join: bool):
        """
        Sets up the title screen.

        Args:
            join (bool): True if the player has joined a game, False otherwise.
        """
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

    def setup(self, join: bool) -> QGridLayout:
        """
        Sets up the main window.

        Args:
            join (bool): True if the player has joined a game, False otherwise.

        Returns:
            QGridLayout: The layout of the main window.
        """
        self.set_rules()
        self.setWindowTitle("KABOOM")
        self.setStyleSheet(main_stylesheet)
        layout = QGridLayout()
        
        self.create_game_button = AnimatedButton("create_game_pushbutton", QColor(164, 255, 174, 1), QColor(187, 186, 255, 1))
        self.create_game_button.setObjectName("create_game_pushbutton")
        self.create_game_button.setText(langue.langue_data["ClientWindow__create_game_button__text"])
        layout.addWidget(self.create_game_button, 1, 0, Qt.AlignHCenter)

        self.join_game = AnimatedButton("join_game_pushbutton", QColor(211, 133, 214, 1), QColor(253, 212, 145, 1))
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
        """
        Sets up the game creation window.
        """
        self.creation_game.show()
        self.creation_game.activateWindow()
        self.creation_game.setup()
        self.creation_game.game_name_lineedit.setFocus()

    def set_rules(self):
        """
        Sets the game rules.
        """
        rules.clear()
        rules.extend([5, 7, 3, 2, 3, 1, 0])

    def join_tools(self, response: str):
        """
        Handles the messages for joining a game.

        Args:
            response (str): The message from the game.
        """
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
                # print("Other player joined")
                pass

        elif reply[1] == "WRONG-PASSWORD":
            self.correct_mdp.emit(False)
        
        elif reply[1] == "GET-PLAYERS":
            self.get_players(players=reply[2], avatars=reply[3], ready_players=reply[4])

        elif reply[1] == "ALREADY-IN-GAME":
            game_name = reply[2]
            players_number = int(reply[3])
            self.in_game_signal.emit(game_name, players_number)

        elif reply[1] == "NEW-PLAYER":
            self.players_number(game_name=reply[2], leave=False)

        elif reply[1] == "LEAVE-GAME":
            if "GAME-DELETED" in reply[3]:
                game_name = reply[4]
                self.delete_item(game_name)
            else:
                game_name = reply[2]
            self.players_number(game_name=game_name, leave=True)

        elif reply[1] == "GAME-FULL":
            self.show_game_is_full_window()

    def game_tools(self, game_message: str):
        """
        Handles the messages for the game.

        Args:
            game_message (str): The message from the game.
        """
        reply = game_message.split("|")        
        if reply[1] == "RIGHT":
            player = reply[2]
            self.text_label.clear()
            if player == username:
                self.text_line_edit.setEnabled(False)

        elif reply[1] == "WRONG":
            button_sound.sound_effects.error_sound.play()
            self.text_label.clear()
        
        elif reply[1] == "TIME'S-UP":
            self.player = reply[2]
            self.remove_heart(self.player)
            self.bomb_label.stop_loop_animation()
            self.bomb_label.setup(self, "bombe_disparition")
            self.bomb_label.start_animation()
            
            if reply[2] == username:
                self.text_line_edit.setEnabled(False)
                self.text_line_edit.clear()
                self.text_label.clear()
        
        elif reply[1] == "GAME-STARTED":
            self.ingame = True
            death_mode_state: int = int(reply[3])
            self.death_mode_state = death_mode_state
            self.bomb_label.setup(self, "bombe_apparition")
            self.bomb_label.start_animation()

        elif reply[1] == "GAME-ENDED":
            self.ingame = False
            self.unsetup_game()
            self.victory_window = VictoryWindow(self, eval(reply[3]))
            self.victory_window.show()

        elif reply[1] == "LIFES-RULES":
            self.ready_button.setEnabled(False)
            self.setup_hearts_rules(lifes=int(reply[2]), ready_players=reply[3])

    def lobby_state_tools(self, lobby_state: str):
        """
        Handles the messages for the lobby.

        Args:
            lobby_state (str): The message from the lobby.
        """
        reply = lobby_state.split("|")

        if reply[1] == "NEW-CREATOR":
            self.new_creator(game_name=reply[2], creator=reply[3])

        elif reply[1] == "LEAVE-GAME":
            self.remove_a_player(game_name=reply[2], player=reply[3])

        elif reply[1] == "PLAYER-DECO":
            self.deco_a_player(player=reply[2])

        elif reply[1] == "READY":
            self.user_ready(player=reply[2], ready=self.bool_convert(reply[3]))

    def set_mqtt(self, game_name: str, username: str):
        """
        Sets up MQTT clients.

        Args:
            game_name (str): Name of the game.
            username (str): Name of the user.
        """
        # Setup MQTT client to receive messages
        self.mqtt_sub = Mqtt_Sub(topic=game_name, label=self.text_label, user=username)
        self.mqtt_sub.start()
        # Setup MQTT client to send messages

    def check_player_already_placed(self, player: str):
        """
        Checks if the player is already placed.

        Args:
            player (str): Name of the player.
        """
        for label in self.player_label_list:
            if player == label.text() or f"<font color='green'>{player}</font>" == label.text():
                return True
        return False
        

    def get_players(self, players: list, avatars: list, ready_players: list):
        """
        Retrieves the players in the game.

        Args:
            players (list): List of players in the game.
            avatars (list): List of avatars of the players.
            ready_players (list): List of players ready to play.
        """
        players = players.split(",")
        avatars = avatars.split(",")
        ready_players = ready_players.split(",")
        for player, avatar, ready in zip(players, avatars, ready_players):
            if player != "":
                for i, (label, avatar_label) in enumerate(zip(self.player_label_list, self.avatar_label_list)):
                    if self.check_player_already_placed(player):
                        continue
                    else:
                        if label.text() == langue.langue_data["ClientWindow__player_label__en_attente_state_text"]:
                            if not self.bool_convert(ready):
                                label.setText(player)
                            else:
                                label.setText(f"<font color='green'>{player}</font>")
                            new_avatar = QPixmap(f"{avatar_path}{avatar}.png")
                            avatar_label.primary_pixmap_name = avatar
                            avatar_label.setPixmap(new_avatar.scaled(avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                            getattr(self, f"player{i+1}_border_color").setRgb(*self.avatars_colors_dico[avatar][0])
                            getattr(self, f"player{i+1}_border_color2").setRgb(*self.avatars_colors_dico[avatar][1])

                            avatar_label.setup(self, avatar.replace("-avatar", ""))
                            break
                        else:
                            continue

    def reset_avatars(self):
        """
        Resets the avatars of the players.
        """
        for label, avatar_label in zip(self.player_label_list, self.avatar_label_list):
            if label.text() != langue.langue_data["ClientWindow__player_label__en_attente_state_text"]:
                avatar = QPixmap(f"{avatar_path}{avatar_label.primary_pixmap_name}.png")
                avatar_label.setPixmap(avatar.scaled(avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                avatar_label.setup(self, avatar_label.primary_pixmap_name.replace("-avatar", ""))

    def players_number(self, game_name: str, leave: bool):
        """
        Updates the number of players in the game.

        Args:
            game_name (str): Name of the game.
            leave (bool): True if the player leaves the game, False otherwise.
        """
        try:
            for index in range(self.game_list_widget.count()):
                item = self.game_list_widget.item(index)
                button = self.game_list_widget.itemWidget(item).findChild(QPushButton)
                label = self.game_list_widget.itemWidget(item).findChild(QLabel, "people_label")
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

    def change_player(self, player: str, avatar_size: float, border_size: int, padding_top: int):
        """
        Updates the interface for the previous player.

        Args:
            player (str): Name of the player.
            avatar_size (float): Size of the avatar.
            border_size (int): Size of the avatar border.
            padding_top (int): Padding of the avatar.
        """
        border_size
        try:
            for i, (label, avatar_label, heart_widget) in enumerate(zip(self.player_label_list, self.avatar_label_list, self.heart_widgets_list)):
                if label.text() == player or label.text() == f"<i><font color='red'>{player}</font></i>" or label.text() == f"<font color='green'>{player}</font>":
                    avatar_label.setFixedSize(int(screen_width / avatar_size), int(screen_height / avatar_size))
                    avatar_label.setPixmap(avatar_label.pixmap().scaled(avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                    self.player_border_size[i] = border_size
                    heart_widget.setContentsMargins(0, padding_top, 0, 0)
                    if player != self.previous_player:
                        avatar_label.play_animation()
                    break
        except IndexError:
            pass

    def remove_a_player(self, game_name: str, player: str):
        """
        Removes a player from the game.

        Args:
            game_name (str): Name of the game.
            player (str): Name of the player to remove.
        """
        try:
            for label, avatar_label in zip(self.player_label_list, self.avatar_label_list):
                if label.text() == player or label.text() == f"<i><font color='red'>{player}</font></i>" or label.text() == f"<font color='green'>{player}</font>":
                    label.setText(langue.langue_data["ClientWindow__player_label__en_attente_state_text"])
                    avatar = QPixmap(f"{avatar_path}no-avatar.png")
                    avatar_label.setPixmap(avatar.scaled(avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                    avatar_label.setup(self, "no-avatar")
                    break
        except IndexError:
            infos_logger.error(f"[HANDLED ERROR] IndexError in remove_a_player: {player} not found in player_label_list")

    def deco_a_player(self, player: str):
        """
        Disconnects a player from the game.

        Args:
            player (str): Name of the player to disconnect.
        """
        try:
            for label in self.player_label_list:
                if label.text() == player or label.text() == f"<font color='green'>{player}</font>":
                    label.setText(f"<i><font color='red'>{player}</font></i>")
                    break
        except IndexError:
            infos_logger.error(f"[HANDLED ERROR] IndexError in deco_a_player: {player} not found in player_label_list")
        except RuntimeError:
            infos_logger.error(f"[HANDLED ERROR] RuntimeError in deco_a_player: {player} not found in player_label_list")
        except AttributeError:
            infos_logger.error(f"[HANDLED ERROR] AttributeError in deco_a_player: {player} not found in player_label_list")
    

    def kill_a_player(self, avatar: AvatarAnimatedLabel):
        """
        Changes the player's avatar to a tombstone.

        Args:
            avatar (AvatarAnimatedLabel): Avatar of the player.
        """
        if avatar.is_animating():
            avatar.stop_animation()
        tombe: str = random.choice(["tombe1_", "tombe2_", "tombe3_", "tombe4_"])
        tombe_sound = getattr(ambiance_sound.sound_effects, f"{tombe}sound")
        tombe_sound.play()
        avatar.setup(self, tombe)
        avatar.start_animation()

    def remove_heart(self, player: str):
        """
        Removes a heart from the player.

        Args:
            player (str): Name of the player."""
        if player == self.player1_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player1_label.text() or f"<font color='green'>{player}</font>" == self.player1_label.text():
            self.heart_list_widget1.takeItem(self.heart_list_widget1.count() - 1)
            if self.heart_list_widget1.count() == 0:
                self.kill_a_player(self.player1_avatar_label)
        elif player == self.player2_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player2_label.text() or f"<font color='green'>{player}</font>" == self.player2_label.text():
            self.heart_list_widget2.takeItem(self.heart_list_widget2.count() - 1)
            if self.heart_list_widget2.count() == 0:
                self.kill_a_player(self.player2_avatar_label)
        elif player == self.player3_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player3_label.text() or f"<font color='green'>{player}</font>" == self.player3_label.text():
            self.heart_list_widget3.takeItem(self.heart_list_widget3.count() - 1)
            if self.heart_list_widget3.count() == 0:
                self.kill_a_player(self.player3_avatar_label)
        elif player == self.player4_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player4_label.text() or f"<font color='green'>{player}</font>" == self.player4_label.text():
            self.heart_list_widget4.takeItem(self.heart_list_widget4.count() - 1)
            if self.heart_list_widget4.count() == 0:
                self.kill_a_player(self.player4_avatar_label)
        elif player == self.player5_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player5_label.text() or f"<font color='green'>{player}</font>" == self.player5_label.text():
            self.heart_list_widget5.takeItem(self.heart_list_widget5.count() - 1)
            if self.heart_list_widget5.count() == 0:
                self.kill_a_player(self.player5_avatar_label)
        elif player == self.player6_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player6_label.text() or f"<font color='green'>{player}</font>" == self.player6_label.text():
            self.heart_list_widget6.takeItem(self.heart_list_widget6.count() - 1)
            if self.heart_list_widget6.count() == 0:
                self.kill_a_player(self.player6_avatar_label)
        elif player == self.player7_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player7_label.text() or f"<font color='green'>{player}</font>" == self.player7_label.text():
            self.heart_list_widget7.takeItem(self.heart_list_widget7.count() - 1)
            if self.heart_list_widget7.count() == 0:
                self.kill_a_player(self.player7_avatar_label)
        elif player == self.player8_label.text() or f"<i><font color='red'>{player}</font></i>" == self.player8_label.text() or f"<font color='green'>{player}</font>" == self.player8_label.text():
            self.heart_list_widget8.takeItem(self.heart_list_widget8.count() - 1)
            if self.heart_list_widget8.count() == 0:
                self.kill_a_player(self.player8_avatar_label)

    def unsetup_game(self):
        """
        Resets the game elements.
        """
        self.start_button.setEnabled(False)
        self.ready_button.setEnabled(True)
        if not self.join:
            self.rules_button.setEnabled(True)
        self.ready_button.setText(langue.langue_data["ClientWindow__ready_button__not_ready_state_text"])
        self.text_line_edit.setEnabled(False)

        self.change_player(self.previous_player, 6.2, int(screen_height//90), int(screen_height//108))
        self.clear_game()
        self.reset_ready_user()

    def clear_game(self):
        """
        Clears the game window elements.
        """
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

    def new_creator(self, game_name: str, creator: str):
        """
        Updates the creator of the game.

        Args:
            game_name (str): Name of the game.
            creator (str): Creator of the game.
        """
        self.join = False
        self.show_password_button.setEnabled(True)
        if self.ready_button.text() == langue.langue_data["ClientWindow__ready_button__ready_state_text"]:
            self.start_button.setEnabled(True)
        else:
            self.rules_button.setEnabled(True)  

    def setup_game(self, layout: QGridLayout, game_name: str, password: str, private_game: bool):
        """
        Sets up the game window.

        Args:
            layout (QGridLayout): Layout of the main window.
            game_name (str): Name of the game.
            password (str): Password of the game.
            private_game (bool): True if the game is private, False otherwise.
        """
        global username
        self.join_menu_loaded = False
        self.kill_button_animation_timer()
        self.check_setup(layout, game_name, password, private_game)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.player1_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player2_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player3_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player4_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player5_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player6_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player7_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)
        self.player8_label = QLabel(langue.langue_data["ClientWindow__player_label__en_attente_state_text"], self)

        self.player_label_list = [self.player1_label, self.player2_label, self.player3_label, self.player4_label, self.player5_label, self.player6_label, self.player7_label, self.player8_label]
        
        for player_label in self.player_label_list:
            player_label.setObjectName("player_label")

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

        self.main_player_widget = QWidget()
        self.main_player_widget.setFixedHeight(int(screen_height * 0.85))
        self.main_player_layout = QHBoxLayout(self.main_player_widget)
        self.main_player_layout.setContentsMargins(35, 0, 35, 0)

        self.sub_1_player_widget = QWidget()
        self.sub_1_player_layout = QVBoxLayout(self.sub_1_player_widget)
        self.sub_1_player_layout.setContentsMargins(0, 0, 0, 0)

        self.sub_2_player_widget = QWidget()
        self.sub_2_player_layout = QVBoxLayout(self.sub_2_player_widget)
        self.sub_2_player_layout.setContentsMargins(0, 0, 0, 0)

        self.sub_sub_2_player_widget = QWidget()
        self.sub_sub_2_player_layout = QHBoxLayout(self.sub_sub_2_player_widget)
        self.sub_sub_2_player_layout.setContentsMargins(0, 0, 0, 0)

        self.sub_3_player_widget = QWidget()
        self.sub_3_player_layout = QVBoxLayout(self.sub_3_player_widget)
        self.sub_3_player_layout.setContentsMargins(0, 0, 0, 0)

        self.text_widget = QWidget()
        sub_layout = QVBoxLayout(self.text_widget)
        self.text_widget.setFixedHeight(int(screen_height * (0.85 * 2 / 3)))

        self.text_widget.setStyleSheet("padding: 0;")
        self.text_widget.setObjectName("text_widget")

        self.bomb_widget = QWidget()
        self.bomb_layout = QGridLayout(self.bomb_widget)
        self.bomb = QPixmap(f"{image_path}bombe.png")
        self.bomb_label = LoopAnimatedLabel()
        self.bomb_label.animation_finished.connect(self.bomb_animation)
        self.bomb_label.setObjectName("bomb_label")
        self.bomb_label.setFixedSize(int(screen_width // 3), int(screen_height // 3))
        self.bomb_label.setAlignment(Qt.AlignHCenter)

        self.bomb_layout.addWidget(self.bomb_label, 0, 0, Qt.AlignmentFlag.AlignCenter)

        self.text_sylb_widget = QWidget()
        self.text_sylb_layout = QGridLayout(self.text_sylb_widget)
        
        self.syllabe_label = QLabel("", self)
        self.syllabe_label.setObjectName("syllabe_label")

        self.text_label = QLabel("", self)
        self.text_label.setObjectName("text_label")

        self.text_line_edit = QLineEdit(self)
        self.text_line_edit.setObjectName("text_line_edit")

        self.text_line_edit.setPlaceholderText(langue.langue_data["ClientWindow__text_line_edit__placeholder"])
        self.text_line_edit.setEnabled(False)
        self.text_line_edit.setStyleSheet("padding: 20")
        self.text_line_edit.returnPressed.connect(self.send_syllabe_message)
        self.text_line_edit.textChanged.connect(self.display_text)

        self.text_line_edit.setFixedWidth(int(screen_width * 0.2))

        self.text_sylb_layout.addWidget(self.syllabe_label, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        self.text_sylb_layout.addWidget(self.text_label, 1, 0, Qt.AlignmentFlag.AlignHCenter)
        self.text_sylb_layout.addWidget(self.text_line_edit, 2, 0, Qt.AlignmentFlag.AlignHCenter)

        sub_layout.addWidget(self.bomb_widget, Qt.AlignmentFlag.AlignHCenter)
        sub_layout.addWidget(self.text_sylb_widget, Qt.AlignmentFlag.AlignHCenter)

        self.main_player_layout.addWidget(self.sub_1_player_widget, Qt.AlignmentFlag.AlignLeft)
        self.main_player_layout.addWidget(self.sub_2_player_widget, Qt.AlignmentFlag.AlignCenter)
        self.main_player_layout.addWidget(self.sub_3_player_widget, Qt.AlignmentFlag.AlignRight)

        self.sub_1_player_layout.addWidget(self.player1_widget)
        self.sub_1_player_layout.addWidget(self.player3_widget)
        self.sub_1_player_layout.addWidget(self.player7_widget)

        self.sub_sub_2_player_layout.addWidget(self.player5_widget)
        self.sub_sub_2_player_layout.addWidget(self.player6_widget)
        self.sub_2_player_layout.addWidget(self.text_widget)
        self.sub_2_player_layout.addWidget(self.sub_sub_2_player_widget)
        
        self.sub_3_player_layout.addWidget(self.player2_widget)
        self.sub_3_player_layout.addWidget(self.player4_widget)
        self.sub_3_player_layout.addWidget(self.player8_widget)

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
        self.home_button_game.setFixedSize(screen_width // 40, screen_width // 40)
        self.home_button_game.setObjectName("other_buttons")
        self.home_button_game.setIcon(QIcon(self.home_logo))
        self.home_button_game.setIconSize(self.home_button_game.size())
        self.home_button_game.clicked.connect(self.leave_game)

        self.settings_logo = QPixmap(f"{image_path}settings.png")
        self.settings_logo_hover = QPixmap(f"{image_path}settings-hover.png")
        self.settings = HoverPixmapButton(self.settings_logo, self.settings_logo_hover)
        self.settings.setFixedSize(screen_width // 40, screen_width // 40)
        self.settings.setObjectName("other_buttons")
        self.settings.setIcon(QIcon(self.settings_logo))
        self.settings.setIconSize(self.settings.size())
        self.settings.clicked.connect(self.display_settings)

        self.wifi_label = QLabel(parent=self)
        self.wifi_label.setObjectName("wifi_label")
        self.wifi_label.setFixedSize(screen_width // 40, screen_width // 40)
        self.wifi_label.setPixmap(self.wifi_logo.scaled(self.wifi_label.width(), self.wifi_label.height(), Qt.KeepAspectRatio))

        self.key_icon = QPixmap(f"{image_path}key.png")
        self.key_hover_icon = QPixmap(f"{image_path}key-hover.png")

        self.show_password_button = ClickButton(parent=self)
        self.show_password_button = HoverPixmapButton(self.key_icon, self.key_hover_icon, self)
        self.show_password_button.setObjectName("hover_buttons")
        self.show_password_button.setFixedSize(screen_width // 40, screen_width // 40)
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

        self.ready_button = StyledBorderButton(langue.langue_data["ClientWindow__ready_button__not_ready_state_text"], self, "ready_button", QColor(4, 245, 130), QColor(243, 108, 108))
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
        self.game_name_label.setFixedWidth(screen_width // 3)
        
        if self.join:  # If the player has joined a game
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

        self.top_widget = QWidget()
        self.top_layout = QGridLayout(self.top_widget)
        self.top_layout.setContentsMargins(50, 0, 50, 0)
        self.top_layout.addWidget(button_widget, 0, 0, Qt.AlignLeft)
        self.top_layout.addWidget(self.game_name_label, 0, 1, Qt.AlignHCenter)
        self.top_layout.addWidget(password_widget, 0, 2, Qt.AlignRight)

        self.bottom_widget = QWidget()
        self.bottom_widget.setFixedHeight(int(screen_height * 0.075))
        self.bottom_layout = QGridLayout(self.bottom_widget)
        self.bottom_layout.setContentsMargins(60, 0, 70, 0)
        self.bottom_layout.addWidget(self.rules_button, 0, 0, Qt.AlignLeft)
        self.bottom_layout.addWidget(self.ready_button, 0, 1, Qt.AlignHCenter)
        self.bottom_layout.addWidget(self.start_button, 0, 2, Qt.AlignRight)

        layout.addWidget(self.top_widget)
        layout.addWidget(self.main_player_widget)
        layout.addWidget(self.bottom_widget)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        music.choose_music(2)

        self.set_avatarBorder_properties()

        self.set_mqtt(game_name, username)

    def check_setup(self, layout: QGridLayout, game_name: str, password: str, private_game: bool):
        """
        Manages elements based on the type of game.

        Args:
            layout (QGridLayout): Layout of the main window.
            game_name (str): Name of the game.
            password (str): Password of the game.
            private_game (bool): True if the game is private, False otherwise.
        """
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
        """
        Toggles the visibility of the password.
        """
        if self.password_linedit.echoMode() == QLineEdit.Password:
            self.password_linedit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_linedit.setEchoMode(QLineEdit.Password)

    def setup_heart_layout(self):
        """
        Sets up the heart widgets for the players.
        """
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

        self.heart_widget_player1.setFixedHeight(int(self.player1_avatar_label.height() / 3))
        self.heart_widget_player2.setFixedHeight(int(self.player2_avatar_label.height() / 3))
        self.heart_widget_player3.setFixedHeight(int(self.player3_avatar_label.height() / 3))
        self.heart_widget_player4.setFixedHeight(int(self.player4_avatar_label.height() / 3))
        self.heart_widget_player5.setFixedHeight(int(self.player5_avatar_label.height() / 3))
        self.heart_widget_player6.setFixedHeight(int(self.player6_avatar_label.height() / 3))
        self.heart_widget_player7.setFixedHeight(int(self.player7_avatar_label.height() / 3))
        self.heart_widget_player8.setFixedHeight(int(self.player8_avatar_label.height() / 3))

        self.heart_widgets_list = [
            self.heart_widget_player1, self.heart_widget_player2, self.heart_widget_player3, 
            self.heart_widget_player4, self.heart_widget_player5, self.heart_widget_player6, 
            self.heart_widget_player7, self.heart_widget_player8
        ]

    def setup_player_layout(self):
        """
        Sets up the layouts for the players.
        """
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
        """
        Sets up the avatar labels for the players.
        """
        self.no_avatar = QPixmap(f"{avatar_path}no-avatar.png")
        self.avatar = QPixmap(f"{avatar_path}{self.avatar_name}.png")
        
        self.player1_avatar_label = AvatarAnimatedLabel()
        self.player1_avatar_label.setObjectName("player1_avatar_label")
        self.player1_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player1_avatar_label.setPixmap(self.avatar.scaled(self.player1_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player1_avatar_label.setup(self, self.avatar_name.replace("-avatar", ""))
        self.player1_avatar_label.primary_pixmap_name = self.avatar_name
        self.player1_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player2_avatar_label = AvatarAnimatedLabel()
        self.player2_avatar_label.setObjectName("player2_avatar_label")
        self.player2_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player2_avatar_label.setPixmap(self.no_avatar.scaled(self.player2_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player2_avatar_label.setup(self, "no-avatar")
        self.player2_avatar_label.primary_pixmap_name = self.avatar_name
        self.player2_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player3_avatar_label = AvatarAnimatedLabel()
        self.player3_avatar_label.setObjectName("player3_avatar_label")
        self.player3_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player3_avatar_label.setPixmap(self.no_avatar.scaled(self.player3_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player3_avatar_label.setup(self, "no-avatar")
        self.player3_avatar_label.primary_pixmap_name = self.avatar_name
        self.player3_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player4_avatar_label = AvatarAnimatedLabel()
        self.player4_avatar_label.setObjectName("player4_avatar_label")
        self.player4_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player4_avatar_label.setPixmap(self.no_avatar.scaled(self.player4_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player4_avatar_label.setup(self, "no-avatar")
        self.player4_avatar_label.primary_pixmap_name = self.avatar_name
        self.player4_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player5_avatar_label = AvatarAnimatedLabel()
        self.player5_avatar_label.setObjectName("player5_avatar_label")
        self.player5_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player5_avatar_label.setPixmap(self.no_avatar.scaled(self.player5_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player5_avatar_label.setup(self, "no-avatar")
        self.player5_avatar_label.primary_pixmap_name = self.avatar_name
        self.player5_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player6_avatar_label = AvatarAnimatedLabel()
        self.player6_avatar_label.setObjectName("player6_avatar_label")
        self.player6_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player6_avatar_label.setPixmap(self.no_avatar.scaled(self.player6_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player6_avatar_label.setup(self, "no-avatar")
        self.player6_avatar_label.primary_pixmap_name = self.avatar_name
        self.player6_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player7_avatar_label = AvatarAnimatedLabel()
        self.player7_avatar_label.setObjectName("player7_avatar_label")
        self.player7_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player7_avatar_label.setPixmap(self.no_avatar.scaled(self.player7_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player7_avatar_label.setup(self, "no-avatar")
        self.player7_avatar_label.primary_pixmap_name = self.avatar_name
        self.player7_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.player8_avatar_label = AvatarAnimatedLabel()
        self.player8_avatar_label.setObjectName("player8_avatar_label")
        self.player8_avatar_label.setFixedSize(int(screen_width // 6.2), int(screen_height // 6.2))
        self.player8_avatar_label.setPixmap(self.no_avatar.scaled(self.player8_avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.player8_avatar_label.setup(self, "no-avatar")
        self.player8_avatar_label.primary_pixmap_name = self.avatar_name
        self.player8_avatar_label.setAlignment(Qt.AlignCenter)  # Center the image

        self.avatar_label_list = [
            self.player1_avatar_label, self.player2_avatar_label, self.player3_avatar_label, 
            self.player4_avatar_label, self.player5_avatar_label, self.player6_avatar_label, 
            self.player7_avatar_label, self.player8_avatar_label
        ]

    def setup_hearts_widget(self):
        """
        Sets up the hearts widget for the players.
        """
        player_avatar_width = self.player1_avatar_label.width()
        player_avatar_height = self.player1_avatar_label.height()
        
        self.heart_list_widget1 = QListWidget()
        self.heart_list_widget1.setWrapping(True)
        self.heart_list_widget1.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget1.setSpacing(5)
        self.heart_list_widget1.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget1.setObjectName("heart_list_widget")
        self.heart_list_widget1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget1.setItemAlignment(Qt.AlignCenter)

        self.heart_list_widget2 = QListWidget()
        self.heart_list_widget2.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget2.setWrapping(True)
        self.heart_list_widget2.setSpacing(5)
        self.heart_list_widget2.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget2.setObjectName("heart_list_widget")
        self.heart_list_widget2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget3 = QListWidget()
        self.heart_list_widget3.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget3.setWrapping(True)
        self.heart_list_widget3.setSpacing(5)
        self.heart_list_widget3.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget3.setObjectName("heart_list_widget")
        self.heart_list_widget3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget3.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget4 = QListWidget()
        self.heart_list_widget4.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget4.setWrapping(True)
        self.heart_list_widget4.setSpacing(5)
        self.heart_list_widget4.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget4.setObjectName("heart_list_widget")
        self.heart_list_widget4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget4.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget5 = QListWidget()
        self.heart_list_widget5.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget5.setWrapping(True)
        self.heart_list_widget5.setSpacing(5)
        self.heart_list_widget5.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget5.setObjectName("heart_list_widget")
        self.heart_list_widget5.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget5.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget6 = QListWidget()
        self.heart_list_widget6.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget6.setWrapping(True)
        self.heart_list_widget6.setSpacing(5)
        self.heart_list_widget6.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget6.setObjectName("heart_list_widget")
        self.heart_list_widget6.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget6.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget7 = QListWidget()
        self.heart_list_widget7.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget7.setWrapping(True)
        self.heart_list_widget7.setSpacing(5)
        self.heart_list_widget7.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget7.setObjectName("heart_list_widget")
        self.heart_list_widget7.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget7.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widget8 = QListWidget()
        self.heart_list_widget8.setFlow(QListWidget.LeftToRight)
        self.heart_list_widget8.setWrapping(True)
        self.heart_list_widget8.setSpacing(5)
        self.heart_list_widget8.setFixedSize(player_avatar_width, int(player_avatar_height // 6.5))
        self.heart_list_widget8.setObjectName("heart_list_widget")
        self.heart_list_widget8.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heart_list_widget8.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.heart_list_widgets_list = [
            self.heart_list_widget1, self.heart_list_widget2, self.heart_list_widget3, 
            self.heart_list_widget4, self.heart_list_widget5, self.heart_list_widget6, 
            self.heart_list_widget7, self.heart_list_widget8
        ]

    def setup_hearts_rules(self, lifes: int, ready_players: str):
        """
        Sets up the hearts based on the game rules.

        Args:
            lifes (int): Number of lives each player has.
            ready_players (str): Comma-separated string of ready players.
        """
        ready_players = ready_players.split(",")
        total_spacing = 10 * self.heart_list_widget1.spacing()
        size = (self.heart_list_widget1.width() - total_spacing) // 10
        size = QSize(size, size)
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
        """
        Opens a window to leave the game.

        Returns:
            None
        """
        if not self.ingame:
            self.leave_game_window = LeaveGameWindow(self, self.mqtt_sub, self.game_name)
            self.leave_game_window.show()
            self.leave_game_window.activateWindow()
        else:
            return

    def leave_join_menu(self):
        """
        Leaves the game window and returns to the main menu.
        """
        self.join_state()
        self.setup(join=False)
        send_server("MENU_STATE|".encode())

    def join_state(self):
        """
        Modifies the player's state based on whether they have joined a game or not.
        """
        self.join = False
        self.join_menu_loaded = False

    def kill_borders(self):
        """
        Kills the avatar border timer.
        """
        try:
            self.avatarBorderBox.kill_timer(self)
        except AttributeError:
            pass
        self.label_loaded = False

    def create_game(self, game_name: str, password: str, private_game: bool):
        """
        Creates a game.

        Args:
            game_name (str): Name of the game.
            password (str): Password for the game.
            private_game (bool): True if the game is private, False otherwise.
        """
        global username
        message = f"CREATE_GAME|{username}|{game_name}|{password}|{private_game}|{self.creation_game.select_langue_combobox.currentText()}|"
        self.game_name = game_name
        send_server(message.encode())

    def join_game_as_a_player(self, username : str, game_name : str):
        """join_game_as_a_player(username, game_name) : Rejoint une partie en tant que joueur
        
        Args:
            username (str): Nom d'utilisateur
            game_name (str): Nom de la partie"""
        message = f"JOIN_GAME_AS_A_PLAYER|{username}|{game_name}|{self.avatar_name}"
        send_server(message.encode())

    def start_game(self, game_name: str):
        """
        Starts the game.

        Args:
            game_name (str): Name of the game.
        """
        global username
        if self.not_alone():
            self.start_button.setEnabled(False)
            self.ready_button.setEnabled(False)
            self.rules_button.setEnabled(False)
            message = f"START_GAME|{username}|{game_name}|{rules[0]}|{rules[1]}|{rules[2]}|{rules[3]}|{rules[4]}|{rules[5]}|{rules[6]}|"
            send_server(message.encode())

    def not_alone(self) -> bool:
        """
        Checks if the player is not alone in the game.

        Returns:
            bool: True if there is more than one player, False otherwise.
        """
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
        """
        Indicates to the server that the player is ready.
        """
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
        send_server(message.encode())

        if self.ready_button.text() == langue.langue_data["ClientWindow__ready_button__ready_state_text"]:
            self.ready_button.setText(langue.langue_data["ClientWindow__ready_button__not_ready_state_text"])
        else:
            self.ready_button.setText(langue.langue_data["ClientWindow__ready_button__ready_state_text"])

    def user_ready(self, player: str, ready: bool):
        """
        Indicates that the player is ready by setting their name in green.

        Args:
            player (str): Player's name.
            ready (bool): True if the player is ready, False otherwise.
        """
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
        """
        Resets the ready status of all players.
        """
        for label in self.player_label_list:
            match = re.search(r"<font color='green'>(.*?)</font>", label.text())
            if match:
                label.setText(match.group(1))

    def filter_game(self):
        """
        Opens the filter window to filter games.
        """
        self.filter_window = FilterWindow(self)
        self.filter_window.show()
        self.filter_window.activateWindow()

    def filter_games(self, filter: str):
        """
        Filters the games based on the provided filter.

        Args:
            filter (str): Filter string to apply.
        """
        self.filter = filter

        try:
            for index in range(self.game_list_widget.count() - 1, -1, -1):
                self.game_list_widget.takeItem(index)
        except RuntimeError:
            pass
        send_server(f"GET_GAMES|{username}|".encode())

    def setup_join_game(self, layout: QGridLayout):
        """
        Sets up the window for joining a game.

        Args:
            layout (QGridLayout): Layout of the main window.
        """
        self.join_menu_loaded = True
        self.kill_button_animation_timer()
        layout.removeWidget(self.create_game_button)
        layout.removeWidget(self.join_game)

        layout = QVBoxLayout()
        sub_layout = QGridLayout()
        button_layout = QHBoxLayout()
        button_layout2 = QHBoxLayout()

        central_widget = QWidget()
        sub_widget = UnderlineWidget()
        button_widget = QWidget()
        button_widget2 = QWidget()

        self.home_logo = QPixmap(f"{image_path}home.png")
        self.home_logo_hover = QPixmap(f"{image_path}home-hover.png")
        self.home_button = HoverPixmapButton(self.home_logo, self.home_logo_hover)
        self.home_button.setFixedSize(screen_width // 15, screen_width // 15)
        self.home_button.setObjectName("other_buttons")
        self.home_button.setIcon(QIcon(self.home_logo))
        self.home_button.setIconSize(self.home_button.size())
        self.home_button.clicked.connect(self.leave_join_menu)

        self.settings_logo = QPixmap(f"{image_path}settings.png")
        self.settings_logo_hover = QPixmap(f"{image_path}settings-hover.png")
        self.settings = HoverPixmapButton(self.settings_logo, self.settings_logo_hover)
        self.settings.setFixedSize(screen_width // 15, screen_width // 15)
        self.settings.setObjectName("other_buttons")
        self.settings.setIcon(QIcon(self.settings_logo))
        self.settings.setIconSize(self.settings.size())
        self.settings.clicked.connect(self.display_settings)

        self.loupe_logo = QPixmap(f"{image_path}loupe.png")
        self.loupe_logo_hover = QPixmap(f"{image_path}loupe-hover.png")
        self.loupe_button = HoverPixmapButton(self.loupe_logo, self.loupe_logo_hover)
        self.loupe_button.setFixedSize(screen_width // 15, screen_width // 15)
        self.loupe_button.setObjectName("other_buttons")
        self.loupe_button.setIcon(QIcon(self.loupe_logo))
        self.loupe_button.setIconSize(self.loupe_button.size())
        self.loupe_button.clicked.connect(self.filter_game)

        self.wifi_label = QLabel("WIFI", self)
        self.wifi_label.setObjectName("wifi_label")
        self.wifi_label.setFixedSize(screen_width // 15, screen_width // 15)
        self.wifi_label.setPixmap(self.wifi_logo.scaled(self.wifi_label.width(), self.wifi_label.height(), Qt.KeepAspectRatio))

        self.join_label = LinearGradiantLabel(langue.langue_data["ClientWindow__join_label__text"], color1=QColor(84, 58, 180, 255), color2=QColor(253, 89, 29, 255))
        self.join_label.setObjectName("join_label")
        self.join_label.setAlignment(Qt.AlignCenter)
        self.join_label.setFixedWidth(screen_width // 2)

        self.game_list_widget = QListWidget()
        self.game_list_widget.setObjectName("game_list_widget")
        self.game_list_widget.setSpacing(15)
        self.game_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.game_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(sub_widget)
        layout.addWidget(self.game_list_widget)

        sub_layout.addWidget(button_widget, 0, 0, Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(self.join_label, 0, 1, Qt.AlignmentFlag.AlignCenter)
        sub_layout.addWidget(button_widget2, 0, 2, Qt.AlignmentFlag.AlignRight)

        button_layout.addWidget(self.home_button)
        button_layout.addWidget(self.loupe_button)

        button_layout2.addWidget(self.wifi_label)
        button_layout2.addWidget(self.settings)

        central_widget.setLayout(layout)
        sub_widget.setLayout(sub_layout)
        button_widget.setLayout(button_layout)
        button_widget2.setLayout(button_layout2)
        self.setCentralWidget(central_widget)

        receiver_thread.game_created.connect(self.add_item)
        receiver_thread.game_deleted.connect(self.delete_item)
        send_server(f"GET_GAMES|{username}".encode())

    def display_sylb(self, sylb: str, player: str | None, death_mode_state: int) -> None:
        """
        Displays the syllable in the main window.

        Args:
            sylb (str): Syllable to display.
            player (str | None): Player's name.
            death_mode_state (int): State of the death mode.
        """
        if self.bomb_label.pixmap_name in ["explosion", "explosion_bleue", "explosion_rose"]:
            if self.bomb_label.is_animating():
                self.bomb_label.stop_animation()
            self.bomb_label.setup(self, "bombe_apparition")
            self.bomb_label.start_animation()

        self.syllabe_label.setText(sylb)
        if self.previous_player:
            self.change_player(self.previous_player, 6.2, int(screen_height//90), int(screen_height//108))
        self.change_player(player, 5.9, int(screen_height//54), int(screen_height//54))
        self.previous_player = player
        ambiance_sound.sound_effects.next_sound.play()
        if player == username:
            self.text_line_edit.setEnabled(True)
            self.text_line_edit.setFocus()

    def add_item(self, game_name: str, private_game: bool, players_number: int, langue: str) -> None:
        """
        Adds an item to the QListWidget.

        Args:
            game_name (str): Name of the game.
            private_game (bool): True if the game is private, False otherwise.
            players_number (int): Number of players in the game.
            langue (str): Language of the game.
        
        Returns:
            None
        """
        cadenas_icon = QPixmap(f"{image_path}cadenas.png")
        globe_icon = QPixmap(f"{image_path}globe.png")
        if self.filter and self.filter.strip():
            if unidecode.unidecode(self.filter).lower() not in unidecode.unidecode(game_name).lower():
                return
        try:
            if not self.game_list_widget.findChild(QPushButton, game_name):
                self.private_game_label = QLabel()
                size = self.private_game_label.fontMetrics().width('A' * 4)
                if private_game == "False":
                    color1, color2 = QColor(100, 198, 129, 1), QColor(197, 186, 255, 1)
                    self.private_game_label.setPixmap(globe_icon.scaled(size, size, Qt.KeepAspectRatio))
                else:
                    color1, color2 = QColor(211, 133, 214, 1), QColor(253, 212, 145, 1)
                    self.private_game_label.setPixmap(cadenas_icon.scaled(size, size, Qt.KeepAspectRatio))
                self.private_game_label.setAlignment(Qt.AlignCenter)

                info_game_widget = QWidget()
                info_game_layout = QHBoxLayout(info_game_widget)
                self.langue_label = QLabel(langue[:2].upper(), self)
                self.langue_label.setObjectName("langue_label")
                self.join_game_pushbutton = QPushButton(f"{game_name}")
                self.join_game_pushbutton.setObjectName(game_name)
                self.join_game_pushbutton.setStyleSheet("background-color: transparent; border: None")
                info_game_widget.setFixedHeight(int(self.height() // 12))

                self.people_label = QLabel(f"{players_number}/8")
                self.people_label.setObjectName("people_label")

                item = QListWidgetItem(self.game_list_widget)
                item_widget = QWidget()
                item_widget.setStyleSheet("font-size: 20pt;")
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

    def delete_item(self, game_name: str):
        """
        Deletes an item from the QListWidget.

        Args:
            game_name (str): Name of the game.
        """
        try:
            for index in range(self.game_list_widget.count()):
                item = self.game_list_widget.item(index)
                button = self.game_list_widget.itemWidget(item).findChild(QPushButton)
                if button.objectName() == game_name:
                    row = self.game_list_widget.row(item)
                    self.game_list_widget.takeItem(row)
                    break
        except RuntimeError:
            pass
        self.join_window_close_signal.emit(game_name)

    def show_join_window(self, game_name: str, private_game: str):
        """
        Displays the password window.

        Args:
            game_name (str): Name of the game.
            private_game (str): To be converted to bool, True if the game is private, False otherwise.
        """
        private_game = self.bool_convert(private_game)
        self.join_window = JoinGameWindow(game_name, private_game, window)
        if private_game:
            self.join_window.show()
            self.join_window.activateWindow()
            self.join_window.setup()
            self.join_window.password_lineedit.setFocus()
        else:
            try:
                self.join_window.join_lobby()
            except Exception as e:
                pass

    def bool_convert(self, boolean: str) -> bool:
        """
        Converts a string to a boolean.

        Args:
            boolean (str): String to convert.

        Returns:
            bool: Converted boolean value.
        """
        if boolean == "False":
            return False
        else:
            return True
        
    def set_bomb_label(self, death_mode_state: int, name: str, frame_rate: int = 24):
        """
        Sets up the bomb label based on the death mode state.

        Args:
            death_mode_state (int): State of the death mode.
            name (str): Name of the image.
            frame_rate (int): Frame rate of the animation.
        """
        if death_mode_state == 0:
            self.bomb_label.setup(self, f"{name}", frame_rate)
        elif death_mode_state == 1:
            self.bomb_label.setup(self, f"{name}_bleue", frame_rate)
        elif death_mode_state == 2:
            self.bomb_label.setup(self, f"{name}_rose", frame_rate)

    def bomb_animation(self, pixmap_name: str):
        """
        Starts the bomb animation.

        Args:
            pixmap_name (str): Name of the image.
        """
        if pixmap_name == "bombe_apparition":
            self.set_bomb_label(self.death_mode_state, "bombe")
            self.bomb_label.start_loop_animation()

        elif pixmap_name == "bombe_disparition":
            self.set_bomb_label(self.death_mode_state, "explosion", 48)
            explosion = random.choice(["explosion1", "explosion2", "explosion3"])
            explosion_sound = getattr(ambiance_sound.sound_effects, f"{explosion}_sound")
            self.bomb_label.start_animation()
            explosion_sound.play()

        # elif pixmap_name == "explosion" or pixmap_name == "explosion_bleue" or pixmap_name == "explosion_rose":
        #     self.remove_heart(self.player)

    def send_syllabe_message(self):
        """
        Sends the syllable message to the server.
        """
        global username
        syllabe = syllabes[-1]
        message = f"NEW_SYLLABE|{username}|{self.text_line_edit.text()}|{syllabe}"
        send_server(message.encode())
        self.text_line_edit.clear()

    def display_text(self):
        """
        Displays the text in the main window label.
        """
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
        """
        Displays the game rules.
        """
        self.rules_window = RulesWindow()

    def display_settings(self):
        """
        Displays the settings window.
        """
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()
        self.settings_window.activateWindow()

    def show_game_is_full_window(self):
        """
        Displays the window informing that the game is full.
        """
        self.game_is_full_window = GameIsFullWindow(self)
        self.game_is_full_window.show()
        self.game_is_full_window.activateWindow()

    def set_avatarBorder_properties(self):
        """
        Sets up the animated borders for avatars.
        """
        self.labels = [self.player1_avatar_label, self.player2_avatar_label, self.player3_avatar_label, self.player4_avatar_label, self.player5_avatar_label, self.player6_avatar_label, self.player7_avatar_label, self.player8_avatar_label]
        self.avatarBorderBox.setup_timer(self)
        self.label_loaded = True
    
    def set_buttonBorder_properties(self):
        """
        Sets up the animated borders for buttons.
        """
        self.buttons = [self.create_game_button, self.join_game]
        self.buttonBorderBox.setup_timer(self)
        self.button_loaded = True

    def kill_button_animation_timer(self):
        """
        Stops the animated borders for buttons.
        """
        self.button_loaded = False
        try:
            self.buttonBorderBox.kill_timer(self)
        except AttributeError:
            pass

    def draw_styled_button(self):
        """
        Draws the animated borders for buttons.
        """
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

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draws the animated borders.

        Args:
            event (QPaintEvent): Paint event.

        Returns:
            None
        """
        if self.label_loaded:
            self.avatarBorderBox.border(self, self.labels)
            self.draw_styled_button()
        if self.button_loaded:
            self.buttonBorderBox.border(self, self.buttons)
        return super().paintEvent(event)
        
    def mousePressEvent(self, event: QMouseEvent | None):
        """
        Handles mouse press event.

        Args:
            event (QMouseEvent): Mouse event.
        """
        if not self.loaded_select_screen:
            self.load_select_screen()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handles key press event.

        Args:
            event (QKeyEvent): Key event.
        """
        if not self.button_loaded and not self.label_loaded and not self.join_menu_loaded:
            self.load_select_screen()
        elif self.join_menu_loaded:
            if event.key() == Qt.Key_Escape:
                self.leave_join_menu()
            if event.key() == Qt.Key_F and event.modifiers() & Qt.ControlModifier:
                self.filter_game()
        elif self.button_loaded:
            if event.key() == Qt.Key_Escape:
                for button in self.buttons:
                    button.clearFocus()
                self.display_settings()
        elif self.label_loaded:
            if event.key() == Qt.Key_Escape:
                self.leave_game()        

    def closeEvent(self, event: QEvent) -> None:
        """
        Handles window close event.

        Args:
            event (QEvent): Close event.
        """
        try:
            self.mqtt_sub.stop_loop()
        except AttributeError:
            pass
        ping_thread.running = False
        event.accept()
    
    def load_select_screen(self):
        """
        Loads the avatar selection screen.
        """
        self.title_screen_label.stop_loop_animation()
        music.choose_music(1)
        self.setup(join=False)
        self.loaded_select_screen = True
        self.set_animated_properties()
        self.mousePressEvent = self.emptyFunction

    def ping(self, ping: float, working_ping: bool):
        """
        Updates the connection label image.

        Args:
            ping (float): Connection ping.
            working_ping (bool): True if the ping is correct, False otherwise.
        """
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
        
    def manage_conexion_info_window(self, working_ping: bool):
        """
        Manages the connection info window.

        Args:
            working_ping (bool): True if the ping is correct, False otherwise.
        """
        if not working_ping:
            if not isinstance(self.connexion_info_window, ConnexionInfoWindow) and self.loaded_select_screen:
                self.connexion_info_window = ConnexionInfoWindow(self)
                self.connexion_info_window.show()
                self.connexion_info_window.activateWindow()

if __name__ == "__main__":
    receiver_thread = ReceptionThread()
    ping_thread = PingThread()
    ping_thread.start()
    window = ClientWindow()
    login = Login()
    login.show()
    sys.exit(app.exec_())