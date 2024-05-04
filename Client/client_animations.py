from client_utils import *

class AvatarBorderBox():
    """AvatarBorderBox : Classe qui permet de dessiner un cadre autour d'un objet"""
    def __init__(self):
        """__init__ : Fonction d'initialisation de la classe AvatarBorderBox"""
        pass        

    def setup_colors(self, clientObject) -> dict:
        """setup_colors : Fonction qui permet de définir les couleurs de bordure
        
        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.player1_border_color = QColor(255, 0, 0)  # Initial border color (red)
        clientObject.player1_border_color2 = QColor(0, 255, 255)

        clientObject.player2_border_color = QColor(255, 0, 0)
        clientObject.player2_border_color2 = QColor(0, 255, 255)

        clientObject.player3_border_color = QColor(255, 0, 0)
        clientObject.player3_border_color2 = QColor(0, 255, 255)

        clientObject.player4_border_color = QColor(255, 0, 0)
        clientObject.player4_border_color2 = QColor(0, 255, 255)

        clientObject.player5_border_color = QColor(255, 0, 0)
        clientObject.player5_border_color2 = QColor(0, 255, 255)

        clientObject.player6_border_color = QColor(255, 0, 0)
        clientObject.player6_border_color2 = QColor(0, 255, 255)

        clientObject.player7_border_color = QColor(255, 0, 0)
        clientObject.player7_border_color2 = QColor(0, 255, 255)

        clientObject.player8_border_color = QColor(255, 0, 0)
        clientObject.player8_border_color2 = QColor(0, 255, 255)

        self.avatars_colors_dico = {
            "bouteille-avatar":((253,72,255),(65,253,164)), 
            "cactus-avatar":((255,150,0),(17,136,0)), 
            "gameboy-avatar":((98,0,84),(0,47,150)), 
            "panneau-avatar":((255,252,156),(186,0,0)), 
            "pizza-avatar":((130,74,0),(114,187,0)), 
            "reveil-avatar":((0, 255, 0),(0, 0, 255)), 
            "robot-ninja-avatar":((255, 0, 0),(0, 0, 255)), 
            "serviette-avatar":((0, 255, 0),(0, 0, 255)), 
            "tasse-avatar":((255, 0, 0),(0, 0, 255)), 
            "television-avatar":((0, 255, 0),(0, 0, 255))
        }

        self.player_border_color1_tuple = (clientObject.player1_border_color, clientObject.player2_border_color, clientObject.player3_border_color, clientObject.player4_border_color, clientObject.player5_border_color, clientObject.player6_border_color, clientObject.player7_border_color, clientObject.player8_border_color)
        self.player_border_color2_tuple = (clientObject.player1_border_color2, clientObject.player2_border_color2, clientObject.player3_border_color2, clientObject.player4_border_color2, clientObject.player5_border_color2, clientObject.player6_border_color2, clientObject.player7_border_color2, clientObject.player8_border_color2)

        return self.avatars_colors_dico
        
    def setup_timer(self, clientObject):
        """setup_timer : Fonction qui permet de lancer le timer

        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.timer = QTimer(clientObject)
        clientObject.timer.timeout.connect(lambda: self.update_border_color(clientObject))
        clientObject.timer.start(500)

    def kill_timer(self, clientObject):
        """kill_timer : Fonction qui permet d'arrêter le timer
        
        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.timer.stop()

    def update_border_color(self, clientObject):
        """update_border_color : Fonction qui permet de mettre à jour la couleur de la bordure

        Args:
            clientObject (object): Objet ClientWindow"""
        color1_tuple = copy.deepcopy(self.player_border_color1_tuple)
        color2_tuple = copy.deepcopy(self.player_border_color2_tuple)
        for i, (color1, color2) in enumerate(zip(self.player_border_color1_tuple, self.player_border_color2_tuple)):
            if color1 == color1_tuple[i]:
                color1.setRgb(*color2_tuple[i].getRgb())
                color2.setRgb(*color1_tuple[i].getRgb())
            else:
                color1.setRgb(*color1_tuple[i].getRgb())
                color2.setRgb(*color2_tuple[i].getRgb())
        clientObject.update()

    def border(self, clientObject : object, labels : list):
        """border() : Fonction qui permet de dessiner un cadre autour d'un objet
        
        Args:
            clientObject (object): Objet ClientWindow
            labels (list): Liste des labels à entourer d'un cadre"""
        avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid = None, None, None, None, None, None, None, None
        avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed = None, None, None, None, None, None, None, None
        avatar_vars_dico = {"Solid": [avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid], "Dashed": [avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed]}
        for i, (label, avatar_solid, avatar_dashed) in enumerate(zip(labels, avatar_vars_dico["Solid"], avatar_vars_dico["Dashed"])):
            label_pos = label.mapTo(clientObject, QPoint(0,0))
            label_x = label_pos.x()
            label_y = label_pos.y()
            label_geometry = label.geometry()
            label_width = label_geometry.width()
            label_height = label_geometry.height()

            avatar_solid = QPainter(clientObject)
            pen1_solid = QPen(self.player_border_color1_tuple[i], 10, style=Qt.SolidLine)
            avatar_solid.setPen(pen1_solid)
            avatar_solid.drawRoundedRect(label_x, label_y, label_width, label_height, 20, 20)

            avatar_dashed = QPainter(clientObject)
            pen1_dashed = QPen(self.player_border_color2_tuple[i], 10, style=Qt.DashLine)
            avatar_dashed.setPen(pen1_dashed)
            avatar_dashed.drawRoundedRect(label_x, label_y, label_width, label_height, 20, 20)

class ButtonBorderBox():
    """ButtonBorderBox : Classe qui permet de dessiner un cadre autour d'un bouton"""
    def __init__(self) -> None:
        """__init__ : Fonction d'initialisation de la classe ButtonBorderBox"""
        pass

    def setup_colors(self, clientObject):
        """setup_colors : Fonction qui permet de définir les couleurs de bordure
        
        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.button1_border_color = QColor(135, 46, 255)
        clientObject.button1_border_color2 = QColor(82, 207, 95)

        clientObject.button2_border_color = QColor(253, 179, 65)
        clientObject.button2_border_color2 = QColor(253, 66, 255)

        self.color1_tuple = (clientObject.button1_border_color, clientObject.button2_border_color)
        self.color2_tuple = (clientObject.button1_border_color2, clientObject.button2_border_color2)
        

    def setup_timer(self, clientObject):
        """setup_timer : Fonction qui permet de lancer le timer

        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.timer = QTimer(clientObject)
        clientObject.timer.timeout.connect(lambda: self.update_border_color(clientObject))
        clientObject.timer.start(500) #500ms

    def kill_timer(self, clientObject):
        """kill_timer : Fonction qui permet d'arrêter le timer
        
        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.timer.stop()

    def update_border_color(self, clientObject):
        """update_border_color : Fonction qui permet de mettre à jour la couleur de la bordure

        Args:
            clientObject (object): Objet ClientWindow"""
        
        if clientObject.button1_border_color == self.color1_tuple[0]:
            clientObject.button1_border_color = QColor(*self.color2_tuple[0].getRgb())
            clientObject.button1_border_color2 = QColor(*self.color1_tuple[0].getRgb())

            clientObject.button2_border_color = QColor(*self.color2_tuple[1].getRgb())
            clientObject.button2_border_color2 = QColor(*self.color1_tuple[1].getRgb())
        else:
            clientObject.button1_border_color = QColor(*self.color1_tuple[0].getRgb())
            clientObject.button1_border_color2 = QColor(*self.color2_tuple[0].getRgb())

            clientObject.button2_border_color = QColor(*self.color1_tuple[1].getRgb())
            clientObject.button2_border_color2 = QColor(*self.color2_tuple[1].getRgb())

        clientObject.update()

    def border(self, clientObject : object, buttons : list):
        """border() : Fonction qui permet de dessiner un cadre autour d'un bouton

        Args:
            clientObject (object): Objet ClientWindow
            buttons (list): Liste des boutons à entourer d'un cadre"""
        button1_solid, button2_solid = None, None
        button1_dashed, button2_dashed = None, None, 
        button_vars_dico = {
            "Solid": [button1_solid, button2_solid], 
            "Dashed": [button1_dashed, button2_dashed],
            "Color1": [clientObject.button1_border_color, clientObject.button2_border_color],
            "Color2": [clientObject.button1_border_color2, clientObject.button2_border_color2],
            }
        for button, avatar_solid, avatar_dashed, border_color, border_color2 in zip(buttons, button_vars_dico["Solid"], button_vars_dico["Dashed"], button_vars_dico["Color1"], button_vars_dico["Color2"]):
            button_pos = button.mapTo(clientObject, QPoint(0,0))
            button_x = button_pos.x()
            button_y = button_pos.y()
            button_geometry = button.geometry()
            button_width = button_geometry.width()
            button_height = button_geometry.height()

            avatar_solid = QPainter(clientObject)
            pen1_solid = QPen(border_color, 40, style=Qt.SolidLine)
            avatar_solid.setPen(pen1_solid)
            avatar_solid.drawRoundedRect(button_x, button_y, button_width, button_height, 20, 20)

            avatar_dashed = QPainter(clientObject)
            pen1_dashed = QPen(border_color2, 40, style=Qt.DashLine)
            avatar_dashed.setPen(pen1_dashed)
            avatar_dashed.drawRoundedRect(button_x, button_y, button_width, button_height, 20, 20)

class AnimatedButton(QPushButton):
    """AnimatedButton : Classe qui permet de créer un bouton animé"""
    def __init__(self, animated_objectName, color1, color2):
        """__init__ : Fonction d'initialisation de la classe AnimatedButton
        
        Args:
            animated_objectName (str): Nom de l'objet à animer
            color1 (QColor): Couleur 1
            color2 (QColor): Couleur 2"""
        super().__init__()

        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setAutoDefault(True)
        self.animated_objectName = animated_objectName
        self.color1 = color1
        self.color2 = color2

        self._animation = QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=250
        )

        self.clicked.connect(self.on_click)

    def on_click(self):
        sound_effects.windows_sound.play()

    def _animate(self, value):
        """_animate : Fonction qui permet d'animer le bouton
        
        Args:
            value (float): Valeur de l'animation"""
        global stylesheet_window
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});border-radius: {radius}; padding: {padding}".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value, radius=30, padding=20
        )
        grad = f"QPushButton#{self.animated_objectName}{{{grad_string}}}"
        stylesheet_window += grad
        self.setStyleSheet(stylesheet_window)

    def enterEvent(self, event):
        """enterEvent : Fonction qui permet de déclencher l'animation lorsque la souris entre dans le bouton
        
        Args:
            event (QEvent): Événement de la souris"""
        self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()
        sound_effects.play_sound(sound_effects.select_sound)
        self.change_size_button(90)
        self.setFocus()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """leaveEvent : Fonction qui permet d'arrêter l'animation lorsque la souris quitte le bouton
        
        Args:
            event (QEvent): Événement de la souris"""
        self._animation.setDirection(QAbstractAnimation.Backward)
        self._animation.start()
        self.change_size_button(80)
        super().enterEvent(event)

    def focusInEvent(self, a0: QFocusEvent) -> None:
        """focusInEvent : Fonction qui permet de jouer un son lorsque le bouton est focusé"""
        if a0.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            sound_effects.play_sound(sound_effects.select_sound)
            self.change_size_button(90)
        return super().focusInEvent(a0)
    
    def focusOutEvent(self, a0: QFocusEvent | None) -> None:
        """focusOutEvent : Fonction qui permet de jouer un son lorsque le bouton n'est plus focusé"""
        if a0.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            self.change_size_button(80)
        return super().focusOutEvent(a0)
    
    def change_size_button(self, size):
        """change_size_button : Fonction qui permet de changer la taille du bouton
        
        Args:
            size (int): Taille du bouton"""
        global stylesheet_window
        style = "QPushButton#{}{{font-size: {}pt}}".format(self.animated_objectName, size)
        stylesheet_window += style
        self.setStyleSheet(stylesheet_window)

class AnimatedWindow(QMainWindow):
    """AnimatedWindow : Classe qui permet de créer une fenêtre avec background animé"""
    def __init__(self):
        """__init__ : Fonction d'initialisation de la classe AnimatedWindow"""
        super().__init__()

    def set_animated_properties(self):
        """set_animated_properties : Fonction qui permet de définir les propriétés de la fenêtre animée"""
        self.color1 = QColor(254, 194, 255)
        self.color2 = QColor(123, 248, 252)
        self.i = 0
        self._animation = QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=9000
        )

    def _animate(self, value):
        """_animate : Fonction qui permet d'animer la fenêtre"""
        global stylesheet_window
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1})".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value
        )
        grad = f"QMainWindow#client_mainwindow{{{grad_string}}}"
        stylesheet_window += grad
        self.setStyleSheet(stylesheet_window)

    def animation(self):
        """animation : Fonction qui permet de lancer l'animation de la fenêtre"""
        self.i += 1
        if self.i%2 == 0:
            self._animation.setDirection(QAbstractAnimation.Backward)
        else:
            self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()

    def event(self, e):
        """event : Fonction qui permet de gérer les événements de la fenêtre"""
        try:
            if self._animation.state() != QAbstractAnimation.Running:
                self.animation()
                return super().event(e)
            else:
                return super().event(e)
        except AttributeError:
            return super().event(e)