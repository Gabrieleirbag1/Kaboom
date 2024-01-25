import sys, socket, threading, time, random, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_thread = None
username = None
syllabes = []
rules = []

styles_file_path = os.path.join(os.path.dirname(__file__), "styles/client.qss")
style_file = QFile(styles_file_path)
style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
stylesheet = QTextStream(style_file).readAll()