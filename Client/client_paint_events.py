from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QPen

class AvatarBorderBox():
    """AvatarBorderBox : Classe qui permet de dessiner un cadre autour d'un objet"""
    def __init__(self) -> None:
        pass        

    def setup_colors(self, clientObject):
        clientObject.border_color = QColor(255, 0, 0)  # Initial border color (red)
        clientObject.border_color2 = QColor(0, 0, 255)

    def setup_timer(self, clientObject):
        clientObject.timer = QTimer(clientObject)
        clientObject.timer.timeout.connect(lambda: self.update_border_color(clientObject))
        clientObject.timer.start(500)

    def kill_timer(self, clientObject):
        clientObject.timer.stop()

    def update_border_color(self, clientObject):
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

    def border(self, clientObject : list, labels : list):
        """border() : Fonction qui permet de dessiner un cadre autour d'un objet
        
        Args:
            clientObject (object): Objet ClientWindow
            labels (list): Liste des labels à entourer d'un cadre"""
        
        label_pos = labels[1].mapTo(clientObject, QPoint(0,0))
        label_x = label_pos.x()
        label_y = label_pos.y()
        label_geometry = labels[1].geometry()
        label_width = label_geometry.width()
        label_height = label_geometry.height()

        avatar1_solid = QPainter(clientObject)
        pen1_solid = QPen(clientObject.border_color, 5, style=Qt.SolidLine)
        avatar1_solid.setPen(pen1_solid)
        avatar1_solid.drawRoundedRect(label_x, label_y, label_width, label_height, 20, 20)

        avatar1_dashed = QPainter(clientObject)
        pen1_dashed = QPen(clientObject.border_color2, 5, style=Qt.DashLine)
        avatar1_dashed.setPen(pen1_dashed)
        avatar1_dashed.drawRoundedRect(label_x, label_y, label_width, label_height, 20, 20)

