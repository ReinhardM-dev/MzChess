import sys,  os.path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets
else:
 from PyQt6 import QtWidgets

class HelpBrowser(QtWidgets.QWidget):
 indexFile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'doc_build', 'html', 'index.html')

 def __init__(self):
   super().__init__()
   
   self.tb = QtWidgets.QTextBrowser()
   self.tb.setAcceptRichText(True)
   self.tb.setOpenExternalLinks(True)
   self.tb.setOpenLinks(True)
   with open(self.indexFile, 'r',  encoding = 'utf-8-sig') as f:
    indexText = f.read()
   self.tb.setHtml(indexText)

   vbox = QtWidgets.QVBoxLayout()
   vbox.addWidget(self.tb, 1)

   self.setLayout(vbox)

   self.setWindowTitle('QTextBrowser')
   self.setGeometry(100, 100, 800, 800)
   self.show()


if __name__ == '__main__':
 if MzChess.useQt5():
  from PyQt5 import QtGui, QtCore
 else:
  from PyQt6 import QtGui, QtCore

 app = QtWidgets.QApplication(sys.argv)
 # ex = HelpBrowser()
 QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(HelpBrowser.indexFile))

 sys.exit(app.exec())
