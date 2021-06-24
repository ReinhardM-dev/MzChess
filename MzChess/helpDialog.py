import os.path
import PyQt5.QtCore,  PyQt5.QtGui, PyQt5.QtWidgets 

class HelpBrowser(PyQt5.QtWidgets.QWidget):
 indexFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', 'html', 'index.html')

 def __init__(self):
   super().__init__()
   
   self.tb = PyQt5.QtWidgets.QTextBrowser()
   self.tb.setAcceptRichText(True)
   self.tb.setOpenExternalLinks(True)
   self.tb.setOpenLinks(True)
   with open(self.indexFile, 'r',  encoding = 'utf-8-sig') as f:
    indexText = f.read()
   self.tb.setHtml(indexText)
   # self.tb.setSource(PyQt5.QtCore.QUrl(self.indexFile))

   vbox = PyQt5.QtWidgets.QVBoxLayout()
   vbox.addWidget(self.tb, 1)

   self.setLayout(vbox)

   self.setWindowTitle('QTextBrowser')
   self.setGeometry(100, 100, 800, 800)
   self.show()


if __name__ == '__main__':
 import sys

 app = PyQt5.QtWidgets.QApplication(sys.argv)
 # ex = HelpBrowser()
 PyQt5.QtGui.QDesktopServices.openUrl(PyQt5.QtCore.QUrl.fromLocalFile(HelpBrowser.indexFile))

 sys.exit(app.exec_())
