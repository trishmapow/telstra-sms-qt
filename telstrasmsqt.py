import sys
import re
import configparser
import requests
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QGridLayout,
    QLineEdit,
    QSizePolicy,
    QInputDialog,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtGui import QIcon

import api
from message import *

config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str # case sensitive keys
config.read('app.conf')

class App(QMainWindow):
    """Main GUI for app"""

    WIDTH = 640
    HEIGHT = 480

    def __init__(self):
        super().__init__()

        self.bearer = None
        self.phone_number = None
        self.received_messages = []
        self.num_label = QLabel()
        self.num_text = QLineEdit()
        self.msg_text = QLineEdit()
        self.msg_table = QTableWidget()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Telstra SMS")
        self.resize(self.WIDTH, self.HEIGHT)
        self.set_status("Ready")

        main_widget = QWidget()
        grid = QGridLayout()

        self.num_label.setText("Num: N/A (request token)")

        bearer_button = QPushButton("Get token")
        bearer_button.clicked.connect(self.choose_bearer)

        self.num_text.setPlaceholderText("Dest. number")

        self.msg_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.msg_text.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.msg_text.setPlaceholderText("Message")

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)

        fetch_button = QPushButton("Receive")
        fetch_button.clicked.connect(self.get_message)
        
        #self.msg_table.setRowCount(10)
        self.msg_table.setColumnCount(3)
        self.msg_table.setHorizontalHeaderLabels(['Sender', 'Time', 'Message'])
        self.msg_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        grid.addWidget(bearer_button, 0, 3)
        grid.addWidget(self.num_label, 0, 0)
        grid.addWidget(self.num_text, 1, 0, 1, 4)
        grid.addWidget(self.msg_text, 2, 0, 1, 4)
        grid.addWidget(send_button, 3, 3)
        grid.addWidget(fetch_button, 3, 0)
        grid.addWidget(self.msg_table, 4, 0, 1, 4)

        main_widget.setLayout(grid)
        self.setCentralWidget(main_widget)

        self.show()

    def set_status(self, message):
        self.statusBar().showMessage(message)

    def api_request(self, f, *args):
        try:
            response = f(*args)
        except requests.exceptions.Timeout:
            self.set_status("Request timed out, try again")
        except requests.exceptions.ConnectionError:
            self.set_status("Network problem, check connection and try again")
        except Exception as e:
            self.set_status(f"Error calling {f.__name__}, check logs")
            print(e)
        else:
            return response

    def get_message(self):
        if self.bearer is None:
            return self.set_status("Request bearer first")

        self.set_status("Fetching messages...")        
        while True:
            response = self.api_request(api.get_message, self.bearer)
            if response:
                if response.status_code == 200:
                    j = response.json()
                    if j['status'] == 'EMPTY':
                        break

                    time = datetime.fromisoformat(j['sentTimestamp'])
                    message = Message(msg_type=MessageType.INCOMING, sender=j['senderAddress'], destination=self.phone_number, 
                                    text=j['message'], msg_id=j['messageId'], timestamp=time)
                    self.received_messages.append(message)

                    i = len(self.received_messages) - 1
                    self.msg_table.setRowCount(i + 1)
                    self.msg_table.setItem(i, 0, QTableWidgetItem(message.sender))
                    self.msg_table.setItem(i, 1, QTableWidgetItem(datetime.strftime(message.timestamp, '%d/%m %H:%M:%S')))
                    self.msg_table.setItem(i, 2, QTableWidgetItem(message.text))
                else:
                    self.set_status(f"Request to fetch message failed with code {response.status_code}")
        self.set_status("Fetched all messages")

    def choose_bearer(self):
        keys = [k for k in config['keys']]

        # padding 'hack' to make dialog wider
        key_pair, ok_pressed = QInputDialog.getItem(self, "Keys", "Choose keys [key secret]:" + " "*80, keys, 0, True)

        if not (key_pair and ok_pressed):
            return
    
        key, secret = key_pair.split(" ")
        response = self.api_request(api.get_bearer, key, secret)
        if response:
            self.bearer = response.json()['access_token']
            self.set_status("Success! Token valid for one hour")
            self.phone_number = self.api_request(api.get_number, self.bearer).json()['destinationAddress']
            self.num_label.setText(f"Num: {self.phone_number}")
    
    def send_message(self):
        if self.bearer is None:
            return self.set_status("Request bearer first")

        message = Message(msg_type=MessageType.OUTGOING, sender=self.phone_number, destination=self.num_text.text(), text=self.msg_text.text())
        if not re.match(r"\+61[0-9]{6,9}|[0-9]{6,10}", message.destination):
            return self.set_status("Expected national or +61 format")

        if len(message.text) == 0:
            return self.set_status("Message cannot be blank")

        self.set_status(f"Sending message to {message.destination}")
        response = self.api_request(api.send_message, self.bearer, message.destination, message.text)
        if response:
            if response.status_code == 201:
                self.set_status("Request to send message successful")
                self.num_text.setText("")
                self.msg_text.setText("")
            else:
                self.set_status(f"Request to send message failed with code {response.status_code}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    app.exec_()