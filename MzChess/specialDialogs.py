from typing import Union, List, Dict
import sys, os.path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtGui, QtCore
else:
 from PyQt6 import QtWidgets, QtGui, QtCore

def treeWidgetItemPos(item : QtWidgets.QTreeWidgetItem) -> QtCore.QPoint:
  pos = item.treeWidget().visualItemRect(item).bottomLeft()
  return item.treeWidget().mapToParent(pos)

class ButtonLine(QtWidgets.QDialog):
 def __init__(self, buttonTexts : Union[List[str], Dict[str, int]],
                          hintDict : Dict[str, str] = dict(), 
                          title : str = ' ', 
                          pointSize : int = 12, 
                          parent = None) -> None:
  super(ButtonLine, self).__init__(parent)
  self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)
  self.hBox = QtWidgets.QHBoxLayout()
  self.hBox.setContentsMargins(pointSize // 2, pointSize // 2, pointSize // 2,  pointSize // 2)
  self.hBox.setSpacing(0)
  font = QtGui.QFont()
  font.setPointSize(pointSize)
  self.setFont(font)
  fontMetrics = self.fontMetrics()
  self.buttonWidth = 0
  for txt in buttonTexts:
   self.buttonWidth = max(self.buttonWidth, fontMetrics.size(QtCore.Qt.TextFlag.TextSingleLine, txt).width())
  self.buttonWidth = self.buttonWidth + pointSize
  self.buttonHeight = 2 * pointSize
  self.buttonTextDict = dict()
  for ID, txt in enumerate(buttonTexts):
   if isinstance(buttonTexts, list):
    self.buttonTextDict[txt] = ID
   if txt in hintDict:
    hint = hintDict[txt]
   else:
    hint = None
   self._addButton(txt, hint)
  if isinstance(buttonTexts, dict):
   self.buttonTextDict = buttonTexts
  self._setSizePolicy(self)
  self.resize(len(buttonTexts) * self.buttonWidth, self.buttonHeight)
  self.setLayout(self.hBox)
  self.setWindowTitle(title)
  
 def setFocus(self, buttonText : str) -> None:
  buttonID = self.buttonTextDict[buttonText]
  self.children()[buttonID].setFocus()
 
 def _setSizePolicy(self, widget : QtWidgets.QWidget) -> None:
  sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
  sizePolicy.setHorizontalStretch(0)
  sizePolicy.setVerticalStretch(0)
  sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
  widget.setSizePolicy(sizePolicy)
 
 def _addButton(self, txt : str,  hint : str) -> None:
  pushButton = QtWidgets.QPushButton(self)
  pushButton.setMinimumSize(QtCore.QSize(self.buttonWidth, self.buttonHeight))
  pushButton.setMaximumSize(QtCore.QSize(self.buttonWidth, self.buttonHeight))
  pushButton.setAutoDefault(True)
  pushButton.setText(txt)
  if hint is not None:
   pushButton.setToolTip(hint)
  pushButton.clicked.connect(self.on_clicked)
  self.hBox.addWidget(pushButton)
  
 @QtCore.pyqtSlot()
 def on_clicked(self):
  sendingItem = self.sender()
  self.done(self.buttonTextDict[sendingItem.text()])
  
class TextEdit(QtWidgets.QDialog):
 def __init__(self, title : str, pointSize : int = 10, parent = None) -> None:
  super(TextEdit, self).__init__(parent)
  self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)
  font = QtGui.QFont()
  font.setPointSize(pointSize)
  self.setFont(font)

  self.verticalLayout = QtWidgets.QVBoxLayout(self)
  self.edit = QtWidgets.QPlainTextEdit(self)
  self.buttonBox = QtWidgets.QDialogButtonBox(self)
  self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
  self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
  self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)

  self.verticalLayout.addWidget(self.edit)
  self.verticalLayout.addWidget(self.buttonBox)

  self.buttonBox.accepted.connect(self.accept)
  self.buttonBox.rejected.connect(self.reject)
  self.setWindowTitle(title)
  
 def setPos(self, masterPos : QtCore.QPoint) -> None:
  self.move(masterPos)
  
 def setText(self, txt : str) -> None:
  self.edit.setPlainText(txt)

 def text(self) -> str:
  return self.edit.toPlainText()

 def accept(self) -> str:
  return self.done(True)

 def reject(self) -> str:
  return self.done(False)

class ItemSelector(QtWidgets.QDialog):
 def __init__(self, title : str, pointSize : int = 10, parent = None) -> None:
  super(ItemSelector, self).__init__(parent)
  self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)
  font = QtGui.QFont()
  font.setPointSize(pointSize)
  self.setFont(font)

  self.verticalLayout = QtWidgets.QVBoxLayout(self)
  self.listWidget = QtWidgets.QListWidget(self)
  self.buttonBox = QtWidgets.QDialogButtonBox(self)
  self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
  self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
  self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)

  self.verticalLayout.addWidget(self.listWidget)
  self.verticalLayout.addWidget(self.buttonBox)

  self.buttonBox.accepted.connect(self.accept)
  self.buttonBox.rejected.connect(self.reject)
  self.setWindowTitle(title)
  
 def setContent(self, allItems : List[str], selectedItems : List[str] = list()) -> None:
  self.listWidget.clear()
  for itemTxt in sorted(allItems):
   item = QtWidgets.QListWidgetItem(itemTxt, self.listWidget)
   item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
   if itemTxt in selectedItems:
    item.setCheckState(QtCore.Qt.CheckState.Checked)
   else:
    item.setCheckState(QtCore.Qt.CheckState.Unchecked)

 def selectedItems(self) -> List[str]:
  selItems = list()
  for item in self.listWidget.findItems('*', QtCore.Qt.MatchFlag.MatchWildcard):
   if item.checkState() == QtCore.Qt.CheckState.Checked:
    selItems.append(item.text())
  return selItems

 def accept(self) -> str:
  return self.done(True)

 def reject(self) -> str:
  return self.done(False)


if __name__ == "__main__":
 import chess
 
 app = QtWidgets.QApplication([])
 if True:
  from enum import IntEnum, unique
  @unique
  class KeyType(IntEnum):
   STR = 0
   INT = 1
   URL = 2
   LABEL = 3
   DATE = 4
   TIME = 5
   EVENT = 6
   SITE = 7
   PLAYER = 8
   TITLE = 9
  stdKey2ValueTypeDict = {
   # seven tag roster
   "Event" : ("?", KeyType.EVENT),
   "Site" : ("?", KeyType.SITE),
   "Date" : ("????.??.??", KeyType.DATE),
   "Round" : ("?", KeyType.STR),
   "White" : ("?", KeyType.PLAYER),
   "Black" : ("?", KeyType.PLAYER),
   "Result" : ("*", KeyType.STR), 
   # player related information 
   "WhiteTitle" : ("", KeyType.TITLE), 
   "BlackTitle" : ("", KeyType.TITLE), 
   "WhiteElo" : ("", KeyType.INT)}
  itemSelect = ItemSelector('Header Elements ...', pointSize = 10)
  itemSelect.setContent(stdKey2ValueTypeDict, ["WhiteElo", "Result"])
  index = itemSelect.exec()
  print('selected = {}'.format(itemSelect.selectedItems()))
 elif True:
  annotationSymbols = ['', '!', '?', '!!', '??', '!?', '?!']
  positionSymbols =  ['','=', '~', '+=', '=+', '+/-', '-/+', '+-','-+', '+--', '-++']
  symbolDescription =  { ''    : 'null annotation',
                              '!'     : 'good move', 
                              '?'     : 'poor move', 
                              '!!'   : 'brilliant move',
                              '??'   : 'blunder',
                              '!?'   : 'intesting move',
                              '?!'   : 'dubious move', 
                              '='     : 'even position', 
                              '~'     : 'unclear position', 
                              '+='   : 'slight advantage for white', 
                              '=+'   : 'slight advantage for black',
                              '+/-' : 'moderate advantage for white', 
                              '-/+' : 'moderate advantage for black', 
                              '+-'   : 'decisive advantage for white',
                              '-+'   : 'decisive advantage for white',
                              '+--' : 'white should resign',
                              '-++' : 'black should resign' }
  chessFigures = { '♕' :  chess.QUEEN, '♖' :  chess.ROOK,  '♗' :  chess.BISHOP,  '♘' :  chess.KNIGHT}

  # buttonLine = ButtonLine(annotationSymbols, hintDict = symbolDescription, pointSize = 12)
  buttonLine = ButtonLine(positionSymbols, hintDict = symbolDescription, pointSize = 12)
  # buttonLine = ButtonLine(chessFigures, pointSize = 30)
  index = buttonLine.exec()
 else:
  myText = '''[Event "Whatever"]
[Site "Wherever"]
[Date "1970.01.01"]
[Round "5"]
[White "Foo"]
[Black "Bla"]
[Result "*"]
1. d4 { [%eval +0.16] } 

1... d5 *
[Event "Whatever"]
[Site "?"]
[Date "1970.01.01"]
[Round "13"]
[White "Foo"]
[Black "Bla"]
[Result "*"]

1. d4 { [%eval +0.16] } 1... c5 { [%eval +0.52] (Benoni-Verteidigung) } *
  '''
  textEdit = TextEdit('Comment ...', pointSize = 10)
  textEdit.setText(myText)
  index = textEdit.exec()
 print(index)
 #sys.exit(app.exec_())

