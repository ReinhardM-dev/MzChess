# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Reinh\OneDrive\Dokumente\python\MzChess\MzChess\AboutDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.5
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutDialog(object):
  def setupUi(self, AboutDialog):
    AboutDialog.setObjectName("AboutDialog")
    AboutDialog.resize(268, 204)
    AboutDialog.setSizeGripEnabled(False)
    self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
    self.verticalLayout.setObjectName("verticalLayout")
    self.pgmLabel = QtWidgets.QLabel(AboutDialog)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.pgmLabel.sizePolicy().hasHeightForWidth())
    self.pgmLabel.setSizePolicy(sizePolicy)
    self.pgmLabel.setMinimumSize(QtCore.QSize(250, 0))
    font = QtGui.QFont()
    font.setPointSize(16)
    self.pgmLabel.setFont(font)
    self.pgmLabel.setAlignment(QtCore.Qt.AlignCenter)
    self.pgmLabel.setObjectName("pgmLabel")
    self.verticalLayout.addWidget(self.pgmLabel)
    self.formLayout = QtWidgets.QFormLayout()
    self.formLayout.setObjectName("formLayout")
    self.label_2 = QtWidgets.QLabel(AboutDialog)
    self.label_2.setObjectName("label_2")
    self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
    self.label_3 = QtWidgets.QLabel(AboutDialog)
    self.label_3.setObjectName("label_3")
    self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_3)
    self.label_4 = QtWidgets.QLabel(AboutDialog)
    self.label_4.setObjectName("label_4")
    self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
    self.shoeboxVersionLabel = QtWidgets.QLabel(AboutDialog)
    self.shoeboxVersionLabel.setObjectName("shoeboxVersionLabel")
    self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.shoeboxVersionLabel)
    self.label_6 = QtWidgets.QLabel(AboutDialog)
    self.label_6.setObjectName("label_6")
    self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
    self.shoeboxDateLabel = QtWidgets.QLabel(AboutDialog)
    self.shoeboxDateLabel.setObjectName("shoeboxDateLabel")
    self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.shoeboxDateLabel)
    self.label_7 = QtWidgets.QLabel(AboutDialog)
    self.label_7.setObjectName("label_7")
    self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_7)
    self.pythonVersionLabel = QtWidgets.QLabel(AboutDialog)
    self.pythonVersionLabel.setObjectName("pythonVersionLabel")
    self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.pythonVersionLabel)
    self.label_11 = QtWidgets.QLabel(AboutDialog)
    self.label_11.setObjectName("label_11")
    self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_11)
    self.qtVersionLabel = QtWidgets.QLabel(AboutDialog)
    self.qtVersionLabel.setObjectName("qtVersionLabel")
    self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.qtVersionLabel)
    self.label_5 = QtWidgets.QLabel(AboutDialog)
    self.label_5.setObjectName("label_5")
    self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_5)
    self.chessVersionLabel = QtWidgets.QLabel(AboutDialog)
    self.chessVersionLabel.setObjectName("chessVersionLabel")
    self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.chessVersionLabel)
    self.label = QtWidgets.QLabel(AboutDialog)
    self.label.setObjectName("label")
    self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label)
    self.pyqt5VersionLabel = QtWidgets.QLabel(AboutDialog)
    self.pyqt5VersionLabel.setObjectName("pyqt5VersionLabel")
    self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.pyqt5VersionLabel)
    self.label_8 = QtWidgets.QLabel(AboutDialog)
    self.label_8.setObjectName("label_8")
    self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_8)
    self.plyVersionLabel = QtWidgets.QLabel(AboutDialog)
    self.plyVersionLabel.setObjectName("plyVersionLabel")
    self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.plyVersionLabel)
    self.verticalLayout.addLayout(self.formLayout)

    self.retranslateUi(AboutDialog)
    QtCore.QMetaObject.connectSlotsByName(AboutDialog)

  def retranslateUi(self, AboutDialog):
    _translate = QtCore.QCoreApplication.translate
    AboutDialog.setWindowTitle(_translate("AboutDialog", "About ..."))
    self.pgmLabel.setText(_translate("AboutDialog", "Mz Chess GUI"))
    self.label_2.setText(_translate("AboutDialog", "Author:"))
    self.label_3.setText(_translate("AboutDialog", "Reinhard Maerz"))
    self.label_4.setText(_translate("AboutDialog", "Version:"))
    self.shoeboxVersionLabel.setText(_translate("AboutDialog", "V?.?"))
    self.label_6.setText(_translate("AboutDialog", "Version-date:"))
    self.shoeboxDateLabel.setText(_translate("AboutDialog", "Apr 99, 2019"))
    self.label_7.setText(_translate("AboutDialog", "Python version:"))
    self.pythonVersionLabel.setText(_translate("AboutDialog", "V?.?.?"))
    self.label_11.setText(_translate("AboutDialog", "Qt version:"))
    self.qtVersionLabel.setText(_translate("AboutDialog", "V?.?.?"))
    self.label_5.setText(_translate("AboutDialog", "chess version"))
    self.chessVersionLabel.setText(_translate("AboutDialog", "V?.?"))
    self.label.setText(_translate("AboutDialog", "PyQT5 version"))
    self.pyqt5VersionLabel.setText(_translate("AboutDialog", "V?.?.?"))
    self.label_8.setText(_translate("AboutDialog", "ply"))
    self.plyVersionLabel.setText(_translate("AboutDialog", "V?.?"))


if __name__ == "__main__":
  import sys
  app = QtWidgets.QApplication(sys.argv)
  AboutDialog = QtWidgets.QDialog()
  ui = Ui_AboutDialog()
  ui.setupUi(AboutDialog)
  AboutDialog.show()
  sys.exit(app.exec_())
