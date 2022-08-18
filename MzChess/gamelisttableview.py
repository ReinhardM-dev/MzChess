import sys,  os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtCore
 from PyQt5.QtWidgets import QAction
else:
 from PyQt6 import QtWidgets, QtCore
 from PyQt6.QtGui import QAction

class GameListTableModel(QtCore.QAbstractTableModel):
 
 def __init__(self, gameList, gameHeaderKeys, parent = None):
  super(GameListTableModel, self).__init__(parent)
  self.gameHeaderKeys = gameHeaderKeys
  self.gameList = gameList

 def rowCount(self, parent = None):
  return len(self.gameList)

 def columnCount(self, parent = None):
  return len(self.gameHeaderKeys)

 def data(self, index, role = QtCore.Qt.ItemDataRole.DisplayRole):
  if index.isValid():
   if role == QtCore.Qt.ItemDataRole.DisplayRole:
    actGameHeaders = self.gameList[index.row()].headers
    columnKey = self.gameHeaderKeys[index.column()]
    return actGameHeaders[columnKey]
   if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
    return QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter
  return None

 def headerData(self, col, orientation, role = QtCore.Qt.ItemDataRole.DisplayRole):
  if role == QtCore.Qt.ItemDataRole.DisplayRole:
   if orientation == QtCore.Qt.Orientation.Horizontal:
    return self.gameHeaderKeys[col]
   if orientation == QtCore.Qt.Orientation.Vertical:
    return '#{0:}'.format(col)
  return None

class GameListTableView(QtWidgets.QTableView):
 sevenTagRoster = ["Event", "Site", "Round", "Date", "White", "Black", "Result"]

 def __init__(self, parent = None):
  super(GameListTableView, self).__init__(parent)
  self.doubleClicked.connect(self.on_doubleClicked)
  self.horizontalHeader().setStretchLastSection(True)
  self.horizontalScrollBar().setDisabled(True)
  self.notifyDoubleClickSignal = None
  self.notifyHeaderChangedSignal = None
  self.sizeHints = None
  self.gameHeaderKeys = ["Date", "White", "Black", "Result"]
  headerWidget = self.horizontalHeader()
  headerWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
  headerWidget.customContextMenuRequested.connect(self.on_menuHorizontalHeader_requested)
  self.context = QtWidgets.QMenu(self)
  self.context.triggered.connect(self.on_menuContext_triggered)
  for tag in self.sevenTagRoster:
   self.context.addAction('Show {}'.format(tag))
  self.context.addSeparator()
  self.context.addAction('Hide')
  
 @QtCore.pyqtSlot(QAction)
 def on_menuContext_triggered(self, action):
  actionText = action.text()
  newGameHeaderKeys = self.gameHeaderKeys.copy()
  if actionText == 'Hide':
   if len(newGameHeaderKeys) <= 1:
    self.notifyError('At least 1 column required')
    return
   newGameHeaderKeys.pop(self.contextColumn)
  else:
   item = actionText.split(' ')[1]
   newGameHeaderKeys.insert(self.contextColumn, item)
  self.gameHeaderKeys = newGameHeaderKeys
  if self.notifyHeaderChangedSignal is not None:
   self.notifyHeaderChangedSignal.emit(newGameHeaderKeys)
  
 def on_menuHorizontalHeader_requested(self, pos):
  self.contextColumn = self.columnAt(pos.x())
  self.context.exec(self.mapToGlobal(pos))
  return
  self.popupMenu = QtWidgets.QMenu()
  self.popupMenu.exec()
  return
 
 def notifyError(self, str : str) -> None:
  msgBox = QtWidgets.QMessageBox()
  msgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
  msgBox.setText(str)
  msgBox.setWindowTitle("Error ...")
  msgBox.exec()

 @property
 def gameHeaderKeys(self):
  return self._gameHeaderKeys

 @gameHeaderKeys.setter
 def gameHeaderKeys(self, newGameHeaderKeys):
  if len(newGameHeaderKeys) == 0:
   self.notifyError('len(newGameHeaderKeys) > 0')
   return
  for tag in newGameHeaderKeys:
   if tag not in self.sevenTagRoster:
    self.notifyError('{} not in {}'.format(tag, self.sevenTagRoster))
    return     
  self._gameHeaderKeys = newGameHeaderKeys
  model = self.model()
  if model is not None:
   model.beginResetModel()
   model.gameHeaderKeys = self._gameHeaderKeys 
   model.endResetModel()
  self.contextColumn = -1
  return 

 def setGameList(self, gameList):
  model = GameListTableModel(gameList, self.gameHeaderKeys)
  self.setModel(model)
  self.sizeHints = 4*[0]
  totSize = 0
  for column, key in enumerate(model.gameHeaderKeys):
   self.sizeHints[column] = self.fontMetrics().size(QtCore.Qt.TextFlag.TextSingleLine, key).width()
   totSize += self.columnWidth(column)
   for n, game in enumerate(gameList):
    if key not in game.headers:
     raise ValueError('GameListTableModel: key {} not in game #{}'.format(key,n))
    actSize = self.fontMetrics().size(QtCore.Qt.TextFlag.TextSingleLine, game.headers[key]).width()
    self.sizeHints[column] = max(self.sizeHints[column], actSize)
  self.setColumnWidths()
  
 def setup(self, notifyDoubleClickSignal = None, notifyHeaderChangedSignal = None):
  self.notifyDoubleClickSignal = notifyDoubleClickSignal
  self.notifyHeaderChangedSignal = notifyHeaderChangedSignal
  
 def resetDB(self):
  self.reset()
 
 def setColumnWidths(self):
  if self.sizeHints is None:
   return
  self.setColumnWidth(0, int(self.sizeHints[0]*1.2))
  #self.setColumnWidth(1, middleWidth)
  #self.setColumnWidth(2, middleWidth)
  self.setColumnWidth(3, self.sizeHints[3])

 def resizeEvent(self, ev):
  QtWidgets.QAbstractItemView.resizeEvent(self, ev)
  self.setColumnWidths()
  
 @QtCore.pyqtSlot(QtCore.QModelIndex)
 def on_doubleClicked(self, index):
  if self.notifyDoubleClickSignal is not None:
   self.notifyDoubleClickSignal.emit(index.row())
  else:
   print('game #{} selected'.format(index.row()))

if __name__ == "__main__":
 from pgnParse import read_game

 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 pgnName = os.path.join(fileDirectory, 'training', 'matein', 'matein1.pgn')
 pgn = open(pgnName, mode = 'r',  encoding = 'utf-8')
 gameList = list()
 for n in range(10):
  game = read_game(pgn)
  if game is None:
   break
  gameList.append(game)
 app = QtWidgets.QApplication([])

 gameView = GameListTableView()
 gameView.show()
 gameView.setGameList(gameList)
 gameView.gameHeaderKeys = ['Event', 'Date']
 
 sys.exit(app.exec())
