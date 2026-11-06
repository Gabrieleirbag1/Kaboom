from client_utils import *
from client_objects import ClickableWidget, ClickButton
from client_logs import ErrorLogger

ErrorLogger.setup_logging()


class OutlinedLabel(QLabel):
    """A one-line label whose letters have an outline, so the text can be read on any background."""
    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.outline_color: QColor | None = None
        self.outline_ratio = 0.0

    def set_outline(self, color: QColor | None, ratio: float = 0.12):
        """
        Args:
            color (QColor | None): Color of the outline (None: no outline).
            ratio (float): Thickness of the outline, as a share of the font's height.
        """
        self.outline_color, self.outline_ratio = color, ratio
        self.updateGeometry()
        self.update()

    def outline_width(self) -> float:
        return max(2.0, QFontMetricsF(self.font()).height() * self.outline_ratio) if self.outline_color else 0.0

    def sizeHint(self) -> QSize:
        extra = int(self.outline_width()) + 2  # room for the outline around the first and last letters
        return super().sizeHint() + QSize(extra, 0)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def paintEvent(self, event: QPaintEvent):
        if not self.outline_color or not self.text():
            return super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        metrics = QFontMetricsF(self.font())
        x = (self.width() - metrics.horizontalAdvance(self.text())) / 2
        y = (self.height() + metrics.ascent() - metrics.descent()) / 2
        path = QPainterPath()
        path.addText(x, y, self.font(), self.text())
        # The pen is centered on the letters' edges: the fill then covers its inner half
        painter.strokePath(path, QPen(self.outline_color, self.outline_width(), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.fillPath(path, self.palette().color(QPalette.WindowText))
        painter.end()


class PulsingGlow(QObject):
    """A colored glow around a widget that gently pulses while it is on (it stays still when the
    player turned animations off in the settings)."""
    def __init__(self, widget: QWidget, color: QColor, low: float, high: float, period_ms: int = 1000):
        """
        Args:
            widget (QWidget): The widget that glows.
            color (QColor): Color of the glow.
            low (float): Smallest glow size (blur radius, in pixels on a 1920x1080 screen).
            high (float): Biggest glow size.
            period_ms (int): Duration of one pulse.
        """
        super().__init__(widget)
        self.high = high * UI_SCALE
        self.effect = QGraphicsDropShadowEffect(widget)
        self.effect.setOffset(0, 0)
        self.effect.setColor(color)
        self.effect.setEnabled(False)
        widget.setGraphicsEffect(self.effect)
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(period_ms)
        self.animation.setKeyValueAt(0, low * UI_SCALE)
        self.animation.setKeyValueAt(0.5, self.high)
        self.animation.setKeyValueAt(1, low * UI_SCALE)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self.effect.setBlurRadius)

    def start(self):
        """Turns the glow on."""
        self.effect.setEnabled(True)
        if settings.accessibility_data[2][1] == "yes":
            if self.animation.state() != QAbstractAnimation.Running:
                self.animation.start()
        else:
            self.effect.setBlurRadius(self.high)

    def stop(self):
        """Turns the glow off."""
        self.animation.stop()
        self.effect.setEnabled(False)

    @property
    def active(self) -> bool:
        return self.effect.isEnabled()


class AvatarBorderBox():
    """AvatarBorderBox: Class to draw a border around an object"""
    def __init__(self):
        """Initialize the AvatarBorderBox class"""
        pass

    def setup_colors(self, clientObject: object) -> dict:
        """
        Define the border colors.

        Args:
            clientObject (object): ClientWindow object

        Returns:
            dict: Dictionary of avatar colors
        """
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
            "bouteille-avatar": ((253, 72, 255), (65, 253, 164)),
            "cactus-avatar": ((255, 150, 0), (17, 136, 0)),
            "gameboy-avatar": ((12, 219, 144), (0, 47, 150)),
            "panneau-avatar": ((244, 186, 85), (226, 18, 81)),
            "pizza-avatar": ((186, 0, 0), (255, 217, 24)),
            "reveil-avatar": ((177, 30, 154), (140, 213, 252)),
            "robot-ninja-avatar": ((252, 144, 144), (145, 4, 122)),
            "serviette-avatar": ((42, 152, 228), (0, 255, 255)),
            "tasse-avatar": ((42, 46, 228), (124, 204, 196)),
            "television-avatar": ((170, 26, 147), (245, 148, 107))
        }

        self.player_border_color1_tuple = (
            clientObject.player1_border_color, clientObject.player2_border_color, clientObject.player3_border_color,
            clientObject.player4_border_color, clientObject.player5_border_color, clientObject.player6_border_color,
            clientObject.player7_border_color, clientObject.player8_border_color)
        self.player_border_color2_tuple = (
            clientObject.player1_border_color2, clientObject.player2_border_color2, clientObject.player3_border_color2,
            clientObject.player4_border_color2, clientObject.player5_border_color2, clientObject.player6_border_color2,
            clientObject.player7_border_color2, clientObject.player8_border_color2)
        clientObject.player_border_size = [12, 12, 12, 12, 12, 12, 12, 12]

        return self.avatars_colors_dico

    def setup_timer(self, clientObject: object):
        """
        Start the timer.

        Args:
            clientObject (object): ClientWindow object
        """
        clientObject.timer2 = QTimer(clientObject)
        clientObject.timer2.timeout.connect(lambda: self.update_border_color(clientObject))
        clientObject.timer2.start(700)

    def kill_timer(self, clientObject: object):
        """
        Stop the timer.

        Args:
            clientObject (object): ClientWindow object
        """
        clientObject.timer2.stop()

    def update_border_color(self, clientObject: object):
        """
        Update the border color.

        Args:
            clientObject (object): ClientWindow object
        """
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

    def border(self, clientObject: object, labels: list):
        """
        Draw a border around an object.

        Args:
            clientObject (object): ClientWindow object
            labels (list): List of labels to surround with a border
        """
        try:
            avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid = None, None, None, None, None, None, None, None
            avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed = None, None, None, None, None, None, None, None
            avatar_vars_dico = {"Solid": [avatar1_solid, avatar2_solid, avatar3_solid, avatar4_solid, avatar5_solid, avatar6_solid, avatar7_solid, avatar8_solid],
                                "Dashed": [avatar1_dashed, avatar2_dashed, avatar3_dashed, avatar4_dashed, avatar5_dashed, avatar6_dashed, avatar7_dashed, avatar8_dashed]}
            for i, (label, avatar_solid, avatar_dashed) in enumerate(zip(labels, avatar_vars_dico["Solid"], avatar_vars_dico["Dashed"])):
                label_pos = label.mapTo(clientObject, QPoint(0, 0))
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
    """ButtonBorderBox: Class to draw a border around a button"""
    def __init__(self) -> None:
        """Initialize the ButtonBorderBox class"""
        pass

    def setup_colors(self, clientObject: object):
        """
        Define the border colors.

        Args:
            clientObject (object): ClientWindow object
        """
        clientObject.button1_border_color = QColor(135, 46, 255)
        clientObject.button1_border_color2 = QColor(82, 207, 95)

        clientObject.button2_border_color = QColor(253, 179, 65)
        clientObject.button2_border_color2 = QColor(253, 66, 255)

        self.color1_tuple = (clientObject.button1_border_color, clientObject.button2_border_color)
        self.color2_tuple = (clientObject.button1_border_color2, clientObject.button2_border_color2)

    def setup_timer(self, clientObject: object):
        """
        Start the timer.

        Args:
            clientObject (object): ClientWindow object
        """
        clientObject.timer = QTimer(clientObject)
        clientObject.timer.timeout.connect(lambda: self.update_border_color(clientObject))
        clientObject.timer.start(500)  # 500ms

    def kill_timer(self, clientObject):
        """
        Stop the timer.

        Args:
            clientObject (object): ClientWindow object
        """
        clientObject.timer.stop()

    def update_border_color(self, clientObject: object):
        """
        Update the border color.

        Args:
            clientObject (object): ClientWindow object
        """
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

    def border(self, clientObject: object, buttons: list):
        """
        Draw a border around a button.

        Args:
            clientObject (object): ClientWindow object
            buttons (list): List of buttons to surround with a border
        """
        button1_solid, button2_solid = None, None
        button1_dashed, button2_dashed = None, None
        button_vars_dico = {
            "Solid": [button1_solid, button2_solid],
            "Dashed": [button1_dashed, button2_dashed],
            "Color1": [clientObject.button1_border_color, clientObject.button2_border_color],
            "Color2": [clientObject.button1_border_color2, clientObject.button2_border_color2],
        }
        for button, avatar_solid, avatar_dashed, border_color, border_color2 in zip(buttons, button_vars_dico["Solid"], button_vars_dico["Dashed"], button_vars_dico["Color1"], button_vars_dico["Color2"]):
            button_pos = button.mapTo(clientObject, QPoint(0, 0))
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
    """AnimatedButton: Class to create an animated button
    
    Attributes:
        animated_objectName (str): Name of the object to animate.
        color1 (QColor): First color.
        color2 (QColor): Second color.
        _animation (QVariantAnimation): Animation object.
    """
    def __init__(self, animated_objectName: str, color1: QColor, color2: QColor):
        """
        Initialize the AnimatedButton class.

        Args:
            animated_objectName (str): Name of the object to animate.
            color1 (QColor): First color.
            color2 (QColor): Second color.
        """
        super().__init__()

        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setAutoDefault(True)
        self.animated_objectName = animated_objectName
        self.color1 = color1
        self.color2 = color2
        self.gradient_style = ""
        self.size_style = ""

        self._animation = QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=250
        )

        self.clicked.connect(self.on_click)

    def on_click(self):
        """
        Play a sound when the button is clicked.
        """
        button_sound.sound_effects.windows_sound.play()

    def _animate(self, value: float):
        """
        Animate the button.

        Args:
            value (float): Animation value.
        """
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});border-radius: {radius}; padding: {padding}".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value, radius=30, padding=20
        )
        self.gradient_style = f"QPushButton#{self.animated_objectName}{{{grad_string}}}"
        self.apply_style()

    def apply_style(self):
        """
        Give the button its own small style sheet: its hover gradient and font size. The rest of its
        look comes from the window's style sheet. (Adding these rules to the whole style sheet at every
        frame made it grow without end and slowed the game down.)
        """
        self.setStyleSheet(self.gradient_style + self.size_style)

    def enterEvent(self, event: QEvent):
        """
        Trigger animation when the mouse enters the button.

        Args:
            event (QEvent): Mouse event.
        """
        self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()
        button_sound.sound_effects.play_sound(button_sound.sound_effects.select_sound)
        self.change_size_button(90)
        self.setFocus()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """
        Stop animation when the mouse leaves the button.

        Args:
            event (QEvent): Mouse event.
        """
        self._animation.setDirection(QAbstractAnimation.Backward)
        self._animation.start()
        self.change_size_button(80)
        super().enterEvent(event)

    def focusInEvent(self, a0: QFocusEvent) -> None:
        """
        Play a sound when the button is focused.

        Args:
            a0 (QFocusEvent): Focus event.

        Returns:
            None
        """
        if a0.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            button_sound.sound_effects.play_sound(button_sound.sound_effects.select_sound)
            self.change_size_button(90)
        return super().focusInEvent(a0)
    
    def focusOutEvent(self, a0: QFocusEvent) -> None:
        """
        Play a sound when the button is no longer focused.

        Args:
            a0 (QFocusEvent): Focus event.

        Returns:
            None
        """
        if a0.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            self.change_size_button(80)
        return super().focusOutEvent(a0)
    
    def change_size_button(self, size: int):
        """
        Change the size of the button.

        Args:
            size (int): Button size.
        """
        self.size_style = "QPushButton#{}{{font-size: {}px}}".format(self.animated_objectName, font_px(size))
        self.apply_style()

class AnimatedWindow(QMainWindow):
    """AnimatedWindow: Class to create a window with animated background.

    The background is a gradient of the two theme colors whose middle slowly moves from the top-left
    corner to the bottom-right one and back. It is painted in paintEvent: changing the window's style
    sheet at every frame instead made Qt restyle every widget of the window ~60 times a second."""
    GRADIENT_PERIOD_S = 14  # there and back
    # Each frame repaints the whole window: at 60 fps that alone took 70 % of a core in 1920x1080.
    # The gradient moves slowly, 20 fps looks just as smooth for a third of the cost.
    GRADIENT_FPS = 20

    def __init__(self):
        """
        Initialize the AnimatedWindow class.
        """
        super().__init__()
        self.join_menu_loaded = False
        self.gradient_timer: QTimer | None = None
        self.gradient_start = 0.0
        self.gradient_position = 0.0

    def set_animated_properties(self):
        """
        Start the moving background, in the colors of the theme chosen in the settings.
        """
        self.color1 = QColor(*self.hex_to_rgb(settings.accessibility_data[0][1].split("/")[0]))
        self.color2 = QColor(*self.hex_to_rgb(settings.accessibility_data[0][1].split("/")[1]))
        if self.gradient_timer is None:
            self.gradient_start = time.monotonic()
            self.gradient_timer = QTimer(self)
            self.gradient_timer.timeout.connect(self._animate)
            self.gradient_timer.start(1000 // self.GRADIENT_FPS)
        self.update()

    def hex_to_rgb(self, hex_code: str) -> tuple:
        """
        Convert a hexadecimal color code to RGBA format.

        Args:
            hex_code (str): Hexadecimal color code.

        Returns:
            tuple: RGBA color values.
        """
        hex_code = hex_code.lstrip('#')
        rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        rgba = (*rgb, 255)
        return rgba

    def _animate(self):
        """
        Move the middle of the background gradient: from the top-left corner (0) to the bottom-right
        one (1) and back, in GRADIENT_PERIOD_S seconds.
        """
        phase = (time.monotonic() - self.gradient_start) % self.GRADIENT_PERIOD_S / self.GRADIENT_PERIOD_S
        self.gradient_position = 0.00001 + 0.99989 * (1 - abs(2 * phase - 1))
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the moving background (once set_animated_properties was called).

        Args:
            event (QPaintEvent): Paint event.
        """
        if self.gradient_timer is not None:
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, self.color1)
            gradient.setColorAt(self.gradient_position, self.color2)
            gradient.setColorAt(1, self.color1)
            painter = QPainter(self)
            painter.fillRect(event.rect(), gradient)
            painter.end()
        super().paintEvent(event)

    def emptyFunction(self, *args):
        """
        Empty function.
        """
        pass

class AnimatedGameWidget(ClickableWidget):
    """AnimatedGameWidget: Class to create an animated game widget"""
    def __init__(self, game_name: str, color1: QColor, color2: QColor):
        """
        Initialize the AnimatedGameWidget class.

        Args:
            game_name (str): Name of the game.
            color1 (QColor): First color.
            color2 (QColor): Second color.
        """
        super().__init__()
        self.animated_objectName = game_name
        self.setObjectName(game_name)
        self.set_animated_properties(color1, color2)

    def set_animated_properties(self, color1: QColor, color2: QColor):
        """
        Set the properties of the animated widget.

        Args:
            color1 (QColor): First color.
            color2 (QColor): Second color.
        """
        self.color1 = color1
        self.color2 = color2
        self._animation = QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=250
        )

    def _animate(self, value: float):
        """
        Animate the widget.

        Args:
            value (float): Animation value.
        """
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});border-radius: {radius}; padding: {padding}; border: 5px outset;".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value, radius=30, padding=20
        )
        # Only its own rule: the rest of its look comes from the window's style sheet
        self.setStyleSheet(f"QWidget#{self.animated_objectName}{{{grad_string}}}")

    def enterEvent(self, event: QEvent):
        """
        Trigger animation when the mouse enters the widget.

        Args:
            event (QEvent): Mouse event.
        """
        self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()
        button_sound.sound_effects.play_sound(button_sound.sound_effects.select_sound)
        self.setFocus()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """
        Stop animation when the mouse leaves the widget.

        Args:
            event (QEvent): Mouse event.
        """
        self._animation.setDirection(QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

class LinearGradiantLabel(QLabel):
    """Class to create a label with a linear gradient"""
    def __init__(self, text: str, color1: QColor = QColor(84, 58, 180, 255), color2: QColor = QColor(253, 89, 29, 255), *args, **kwargs):
        """
        Initialize the LinearGradiantLabel class.

        Args:
            text (str): Text to display on the label.
            color1 (QColor): First color of the gradient.
            color2 (QColor): Second color of the gradient.
        """
        super().__init__(*args, **kwargs)
        self.text_label = text
        self.color1 = color1
        self.color2 = color2

    def paintEvent(self, event: QPaintEvent | None) -> None:
        """
        Paint the label with a linear gradient.

        Args:
            event (QPaintEvent): Paint event.

        Retunrs:
            None
        """
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
    """Class to create a styled button
    
    Attributes:
        clientObject (object): Client object.
        button_width (int | float): Width multiplier.
        button_height (int | float): Height multiplier.
        color1 (str): First color.
        color2 (str): Second color.
        offset (tuple): Offset for the shadow effect.
        """
    def __init__(self, 
                 text: str | None, 
                 clientObject: object = None,
                 button_width: int | float = 0.5,
                 button_height: int | float = 0.15,
                 color1: str = "lightblue", 
                 color2: str = "pink", 
                 offset: tuple = (15, 15)) -> None:
        """
        Initialize the StyledButton class.

        Args:
            text (str): Text to display on the button.
            parent (object): Parent object.
            button_width (int | float): Width multiplier.
            button_height (int | float): Height multiplier.
            color1 (str): First color.
            color2 (str): Second color.
            offset (tuple): Offset for the shadow effect.
        """
        super().__init__(text, clientObject)

        self.clientObject = clientObject
        self.button_width = button_width
        self.button_height = button_height
        self.offset: tuple = offset
        self.color1: str = color1
        self.color2: str = color2

        self.setFixedSize(int(self.clientObject.width() * self.button_width), int(self.clientObject.height() * self.button_height))

        self.setStyleSheet(scale_stylesheet(f'''
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
        '''))
        effect = QGraphicsDropShadowEffect()
        self.effect = effect
        effect.setOffset(*self.offset)
        effect.setBlurRadius(5)

        self.setGraphicsEffect(effect)

    def showEvent(self, event: QShowEvent):
        """Makes the button tall enough for its text (its font is known once it is shown)."""
        padding, margin = 2 * max(1, round(15 * UI_SCALE)), 2 * max(1, round(4 * UI_SCALE))
        needed = self.fontMetrics().height() + padding + margin + 2
        if self.height() < needed:
            self.setFixedHeight(needed)
        super().showEvent(event)

    def mousePressEvent(self, event: QMouseEvent | None):
        """Handle mouse press event.

        Args:
            event (QMouseEvent): Mouse event.
        """
        self.setStyleSheet(self.styleSheet() + f'''QPushButton{{background-color: {self.color2};}}''')
        self.effect.setOffset(0, 0)
        self.move(self.x() + self.offset[0], self.y() + self.offset[1])  # Move the button
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent | None):
        """Handle mouse release event.

        Args:
            event (QMouseEvent): Mouse event.
        """
        self.setStyleSheet(self.styleSheet() + f'''QPushButton{{background-color: {self.color1};}}''')
        self.effect.setOffset(*self.offset)
        self.move(self.x() - self.offset[0], self.y() - self.offset[1])  # Move the button back to its original position
        super().mouseReleaseEvent(event)

class StyledBorderButton(ClickButton):
    """Class to create a button with a styled border
    
    Attributes:
        clientObject (object): Client object.
        parent_name (str): Name of the parent.
        color1 (QColor): First color.
        color2 (QColor): Second color."""
    def __init__(self, 
                 text: str | None, 
                 parent: object = None,
                 parent_name: str = None,
                 color1: str = "lightblue", 
                 color2: str = "pink") -> None:
        """
        Initialize the StyledBorderButton class.

        Args:
            text (str): Text to display on the button.
            parent (object): Parent object.
            parent_name (str): Name of the parent.
            color1 (str): First color.
            color2 (str): Second color.
        """
        super().__init__(text, parent)
        
        self.clientObject: object = parent
        self.parent_name = parent_name
        self.color1: QColor = color1
        self.color2: QColor = color2

        setattr(self.clientObject, f"should_draw_{parent_name}", True)
        self.should_draw = getattr(self.clientObject, f"should_draw_{self.parent_name}")

        self.setStyleSheet(scale_stylesheet(f'''
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
        '''))

    def set_drop_shadow_effect_text(self):
        """Set the drop shadow effect for the button text."""
        effect = QGraphicsDropShadowEffect()
        self.effect = effect
        effect.setOffset(3, 3)
        effect.setBlurRadius(10)
        self.setGraphicsEffect(effect)
    

    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        """
        Handle mouse press event.

        Args:
            e (QMouseEvent): Mouse event.
        """
        setattr(self.clientObject, f"should_draw_{self.parent_name}", False)
        self.clientObject.update()  # the window draws this button's border (DrawStyledButton)
        super().mousePressEvent(e)
    
    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        """
        Handle mouse release event.

        Args:
            e (QMouseEvent): Mouse event.
        """
        setattr(self.clientObject, f"should_draw_{self.parent_name}", True)
        self.clientObject.update()
        super().mouseReleaseEvent(e)

    def changeEvent(self, e: QEvent) -> None:
        """
        Redraw the border when the button is enabled or disabled (it's grey when disabled).

        Args:
            e (QEvent): Change event.
        """
        if e.type() == QEvent.EnabledChange:
            self.clientObject.update()
        super().changeEvent(e)

class DrawStyledButton():
    """DrawStyledButton: Class to draw a styled button
    
    Attributes:
        button (QPushButton): Button to draw.
        clientObject (object): Client object."""
    def __init__(self, button: QPushButton, clientObject: object) -> None:
        """
        Initialize the DrawStyledButton class.

        Args:
            button (QPushButton): Button to draw.
            clientObject (object): Client object.
        """
        self.button = button
        self.clientObject = clientObject

    def draw_border(self, offset: int, color: QColor) -> None:
        """
        Draw the border of the button.

        Args:
            offset (int): Offset for the border.
            color (QColor): Color of the border.
        """
        if self.button.isEnabled():
            border_color = QColor(61, 59, 57)
        else:
            border_color = QColor(180, 180, 180)

        border_solid = QPainter(self.clientObject)
        solid_pen = QPen(border_color, 4, style=Qt.PenStyle.SolidLine)
        border_solid.setPen(solid_pen)

        button_pos = self.button.mapTo(self.clientObject, QPoint(0, 0))
        button_x = button_pos.x()
        button_y = button_pos.y()

        button_geometry = self.button.geometry()
        button_width = button_geometry.width()
        button_height = button_geometry.height()

        self.fill_button(border_solid, button_x, button_y, button_width, button_height, color)

        border_solid.drawRoundedRect(button_x + offset, button_y - offset, button_width, button_height, 10, 10)
        # No update() here: this runs while the window paints, so asking for another paint made the
        # lobby and the game repaint without stop (a whole CPU core). StyledBorderButton asks for a
        # repaint when its border changes.
        
    def fill_button(self, 
                    border_solid: QPainter, 
                    button_x: int, button_y: int, 
                    button_width: int, 
                    button_height: int,
                    color: QColor) -> None:
        """
        Fill the button with color.

        Args:
            border_solid (QPainter): QPainter object.
            button_x (int): X position of the button.
            button_y (int): Y position of the button.
            button_width (int): Width of the button.
            button_height (int): Height of the button.
            color (QColor): Color to fill the button.
        """
        fill_path = QPainterPath()
        fill_path.addRoundedRect(button_x, button_y, button_width, button_height, 10, 10)

        border_solid.fillPath(fill_path, color)