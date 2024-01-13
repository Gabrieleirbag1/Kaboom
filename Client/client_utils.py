import sys, socket, threading, time, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_thread = None