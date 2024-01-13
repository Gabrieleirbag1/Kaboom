import sys, socket, threading, time, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from client_reception import ReceptionThread, ConnectThread
from client_utils import *

class Login(QMainWindow):
    login_accepted = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.setup()

    def setup(self):
        global receiver_thread
        self.setWindowTitle("Login")
        layout = QGridLayout()

        self.label = QLabel("Username:", self)
        layout.addWidget(self.label, 0, 0)

        self.username_edit = QLineEdit(self)
        layout.addWidget(self.username_edit, 0, 1)
        self.username_edit.returnPressed.connect(self.send_username)

        self.alert_label = QLabel("", self)
        self.alert_label.setStyleSheet("color: red;")
        layout.addWidget(self.alert_label, 1, 0, 1, 2)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.send_username)
        layout.addWidget(self.login_button, 2, 0, 1, 2)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)
        receiver_thread.name_correct.connect(self.show_window)

    def send_username(self):
        username = self.username_edit.text()
        client_socket.send(f"NEW_USER|{username}".encode())
        self.username_edit.clear()

    def show_window(self, name_correct):
        if name_correct:
            self.close()
            window.show()
        else:
            self.alert_label.setText("Username already used")

class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setup()
    
    def setup(self):
        self.setWindowTitle("Client")
        layout = QGridLayout()

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit, 0, 0, 1, 2)

        self.send_button = QPushButton("Send", self)
        layout.addWidget(self.send_button, 1, 0)
        self.send_button.clicked.connect(self.send_message)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


        self.setup_threads()

    def setup_threads(self):
        global receiver_thread
        self.connect_thread = ConnectThread()
        self.connect_thread.start()
        self.connect_thread.connection_established.connect(self.connect_to_server)

        receiver_thread = ReceptionThread()




    def connect_to_server(self):
        global receiver_thread
        receiver_thread.message_received.connect(self.display_message)
        receiver_thread.start()

    def send_message(self):
        message = self.text_edit.toPlainText()
        client_socket.send(message.encode())
        self.text_edit.clear()

    def display_message(self, message):
        self.text_edit.append(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientWindow()
    login = Login()
    login.show()
    sys.exit(app.exec_())
