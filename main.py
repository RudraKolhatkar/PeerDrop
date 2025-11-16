import os
import socket
from io import BufferedReader, BufferedWriter
from typing import Optional

import requests as req

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
import mainwindow
import SendDialog
import RecvDialog

MSG_SIZE = 128
FILE_NAME_SIZE = 64 * 1024
FILE_WRITE_BUFFER_SIZE = 256 * 1024
FILE_READ_BUFFER_SIZE = 16 * 1024

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.SendButton.clicked.connect(self.openSendDiag)
        self.ui.RecvButton.clicked.connect(self.openRecvDiag)

    def openSendDiag(self):
        filePath = QFileDialog.getOpenFileName()[0]
        fileName = filePath.split('/')[-1]

        diag = SendDialogWidget(filePath)
        diag.ui.FileNameEditLabel.setText(fileName)
        diag.exec()

    def openRecvDiag(self):
        diag = RecvDialogWidget()
        diag.exec()


class SendDialogWidget(QDialog):
    def __init__(self, path: str):
        super().__init__()
        self.ui = SendDialog.Ui_Dialog()
        self.ui.setupUi(self)

        file = open(path, 'rb')
        print(f"Path: {file.name}")
        name = file.name.split('/')[-1]
        file.seek(0, os.SEEK_END)
        size = file.tell()
        print(f"Size: {size}")

        s = CustomSocket()
        s.sendConn(('localhost', 14400))

        s.sendMsg(str(size))
        ack = s.recvMsg()
        if ack != "Size Received":
            print("Error: Something went fucky wucky UwU 1")
            app.exit()

        s.sendMsg(name)
        ack = s.recvMsg()
        if ack != "Name Received":
            print("Error: Something went fucky wucky UwU 2")
            app.exit()

        s.sendFile(file, size)
        s.closeSockets()

class RecvDialogWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = RecvDialog.Ui_Dialog()
        self.ui.setupUi(self)

        s = CustomSocket()
        s.recvConn(('localhost', 14400))
        size = int(s.recvMsg())
        print(f"Size: {size}")
        s.sendMsg("Size Received")
        name = s.recvMsg()
        print(f"Name: {name}")
        s.sendMsg("Name Received")
        s.recvFile(name, size)

        s.closeSockets()


class CustomSocket:
    def __init__(self):
        self.mainSock = socket.socket()
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connEstablished = False

    def sendConn(self, addrinfo: tuple):
        if self.connEstablished:
            print("Error: Connection already established")
            return

        self.serverSock.bind(addrinfo)
        self.serverSock.listen()
        self.mainSock = self.serverSock.accept()[0]
        self.connEstablished = True

    def sendMsg(self, msg:str):
        if self.connEstablished:
            self.mainSock.send(msg.encode())
        else:
            print("Error: Connection not established")

    def sendFile(self, file: BufferedReader, size: int):
        file.seek(0)
        if self.connEstablished:
            totalSent = 0
            while totalSent < size:
                chunk = file.read(FILE_WRITE_BUFFER_SIZE)
                self.mainSock.send(chunk)
                totalSent += FILE_WRITE_BUFFER_SIZE
                print(f"Sent Bytes: {totalSent}")
            file.close()
        else:
            print("Error: Connection not established")

    def closeSockets(self):
        self.mainSock.close()
        self.serverSock.close()

    def recvConn(self, addrinfo: tuple):
        if self.connEstablished:
            print("Error: Connection already established")

        self.mainSock.connect(addrinfo)
        self.connEstablished = True

    def recvMsg(self) -> Optional[str]:
        if self.connEstablished:
            msg = self.mainSock.recv(FILE_NAME_SIZE).decode()
            return msg
        else:
            print("Error: Connection not established")
            return None

    def recvFile(self, filename: str, size: int):
        if self.connEstablished:
            totalRecv = 0
            file = open(filename, 'wb')
            while totalRecv < size:
                chunk = self.mainSock.recv(FILE_READ_BUFFER_SIZE)
                file.write(chunk)
                totalRecv += len(chunk)
                print(f"Received Bytes: {totalRecv}")
            file.close()
        else:
            print("Error: Connection not established")

if __name__ == "__main__":
    app = QApplication()
    win = MainWindow()
    win.show()
    app.exec()