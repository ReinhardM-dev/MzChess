# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Reinh\OneDrive\Dokumente\python\MzChess\propagatePawn.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(220, 70)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(220, 70))
        Form.setMaximumSize(QtCore.QSize(220, 70))
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.queenButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queenButton.sizePolicy().hasHeightForWidth())
        self.queenButton.setSizePolicy(sizePolicy)
        self.queenButton.setMinimumSize(QtCore.QSize(50, 50))
        self.queenButton.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.queenButton.setFont(font)
        self.queenButton.setObjectName("queenButton")
        self.horizontalLayout.addWidget(self.queenButton)
        self.rookButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rookButton.sizePolicy().hasHeightForWidth())
        self.rookButton.setSizePolicy(sizePolicy)
        self.rookButton.setMinimumSize(QtCore.QSize(50, 50))
        self.rookButton.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.rookButton.setFont(font)
        self.rookButton.setObjectName("rookButton")
        self.horizontalLayout.addWidget(self.rookButton)
        self.bishopButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bishopButton.sizePolicy().hasHeightForWidth())
        self.bishopButton.setSizePolicy(sizePolicy)
        self.bishopButton.setMinimumSize(QtCore.QSize(50, 50))
        self.bishopButton.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.bishopButton.setFont(font)
        self.bishopButton.setObjectName("bishopButton")
        self.horizontalLayout.addWidget(self.bishopButton)
        self.knightButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.knightButton.sizePolicy().hasHeightForWidth())
        self.knightButton.setSizePolicy(sizePolicy)
        self.knightButton.setMinimumSize(QtCore.QSize(50, 50))
        self.knightButton.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.knightButton.setFont(font)
        self.knightButton.setObjectName("knightButton")
        self.horizontalLayout.addWidget(self.knightButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Propagate ..."))
        self.queenButton.setText(_translate("Form", "♕"))
        self.rookButton.setText(_translate("Form", "♖"))
        self.bishopButton.setText(_translate("Form", "♗"))
        self.knightButton.setText(_translate("Form", "♘"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
