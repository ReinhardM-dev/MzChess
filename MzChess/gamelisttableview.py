from PyQt6 import QtWidgets, QtCore

class GameListTableModel(QtCore.QAbstractTableModel):
 gameHeaderKeys = ["Date", "White", "Black", "Result"]
 
 def __init__(self, gameList, parent = None):
  super(GameListTableModel, self).__init__(parent)
  self.gameList = gameList

 def rowCount(self, parent = None):
  return len(self.gameList)

 def columnCount(self, parent = None):
  return 4

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
   self.sizeHints[column] = self.fontMetrics().size(QtCore.Qt.TextFlag.TextSingleLine, key).width()
   totSize += self.columnWidth(column)
   for n, game in enumerate(gameList):
    if key not in game.headers:
     raise ValueError('GameListTableModel: key {} not in game #{}'.format(key,n))
    actSize = self.fontMetrics().size(QtCore.Qt.TextFlag.TextSingleLine, game.headers[key]).width()
    self.sizeHints[column] = max(self.sizeHints[column], actSize)
  self.setColumnWidths()
  
 def setup(self, notifyDoubleClickSignal):
  self.notifyDoubleClickSignal = notifyDoubleClickSignal
  
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

