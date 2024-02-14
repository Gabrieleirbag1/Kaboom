import sys, socket, threading, time, random, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_thread = None
username = None
syllabes = []
rules = [5, 7, 3, 3]
list_syllabes = ("ai", "an", "au", "ay", "ea", "ee", "ei", "eu", "ey", "ie", "is", "oe", "oi", "oo", "ou", "oy", "ui", "uy", "y", "ch", "sh", "th", "dge", "tch", "ng", "ph", "gh", "kn", "wr", "mb", "ll", "mm", "nn", "pp", "rr", "ss", "tt", "zz", "qu", "ce", "ci", "ge", "gi", "gue", "que", "se", "si", "ze", "ssi", "s", "c", "g", "sc", "xo","cq", "bra", "bre", "bri", "bro", "bru", "dra", "dre", "dri", "dro", "dru", "fra", "fre", "fri", "fro", "fru", "gra", "gre", "gri", "gro", "gru", "pra", "pre", "pri", "pro", "pru", "tra", "tre", "tri", "tro", "tru", "bla", "ble", "bli", "blo", "blu", "cla", "cle", "cli", "clo", "dra", "dre", "dri", "dro", "dru", "fra", "fre", "fri", "fro", "fru", "gra", "gre", "gri", "gro", "gru", "pra", "pre", "pri", "pro", "pru", "tra", "tre", "tri", "tro", "tru")


styles_file_path = os.path.join(os.path.dirname(__file__), "styles/client.qss")
style_file = QFile(styles_file_path)
style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
stylesheet = QTextStream(style_file).readAll()