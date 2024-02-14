import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.zebi = QLabel("z   e    b    i")
        self.coeur = QPixmap("./Client/images/coeur.png")
        self.coeur_label = QLabel()
        self.coeur_label.setPixmap(self.coeur)

        self.grid = QVBoxLayout()
        self.grid.addWidget(self.coeur_label)
        self.grid.addWidget(self.zebi)
        self.setLayout(self.grid)

        self.setGeometry(10,10,20,20)
        self.setWindowTitle("PyQT show image")
        self.show()

        # Create a property animation for the QLabel
        self.animation = QPropertyAnimation(self.coeur_label, b"geometry")
        self.animation.setDuration(1000)  # Animation duration in milliseconds
        self.animation.setStartValue(self.coeur_label.geometry())
        self.animation.setEndValue(self.coeur_label.geometry().translated(100, 100))
        self.animation.setLoopCount(-1)  # Infinite loop
        self.animation.start()

    def resizeEvent(self, event):
        # Scale the font size based on the window size
        font_size = min(self.width(), self.height()) // 10
        font = QFont("Arial", font_size)
        self.zebi.setFont(font)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())