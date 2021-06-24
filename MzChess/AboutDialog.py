import PyQt5.QtWidgets
from sys import version_info
from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

import chess

import Ui_AboutDialog
class AboutDialog(PyQt5.QtWidgets.QDialog, Ui_AboutDialog.Ui_AboutDialog):
 """
 Class documentation goes here.
 """
 def __init__(self, parent=None):
  """
  Constructor
  
  @param parent reference to the parent widget
  @type QWidget
  """
  super(AboutDialog, self).__init__(parent)
  self.setupUi(self)

 def setup(self, 
  pgm = None, 
  version = '?.?.?', 
  dateString = 'Jan 01, 1970'):
  self.pgmLabel.setText(pgm)
  self.shoeboxVersionLabel.setText('V' + version)
  self.shoeboxDateLabel.setText(dateString)
  self.chessVersionLabel.setText('V' + chess.__version__)
  self.pythonVersionLabel.setText('V' + str(version_info[0]) + '.' + str(version_info[1]) + '.' + str(version_info[2]) ) 
  self.qtVersionLabel.setText('V' + QT_VERSION_STR ) 
  self.pyqt5VersionLabel.setText('V' + PYQT_VERSION_STR )

if __name__ == "__main__":
 import sys
 app =  PyQt5.QtWidgets.QApplication(sys.argv)
 dialog = AboutDialog()
 dialog.setup()
 dialog.show()
 sys.exit(app.exec_())
