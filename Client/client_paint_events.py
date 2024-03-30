from PyQt5.QtCore import *
from PyQt5.QtGui import *

class AvatarBorderBox():
    """AvatarBorderBox : Classe qui permet de dessiner un cadre autour d'un objet"""
    def __init__(self) -> None:
        pass        

    def setup_colors(self, clientObject):
        clientObject.border_color = QColor(255, 0, 0)  # Initial border color (red)
        clientObject.border_color2 = QColor(0, 255, 255)

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