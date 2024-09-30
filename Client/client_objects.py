from PyQt5.QtGui import QMouseEvent
from client_utils import *
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

class ToolMainWindow(QMainWindow):
    """Class to create a main window for the tools
    
    Attributes:
        parent (object): The parent object
    """
    def __init__(self, parent: object = None):
        """Constructor of the ToolMainWindow class
        
        Args:
            parent (object): The parent object"""
        super().__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.setStyleSheet(windows_stylesheet)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handles key press events
        
        Args:
            event (QKeyEvent): Keyboard event

        Returns:
            None
        """
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyPressEvent(event)
    
class DialogMainWindow(ToolMainWindow):
    """Class to create a dialog main window
    
    Attributes:
        parent (object): The parent object
    """
    def __init__(self, parent: object = None):
        """Constructor of the DialogMainWindow class

        Args:
            parent (object): The parent object"""
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
    """Class to create a clickable button with sound effects"""
    def __init__(self, *args, **kwargs):
        """Constructor of the ClickButton class"""
        super().__init__(*args, **kwargs)
        self.setAutoDefault(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.clicked.connect(self.on_click)

    def on_click(self):
        """Handles button click event"""
        button_sound.sound_effects.windows_sound.play()

    def enterEvent(self, a0: QEvent | None) -> None:
        """Handles mouse enter event
        
        Returns:
            None"""
        button_sound.sound_effects.ubuntu_sound.play()
        return super().enterEvent(a0)

class HoverPixmapButton(ClickButton):
    """Class to create a button that changes icon on hover
    
    Attributes:
        image (QPixmap): Default image
        image_hover (QPixmap): Image on hover
    """
    def __init__(self, image: QPixmap, image_hover: QPixmap, parent: object = None):
        """Constructor of the HoverPixmapButton class

        Args:
            image (QPixmap): Default image
            image_hover (QPixmap): Image on hover
            parent (object): The parent object"""
        super().__init__()
        self.image = image
        self.image_hover = image_hover
    
    def enterEvent(self, event: QEvent) -> None:
        """Handles mouse enter event
        
        Returns:
            None"""
        self.setIcon(QIcon(self.image_hover))
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handles mouse leave event
        
        Returns:
            None"""
        self.setIcon(QIcon(self.image))
        return super().leaveEvent(event)
    
class ClickableWidget(QWidget):
    """Class to create a clickable widget
    
    Signals:
        click_widget_signal: Emitted when the widget is clicked
    """
    click_widget_signal = pyqtSignal()

    def __init__(self, parent: object = None):
        """Constructor of the ClickableWidget class"""
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event: QEvent):
        """Handles mouse press event"""
        super().mousePressEvent(event)
        self.click_widget_signal.emit()

class UnderlineWidget(QWidget):
    """Class to create a widget with an underline
    
    Attributes:
        underline_color (QColor): Color of the underline
    """
    def __init__(self):
        """Constructor of the UnderlineWidget class"""
        super().__init__()
        self.underline_color = QColor(0, 0, 0)

    def paintEvent(self, event: QEvent):
        """Handles paint event"""
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
    """Class to create a QLineEdit with an underline
    
    Attributes:
        underline_color (QColor): Color of the underline
    """
    def __init__(self):
        """Constructor of the UnderlineLineEdit class"""
        super().__init__()
        self.underline_color = QColor(0, 0, 0)

    def paintEvent(self, event: QEvent):
        """Handles paint event"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.underline_color, 10, Qt.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.rect().bottomLeft(), self.rect().bottomRight())

class CustomTabBar(QTabBar):
    """Class to create a custom tab bar with sound effects"""
    def __init__(self, parent: object = None):
        """Constructor of the CustomTabBar class

        Args:
            parent (object): The parent object"""
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.currentChanged.connect(lambda _: button_sound.sound_effects.windows_sound.play())

    def on_click(self):
        """Handles tab click event"""
        button_sound.sound_effects.windows_sound.play()

    def enterEvent(self, a0: QEvent | None) -> None:
        """Handles mouse enter event
        
        Returns:
            None"""
        button_sound.sound_effects.ubuntu_sound.play()
        return super().enterEvent(a0)

class CustomTabWidget(QTabWidget):
    """Class to create a custom tab widget with a custom tab bar"""
    def __init__(self, parent: object = None):
        """Constructor of the CustomTabWidget class"""
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))

class ClickedSlider(QSlider):
    """Class to create a slider with sound effects"""
    def __init__(self, *args, **kwargs):
        """Constructor of the ClickedSlider class"""
        super().__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.sliderReleased.connect(self.on_click)

    def on_click(self):
        """Handles slider release event"""
        button_sound.sound_effects.ubuntu_sound.play()

    def mousePressEvent(self, ev: QMouseEvent | None) -> None:
        """Handles mouse press event
        
        Returns:
            None"""
        button_sound.sound_effects.ubuntu_sound.play()
        return super().mousePressEvent(ev)

class ClickedCheckbox(QCheckBox):
    """Class to create a checkbox with sound effects"""
    def __init__(self, *args, **kwargs):
        """Constructor of the ClickedCheckbox class"""
        super().__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.clicked.connect(self.on_click)

    def on_click(self):
        """Handles checkbox click event"""
        button_sound.sound_effects.windows_sound.play()