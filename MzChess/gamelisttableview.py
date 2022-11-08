'''Database Editor
================================
The *database* editor is based on Qt's QTableView. 

|DatabaseEditor|

It allows for 3 types of actions:

 * select a game by a double-click into the corresponding row
 * add/remove the displayed header items (limited to the 7-tag roster) by a right-clicking the column header
 * changing the sequence of games in the database by drag/drop or the menu items *Move Games>Up/Down*

.. |DatabaseEditor| image:: gameListTableView.png
  :width: 800
  :alt: Game Editor
'''
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

 def flags(self, index):
  return QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsDragEnabled | QtCore.Qt.ItemFlag.ItemIsDropEnabled

 def supportedDropActions(self):
  return QtCore.Qt.DropAction.MoveAction

 def data(self, index, role = QtCore.Qt.ItemDataRole.DisplayRole):
  if index.isValid():
   if role == QtCore.Qt.ItemDataRole.DisplayRole:
    actGameHeaders = self.gameList[index.row()].headers
    columnKey = self.gameHeaderKeys[index.column()]
    return actGameHeaders[columnKey]
   elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
    return int(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
  return None

 def headerData(self, col, orientation, role = QtCore.Qt.ItemDataRole.DisplayRole):
  if role == QtCore.Qt.ItemDataRole.DisplayRole:
   if orientation == QtCore.Qt.Orientation.Horizontal:
    return self.gameHeaderKeys[col]
   if orientation == QtCore.Qt.Orientation.Vertical:
    return '#{0:}'.format(col)
  return None

 def moveRows(self, srcRowRange, tgtRow):
  if tgtRow < 0 or tgtRow > self.rowCount():
   return False
  assert isinstance(srcRowRange, range)
  parent = QtCore.QModelIndex()
  self.beginMoveRows(parent, srcRowRange.start, srcRowRange.stop - 1, parent, tgtRow)
  newGameList = list()
  if tgtRow < srcRowRange.start:
   newGameList += self.gameList[:tgtRow]
   newGameList += self.gameList[srcRowRange.start:srcRowRange.stop]
   newGameList += self.gameList[tgtRow:srcRowRange.start]
   newGameList += self.gameList[srcRowRange.stop:]
  else:
   newGameList += self.gameList[:srcRowRange.start]
   newGameList += self.gameList[srcRowRange.stop:tgtRow]
   newGameList += self.gameList[srcRowRange.start:srcRowRange.stop]
   newGameList += self.gameList[tgtRow:]
  for n, game in enumerate(newGameList):
   self.gameList[n] = newGameList[n]
  self.endMoveRows()
  return True

 def removeRows(self, srcRowList):
  if len(srcRowList) == 0:
   return False
  newGameList = list()
  for row, game in enumerate(self.gameList):
   if row not in srcRowList:
    newGameList.append(game)
  self.beginResetModel()
  for n, game in enumerate(newGameList):
   self.gameList[n] = newGameList[n]
  del self.gameList[len(newGameList):]
  self.endResetModel()
  return True
  
class GameListTableView(QtWidgets.QTableView):
 sevenTagRoster = ["Event", "Site", "Round", "Date", "White", "Black", "Result"]

 def __init__(self, parent = None):
  super(GameListTableView, self).__init__(parent)
  self.doubleClicked.connect(self.on_doubleClicked)
  self.horizontalHeader().setStretchLastSection(True)
  self.horizontalScrollBar().setDisabled(True)
  self.notifyDoubleClickSignal = None
  self.notifyHeaderChangedSignal = None
  self.notifyListChangedSignal = None
  self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
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
  
  self.setAcceptDrops(True)
  self.setDragEnabled(True)
  self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
  
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
   
 def _selection2rowRange(self):
  selection = self.selectionModel().selectedRows()   
  if len(selection) == 0:
   self.notifyError('No game selected.')
   return None
  srcRowList = list()
  for rowSelection in selection:
   srcRowList.append(rowSelection.row())
  srcRowList = sorted(srcRowList)
  for n, srcRow in enumerate(srcRowList):
   if n > 0:
    if srcRowList[n] - srcRowList[n-1] != 1:
     self.notifyError('The selected rows must be simply connected.')
     return None
  return range(srcRowList[0], srcRowList[-1] + 1)

 def on_actionRemoveGames_triggered(self):
  selection = self.selectionModel().selectedRows()   
  srcRowList = list()
  for rowSelection in selection:
   srcRowList.append(rowSelection.row())
  return self.model().removeRows(srcRowList)

 def on_menuMoveGame_triggered(self, action):
  srcRowRange = self._selection2rowRange()
  if srcRowRange is None:
   return False
  if action.text() == 'Down':
   return self.model().moveRows(srcRowRange, srcRowRange.stop + 1)
  else:
   return self.model().moveRows(srcRowRange, srcRowRange.start - 1)

 def dropEvent(self, event):
  if (event.source() is self \
   and event.dropAction() == QtCore.Qt.DropAction.MoveAction and self.dragDropMode() == QtWidgets.QAbstractItemView.DragDropMode.InternalMove):
   if MzChess.useQt5():
    tgtRow = self.indexAt(event.pos()).row()
   else:
    tgtRow = self.indexAt(event.position().toPoint()).row()
   srcRowRange = self._selection2rowRange()
   if srcRowRange is not None and tgtRow != srcRowRange.start + 1:
    if tgtRow >= srcRowRange.start and tgtRow <= srcRowRange.stop:
     self.notifyError('The target row must be outside the range of source rows.')
     return None
    self.model().moveRows(srcRowRange, tgtRow)
   if self.notifyListChangedSignal is not None:
    self.notifyListChangedSignal.emit()
   event.accept()
  else:
   super().dropEvent(event)
   
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

 def moveRow(self, up=True):
  selection = self.selectedIndexes()
  if selection:
   header = self.verticalHeader()
   row = header.visualIndex(selection[0].row())
   if up and row > 0:
    header.moveSection(row, row - 1)
   elif not up and row < header.count() - 1:
    header.moveSection(row, row + 1)

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
  
 def setup(self, notifyDoubleClickSignal = None, notifyHeaderChangedSignal = None, notifyListChangedSignal = None):
  self.notifyDoubleClickSignal = notifyDoubleClickSignal
  self.notifyHeaderChangedSignal = notifyHeaderChangedSignal
  self.notifyListChangedSignal  = notifyListChangedSignal 
  
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
