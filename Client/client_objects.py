from client_utils import *

class ToolMainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)

        self.setStyleSheet(stylesheet_window)

    def keyPressEvent(self, event: QKeyEvent):
        """keyPressEvent(event) : Appui sur une touche du clavier
        
        Args:
            event (QKeyEvent): Événement du clavier"""
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyPressEvent(event)
    
class ClickButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoDefault(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.clicked.connect(self.on_click)

    def on_click(self):
        button_sound.sound_effects.windows_sound.play()

    def enterEvent(self, a0: QEvent | None) -> None:
        button_sound.sound_effects.ubuntu_sound.play()
        return super().enterEvent(a0)
    
class ClickableWidget(QWidget):
    click_widget_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.click_widget_signal.emit()

class UnderlineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.underline_color = QColor(0, 0, 0)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.underline_color, 10, Qt.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        bottomLeftPoint = QPoint(self.rect().bottomLeft().x() + 30, self.rect().bottomLeft().y())
        bottomeRightPoint = QPoint(self.rect().bottomRight().x() - 30, self.rect().bottomRight().y())
        painter.drawLine(bottomLeftPoint, bottomeRightPoint)

class UnderlineLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.underline_color = QColor(0, 0, 0)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.underline_color, 10, Qt.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.rect().bottomLeft(), self.rect().bottomRight())