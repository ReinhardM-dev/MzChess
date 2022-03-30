'''Game Editor
================================
The *game* editor is based on Qt's QTreeWidget. 

|GameEditor|
It has 2 types of lines:

 * regular moves where all columns have a white background
 * beginning of a variant where the middle columns have a grey background

The tree widget has 4 colums:

 #. *Move* shows the actual move or the beginning of a variant in SAN notation 
 #. *Ann* shows the annotation, i.e. a symbolic move assessment
 #. *Pos* shows the position assessment
 #. *Score* shows the engine or material score of the last move in pawns, material score ending with M
 #. *Comment* shows either the move comment or starting comment of a variant
 
By clicking the annotation (*Ann*) and position assessment (*Pos*) fields, a popup dialog
opens which allows to change the contents   
.. |GameEditor| image:: gameEditor.png
  :width: 800
  :alt: Game Editor
'''
from typing import Optional, Set
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

import chess, chess.pgn
from chessengine import PGNEval_REGEX
from specialDialogs import ButtonLine, TextEdit, treeWidgetItemPos

class GameTreeView(PyQt5.QtWidgets.QTreeWidget):
 '''Game Editor object
 '''
 itemFlags = PyQt5.QtCore.Qt.ItemIsEnabled | PyQt5.QtCore.Qt.ItemIsSelectable
 inactiveBrush = PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor('lightgray'))
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
 piecePawnScoreDict = {
  chess.PAWN : 1, 
  chess.KNIGHT : 3, 
  chess.BISHOP : 3, 
  chess.ROOK : 5, 
  chess.QUEEN : 9
 }

 def __init__(self, parent = None) -> None:
  super(GameTreeView, self).__init__(parent)
  self.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
  self.setSelectionMode(PyQt5.QtWidgets.QAbstractItemView.SingleSelection)
  self.setFocusPolicy(PyQt5.QtCore.Qt.StrongFocus)
  scUp = PyQt5.QtWidgets.QShortcut(self)
  scUp.setKey(PyQt5.QtCore.Qt.Key_Up)
  scUp.activated.connect(self.on_sc_activated)
  scDown = PyQt5.QtWidgets.QShortcut(self)
  scDown.setKey(PyQt5.QtCore.Qt.Key_Down)
  scDown.activated.connect(self.on_sc_activated)
  self.notifyGameNodeSelectedSignal = None
  self.notifyGameChangedSignal = None
  self._clear()
  self.setColumnCount(5)
  self.setHeaderLabels(['Move', 'Ann', 'Pos', 'Score', 'Comment'])
  headerItem = self.headerItem()
  headerItem.setToolTip(0, 'SAN notation')
  headerItem.setToolTip(1, 'Move assessments')
  headerItem.setToolTip(2, 'Positional assessments')
  headerItem.setToolTip(3, 'Score [pawns] (<float>M == material score)')
  headerItem.setToolTip(4, 'Comment of move or variation')
  self._resetColumnWidth()
  self.clicked.connect(self.on_clicked)
  self.annotationLine = ButtonLine(self.annotationSymbols, hintDict = self.symbolDescription, pointSize = 12, title = 'Move Annotation', parent = self)
  self.positionLine = ButtonLine(self.positionSymbols, hintDict = self.symbolDescription, pointSize = 12, title = 'Position', parent = self)
  self.endGameLine = ButtonLine(self.endGameSymbols, hintDict = self.endGameDescription, title = 'End Game',  pointSize = 12, parent = self)
  self.commentEdit = TextEdit('Comment ...', pointSize = 10)
  
 def _resetColumnWidth(self) -> None:
  test = PyQt5.QtWidgets.QLabel()
  zeroWidth = test.fontMetrics().size(PyQt5.QtCore.Qt.TextSingleLine, '0').width()
  self.setColumnWidth(1, 20*zeroWidth)
  self.setColumnWidth(1, 4*zeroWidth)
  self.setColumnWidth(2, 8*zeroWidth)
  self.setColumnWidth(3, 8*zeroWidth)
  
 def _clear(self) -> None:
  self.game = None
  self.gameNodeList = list()
  self.gameItemList = list()
  self.gameVariantNodeList = list()
  self.gameVariantItemList = list()
  super(GameTreeView, self).clear()

 def setup(self, notifyGameNodeSelectedSignal : Optional[PyQt5.QtCore.pyqtSignal], 
                       notifyGameChangedSignal : Optional[PyQt5.QtCore.pyqtSignal]) -> None:
  '''Set up of the game editor
  
:param notifyGameNodeSelectedSignal: signal to be emitted if a game node is selected
:param notifyGameChangedSignal: signal to be emitted if the loaded game is changed
  '''
  self.notifyGameNodeSelectedSignal = notifyGameNodeSelectedSignal
  self.notifyGameChangedSignal = notifyGameChangedSignal

 def addVariant(self, gameNode :  chess.pgn.GameNode) -> None:
  '''Adds a new variant, parent node must exist in the editor
  
:param gameNode: game node to be added (must not be main_variation !!)
  '''
  if gameNode in self.gameVariantNodeList:
   return
  if gameNode.parent not in self.gameNodeList:
   raise ValueError('Parent Node {} not found'.format(gameNode.parent))
  if gameNode.is_main_variation():
   raise ValueError('Node {} is not a variant'.format(gameNode))

  parent = gameNode.parent.variations[0]
  parentIndex = self.gameNodeList.index(parent)
  parentItem = self.gameItemList[parentIndex]
  newVariant = PyQt5.QtWidgets.QTreeWidgetItem()
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
                                     parentItem : Optional[PyQt5.QtWidgets.QTreeWidgetItem] = None) -> None:
  '''Adds 1 or more nodes, parent node of first node must exist in the editor
  
:param gameNode: game node to be added (must be main_variation !!)
:param parentItem: parent item of the gameNode (used only for internal use)
  '''
  if gameNode is None:
   return
  if gameNode.parent not in self.gameNodeList:
   raise ValueError('Parent Node {} not found'.format(gameNode.parent))
  parent = gameNode.parent
  if parentItem is None:
   if gameNode in self.gameNodeList:
    return
   if False and not gameNode.is_main_variation():
    raise ValueError('Node {} is not in the main variation'.format(gameNode))
   parentIndex = self.gameNodeList.index(parent)
   parentItem = self.gameItemList[parentIndex]
   if parent.is_main_variation() and parentItem != self.gameItemList[0]:
    parentItem = parentItem.parent()
  board = gameNode.parent.board()
  while gameNode is not None: 
   newNode = PyQt5.QtWidgets.QTreeWidgetItem()
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
        pawnScore += self.piecePawnScoreDict[piece.piece_type]
       else:
        pawnScore -= self.piecePawnScoreDict[piece.piece_type]
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
  master = PyQt5.QtWidgets.QTreeWidgetItem()
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
  self.setCurrentItem(self.gameItemList[selIndex], 0, PyQt5.QtCore.QItemSelectionModel.SelectCurrent)

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
   if newNodeIndex > 0:
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
  
 def _editComment(self, item :  PyQt5.QtWidgets.QTreeWidgetItem) -> str:
  self.commentEdit.setText(item.text(4).replace('\\n','\n'))
  if not self.commentEdit.exec():
   return None
  comment = self.commentEdit.text().replace('\n','\\n')
  item.setText(4, comment)
  score = item.text(3)
  if len(score) > 0 and score[-1] != 'M':
   comment = '[%eval {}] {}'.format(score, comment)
  return comment

 @PyQt5.QtCore.pyqtSlot(PyQt5.QtCore.QModelIndex)
 def on_clicked(self, index):
  item = self.itemFromIndex(index)
  column = index.column()
  isVariant = False
  parent = index
  while parent.isValid():
   isVariant = not isVariant
   parent = parent.parent()
  if isVariant:
   if column == 4:
    if item in self.gameVariantItemList:
     selIndex = self.gameVariantItemList.index(item)
     gameNode = self.gameVariantNodeList[selIndex]
     gameNode.starting_comment = self._editComment(item)
    else:
     self.game.comment = self._editComment(item)
     gameNode = self.game
   else:
    if column == 0 and self.notifyGameNodeSelectedSignal is not None:
     self.notifyGameNodeSelectedSignal.emit(self.game)
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
    nag = self.annotationLine.exec()
    gameNode.nags = self._updateNAGs(True, gameNode, nag)
    item.setText(column, self._findNAGSymbol (True,  gameNode))
   elif column == 2:
    self.positionLine.move(treeWidgetItemPos(item))
    nag = self.positionLine.exec()
    gameNode.nags = self._updateNAGs(True, gameNode, nag)
    item.setText(column, self._findNAGSymbol (False,  gameNode))
   elif column == 4:
    gameNode.comment = self._editComment(item)
   else:
    return
  self._emitGameChanged()
  
 def _isVariant(self, item : PyQt5.QtWidgets.QTreeWidgetItem) -> bool:
  isTrue = False
  parent = item
  while parent is not None:
   isTrue = not isTrue
   parent = parent.parent()
  return isTrue

 def removeVariant(self) -> None:
  '''Remove variant, if currently selected item is a variant
  '''
  item = self.currentItem()
  if item is not None and self._isVariant(item):
   parent = item.parent()
   if parent is None:
    return
   index = parent.indexOfChild(item)
   parent.removeChild(item)
   self.setCurrentItem(parent.child(index))
   selIndex = self.gameVariantItemList.index(item)
   itemNode = self.gameVariantNodeList[selIndex]
   itemNode.parent.remove_variation(itemNode)
   self._emitGameChanged()

 def promoteVariant(self) -> None:
  '''Promote variant, if currently selected item is a variant
  '''
  item = self.currentItem()
  if item is not None and self._isVariant(item):
   parent = item.parent()
   if parent is None:
    return
   index = parent.indexOfChild(item)
   if index > 0:
    parent.takeChild(index)
    parent.insertChild(index - 1, item)
    self.setCurrentItem(item)
    parent.setExpanded(True)
    item.setExpanded(False)
    selIndex = self.gameVariantItemList.index(item)
    itemNode = self.gameVariantNodeList[selIndex]
    itemNode.parent.promote(itemNode)
    self._emitGameChanged()

 def demoteVariant(self) -> None:
  '''Demote variant, if currently selected item is a variant
  '''
  item = self.currentItem()
  if item is not None and self._isVariant(item):
   parent = item.parent()
   if parent is None:
    return
   index = parent.indexOfChild(item)
   if index < parent.childCount():
    parent.takeChild(index)
    parent.insertChild(index + 1, item)
    self.setCurrentItem(item)
    parent.setExpanded(True)
    item.setExpanded(False)
    selIndex = self.gameVariantItemList.index(item)
    itemNode = self.gameVariantNodeList[selIndex]
    itemNode.parent.demote(itemNode)
    self._emitGameChanged()

 def promoteVariant2Main(self) -> None:
  '''Promote variant to main line, if currently selected item is a variant
  '''
  item = self.currentItem()
  if item is not None:
   parent = item.parent()
   if self._isVariant(item):
    index = parent.indexOfChild(item)
    if index > 0:
     child = parent.takeChild(index)
     parent.insertChild(0, child)
    vChildren = item.takeChildren()
    gParent = parent.parent()
    fIndex = gParent.indexOfChild(parent)
    pChildren = parent.takeChildren()
    mChildren = list()
    for idx in reversed(range(fIndex, gParent.childCount())):
     mChildren.insert(0, gParent.takeChild(idx))
    gParent.addChildren(vChildren)
    vChildren[0].addChildren(pChildren)
    item.addChildren(mChildren)
    self.setCurrentItem(vChildren[0])
    parent.setExpanded(True)
    item.setExpanded(False)
    selIndex = self.gameVariantItemList.index(item)
    itemNode = self.gameVariantNodeList[selIndex]
    itemNode.parent.promote_to_main(itemNode)
    self._emitGameChanged()

 @PyQt5.QtCore.pyqtSlot()
 def on_sc_activated(self):
  itemList = self.selectedItems()
  if len(itemList) > 0 and not self._isVariant(itemList[0]):
   row = self.gameItemList.index(itemList[0])
   gameNode = self.gameNodeList[row]
   sendingSC = self.sender()
   if sendingSC.key() == PyQt5.QtCore.Qt.Key_Down:
    newGameNode = gameNode.next()
    if newGameNode is not None:
     self.notifyGameNodeSelectedSignal.emit(newGameNode)
     self.setCurrentItem(self.itemBelow(itemList[0]))
    else:
     print("next({}) == None".format(gameNode))
   else:
    if gameNode.parent is not None:
     self.notifyGameNodeSelectedSignal.emit(gameNode.parent)
     self.setCurrentItem(self.itemAbove(itemList[0]))
    else:
     print("previous({}) == None".format(gameNode))

 def _emitGameChanged(self) -> None:
  if self.notifyGameChangedSignal is not None:
   self.notifyGameChangedSignal.emit(self.game)

if __name__ == "__main__":
 import io, sys
 from pgnParse import read_game

 if False:
  isNewGame = False
  newData = """[Event "matein2"]
[Site "problem solved"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[SetUp "1"]
[PlyCount "0"]
[FEN "1k6/Rp1K4/1P5P/8/P7/3pP3/1p1P4/8 w - - 0 1"]
  
1.h7 b1=Q! $20 {[% -4.80]} 2.h8=R# *"""
 else:
  isNewGame = True
  ps = "C:/Users/Reinh/OneDrive/Dokumente/Schach/kingsPawn.pgn"
  with open(ps, mode = 'r',  encoding = 'utf-8') as f:
   newData = f.read()
 
 pgn = io.StringIO(newData)
 game = read_game(pgn)
 app = PyQt5.QtWidgets.QApplication([])

 tree = GameTreeView()
 
 msgSc = PyQt5.QtWidgets.QShortcut(PyQt5.QtGui.QKeySequence('Ctrl+U'), tree)
 msgSc.activated.connect(tree.promoteVariant)

 msgSc = PyQt5.QtWidgets.QShortcut(PyQt5.QtGui.QKeySequence('Ctrl+D'), tree)
 msgSc.activated.connect(tree.demoteVariant)

 msgSc = PyQt5.QtWidgets.QShortcut(PyQt5.QtGui.QKeySequence('Ctrl+X'), tree)
 msgSc.activated.connect(tree.removeVariant)

 msgSc = PyQt5.QtWidgets.QShortcut(PyQt5.QtGui.QKeySequence('Ctrl+M'), tree)
 msgSc.activated.connect(tree.promoteVariant2Main)

 tree.setGame(game)
 if isNewGame:
  newVariant = game.add_variation(chess.Move.from_uci('a2a3'), comment = 'move #1', starting_comment = 'variant', nags = [2, 17]) 
  tree.addGameNodes(newVariant)
  gameNode = newVariant.add_variation(chess.Move.from_uci('a7a6'), comment = 'move #2', starting_comment = '???', nags = [3, 20]) 
  tree.addGameNodes(gameNode)
 tree.resize(500,400)
 tree.show()
 sys.exit(app.exec_())
