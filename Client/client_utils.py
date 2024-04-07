import sys, socket, threading, time, random, os, datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

broker = 'localhost'
port = 1883
topic = "test"
client_id = f'publish-{random.randint(0, 1000)}'
username = 'frigiel'
password = 'toto'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None
syllabes = []
rules = [5, 7, 3, 2, 3, 1]

image_path = os.path.join(os.path.dirname(__file__), "images/")

styles_file_path = os.path.join(os.path.dirname(__file__), "styles/client.qss")
style_file = QFile(styles_file_path)
style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
stylesheet_window = QTextStream(style_file).readAll()

app = QApplication(sys.argv)
QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Bubble Love Demo.otf"))
QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Game On_PersonalUseOnly.ttf"))
screen_size = QDesktopWidget().screenGeometry()
screen_width, screen_height = screen_size.width(), screen_size.height()



def center_window(object):
    qr = object.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    object.move(qr.topLeft())
