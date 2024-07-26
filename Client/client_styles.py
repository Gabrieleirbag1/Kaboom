from client_utils import *
from client_objects import ClickableWidget, ClickButton
import log_config

log_config.setup_logging()

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
        clientObject.player1_border_color2 = QColor(20, 223, 200)

        clientObject.player2_border_color = QColor(255, 0, 0)
        clientObject.player2_border_color2 = QColor(20, 223, 200)

        clientObject.player3_border_color = QColor(255, 0, 0)
        clientObject.player3_border_color2 = QColor(20, 223, 200)

        clientObject.player4_border_color = QColor(255, 0, 0)
        clientObject.player4_border_color2 = QColor(20, 223, 200)

        clientObject.player5_border_color = QColor(255, 0, 0)
        clientObject.player5_border_color2 = QColor(20, 223, 200)

        clientObject.player6_border_color = QColor(255, 0, 0)
        clientObject.player6_border_color2 = QColor(20, 223, 200)

        clientObject.player7_border_color = QColor(255, 0, 0)
        clientObject.player7_border_color2 = QColor(20, 223, 200)

        clientObject.player8_border_color = QColor(255, 0, 0)
        clientObject.player8_border_color2 = QColor(20, 223, 200)

        self.avatars_colors_dico = {
            "bouteille-avatar":((253, 72, 255),(65, 253, 164)), 
            "cactus-avatar":((255, 150, 0),(17, 136, 0)), 
            "gameboy-avatar":((12, 219, 144),(0, 47, 150)), 
            "panneau-avatar":((244,186,85),(226, 18, 81)), 
            "pizza-avatar":((186, 0, 0),(255, 217, 24)), 
            "reveil-avatar":((177, 30, 154),(140, 213, 252)), 
            "robot-ninja-avatar":((252, 144, 144),(145, 4, 122)), 
            "serviette-avatar":((42, 152, 228),(0, 255, 255)), 
            "tasse-avatar":((42, 46, 228),(124, 204, 196)), 
            "television-avatar":((170, 26, 147),(245, 148, 107))
        }

        self.player_border_color1_tuple = (clientObject.player1_border_color, clientObject.player2_border_color, clientObject.player3_border_color, clientObject.player4_border_color, clientObject.player5_border_color, clientObject.player6_border_color, clientObject.player7_border_color, clientObject.player8_border_color)
        self.player_border_color2_tuple = (clientObject.player1_border_color2, clientObject.player2_border_color2, clientObject.player3_border_color2, clientObject.player4_border_color2, clientObject.player5_border_color2, clientObject.player6_border_color2, clientObject.player7_border_color2, clientObject.player8_border_color2)
        clientObject.player_border_size = [12, 12, 12, 12, 12, 12, 12, 12]

        return self.avatars_colors_dico
        
    def setup_timer(self, clientObject):
        """setup_timer : Fonction qui permet de lancer le timer

        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.timer2 = QTimer(clientObject)
        clientObject.timer2.timeout.connect(lambda: self.update_border_color(clientObject))
        clientObject.timer2.start(700)

    def kill_timer(self, clientObject):
        """kill_timer : Fonction qui permet d'arrêter le timer
        
        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.timer2.stop()

    def update_border_color(self, clientObject):
        """update_border_color : Fonction qui permet de mettre à jour la couleur de la bordure

        Args:
            clientObject (object): Objet ClientWindow"""
        if settings.accessibility_data[3][1] == "yes":
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
        try:
            avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid = None, None, None, None, None, None, None, None
            avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed = None, None, None, None, None, None, None, None
            avatar_vars_dico = {"Solid": [avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid], 
                                "Dashed": [avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed]}
            for i, (label, avatar_solid, avatar_dashed) in enumerate(zip(labels, avatar_vars_dico["Solid"], avatar_vars_dico["Dashed"])):
                label_pos = label.mapTo(clientObject, QPoint(0,0))
                label_x = label_pos.x()
                label_y = label_pos.y()
                label_geometry = label.geometry()
                label_width = label_geometry.width()
                label_height = label_geometry.height()

                avatar_solid = QPainter(clientObject)
                pen1_solid = QPen(self.player_border_color1_tuple[i], clientObject.player_border_size[i], style=Qt.SolidLine)
                avatar_solid.setPen(pen1_solid)
                avatar_solid.drawRoundedRect(label_x, label_y, label_width, label_height, 20, 20)

                avatar_dashed = QPainter(clientObject)
                pen1_dashed = QPen(self.player_border_color2_tuple[i], clientObject.player_border_size[i], style=Qt.DashLine)
                avatar_dashed.setPen(pen1_dashed)
                avatar_dashed.drawRoundedRect(label_x, label_y, label_width, label_height, 20, 20)
        except RuntimeError:
            pass

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
        if settings.accessibility_data[3][1] == "yes":
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
        button_sound.sound_effects.windows_sound.play()

    def _animate(self, value):
        """_animate : Fonction qui permet d'animer le bouton
        
        Args:
            value (float): Valeur de l'animation"""
        global main_stylesheet
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});border-radius: {radius}; padding: {padding}".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value, radius=30, padding=20
        )
        grad = f"QPushButton#{self.animated_objectName}{{{grad_string}}}"
        main_stylesheet += grad
        self.setStyleSheet(main_stylesheet)

    def enterEvent(self, event):
        """enterEvent : Fonction qui permet de déclencher l'animation lorsque la souris entre dans le bouton
        
        Args:
            event (QEvent): Événement de la souris"""
        self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()
        button_sound.sound_effects.play_sound(button_sound.sound_effects.select_sound)
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
            button_sound.sound_effects.play_sound(button_sound.sound_effects.select_sound)
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
        global main_stylesheet
        style = "QPushButton#{}{{font-size: {}pt}}".format(self.animated_objectName, size)
        main_stylesheet += style
        self.setStyleSheet(main_stylesheet)

class AnimatedWindow(QMainWindow):
    """AnimatedWindow : Classe qui permet de créer une fenêtre avec background animé"""
    def __init__(self):
        """__init__ : Fonction d'initialisation de la classe AnimatedWindow"""
        super().__init__()
        self.join_menu_loaded = False
        self.stylesheet_copy = copy.deepcopy(main_stylesheet)
        self.animation_started = False

    def set_animated_properties(self):
        """set_animated_properties() : Fonction qui permet de définir les propriétés de la fenêtre animée"""
        
        self.color1 = QColor(*self.hex_to_rgb(settings.accessibility_data[0][1].split("/")[0]))
        self.color2 = QColor(*self.hex_to_rgb(settings.accessibility_data[0][1].split("/")[1]))
        self.i = 0
        self._animation = QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=7000
        )

    def hex_to_rgb(self, hex_code: str) -> tuple:
        """hex_to_rbg(hex_code): Convertit un code couleur hexadécimal en format RGBA.

        Args:
            hex_code (str): Code couleur hexadécimal.

        Returns:
            tuple: Valeurs de couleur RGBA.
        """
        hex_code = hex_code.lstrip('#')
        rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        rgba = (*rgb, 255)
        return rgba

    def _animate(self, value : int):
        """_animate : Fonction qui permet d'animer la fenêtre"""
        global main_stylesheet
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1})".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value
        )
        grad = f"QMainWindow#client_mainwindow{{{grad_string}}}"
        main_stylesheet += grad
        self.setStyleSheet(main_stylesheet)

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
                if self._animation.direction() == QAbstractAnimation.Backward and not self.join_menu_loaded:
                    global main_stylesheet
                    main_stylesheet = self.stylesheet_copy
                self.animation()
                return super().event(e)
            else:
                return super().event(e)
        except AttributeError:
            return super().event(e)
        
    def emptyFunction(self, *args):
        """emptyFunction(event) : Fonction vide"""
        pass

class AnimatedGameWidget(ClickableWidget):
    """AnimatedGameWidget : Classe qui permet de créer un widget de jeu animé"""
    def __init__(self, game_name : str, color1 : QColor, color2 : QColor):
        """__init__ : Fonction d'initialisation de la classe AnimatedGameWidget"""
        super().__init__()
        self.animated_objectName = game_name
        self.setObjectName(game_name)
        self.set_animated_properties(color1, color2)

    def set_animated_properties(self, color1 : QColor, color2 : QColor):
        """set_animated_properties : Fonction qui permet de définir les propriétés de la fenêtre animée"""

        self.color1 : QColor = color1
        self.color2 : QColor = color2
        self._animation = QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=250
        )

    def _animate(self, value):
        """_animate : Fonction qui permet d'animer le bouton
        
        Args:
            value (float): Valeur de l'animation"""
        global main_stylesheet
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});border-radius: {radius}; padding: {padding}; border: 5px outset;".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value, radius=30, padding=20
        )
        grad = f"QWidget#{self.animated_objectName}{{{grad_string}}}"
        main_stylesheet += grad
        self.setStyleSheet(main_stylesheet)

    def enterEvent(self, event):
        """enterEvent : Fonction qui permet de déclencher l'animation lorsque la souris entre dans le bouton
        
        Args:
            event (QEvent): Événement de la souris"""
        self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()
        button_sound.sound_effects.play_sound(button_sound.sound_effects.select_sound)
        self.setFocus()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """leaveEvent : Fonction qui permet d'arrêter l'animation lorsque la souris quitte le bouton
        
        Args:
            event (QEvent): Événement de la souris"""
        self._animation.setDirection(QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

class LinearGradiantLabel(QLabel):
    """LinearGradiantLabel : Classe qui permet de créer un label avec un dégradé linéaire"""
    def __init__(self, text : str, color1=QColor(84,58,180,255), color2=QColor(253,89,29,255), *args, **kwargs):
        """__init__() : Fonction d'initialisation de la classe LinearGradiantLabel"""
        super().__init__(*args, **kwargs)
        self.text_label = text
        self.color1 = color1
        self.color2 = color2
        # self.setFixedWidth(screen_width//2)

    def paintEvent(self, event : QPaintEvent | None):
        """paintEvent(event) : Fonction qui permet de peindre le label
        
        Args:
            event (QPaintEvent): Événement qui permet d'écrire le texte du label avec un dégradé linéaire"""
        super().paintEvent(event)
        painter = QPainter(self)
        rect = self.rect()
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, self.color1)
        gradient.setColorAt(1, self.color2)
        pen = QPen()
        pen.setBrush(gradient)
        painter.setPen(pen)
        painter.drawText(QRectF(rect), self.text_label, QTextOption(Qt.AlignCenter))
        return super().paintEvent(event)
    
class StyledButton(ClickButton):
    def __init__(self, 
                 text : str | None, 
                 parent: object = None,
                 width: int | float = 3,
                 height: int | float = 3,
                 color1 : str = "lightblue", 
                 color2 : str = "pink", 
                 offset : tuple = (15, 15)) -> None:
        """__init__() : Fonction d'initialisation de la classe StyledButton"""
        super().__init__(text, parent)

        self.offset : tuple = offset
        self.color1 : str = color1
        self.color2 : str = color2

        self.setFixedSize(int(self.width()*width), int(self.height()*height))

        self.setStyleSheet(f'''
            QPushButton {{
                background-color: {self.color1};
                color: black;
                border: none;
                padding: 15px;
                text-align: center;
                text-decoration: none;
                margin: 4px 2px;
                border-radius: 15px;
            }}

            QPushButton:hover {{
                border: 5 outset #555151;
            }}

        ''')
        effect = QGraphicsDropShadowEffect()
        self.effect = effect
        effect.setOffset(*self.offset)
        effect.setBlurRadius(5)

        self.setGraphicsEffect(effect)

    def mousePressEvent(self, event : QMouseEvent | None):
        """mousePressEvent : Fonction qui permet de gérer l'événement de pression de la souris sur le bouton
        
        Args:
            event (QMouseEvent): Événement souris"""
        self.setStyleSheet(self.styleSheet() + f'''QPushButton{{background-color: {self.color2};}}''')
        self.effect.setOffset(0, 0)
        self.move(self.x() + self.offset[0], self.y() + self.offset[1])  # déplace le bouton
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event : QMouseEvent | None):
        """mouseReleaseEvent : Fonction qui permet de gérer l'événement de relâchement de la souris sur le bouton
        
        Args:
            event (QMouseEvent): Événement souris"""
        self.setStyleSheet(self.styleSheet() + f'''QPushButton{{background-color: {self.color1};}}''')
        self.effect.setOffset(*self.offset)
        self.move(self.x() - self.offset[0], self.y() - self.offset[1])  # replace le bouton à sa position initiale
        super().mouseReleaseEvent(event)

class StyledBorderButton(ClickButton):
    """StyledBorderButton : Classe qui permet de créer un bouton avec bordure stylisée"""
    def __init__(self, 
                 text : str | None, 
                 parent: object = None,
                 parent_name: str = None,
                 color1 : str = "lightblue", 
                 color2 : str = "pink", ) -> None:
        """__init__() : Fonction d'initialisation de la classe StyledBorderButton"""
        super().__init__(text, parent)
        
        self.clientObject : object = parent
        self.parent_name = parent_name
        self.color1 : QColor = color1
        self.color2 : QColor = color2

        setattr(self.clientObject, f"should_draw_{parent_name}", True)
        self.should_draw = getattr(self.clientObject, f"should_draw_{self.parent_name}")

        self.setStyleSheet(f'''
            QPushButton {{
                    background-color: transparent;
                    border-radius: 10px;
                    font-size: 15pt;
                    padding-left: 15px;
                    padding-bottom: 15px;
                    border: None;
                    text-align: right;
            }}

            QPushButton::disabled {{
                color: darkgray
            }}
        ''')

    def set_drop_shadow_effect_text(self):
        """set_drop_shadow_effect_text() : Fonction qui permet de définir l'effet de l'ombre du texte du bouton"""
        effect = QGraphicsDropShadowEffect()
        self.effect = effect
        effect.setOffset(3, 3)
        effect.setBlurRadius(10)
        self.setGraphicsEffect(effect)
    

    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        """mousePressEvent(e) : Fonction qui permet de dessiner la bordure du bouton
        
        Args:
            e (QMouseEvent): Événement souris"""
        setattr(self.clientObject, f"should_draw_{self.parent_name}", False)
        super().mousePressEvent(e)
    
    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        """mouseReleaseEvent(e) : Fonction qui permet de dessiner la bordure du bouton
        
        Args:
            e (QMouseEvent): Événement souris"""
        setattr(self.clientObject, f"should_draw_{self.parent_name}", True)
        super().mouseReleaseEvent(e)

class DrawStyledButton():
    """DrawStyledButton : Classe qui permet de dessiner un bouton stylisé"""
    def __init__(self, button, clientObject) -> None:
        """__init__() : Fonction d'initialisation de la classe DrawStyledButton"""
        self.button = button
        self.clientObject = clientObject

    def draw_border(self, offset : int, color : QColor) -> None:
        """draw_border(offset) : Fonction qui permet de dessiner la bordure du bouton
        
        Args:
            offset (int): Offset de la bordure du bouton"""
        if self.button.isEnabled():
            border_color = QColor(61, 59, 57)
        else:
            border_color = QColor(180, 180, 180)

        border_solid = QPainter(self.clientObject)
        solid_pen = QPen(border_color, 4, style=Qt.PenStyle.SolidLine)
        border_solid.setPen(solid_pen)

        button_pos = self.button.mapTo(self.clientObject, QPoint(0,0))
        button_x = button_pos.x()
        button_y = button_pos.y()

        button_geometry = self.button.geometry()
        button_width = button_geometry.width()
        button_height = button_geometry.height()

        self.fill_button(border_solid, button_x, button_y, button_width, button_height, color)

        border_solid.drawRoundedRect(button_x+offset, button_y-offset, button_width, button_height, 10, 10)

        self.clientObject.update()
        
    def fill_button(self, 
                    border_solid : QPainter, 
                    button_x : int, button_y : int, 
                    button_width : int, 
                    button_height : int,
                    color : QColor) -> None:
        """fill_button(border_solid, button_x, button_y, button_width, button_height) : Fonction qui permet de remplir le bouton
        
        Args:
            border_solid (QPainter): Objet QPainter
            button_x (int): Position x du bouton
            button_y (int): Position y du bouton
            button_width (int): Largeur du bouton
            button_height (int): Hauteur du bouton"""
        fill_path = QPainterPath()
        fill_path.addRoundedRect(button_x, button_y, button_width, button_height, 10, 10)

        border_solid.fillPath(fill_path, color)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    layout = QHBoxLayout(window)
    window.resize(1000, 1000)

    button = StyledBorderButton('Click me!', None, "lightblue", "pink")
    button.resize(200, 70)
    layout.addWidget(button)

    window.show()
    sys.exit(app.exec_())