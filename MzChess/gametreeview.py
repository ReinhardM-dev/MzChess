'''Game Editor
================================
The *game* editor is based on Qt's QTreeWidget. 

|GameEditor|
Since Qt's QTreeWidget does not fit the tree representing the Portable Game Notation (PGN), i.e.

 * *n* variations per move supported
 * the main (first) variation is privileged.

This behavior is implemented using 2 types of lines:

 * regular moves where all columns have a white background
 * beginning of a variation marked with a green cross

The tree widget has 4 colums:

 #. *Move* shows the actual move or the beginning of a variation in SAN notation 
 #. *Ann* shows the annotation, i.e. a symbolic move assessment
 #. *Pos* shows the position assessment
 #. *Score* shows the engine or material score [centipawn] of the last move, material score ending with M
 #. *Comment* shows either the move comment or starting comment of a variation
 
By clicking the annotation (*Ann*) and position assessment (*Pos*) fields, a popup dialog
opens which allows to change the contents   

.. |GameEditor| image:: gameEditor.png
  :width: 800
  :alt: Game Editor
'''
from typing import Optional, Set

import sys,  os.path
import copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtGui, QtCore
else:
 from PyQt6 import QtWidgets, QtGui,  QtCore

import chess, chess.pgn
from chessengine import PGNEval_REGEX
from specialDialogs import ButtonLine, TextEdit, treeWidgetItemPos

class GameTreeView(QtWidgets.QTreeWidget):
 '''Game Editor object
 '''
 itemFlags = QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable
 inactiveBrush = QtGui.QBrush(QtGui.QColor('lightgray'))
 colorChars = ('black', 'white')
 endGameSymbols = ['1-0', '0-1', '1/2-1/2', '*']
 endGameDescription = { '1-0'      : 'White wins',
                                  '0-1'       : 'Black wins', 
                                  '1/2-1/2' : 'Drawn game', 
                                  '*'          : 'game in progress' }
 annotationSymbols = ['', '!', '?', '!!', '??', '!?', '?!']
 positionSymbols =  { ''       :  0,
                              '='     : 10, 
                              '~'     : 13, 
                              '+='   : 14, 
                              '=+'   : 15,
                              '+/-' : 16, 
                              '-/+' : 17, 
                              '+-'   : 18,
                              '-+'   : 19,
                              '+--' : 20,
                              '-++' : 21 }
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
 
 def __init__(self, parent = None) -> None:
  super(GameTreeView, self).__init__(parent)
  cross16x16File = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pieces', 'cross16x16.ico')
  self.crossIcon = QtGui.QIcon(cross16x16File)
  self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
  self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
  self.notifyGameNodeSelectedSignal = None
  self.notifyGameNodeChangedSignal = None
  self._clear()
  self.setColumnCount(5)
  self.setHeaderLabels(['Move', 'Ann', 'Pos', 'Score', 'Comment'])
  headerItem = self.headerItem()
  headerItem.setToolTip(0, 'SAN notation')
  headerItem.setToolTip(1, 'Move assessments')
  headerItem.setToolTip(2, 'Positional assessments')
  headerItem.setToolTip(3, 'Score [centipawn] (<int>M == material score)')
  headerItem.setToolTip(4, 'Comment of move or variation')
  self._resetColumnWidth()
  self.clicked.connect(self.on_clicked)
  self.itemExpanded.connect(self.on_itemExpanded)
  self.annotationLine = ButtonLine(self.annotationSymbols, hintDict = self.symbolDescription, pointSize = 12, title = 'Move Annotation', parent = self)
  self.positionLine = ButtonLine(self.positionSymbols, hintDict = self.symbolDescription, pointSize = 12, title = 'Position', parent = self)
  self.endGameLine = ButtonLine(self.endGameSymbols, hintDict = self.endGameDescription, title = 'End Game',  pointSize = 12, parent = self)
  self.commentEdit = TextEdit('Comment ...', pointSize = 10)
  
 def _resetColumnWidth(self) -> None:
  test = QtWidgets.QLabel()
  self.zeroWidth = test.fontMetrics().size(QtCore.Qt.TextFlag.TextSingleLine, '0').width()
  # self.setColumnWidth(1, 20*zeroWidth)
  self.depth = 0
  self.setColumnWidth(0, 15*self.zeroWidth)
  self.setColumnWidth(1, 4*self.zeroWidth)
  self.setColumnWidth(2, 8*self.zeroWidth)
  self.setColumnWidth(3, 8*self.zeroWidth)
  
 @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem)
 def on_itemExpanded(self, widgetItem):
  depth = -1
  while widgetItem is not None:
   depth +=1
   widgetItem = widgetItem.parent()
  self.setColumnWidth(0, (depth*4 + 15)*self.zeroWidth)

 def _clear(self) -> None:
  self.game = None
  self.gameNodeList = list()
  self.gameItemList = list()
  self.gameVariantNodeList = list()
  self.gameVariantItemList = list()
  super(GameTreeView, self).clear()

 def setup(self, notifyGameNodeSelectedSignal : Optional[QtCore.pyqtSignal], 
                       notifyGameNodeChangedSignal : Optional[QtCore.pyqtSignal]) -> None:
  '''Set up of the game editor
  
:param notifyGameNodeSelectedSignal: signal to be emitted if a game node is selected
:param notifyGameNodeChangedSignal: signal to be emitted if the loaded game is changed
  '''
  self.notifyGameNodeSelectedSignal = notifyGameNodeSelectedSignal
  self.notifyGameNodeChangedSignal = notifyGameNodeChangedSignal
 
 def getGameNode(self, item : QtWidgets.QTreeWidgetItem):
  index = self.gameNodeList.index(item)
  return self.gameNodeList[index]

 def addVariant(self, gameNode :  chess.pgn.GameNode) -> None:
  '''Adds a new variant, parent node must exist in the editor
  
:param gameNode: game node to be added (must not be main_variation !!)
  '''
  if gameNode is None or gameNode in self.gameVariantNodeList:
   return
  if gameNode.parent not in self.gameNodeList:
   raise ValueError('Parent Node {} not found'.format(gameNode.parent))
  if gameNode.is_main_variation():
   raise ValueError('Node {} is not a variant'.format(gameNode))

  parent = gameNode.parent.variations[0]
  parentIndex = self.gameNodeList.index(parent)
  parentItem = self.gameItemList[parentIndex]
  newVariant = QtWidgets.QTreeWidgetItem()
  newVariant.setIcon(0, self.crossIcon)
  for column in range(1, 4):
   newVariant.setBackground(column, self.inactiveBrush)
  newVariant.setFlags(self.itemFlags)
  board = gameNode.parent.board()
  san = board.san(gameNode.move)
  if board.turn:
   moveText = '{}.{}'.format(board.fullmove_number, san)
  else:
   moveText = '... {}'.format(san)
  newVariant.setText(0, '{} ...'.format(moveText))
  newVariant.setText(4, gameNode.starting_comment)
  parentItem.addChild(newVariant)

  self.gameVariantNodeList.append(gameNode)
  self.gameVariantItemList.append(newVariant)

  self.addGameNodes(gameNode, parentItem = newVariant)

 def addGameNodes(self, gameNode :  chess.pgn.GameNode,  
                                     parentItem : Optional[QtWidgets.QTreeWidgetItem] = None) -> None:
  '''Adds 1 or more nodes, parent node of first node must exist in the editor
  
:param gameNode: game node to be added (must be main_variation !!)
:param parentItem: parent item of the gameNode (used only for internal use)
  '''
  if gameNode is None:
   return
  if isinstance(gameNode, chess.pgn.Game):
   self.setGame(gameNode)
   return
  if gameNode.parent not in self.gameNodeList:
   raise ValueError('Parent Node {} not found'.format(gameNode.parent))
  parent = gameNode.parent
  if parentItem is None:
   if gameNode in self.gameNodeList:
    return
   if not gameNode.is_main_variation():
    raise ValueError('Node {} is not in the main variation'.format(gameNode))
   parentIndex = self.gameNodeList.index(parent)
   parentItem = self.gameItemList[parentIndex]
   if parentItem != self.gameItemList[0]:
    parentItem = parentItem.parent()
  board = gameNode.parent.board()
  while gameNode is not None: 
   newNode = QtWidgets.QTreeWidgetItem()
   newNode.setFlags(self.itemFlags)
   parent = gameNode.parent
   san = board.san(gameNode.move)
   if board.turn:
    moveText = '{}.{}'.format(board.fullmove_number, san)
   else:
    moveText = '... {}'.format(san)
   newNode.setText(0, moveText)
   newNode.setText(1, self._findNAGSymbol (True,  gameNode))
   newNode.setText(2, self._findNAGSymbol (False,  gameNode))
   comment = gameNode.comment
   comment = comment.replace('\n','\\n')
   if board.is_checkmate():
    scoreText = 'MATE'
   elif board.is_stalemate():
    scoreText = 'SMATE'
   else:
    scoreText = None
    while True:
     match = PGNEval_REGEX.search(comment)
     if match is None:
      break
     if match.group(1) == '%' or match.group(1) == '%eval':
      scoreText = match.group(2)
     comment = comment.replace(match.group(0),'')
    if scoreText is None:
     pieceMap = gameNode.board().piece_map()
     pawnScore = 0
     for piece in list(pieceMap.values()):
      if piece.piece_type != chess.KING:
       if piece.color == chess.WHITE:
        pawnScore += MzChess.piecePawnScoreDict[piece.piece_type]
       else:
        pawnScore -= MzChess.piecePawnScoreDict[piece.piece_type]
     scoreText = '{}M'.format(pawnScore)
   newNode.setText(3, scoreText)
   newNode.setText(4, comment)
   
   parentItem.addChild(newNode)
   self.gameNodeList.append(gameNode)
   self.gameItemList.append(newNode)
   for variantNode in parent.variations[1:]:
    self.addVariant(variantNode)
    
   board.push(gameNode.move)
   gameNode = gameNode.next()
   
 def removeGameNode(self, gameNode : chess.pgn.GameNode) -> None: 
  if not gameNode.is_end() or gameNode.parent is None or gameNode not in self.gameNodeList:
   return
  index = self.gameNodeList.index(gameNode)
  self.gameItemList[index].parent().removeChild(self.gameItemList[index])
  self.gameNodeList.pop(index)
  self.gameItemList.pop(index)
  
 def setGameResult(self, result : str) -> None:
  '''Sets the 'Result' header element

:param result: one out of *1-0*, *0-1*, *1/2-1/2*, *\**
  '''
  gameResult = ["1-0", "0-1", "1/2-1/2", "*"]
  if result not in gameResult:
   result = gameResult[3]
  if len(self.gameItemList) > 0:
   self.gameItemList[0].setText(0, 'Result: {}'.format(result))
   
 def setGame(self, game : chess.pgn.Game) -> None:
  '''Clears the editor and sets new game
  
:param game: game to be set
  '''
  self._clear()
  self.game = game
  master = QtWidgets.QTreeWidgetItem()
  master.setFlags(self.itemFlags)
  master.setText(4, self.game.comment)
  self.addTopLevelItem(master)
  self.gameNodeList = [self.game]
  self.gameItemList = [master]
  self.setGameResult(self.game.headers['Result'])
  self.addGameNodes(self.game.next(), master)
  master.setExpanded(True)

 def selectNodeItem(self, gameNode : chess.pgn.GameNode) -> None:
  '''Selects a game node
  
:param gameNode: game node to be selected
  '''
  if gameNode not in self.gameNodeList:
   selIndex = 0
  else:
   selIndex = self.gameNodeList.index(gameNode)
  if selIndex > 0:
   self.expandItem(self.gameItemList[selIndex])
  self.setCurrentItem(self.gameItemList[selIndex], 0, QtCore.QItemSelectionModel.SelectionFlag.SelectCurrent)

 def selectSubnodeItem(self, gameNode : chess.pgn.GameNode, next : bool = True):
  '''Selects the next or previous variant
  
:param gameNode: reference game node
:param next: if True select the next variant, else select previous variant
  '''
  if gameNode not in self.gameNodeList:
   raise ValueError('selectSubnodeItem/gameNode: {} not found'.format(gameNode))
  parentNode = gameNode.parent
  if parentNode is None:
   return
  if not next:
   # go back to the first variation
   newNodeIndex = parentNode.variations.index(gameNode) - 1
   if newNodeIndex >= 0:
    self.selectNodeItem(parentNode.variations[newNodeIndex])
  else:
   # go to next variation
   newNodeIndex = parentNode.variations.index(gameNode) + 1
   if newNodeIndex < len(parentNode.variations):
    selIndex = self.gameNodeList.index(gameNode)
    self.expandItem(self.gameItemList[selIndex])
    newGameNode = parentNode.variations[newNodeIndex]
    self.selectNodeItem(newGameNode)
    self.notifyGameNodeSelectedSignal.emit(newGameNode)
    
 def _findNAGSymbol(self, isAnnotation : bool,  gameNode : chess.pgn.GameNode) -> str:
  if isAnnotation:
   for nag, sym in enumerate(self.annotationSymbols):
    if nag in gameNode.nags:
     return sym
  else:
   for sym, nag in self.positionSymbols.items():
    if nag in gameNode.nags:
     return sym

 def _updateNAGs(self, isAnnotation : bool,  gameNode : chess.pgn.GameNode,  nag : int) -> Set[int]:
  newNAGs = set()
  if nag != 0:
   if isAnnotation:
    r = range(1, 10)
   else:
    r = range(10, 140)
   for _nag in gameNode.nags:
    if _nag not in r:
     newNAGs .add(_nag)
   newNAGs .add(nag)
  return newNAGs
  
 def _editComment(self, item :  QtWidgets.QTreeWidgetItem) -> str:
  self.commentEdit.setText(item.text(4).replace('\\n','\n'))
  if not self.commentEdit.exec():
   return None
  comment = self.commentEdit.text().replace('\n','\\n')
  item.setText(4, comment)
  score = item.text(3)
  if len(score) > 0 and score[-1] != 'M':
   comment = '[%eval {}] {}'.format(score, comment)
  return comment

 @QtCore.pyqtSlot(QtCore.QModelIndex)
 def on_clicked(self, index):
  item = self.itemFromIndex(index)
  column = index.column()
  if item in self.gameVariantItemList:
   if column == 4:
    selIndex = self.gameVariantItemList.index(item)
    gameNode = self.gameVariantNodeList[selIndex]
    attr = 'starting_comment'
    oldAttrValue = gameNode.starting_comment
    gameNode.starting_comment = self._editComment(item)
   else:
    if column == 0 and self.notifyGameNodeSelectedSignal is not None:
     selIndex = self.gameVariantItemList.index(item)
     gameNode = self.gameVariantNodeList[selIndex]
     self.notifyGameNodeSelectedSignal.emit(gameNode)
    return
  else:
   if item in self.gameItemList:
    selIndex = self.gameItemList.index(item)
    gameNode = self.gameNodeList[selIndex]
   else:
    return
   if column == 0:
    if gameNode is None:
     self.endGameLine.setFocus('*')
     self.endGameLine.move(treeWidgetItemPos(item))
     endGameID = self.endGameLine.exec()
     self.game.headers['Result'] = self.endGameSymbols[endGameID]
     item.setText(column, self.endGameSymbols[endGameID])
    else:
     if self.notifyGameNodeSelectedSignal is not None:
      self.notifyGameNodeSelectedSignal.emit(gameNode)
     return
   elif column == 1:
    self.annotationLine.move(treeWidgetItemPos(item))
    attr = 'nags'
    oldAttrValue = copy.copy(gameNode.nags)
    nag = self.annotationLine.exec()
    gameNode.nags = self._updateNAGs(True, gameNode, nag)
    item.setText(column, self._findNAGSymbol (True,  gameNode))
   elif column == 2:
    self.positionLine.move(treeWidgetItemPos(item))
    attr = 'nags'
    oldAttrValue = copy.copy(gameNode.nags)
    nag = self.positionLine.exec()
    gameNode.nags = self._updateNAGs(True, gameNode, nag)
    item.setText(column, self._findNAGSymbol (False,  gameNode))
   elif column == 4:
    attr = 'comment'
    oldAttrValue = gameNode.comment
    gameNode.comment = self._editComment(item)
   else:
    return
  if self.notifyGameNodeChangedSignal is not None:
   self.notifyGameNodeChangedSignal.emit(gameNode, (attr, oldAttrValue))

 def moveVariant(self, parentNode : chess.pgn.GameNode, nodeID : int,  promoteItem : Optional[bool]) -> None:
  assert parentNode in self.gameNodeList and nodeID is not None and nodeID > 0
  gameNode = parentNode.variations[nodeID]
  assert gameNode in self.gameVariantNodeList
  oldIndex = self.gameVariantNodeList.index(gameNode)
  item = self.gameVariantItemList[oldIndex]
  parentItem = item.parent()
  if promoteItem is None:
   parentItem.removeChild(item)
   self.gameVariantItemList.pop(oldIndex)
   self.gameVariantNodeList.pop(oldIndex)
   self.setCurrentItem(parentItem)
   return
  itemID = parentItem.indexOfChild(item)
  if promoteItem:
   assert itemID > 0
   itemID2 = itemID - 1
  else:
   assert itemID < len(parentNode.variations) - 2
   itemID2 = itemID + 1
  childItem = parentItem.takeChild(itemID)
  parentItem.insertChild(itemID2, childItem)
  self.setCurrentItem(childItem)
  return

 def _takeChildren(self, startingNode : QtWidgets.QTreeWidgetItem, parentNode : Optional[QtWidgets.QTreeWidgetItem] = None):
  if parentNode is None:
   parentNode = startingNode.parent()
  else:
   assert startingNode.parent() == parentNode
  children = list()
  startNodeIndex = parentNode.indexOfChild(startingNode)
  for index in range(parentNode.childCount(), startNodeIndex, -1):
   children.insert(0, parentNode.takeChild(index - 1))
  return children
  index = parentNode.indexOfChild(startingNode)
  while True:
   item = parentNode.takeChild(index)
   if item is None:
    return children
   children.append(item)
   index += 1
  
 def moveVariant2Main(self, parentNode : chess.pgn.GameNode, nodeID : Optional[int]) -> None:
  assert parentNode in self.gameNodeList
  deleteItem = nodeID is None
  if deleteItem:
   nodeID = 1
  else:
   assert nodeID > 0
  gameNode = parentNode.variations[nodeID]
  assert gameNode in self.gameVariantNodeList
  oldIndex = self.gameVariantNodeList.index(gameNode)
  item = self.gameVariantItemList[oldIndex]
  self.gameVariantItemList.pop(oldIndex)
  self.gameVariantNodeList.pop(oldIndex)
  parentItem = item.parent()
  itemID = parentItem.indexOfChild(item)
  self.setUpdatesEnabled(False)
  nodeItemList = self._takeChildren(item.child(0))
  variantItem = parentItem.takeChild(itemID)
  children = parentItem.takeChildren()
  mainParentItem = parentItem.parent()
  mainItemList = self._takeChildren(parentItem)
  mainParentItem.addChildren(nodeItemList)
  if not deleteItem:
   variantItem.setText(0,'{} ...'.format(mainItemList[0].text(0)))
   newIndex = self.gameItemList.index(mainItemList[0])
   nodeItemList[0].addChild(variantItem)
   variantItem.addChildren(mainItemList)
   self.gameVariantItemList.append(variantItem)
   self.gameVariantNodeList.append(self.gameNodeList[newIndex])
  nodeItemList[0].addChildren(children)
  self.setUpdatesEnabled(True)
  return

if __name__ == "__main__":
 import io, sys
 from pgnParse import read_game

 if False:
  newData = """[Event "matein2"]
[Site "problem solved"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Comment "1"]
[PlyCount "0"]
[FEN "1k6/Rp1K4/1P5P/8/P7/3pP3/1p1P4/8 w - - 0 1"]
  
1.h7 b1=Q! $20 {[% -4.80]} 2.h8=R# *"""
 else:
  import os.path
  fileDirectory = os.path.dirname(os.path.abspath(__file__))
  ps = os.path.join(fileDirectory, 'training', 'openings', 'kingsPawn.pgn')
  with open(ps, mode = 'r',  encoding = 'utf-8') as f:
   newData = f.read()
 
 pgn = io.StringIO(newData)
 game = read_game(pgn)
 app = QtWidgets.QApplication([])

 tree = GameTreeView()
 
 tree.setGame(game)
 tree.resize(500,400)
 tree.show()
 sys.exit(app.exec())
