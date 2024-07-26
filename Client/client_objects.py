from PyQt5.QtGui import QMouseEvent
from client_utils import *
import log_config

log_config.setup_logging()

class ToolMainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.setStyleSheet(windows_stylesheet)

    def keyPressEvent(self, event: QKeyEvent):
        """keyPressEvent(event) : Appui sur une touche du clavier
        
        Args:
            event (QKeyEvent): Événement du clavier"""
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyPressEvent(event)
    
class DialogMainWindow(ToolMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setObjectName("dialog_window")
        self.setStyleSheet('''*{
                                font-family: Chilanka; 
                                font-size: 13pt;}
                           
                           QMainWindow#dialog_window{
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(140, 220, 220, 1), stop:1 rgba(169, 240, 191, 1));}
                           
                           QPushButton{
                                padding: 10;
                                border-radius: 10;
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(140, 220, 220, 1), stop:1 rgba(147, 190, 191, 1));
                                border: 3px solid rgba(0, 0, 0, 1);}
                           
                           QPushButton:hover{
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(147, 190, 191, 1), stop:1 rgba(140, 220, 220, 1));}
                           
                           QPushButton:pressed{
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(127, 170, 191, 1), stop:1 rgba(120, 200, 220, 1));}''')
        self.resize(int(screen_width // 6), int(screen_height // 7))
        center_window(self)
          
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

class HoverPixmapButton(ClickButton):
    def __init__(self, image : QPixmap, image_hover : QPixmap, parent = None):
        super().__init__()
        self.image = image
        self.image_hover = image_hover
    
    def enterEvent(self, event):
        self.setIcon(QIcon(self.image_hover))
        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(QIcon(self.image))
        return super().leaveEvent(event)
    
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

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.currentChanged.connect(lambda _: button_sound.sound_effects.windows_sound.play())

    def on_click(self):
        button_sound.sound_effects.windows_sound.play()

    def enterEvent(self, a0: QEvent | None) -> None:
        button_sound.sound_effects.ubuntu_sound.play()
        return super().enterEvent(a0)

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))

class ClickedSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.sliderReleased.connect(self.on_click)

    def on_click(self):
        button_sound.sound_effects.ubuntu_sound.play()

    def mousePressEvent(self, ev: QMouseEvent | None) -> None:
        button_sound.sound_effects.ubuntu_sound.play()
        return super().mousePressEvent(ev)

class ClickedCheckbox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.clicked.connect(self.on_click)

    def on_click(self):
        button_sound.sound_effects.windows_sound.play()