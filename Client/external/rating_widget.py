import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class RatingWidget(QWidget):
    """A QWidget that enables a user to choose a rating.
    """

    # Signal thta emits the value of the widget when changed.
    value_updated =pyqtSignal(int)

    def __init__(self, parent=None, icon_path=None, num_icons=9, rule_value=3):
        """Constructor.

        Kwargs:
            parent (QtCore.QObject): Parent of the RatingWigdet.
            icon_path (str): The location of the icon used to represent one value of a
                rating.
            num_icons (int): The number of icons the RatingWidget will display.
        """
        super(RatingWidget, self).__init__(parent)

        # Set defaults.
        self._value = 0
        self._max_value = num_icons

        # Fallback for the icon_path.
        icon_path=os.path.join(os.path.dirname(__file__), "../images/coeur.png")

        # Dynamically create QWidget layout.
        hbox = QHBoxLayout()
        hbox.setSpacing(10)

        # Add icons to the layout.
        self.icons = []
        for icon_value in range(1, self._max_value+ 1):
            icon_label = IconLabel(icon_path, icon_value, parent=self)
            icon_label.mouse_enter_icon.connect(self._set_icons_visible)
            icon_label.mouse_leave_icon.connect(self._set_active_icons_visible)
            icon_label.mouse_release_icon.connect(self.set_icons_active)

            self.icons.append(icon_label)
            hbox.addWidget(icon_label)

        # Set the created layout to the widget.
        self.setLayout(hbox)

        self.installEventFilter(self)

        self.set_icons_active(self.icons[rule_value-1])
        self._set_icons_visible(self.icons[rule_value-1])

    def _set_active_icons_visible(self):
        """Display any icons that are active.
        """
        for icon in self.icons:
            icon.visible = icon.active

    def set_icons_active(self, icon_label):
        """Update the icons active state.

        All icons less and equal to the value of the icon_label have their active status
        set to True. Everything higher than the icon_label have their active
        status set to False.
        eg. If icon_label 3 is passed in, then 1, 2 and 3 are active
           and 4 and 5 are innactive.

        Args:
            icons_label (IconLabel): The icon to update to.
        """
        self._value = icon_label.value
        self.value_updated.emit(self._value)
        for icon in self.icons:
            icon.active = (icon.value <= icon_label.value)

    def _set_icons_visible(self, icon_label):
        """Update the icons visibility.

        Args:
            icons_label (IconLabel): The icon to update to.
            visible (bool): Control if the visibility is set based on the icon_label
                or the active status.
                TODO. Rename this. Confusing.
        """
        for icon in self.icons:
            icon.visible = (icon.value <= icon_label.value)

    def eventFilter(self, obj, event):
        """Event filter defining custom actions.

        Args:
            obj (QObject): Unused by this derived method.
            event (QEvent): The event that occured.

        Returns:
            (bool) True. So the event can be handled further if required.
        """
        # When the mouse leaves the widget, set the icons visibility to it's value state.
        if event.type() == QEvent.Leave:
            self._set_active_icons_visible()
        else:
            super(RatingWidget, self).eventFilter(obj, event)
        return False

    @property
    def value(self):
        return self._value

    @property
    def max_value(self):
        return self._max_value

class IconLabel(QLabel):
    """A Qlabel that to represent an icon in the rating widget.
    """

    # Signal emitted when the mouse enteres the icon.
    mouse_enter_icon = pyqtSignal(QLabel)
    # Signal emitted when the mouse leaves the icon.
    mouse_leave_icon = pyqtSignal(QLabel)
    # Signal emitted when the mouse is released over an icon.
    mouse_release_icon = pyqtSignal(QLabel)

    def __init__(self, image_path, value, parent=None):
        """Constructor.
        Args:
            image_path (str): Path to the image to use for the icon.
            value (int): value of the icon.
            parent (QObject): Parent object for this class.
        """
        super(IconLabel, self).__init__(parent)

        self.setCursor(Qt.PointingHandCursor)
        # TODO protect image_path
        self._image_path = image_path
        self._active = False
        self._value = value
        self.image_path_not_selected = os.path.join(os.path.dirname(__file__), "../images/coeur-not-selected.png")

        # Enable mouse events without buttons being held down.
        self.setMouseTracking(True)

        self.installEventFilter(self)

    def set_image(self, value):
        """Set the image for the label.

        Args:
            value (bool): Flag for whether to use the image_path or no image for
                the in picture in the label.
        """
        if value:
            self.setPixmap(QPixmap(self._image_path))
        else:
            # TODO. Could have an empty equivalent of the image_path.
            self.setPixmap(QPixmap(self.image_path_not_selected))

    def eventFilter(self, obj, event):
        """Event filter defining custom actions.
        """
        # When the mouse _enters_ the label area, set the icon visible.
        if event.type() == QEvent.Enter:
            self.mouse_enter_icon.emit(self)
        # When the mouse _leaves_ the label area, set the icon invisible.
        elif event.type() == QEvent.Leave:
            self.mouse_leave_icon.emit(self)
        # When the mouse _clicks_ the label area, set the icon active.
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouse_release_icon.emit(self)
        else:
            super(IconLabel, self).eventFilter(obj, event)
        return False

    # Properties
    def _get_active(self):
        """Get the active state of the label.
        """
        return self._active

    def _set_active(self, value):
        """Set the active state of the label.
        Args:
            value (bool): The active state to set for the label.
        """
        self._active = value

    def _get_value(self):
        """Get the value state of the label.
        """
        return self._value

    def _get_visible(self):
        """Get the visible state of the label.
        """
        if not self.pixmap():
            return False
        else:
            return not self.pixmap().isNull()

    def _set_visible(self, value):
        """Set the visible state of the label.

        Args:
            value (bool): The visible state for the label.
        """
        self.set_image(value)

    active = property(_get_active, _set_active,
        doc="Get/Set the active state of the icon."
    )

    value = property(_get_value,
        doc="Get the value of the icon."
    )

    visible = property(_get_visible, _set_visible,
        doc="Get/Set the visible state of the icon."
    )

if __name__ == '__main__':
    app = QApplication([])
    rating_widget = RatingWidget()
    rating_widget.value_updated.connect(lambda value: print(value))
    rating_widget.show()
    app.exec_()

