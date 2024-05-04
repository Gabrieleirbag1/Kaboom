from client_utils import *

class ClickButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoDefault(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.clicked.connect(self.on_click)

    def on_click(self):
        sound_effects.windows_sound.play()

    def enterEvent(self, a0: QEvent | None) -> None:
        sound_effects.ubuntu_sound.play()
        return super().enterEvent(a0)