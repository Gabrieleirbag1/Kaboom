from client_utils import *
from client_objects import ClickableWidget, ClickButton
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

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
        global main_stylesheet
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});border-radius: {radius}; padding: {padding}".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value, radius=30, padding=20
        )
        grad = f"QPushButton#{self.animated_objectName}{{{grad_string}}}"
        main_stylesheet += grad
        self.setStyleSheet(main_stylesheet)

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
        global main_stylesheet
        style = "QPushButton#{}{{font-size: {}pt}}".format(self.animated_objectName, size)
        main_stylesheet += style
        self.setStyleSheet(main_stylesheet)

class AnimatedWindow(QMainWindow):
    """AnimatedWindow: Class to create a window with animated background"""
    def __init__(self):
        """
        Initialize the AnimatedWindow class.
        """
        super().__init__()
        self.join_menu_loaded = False
        self.stylesheet_copy = copy.deepcopy(main_stylesheet)
        self.animation_started = False

    def set_animated_properties(self):
        """
        Set the properties of the animated window.
        """
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

    def _animate(self, value: float):
        """
        Animate the window.

        Args:
            value (float): Animation value.
        """
        global main_stylesheet
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1})".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value
        )
        grad = f"QMainWindow#client_mainwindow{{{grad_string}}}"
        main_stylesheet += grad
        self.setStyleSheet(main_stylesheet)

    def animation(self):
        """
        Start the window animation.
        """
        self.i += 1
        if self.i % 2 == 0:
            self._animation.setDirection(QAbstractAnimation.Backward)
        else:
            self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()

    def event(self, e: QEvent) -> bool:
        """
        Handle window events.

        Args:
            e (QEvent): Window event.

        Returns:
            bool: True if the event is handled.
        """
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
        global main_stylesheet
        grad_string = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});border-radius: {radius}; padding: {padding}; border: 5px outset;".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value, radius=30, padding=20
        )
        grad = f"QWidget#{self.animated_objectName}{{{grad_string}}}"
        main_stylesheet += grad
        self.setStyleSheet(main_stylesheet)

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
        button_width (int | float): Width multiplier.
        button_height (int | float): Height multiplier.
        color1 (str): First color.
        color2 (str): Second color.
        offset (tuple): Offset for the shadow effect.
        """
    def __init__(self, 
                 text: str | None, 
                 parent: object = None,
                 button_width: int | float = 3,
                 button_height: int | float = 3,
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
        super().__init__(text, parent)

        self.button_width = button_width
        self.button_height = button_height
        self.offset: tuple = offset
        self.color1: str = color1
        self.color2: str = color2

        self.resize(int(self.width() * self.button_width), int(self.height() * self.button_height))

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
        super().mousePressEvent(e)
    
    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        """
        Handle mouse release event.

        Args:
            e (QMouseEvent): Mouse event.
        """
        setattr(self.clientObject, f"should_draw_{self.parent_name}", True)
        super().mouseReleaseEvent(e)

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

        self.clientObject.update()
        
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