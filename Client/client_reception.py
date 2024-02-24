import sys, socket, threading, time, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from client_utils import *

class ReceptionThread(QThread):
    name_correct = pyqtSignal(bool)
    sylb_received = pyqtSignal(str)
    game_signal = pyqtSignal(str)
    game_created = pyqtSignal(str, str)
    game_deleted = pyqtSignal(str)

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
                #print("Username already used")
                self.name_correct.emit(False)

            elif reply[0] == "NAME_CORRECT":
                #print("Username correct")
                self.name_correct.emit(True)
            
            elif reply[0] == "GAME":
                game_message = f"{reply[0]}|{reply[1]}|{reply[2]}"
                self.game_signal.emit(game_message)

            elif reply[0] == "GAME_CREATED":
                print("Game created")
                game_name = reply[1]
                private_game = reply[2]
                self.game_created.emit(game_name, private_game)

            elif reply[0] == "GAME_DELETED":
                print("Game deleted")
                game_name = reply[1]
                self.game_deleted.emit(f"{game_name}")

            else:
                self.sylb_received.emit(response)
                syllabe = response
                if syllabe in list_syllabes:
                    syllabes.append(syllabe)
                    print("///////////////////::ta mère")


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