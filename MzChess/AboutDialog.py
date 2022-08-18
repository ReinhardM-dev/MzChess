from sys import version_info, path
import os.path

path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtCore
 from PyQt5 import uic
else:
 from PyQt6 import QtWidgets, QtCore
 from PyQt6 import uic

import chess
import ply

class AboutDialog(QtWidgets.QDialog):
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
  fileDirectory = os.path.dirname(os.path.abspath(__file__))
  uic.loadUi(os.path.join(fileDirectory, 'AboutDialog.ui'), self)

 def setup(self, 
  pgm = None, 
  version = '?.?.?', 
  dateString = 'Jan 01, 1970'):
  self.pgmLabel.setText(pgm)
  self.shoeboxVersionLabel.setText('V' + version)
  self.shoeboxDateLabel.setText(dateString)
  self.pythonVersionLabel.setText('V' + str(version_info[0]) + '.' + str(version_info[1]) + '.' + str(version_info[2]) ) 
  self.qtVersionLabel.setText('V' + QtCore.QT_VERSION_STR ) 
  self.pyqt6VersionLabel.setText('V' + QtCore.PYQT_VERSION_STR )
  self.chessVersionLabel.setText('V' + chess.__version__)
  self.plyVersionLabel.setText('V' + ply.__version__)

if __name__ == "__main__":
 import sys

 app =  QtWidgets.QApplication(sys.argv)
 dialog = AboutDialog()
 dialog.setup('About')
 dialog.show()
 sys.exit(app.exec())
