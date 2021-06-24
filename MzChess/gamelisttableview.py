import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

class GameListTableModel(PyQt5.QtCore.QAbstractTableModel):
 gameHeaderKeys = ["Date", "White", "Black", "Result"]
 
 def __init__(self, gameList, parent = None):
  super(GameListTableModel, self).__init__(parent)
  self.gameList = gameList

 def rowCount(self, parent = None):
  return len(self.gameList)

 def columnCount(self, parent = None):
  return 4

 def data(self, index, role = PyQt5.QtCore.Qt.DisplayRole):
  if index.isValid():
   if role == PyQt5.QtCore.Qt.DisplayRole:
    actGameHeaders = self.gameList[index.row()].headers
    columnKey = self.gameHeaderKeys[index.column()]
    return actGameHeaders[columnKey]
   if role == PyQt5.QtCore.Qt.TextAlignmentRole:
    return PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter
  return None

 def headerData(self, col, orientation, role = PyQt5.QtCore.Qt.DisplayRole):
  if role == PyQt5.QtCore.Qt.DisplayRole:
   if orientation == PyQt5.QtCore.Qt.Horizontal:
    return self.gameHeaderKeys[col]
   if orientation == PyQt5.QtCore.Qt.Vertical:
    return '#{0:}'.format(col)
  return None

class GameListTableView(PyQt5.QtWidgets.QTableView):
 def __init__(self, parent = None):
  super(GameListTableView, self).__init__(parent)
  self.doubleClicked.connect(self.on_doubleClicked)
  self.horizontalHeader().setStretchLastSection(True)
  self.horizontalScrollBar().setDisabled(True)
  self.notifyDoubleClickSignal = None
  self.sizeHints = None

 def setGameList(self, gameList):
  model = GameListTableModel(gameList)
  self.setModel(model)
  self.sizeHints = 4*[0]
  totSize = 0
  for column, key in enumerate(model.gameHeaderKeys):
   self.sizeHints[column] = self.fontMetrics().size(PyQt5.QtCore.Qt.TextSingleLine, key).width()
   totSize += self.columnWidth(column)
   for n, game in enumerate(gameList):
    if key not in game.headers:
     raise ValueError('GameListTableModel: key {} not in game #{}'.format(key,n))
    actSize = self.fontMetrics().size(PyQt5.QtCore.Qt.TextSingleLine, game.headers[key]).width()
    self.sizeHints[column] = max(self.sizeHints[column], actSize)
  self.setColumnWidths()
  
 def setup(self, notifyDoubleClickSignal):
  self.notifyDoubleClickSignal = notifyDoubleClickSignal
  
 def resetDB(self):
  self.reset()
 
 def setColumnWidths(self):
  if self.sizeHints is None:
   return
  self.setColumnWidth(0, self.sizeHints[0]*1.2)
  #self.setColumnWidth(1, middleWidth)
  #self.setColumnWidth(2, middleWidth)
  self.setColumnWidth(3, self.sizeHints[3])

 def resizeEvent(self, ev):
  PyQt5.QtWidgets.QAbstractItemView.resizeEvent(self, ev)
  self.setColumnWidths()
  
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtCore.QModelIndex)
 def on_doubleClicked(self, index):
  if self.notifyDoubleClickSignal is not None:
   self.notifyDoubleClickSignal.emit(index.row())
  else:
   print('game #{} selected'.format(index.row()))

