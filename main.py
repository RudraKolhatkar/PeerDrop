import os
import socket
import socket as sock
from io import BufferedReader
import requests as req

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
import mainwindow
import SendDialog
import RecvDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.SendButton.clicked.connect(self.openSendDiag)
        self.ui.RecieveButton.clicked.connect(self.openRecvDiag)

    def openSendDiag(self):
        filePath = QFileDialog.getOpenFileName()[0]
        fileName = filePath.split('/')[-1]

        diag = SendDialogWidget()
        diag.ui.FileNameEditLabel.setText(fileName)
        diag.exec()

    def openRecvDiag(self):
        diag = RecvDialogWidget()
        diag.exec()


class SendDialogWidget(QDialog):
    def __init__(self, ):
        super().__init__()
        self.ui = SendDialog.Ui_Dialog()
        self.ui.setupUi(self)


class RecvDialogWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = RecvDialog.Ui_Dialog()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication()
    win = MainWindow()
    win.show()
    app.exec()