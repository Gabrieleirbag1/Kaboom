import sys, socket, threading, time, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from client_utils import *

class ReceptionThread(QThread):
    message_received = pyqtSignal(str)
    name_correct = pyqtSignal(bool)
    sylb_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        global syllabe
        flag = False
        while not flag:
            response = client_socket.recv(1024).decode()
            print(response)
            try:
                reply = response.split("|")
            except:
                reply = response

            if not response:
                flag = True

            elif reply[0] == "NAME_ALREADY_USED":
                print("Username already used")
                self.name_correct.emit(False)

            elif reply[0] == "NAME_CORRECT":
                print("Username correct")
                self.name_correct.emit(True)
            
            else:
                self.sylb_received.emit(response)
                syllabe = response
                syllabes.append(syllabe)


class ConnectThread(QThread):
    connection_established = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            client_socket.connect(("localhost", 22222))
            self.connection_established.emit()
            print("Connection established")
        except:
            print("Connection failed")
            time.sleep(5)
            self.run()