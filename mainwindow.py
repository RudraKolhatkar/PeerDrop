# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(810, 576)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.SendButton = QPushButton(self.centralwidget)
        self.SendButton.setObjectName(u"SendButton")
        self.SendButton.setMinimumSize(QSize(350, 350))
        icon = QIcon()
        icon.addFile(u"downloads.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.SendButton.setIcon(icon)
        self.SendButton.setIconSize(QSize(150, 250))
        self.SendButton.setFlat(False)

        self.horizontalLayout.addWidget(self.SendButton)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.RecieveButton = QPushButton(self.centralwidget)
        self.RecieveButton.setObjectName(u"RecieveButton")
        self.RecieveButton.setMinimumSize(QSize(350, 350))
        icon1 = QIcon()
        icon1.addFile(u"up-loading.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.RecieveButton.setIcon(icon1)
        self.RecieveButton.setIconSize(QSize(150, 200))
        self.RecieveButton.setFlat(False)

        self.horizontalLayout.addWidget(self.RecieveButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.SendButton.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.SendButton.setText("")
        self.RecieveButton.setText("")
    # retranslateUi

