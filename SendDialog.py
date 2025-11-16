# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SendDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QProgressBar, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(539, 169)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.TopFrame = QFrame(Dialog)
        self.TopFrame.setObjectName(u"TopFrame")
        self.TopFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.TopFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout = QHBoxLayout(self.TopFrame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.TopFrameLeftr = QFrame(self.TopFrame)
        self.TopFrameLeftr.setObjectName(u"TopFrameLeftr")
        self.TopFrameLeftr.setMaximumSize(QSize(80, 16777215))
        font = QFont()
        font.setWeight(QFont.Medium)
        self.TopFrameLeftr.setFont(font)
        self.TopFrameLeftr.setFrameShape(QFrame.Shape.NoFrame)
        self.TopFrameLeftr.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.TopFrameLeftr)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.FileLabel = QLabel(self.TopFrameLeftr)
        self.FileLabel.setObjectName(u"FileLabel")
        self.FileLabel.setMaximumSize(QSize(1600, 1600))
        font1 = QFont()
        font1.setPointSize(16)
        font1.setWeight(QFont.Medium)
        self.FileLabel.setFont(font1)

        self.verticalLayout_2.addWidget(self.FileLabel)

        self.CodeLabel = QLabel(self.TopFrameLeftr)
        self.CodeLabel.setObjectName(u"CodeLabel")
        self.CodeLabel.setFont(font1)

        self.verticalLayout_2.addWidget(self.CodeLabel)


        self.horizontalLayout.addWidget(self.TopFrameLeftr)

        self.TopFrameRight = QFrame(self.TopFrame)
        self.TopFrameRight.setObjectName(u"TopFrameRight")
        self.TopFrameRight.setFrameShape(QFrame.Shape.NoFrame)
        self.TopFrameRight.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.TopFrameRight)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.FileNameEditLabel = QLabel(self.TopFrameRight)
        self.FileNameEditLabel.setObjectName(u"FileNameEditLabel")
        self.FileNameEditLabel.setFont(font1)

        self.verticalLayout_3.addWidget(self.FileNameEditLabel)

        self.CodeEditLabel = QLabel(self.TopFrameRight)
        self.CodeEditLabel.setObjectName(u"CodeEditLabel")
        self.CodeEditLabel.setFont(font1)

        self.verticalLayout_3.addWidget(self.CodeEditLabel)


        self.horizontalLayout.addWidget(self.TopFrameRight)


        self.verticalLayout.addWidget(self.TopFrame)

        self.progressBar = QProgressBar(Dialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.verticalLayout.addWidget(self.progressBar)

        self.StatusLabel = QLabel(Dialog)
        self.StatusLabel.setObjectName(u"StatusLabel")
        self.StatusLabel.setMaximumSize(QSize(16777215, 20))
        self.StatusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.StatusLabel)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.FileLabel.setText(QCoreApplication.translate("Dialog", u"File: ", None))
        self.CodeLabel.setText(QCoreApplication.translate("Dialog", u"Code: ", None))
        self.FileNameEditLabel.setText(QCoreApplication.translate("Dialog", u"FileName", None))
        self.CodeEditLabel.setText(QCoreApplication.translate("Dialog", u"Placeholder Code", None))
        self.StatusLabel.setText(QCoreApplication.translate("Dialog", u"Status", None))
    # retranslateUi

