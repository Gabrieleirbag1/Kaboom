from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton
from client_utils import stylesheet_window, screen_height

class AvatarBorderBox():
    """AvatarBorderBox : Classe qui permet de dessiner un cadre autour d'un objet"""
    def __init__(self) -> None:
        """__init__ : Fonction d'initialisation de la classe AvatarBorderBox"""
        pass        

    def setup_colors(self, clientObject):
        """setup_colors : Fonction qui permet de définir les couleurs de bordure
        
        Args:
            clientObject (object): Objet ClientWindow"""
        clientObject.border_color = QColor(255, 0, 0)  # Initial border color (red)
        clientObject.border_color2 = QColor(0, 255, 255)

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
        # Change the border color to a random color
        clientObject.border_color = QColor.fromRgbF(
            1.0 if clientObject.border_color.redF() == 0.0 else 0.0,
            1.0 if clientObject.border_color.greenF() == 0.0 else 0.0,
            1.0 if clientObject.border_color.blueF() == 0.0 else 0.0,
        )

        clientObject.border_color2 = QColor.fromRgbF(
            1.0 if clientObject.border_color2.redF() == 0.0 else 0.0,
            1.0 if clientObject.border_color2.greenF() == 0.0 else 0.0,
            1.0 if clientObject.border_color2.blueF() == 0.0 else 0.0,
        )
        clientObject.update()

    def border(self, clientObject : object, labels : list):
        """border() : Fonction qui permet de dessiner un cadre autour d'un objet
        
        Args:
            clientObject (object): Objet ClientWindow
            labels (list): Liste des labels à entourer d'un cadre"""
        avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid = None, None, None, None, None, None, None, None
        avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed = None, None, None, None, None, None, None, None
        avatar_vars_dico = {"Solid": [avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid], "Dashed": [avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed]}
        for label, avatar_solid, avatar_dashed in zip(labels, avatar_vars_dico["Solid"], avatar_vars_dico["Dashed"]):
            label_pos = label.mapTo(clientObject, QPoint(0,0))
            label_x = label_pos.x()
            label_y = label_pos.y()
            label_geometry = label.geometry()
            label_width = label_geometry.width()
            label_height = label_geometry.height()

            avatar_solid = QPainter(clientObject)
            pen1_solid = QPen(clientObject.border_color, 5, style=Qt.SolidLine)
            avatar_solid.setPen(pen1_solid)
            avatar_solid.drawRoundedRect(label_x, label_y, label_width, label_height, 20, 20)

            avatar_dashed = QPainter(clientObject)
            pen1_dashed = QPen(clientObject.border_color2, 5, style=Qt.DashLine)
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

        clientObject.color1_tuple = (clientObject.button1_border_color, clientObject.button2_border_color)
        clientObject.color2_tuple = (clientObject.button1_border_color2, clientObject.button2_border_color2)
        

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
        
        if clientObject.button1_border_color == clientObject.color1_tuple[0]:
            clientObject.button1_border_color = QColor(*clientObject.color2_tuple[0].getRgb())
            clientObject.button1_border_color2 = QColor(*clientObject.color1_tuple[0].getRgb())

            clientObject.button2_border_color = QColor(*clientObject.color2_tuple[1].getRgb())
            clientObject.button2_border_color2 = QColor(*clientObject.color1_tuple[1].getRgb())
        else:
            clientObject.button1_border_color = QColor(*clientObject.color1_tuple[0].getRgb())
            clientObject.button1_border_color2 = QColor(*clientObject.color2_tuple[0].getRgb())

            clientObject.button2_border_color = QColor(*clientObject.color1_tuple[1].getRgb())
            clientObject.button2_border_color2 = QColor(*clientObject.color2_tuple[1].getRgb())

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
            pen1_solid = QPen(border_color, 30, style=Qt.SolidLine)
            avatar_solid.setPen(pen1_solid)
            avatar_solid.drawRoundedRect(button_x, button_y, button_width, button_height, 20, 20)

            avatar_dashed = QPainter(clientObject)
            pen1_dashed = QPen(border_color2, 30, style=Qt.DashLine)
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

        self.setMinimumSize(60, 60)

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
        super().enterEvent(event)

    def leaveEvent(self, event):
        """leaveEvent : Fonction qui permet d'arrêter l'animation lorsque la souris quitte le bouton
        
        Args:
            event (QEvent): Événement de la souris"""
        self._animation.setDirection(QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)