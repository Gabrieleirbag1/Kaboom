import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())