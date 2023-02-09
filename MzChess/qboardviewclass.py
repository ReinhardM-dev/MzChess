'''
The use of the chessboard requires a mouse or a mousepad. A piece is moved like that: 
  
  * :kbd:`mouse-left-press`: begin move of selected piece
  * :kbd:`mouse-left-release`: end move

For training purposes, several helpers are available.

Warn of Danger
===================

The *Warn of Danger* is enabled by the ``Game/Warn of Danger`` action.
It runs as follows:

  #. assign material scores to each attack and reply for every ply
  #. create a combined  list of attacks and replies (cheapest first)
  #. create a list of total scores for every ply

Effect on other pieces like discovered check are not considered. An example:

|WarnOfDanger|

Obviously, the rook at ``b8`` is danger.

Move Options
===================

The *Move Options* are enabled by the ``Game/Show Move Options`` action.
By pressing the left mouse button at ``b8``, we see:

|MoveOptions|

It seem that ``b8-d8`` is the best move, but it is dubious ...


 .. |WarnOfDanger| image:: warnOfDanger.png
  :width: 600
  :alt: Warn of Danger
 .. |MoveOptions| image:: moveOptions.png
  :width: 600
  :alt: Move Options
'''
from typing import Optional
import sys, os, os.path
import copy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtGui, QtCore
 from PyQt5.QtSvg import QGraphicsSvgItem 
else:
 from PyQt6 import QtWidgets, QtGui, QtCore
 from PyQt6.QtSvgWidgets import QGraphicsSvgItem

import chess, chess.pgn
import chessengine
from specialDialogs import ButtonLine
import warnOfDanger

def showStatus(board):
 print('fen = {}'.format(board.fen(en_passant = 'fen')))
 for row in range(8):
  for col in range(8):
   chessSquare = chess.square(col, row)
   piece = board.piece_at(chessSquare)
   if piece is not None:
    print(' square = {}, name = {}, symbol = {}'.format(
     chessSquare, chess.square_name(chessSquare), piece.symbol()))
 for n, move in enumerate(board.move_stack):
  print('{}. {}'.format(n, move.uci()))

class QBoardViewClass(QtWidgets.QGraphicsView):
 '''The *chessboard* is based on Qt's QGraphicsView.
 '''

 def __init__(self, parent = None) -> None:
  super(QBoardViewClass, self).__init__(parent)
  self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
  self.border = 0
  self.game = Game()
  self.setMouseTracking(True)
  self.setScene(self.game)
  self.game.installEventFilter(self.game)
  
 def setup(self, notifyNewGameNodeSignal : Optional[QtCore.pyqtSignal] = None, 
                       notifyGameNodeSelectedSignal : Optional[QtCore.pyqtSignal] = None, 
                      materialLabel : Optional[QtWidgets.QLabel] = None, 
                      squareLabel : Optional[QtWidgets.QLabel] = None, 
                      turnFrame : Optional[QtWidgets.QFrame]  = None, 
                      hintLabel : Optional[QtWidgets.QLabel]  = None, 
                      flipped : bool = False) -> None:
  '''Set up of the game editor
  
:param notifyNewGameNodeSignal: signal to be emitted if a move is added
:param notifyGameNodeSelectedSignal: signal to be emitted if a game node is selected
:param materialLabel: label showing the material budget
:param squareLabel: label showing the square under mouse pointer (usually in the status bar)
:param turnFrame: frame showing the color of player making the move
:param hintLabel: label showing the engine's hints and scores (usually in the status bar)
:param flipped: if True, the square *a1* is on top
  '''
  self.notifyGameNodeSelectedSignal = notifyGameNodeSelectedSignal 
  self.game.setup(notifyNewGameNodeSignal = notifyNewGameNodeSignal,  materialLabel = materialLabel, squareLabel = squareLabel, 
   hintLabel = hintLabel, turnFrame =turnFrame,  flipped = flipped)
  self._configureScene()
  self.game.draw_board()

 def setHint(self, enableHint : int = 0, enableScore : bool = False, 
                         engine : Optional[chessengine.ChessEngine] = None) -> None:
  '''Controls the usage of the hint label

:param enableHint: If True, the *hintLabel* shows the *engine* hint
:param enableScore: If True, the *hintLabel* shows the *engine* scores
:param engine: engine to be used (required, if *enableHint or enableScore*
  '''
  self.game.setHint(enableHint, enableScore,  engine = engine)

 def setFlipped(self, enable : bool) -> None:
  '''Controls the board orientation

:param enable: if True, the square *a1* is on top
  '''
  self.game.setFlipped(enable)

 def setDrawOptions(self, enable : bool) -> None:
  '''Controls the draw options. Draw options are shown when :kbd:`mouse-left-press` on a piece

:param enable: if True, the draw options are enabled
  '''
  self.game.setDrawOptions(enable)
  
 def setWarnOfDanger(self, enable : bool) -> None:
  '''Controls the warn of danger, i.e. shows attacked pieces

:param enable: if True, the warn of danger is enabled
  '''
  self.game.setWarnOfDanger(enable)
  
 def _fen(self) -> str:
  return self.game.fen(en_passant = 'fen')
 
 def set_fen(self, fen : str) -> None:
  '''Configures the *chessboard*

:param fen: position in `Forsyth-Edwards` Notation
  .. _Forsyth-Edwards: https://github.com/fsmosca/PGN-Standard
  '''
  self.game.set_fen(fen)
 
 def setGameNode(self, gameNode : chess.pgn.GameNode) -> None:
  '''Sets the game node displayed by the *chessBoard* 
  
:param gameNode : game node to be displayed
  '''
  self.game.setGameNode(gameNode)
  
 def nextMove(self) -> None:
  '''Go 1 move forward, if possible
  '''
  return self.game.nextMove()
 
 def previousMove(self) -> None:
  '''Go 1 move backward, if possible
  '''
  return self.game.previousMove()

 def _configureScene(self):
  self.fitInView(QtCore.QRectF(0, 0, 8 * Game.pieceSize, 8 * Game.pieceSize), mode = QtCore.Qt.AspectRatioMode.KeepAspectRatio)
  # self.setScene(self.game)
  
 def resizeEvent(self, ev) -> None:
  # print('oldSize = {}, size = {}'.format(ev.oldSize(), ev.size()))
  QtWidgets.QGraphicsView.resizeEvent(self, ev)
  self._configureScene()
  if self.game.pressedPiece is None:
   self.game.draw_board()
   
 @QtCore.pyqtSlot(QtGui.QKeyEvent)
 def keyPressEvent(self, ev):
  if ev.key() == QtCore.Qt.Key.Key_Up:
   newGameNode = self.game.gameNode.parent
  else:
   newGameNode = self.game.gameNode.next()
  if newGameNode is not None:
   self.notifyGameNodeSelectedSignal.emit(newGameNode)

class Piece(QGraphicsSvgItem):
 '''Internal class
 '''
 piecesDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)), ':/pieces/')
 colorChars = ('black', 'white')

 def __init__(self, symbolName : str, size : int, parent = None) -> None:
  '''
  symbol values (according to PGN spec)
   p,P = white pawn, black ~
   n,N = white knight, black ~ 
   b,B = white bishop, black ~ 
   r,R = white rook, black ~ 
   q,Q = white queen, black ~
   k,K = white king, black ~
  '''
  self.llPiece = chess.Piece.from_symbol(symbolName)
  fileDirectory = os.path.dirname(os.path.abspath(__file__))
  svgPath = os.path.join(fileDirectory , 'pieces', 
    '{}-{}.svg'.format(self.colorChars[self.llPiece.color], chess.piece_name(self.llPiece.piece_type)))
  super(Piece, self).__init__(svgPath, parent)
  self.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
  bwidth = self.boundingRect().width()
  self.setScale(size/bwidth)
  # self.setAcceptHoverEvents(True)
  self.setCacheMode(QtWidgets.QGraphicsItem.CacheMode.NoCache)
  self.setZValue(1)

class Game(QtWidgets.QGraphicsScene):
 '''Internal class
 '''
 whiteSquareBrush = QtGui.QBrush( QtCore.Qt.GlobalColor.white, QtCore.Qt.BrushStyle.SolidPattern)
 blackSquareBrush = QtGui.QBrush( QtCore.Qt.GlobalColor.gray, QtCore.Qt.BrushStyle.SolidPattern)
 goodSquareBrush = QtGui.QBrush( QtCore.Qt.GlobalColor.green, QtCore.Qt.BrushStyle.SolidPattern)
 intermediateSquareBrush = QtGui.QBrush( QtCore.Qt.GlobalColor.yellow, QtCore.Qt.BrushStyle.SolidPattern)
 badSquareBrush = QtGui.QBrush( QtCore.Qt.GlobalColor.red, QtCore.Qt.BrushStyle.SolidPattern)
 requestHint = QtCore.pyqtSignal(str)
 pieceSize = 45
 leipzigEncodeDict = {
   'P' : 'p', 'N' : 'n', 'B' : 'b', 'R' : 'r', 'Q' : 'q', 
   'p' : 'o', 'n' : 'm', 'b' : 'v', 'r' : 't', 'q' : 'w' 
  }
 chessFigures = { '♕' :  chess.QUEEN, '♖' :  chess.ROOK,  '♗' :  chess.BISHOP,  '♘' :  chess.KNIGHT}
 chessFiguresDescription =  { '♕' : 'Queen', '♖' : 'Rook', '♗' :  'Bishop', '♘' :  'Knight'}
 encodePiece = lambda piece_type, color : Game.leipzigEncodeDict[chess.Piece(piece_type, color).symbol()]
 
 def __init__(self, parent = None) -> None:
  super(Game, self).__init__(parent)
  
  self.timer = QtCore.QTimer()
  self.timer.timeout.connect(self.flushHint)
  self.requestHint.connect(self.hintRequested)
  self.hintDelay = 100

  self.promotePawn = ButtonLine(self.chessFigures, hintDict = self.chessFiguresDescription, title = 'Promotion', pointSize = 30)
  self.gameNode = chess.pgn.Game()

  self.boardElementGroup = None
  self.drawOptionsGroup = list()
  self.boardPieces = list()
  self.flipped = False
  self.engine = None
  self.hint = False
  self.score = False
  self.drawOptions = False
  self.warnOfDanger = False
  self.materialLabel = None
  self.squareLabel = None
  self.turnFrame = None
  self.hintLabel = None
  
 def needHint(self):
  board = self.gameNode.board()
  return self.hint & (int(not board.turn) + 1) > 0
  
 def setup(self, notifyNewGameNodeSignal : Optional[QtCore.pyqtSignal] = None, 
                      materialLabel : Optional[QtWidgets.QLabel] = None, 
                      squareLabel : Optional[QtWidgets.QLabel] = None, 
                      turnFrame : Optional[QtWidgets.QFrame]  = None, 
                      hintLabel : Optional[QtWidgets.QLabel]  = None, 
                      flipped : bool = False, 
                      gameNode : Optional[chess.pgn.GameNode]= None) -> None:
  self.notifyNewGameNodeSignal = notifyNewGameNodeSignal
  self.materialLabel = materialLabel
  self.squareLabel = squareLabel
  self.turnFrame = turnFrame
  self.hintLabel = hintLabel
  if gameNode is not None:
   self.gameNode = gameNode
  self.boardElementGroup = None
  self.boardPieces = list()
  self.flipped = flipped
  board = self.gameNode.board()
  self.showMaterial(board)
  self.showTurn(board)
  self.pressedPiece = None
  
 def boardRect(self) -> QtCore.QRectF:
  return QtCore.QRectF(0, 0, 8 * self.pieceSize, 8 * self.pieceSize)

 def setDrawOptions(self, enable : bool) -> None:
  self.drawOptions = enable
  
 def setWarnOfDanger(self, enable : bool) -> None:
  if enable != self.warnOfDanger:
   self.warnOfDanger = enable
   if enable:
    self.draw_warnOfDanger()
   else:
    self.remove_warnOfDanger()
  
 def fen(self):
  return self.gameNode.board().fen(en_passant = 'fen')
  
 def setGameNode(self, gameNode : bool) -> None:
  if gameNode is None:
   return
  self.gameNode = gameNode
  self.draw_board()
  board = self.gameNode.board()
  self.showMaterial(board)
  self.isGameOver = False
  self.showTurn(board)
  if self.needHint() or self.score:
   self.requestHint.emit(self.fen())
  self.draw_warnOfDanger()

 # -------------------------------------------------------

 def nextMove(self) -> None:
  newGameNode = self.gameNode.next()
  if newGameNode is None:
   return self.gameNode
  self.gameNode = newGameNode
  self.draw_board()
  board = self.gameNode.board()
  self.showTurn(board)
  if self.needHint() or self.score:
    self.requestHint.emit(self.fen())
  self.showMaterial(board)
  self.showTurn(board)
  self.draw_warnOfDanger()
  return newGameNode
 
 def previousMove(self) -> None:
  newGameNode = self.gameNode.parent
  if newGameNode is None:
   return self.gameNode
  self.gameNode = newGameNode
  self.draw_board()
  board = self.gameNode.board()
  self.showTurn(board)
  if self.needHint() or self.score:
   self.requestHint.emit(self.fen())
  self.showMaterial(board)
  self.showTurn(board)
  self.draw_warnOfDanger()
  return newGameNode

 # -------------------------------------------------------

 def showTurn(self, board : chess.Board) -> None:
  if self.turnFrame is None:
   return
  self.gameIsOver = board.is_game_over()
  game = self.gameNode.game()
  border = ' border-color: black; border-style: solid; border-width: 1px;'
  if self.gameIsOver:
   game.headers['Result'] = board.result()
   if board.is_checkmate():
    self.turnFrame.setStyleSheet('background-color: red;' + border)
   else:
    self.turnFrame.setStyleSheet('background-color: yellow;' + border)
  elif game.headers['Result'] != '*' and self.gameNode.is_mainline() and self.gameNode.is_end():
   if game.headers['Result'] == '1/2-1/2':
    self.turnFrame.setStyleSheet('background-color: yellow;' + border)
   else:
    self.turnFrame.setStyleSheet('background-color: red;' + border)
  elif board.turn:
   self.turnFrame.setStyleSheet('background-color: white;' + border)
  else:
   self.turnFrame.setStyleSheet('background-color: black;')

 def showMaterial(self, board : chess.Board) -> None:
  if self.materialLabel is None:
   return
  pieceMap = board.piece_map()
  whiteCountList = 7 * [0]
  blackCountList = 7 * [0]
  for piece in list(pieceMap.values()):
   if piece.color == chess.WHITE:
    whiteCountList[piece.piece_type] += 1
   else:
    blackCountList[piece.piece_type] += 1
  piece_text =''
  for piece_type in range(5, 0,-1):
   delta = whiteCountList[piece_type] - blackCountList[piece_type]
   if delta == 0:
    continue
   if delta > 0:
    piece_text += delta * Game.encodePiece(piece_type, chess.WHITE)
   else:
    piece_text += abs(delta) * Game.encodePiece(piece_type, chess.BLACK)
  self.materialLabel.setText(piece_text)

 # -------------------------------------------------------

 def draw_board(self, flipped : Optional[bool] = None) -> None:
  self.clear()
  elementWidth = self.pieceSize
  for row in range(8):
   for col in range(8):
    rect = QtWidgets.QGraphicsRectItem( row * elementWidth, col * elementWidth, elementWidth, elementWidth)
    if row % 2 == col % 2:
     rect.setBrush( self.whiteSquareBrush )
    else:
     rect.setBrush( self.blackSquareBrush )
    rect.setCacheMode(QtWidgets.QGraphicsItem.CacheMode.NoCache)
    rect.setZValue(0)
    self.addItem(rect)
  if flipped is not None:
   self.flipped = flipped
  self.draw_pieces()
  
 def draw_pieces(self) -> None:
  symbolWidth = self.pieceSize
  for row in range(8):
   for col in range(8):
    if self.flipped:
     chessSquare = 63 - chess.square(col, row)
    else:
     chessSquare = chess.square(col, row)
    piece = self.gameNode.board().piece_at(chessSquare)
    if piece is not None:
     # print('draw_pieces: square = {}, name = {}'.format(chessSquare, chess.square_name(chessSquare)))
     # print('draw_pieces: piece = {}, scenePos = {}'.format(piece.symbol(), self.getScenePos(chessSquare)))
     bPiece = Piece(piece.symbol(), size = symbolWidth)
     bPiece.setPos(self.getScenePos(chessSquare))
     # bPiece.setScale(symbolWidth/bPiece.boundingRect().width())
     self.addItem(bPiece)
  self.update()

 def draw_drawOptions(self) -> None:
  if len(self.legal_targets) == 0 or not self.drawOptions:
   return 
  elementSize = QtCore.QSizeF(self.pieceSize, self.pieceSize)
  board = self.gameNode.board()
  self.drawOptionsGroup = len(self.legal_targets)*[None]
  for n, chessSquare in enumerate(self.legal_targets):
   self.drawOptionsGroup[n] = QtWidgets.QGraphicsRectItem(
              QtCore.QRectF(self.getScenePos(chessSquare), elementSize))
   self.drawOptionsGroup[n].setCacheMode(QtWidgets.QGraphicsItem.CacheMode.NoCache)
   if board.is_attacked_by(not board.turn, chessSquare):
    self.drawOptionsGroup[n].setBrush(self.badSquareBrush)
   else:
    self.drawOptionsGroup[n].setBrush(self.goodSquareBrush)
   self.drawOptionsGroup[n].setZValue(0.8)
   self.addItem(self.drawOptionsGroup[n])
  self.update()

 def remove_drawOptions(self) -> None:
  try:
   for rect in self.drawOptionsGroup:
    self.removeItem(rect)
   self.update()
  except:
   pass
  self.drawOptionsGroup = list()
   
 def draw_warnOfDanger(self) -> None:
  if not self.warnOfDanger:
   return 
  elementSize = QtCore.QSizeF(self.pieceSize, self.pieceSize)
  square2ScoreDict = warnOfDanger.warnOfDanger(self.gameNode.board())
  if square2ScoreDict is None or len(square2ScoreDict) == 0:
   return
  self.warnOfDangerGroup = len(square2ScoreDict)*[None]
  for n, chessSquare in enumerate(square2ScoreDict):
   score = square2ScoreDict[chessSquare]
   self.warnOfDangerGroup[n] = QtWidgets.QGraphicsRectItem(
              QtCore.QRectF(self.getScenePos(chessSquare), elementSize))
   self.warnOfDangerGroup[n].setCacheMode(QtWidgets.QGraphicsItem.CacheMode.NoCache)
   if score > 0:
    self.warnOfDangerGroup[n].setBrush(self.badSquareBrush)
   elif score == 0:
    self.warnOfDangerGroup[n].setBrush(self.intermediateSquareBrush)
   else:
    self.warnOfDangerGroup[n].setBrush(self.goodSquareBrush)
   self.warnOfDangerGroup[n].setZValue(0.4)
   self.addItem(self.warnOfDangerGroup[n])
  self.update()

 def remove_warnOfDanger(self) -> None:
  try:
   for rect in self.warnOfDangerGroup:
    self.removeItem(rect)
  except:
   pass
  self.warnOfDangerGroup = list()
   
 def getScenePos(self, chessSquare : int, center : bool = False) -> QtCore.QPointF:
  if chessSquare < 0 or chessSquare > 63:
   return None 
  if center:
   delta = self.pieceSize / 2
  else:
   delta = 0
  if self.flipped:
   row = chess.square_rank(chessSquare)
   col = 7 - chess.square_file(chessSquare)
  else:
   row = 7 - chess.square_rank(chessSquare)
   col = chess.square_file(chessSquare)
  return QtCore.QPointF(col * self.pieceSize + delta, row * self.pieceSize + delta)

 # -------------------------------------------------------
   
 def getChessSquareAt(self, scenePos : QtCore.QPointF) -> int:
  iPos = scenePos/self.pieceSize
  if self.flipped:
   id = chess.square(7 - int(iPos.x()), int(iPos.y()))
  else:
   id = chess.square(int(iPos.x()), 7 - int(iPos.y()))
  if id < 0 or id > 63:
   return None 
  return id

 # -------------------------------------------------------
 
 def setHint(self, enableHint : int = 0, enableScore : bool = False, 
                         engine : Optional[chessengine.ChessEngine] = None) -> None:
  self.engine = engine
  if self.engine is not None:
   self.hint = enableHint
  else:
   self.hint = 0
  self.score = (self.engine is not None and enableScore)
  if self.needHint() or self.score:
   self.hintFen = None
   self.engine.bestMoveScoreSignal.connect(self.bestMoveScoreAvailable)
   self.requestHint.emit(self.fen())
  else:
   self.hintLabel.setText('-/-')

 def setFlipped(self, enable : bool) -> None:
  self.flipped = enable
  self.setGameNode(self.gameNode)
  
 def hintRequested(self, fen : str) -> None:
  if not (self.needHint() or self.score):
   return
  self.timer.stop()
  self.timer.start(self.hintDelay+1)
 
 def flushHint(self) -> None:
  fen = self.fen()
  if self.hintFen != fen and self.engine is not None and self.engine.uciNewGame(fen):
   self.engine.startPlay()
   self.hintFen = fen

 @QtCore.pyqtSlot(chess.Move, str)
 def bestMoveScoreAvailable(self, move, score):
  if self.hintLabel is not None:
   board = self.gameNode.board()
   if self.hint & (int(not board.turn) + 1) > 0:
    try:
     moveString = board.lan(move)
    except:
     moveString = '?{}'.format(move.uci())
   else:
    moveString = '-'
   if self.score:
    self.hintLabel.setText('{}/{}'.format(moveString, score))
   else:
    self.hintLabel.setText('{}/-'.format(moveString))

 # -------------------------------------------------------

 def mouseDoubleClickEvent(self, mouseEvent):
  self.mousePressed = False
  # print('==> mouseDoubleClickEvent')

 def eventFilter(self, source, event):
  if event.type() == QtCore.QEvent.Type.GraphicsSceneMouseMove:
   square = self.getChessSquareAt(event.scenePos())
   if square is not None:
    self.squareLabel.setText(chess.square_name(square))
   else:
    self.squareLabel.setText('')
  elif event.type() == QtCore.QEvent.Type.GraphicsSceneLeave:
   self.squareLabel.setText('')
  return QtWidgets.QGraphicsScene.eventFilter(self, source, event)

 def mousePressEvent(self, qGraphicsSceneMouseEvent : QtWidgets.QGraphicsSceneMouseEvent) -> None:
  self.mousePressed = True
  self.pressedPiece = None
  self.remove_warnOfDanger()
  self.pressedSquareId = self.getChessSquareAt(qGraphicsSceneMouseEvent.scenePos())
  if self.pressedSquareId is not None:
   self.pressedPiece = self.itemAt(self.getScenePos(self.pressedSquareId), QtGui.QTransform())
   # print('==> mousePressEvent: scene = {} => square = {}'.format(qGraphicsSceneMouseEvent.scenePos(), chess.square_name(self.pressedSquareId)))
   if isinstance(self.pressedPiece,QtWidgets.QGraphicsRectItem):
    self.pressedPiece = None # empty field hitten
  board = self.gameNode.board()
  if not self.gameIsOver:
   self.pressedSquareId = self.getChessSquareAt(qGraphicsSceneMouseEvent.scenePos())
   if self.pressedPiece is not None:
    self.pressedPiece = self.itemAt(self.getScenePos(self.pressedSquareId), QtGui.QTransform())
    self.legal_targets = list()
    for move in list(board.legal_moves):
     if move.from_square == self.pressedSquareId:
      self.legal_targets.append(move.to_square)
    self.attackedPieceDict = dict()
    for pieceID in board.attacks(self.pressedSquareId): 
     actPiece = self.itemAt(self.getScenePos(pieceID), QtGui.QTransform())
     if not isinstance(actPiece,QtWidgets.QGraphicsRectItem):
      self.attackedPieceDict[pieceID] = actPiece
    self.draw_drawOptions()
  QtWidgets.QGraphicsScene.mousePressEvent(self, qGraphicsSceneMouseEvent)

 def mouseReleaseEvent(self, qGraphicsSceneMouseEvent : QtWidgets.QGraphicsSceneMouseEvent) -> None:
  # print('==> mouseReleaseEvent: mousePressed = {}, scene = {}'.format(self.mousePressed, qGraphicsSceneMouseEvent.scenePos()))
  QtWidgets.QGraphicsScene.mouseReleaseEvent(self, qGraphicsSceneMouseEvent)
  if self.pressedPiece is None or not self.mousePressed or self.gameIsOver:
   if self.pressedPiece is not None:
    self.pressedPiece.setPos(self.getScenePos(self.pressedSquareId))
   return
  self.remove_drawOptions()
  releasedSquareId = self.getChessSquareAt(qGraphicsSceneMouseEvent.scenePos())
  if releasedSquareId in self.legal_targets:
   if releasedSquareId in self.attackedPieceDict:
    self.removeItem(self.attackedPieceDict[releasedSquareId])
  else:
   releasedSquareId = self.pressedSquareId
  # print('==> mouseReleaseEvent: square = {}'.format(chess.square_name(releasedSquareId)))
  if releasedSquareId != self.pressedSquareId:
   oldBoard = self.gameNode.board()
   if self.pressedPiece.llPiece.piece_type == chess.PAWN and \
     ((self.pressedPiece.llPiece.color == chess.WHITE and releasedSquareId > chess.H7) \
     or (self.pressedPiece.llPiece.color == chess.BLACK and releasedSquareId < chess.A2)):
    self.promotePawn.move(qGraphicsSceneMouseEvent.screenPos())
    promotedPieceType = self.promotePawn.exec()
    move = chess.Move(self.pressedSquareId, releasedSquareId, promotion = promotedPieceType)
    self.removeItem(self.pressedPiece)
    promotedPiece = chess.Piece(promotedPieceType, self.pressedPiece.llPiece.color)
    pPiece = Piece(promotedPiece.symbol(), self.pieceSize)
    pPiece.setPos(self.getScenePos(releasedSquareId))
    self.addItem(pPiece)
    self.update()
   else:
    move = chess.Move(self.pressedSquareId, releasedSquareId)
    if oldBoard.is_castling(move): 
     isWhite = (self.pressedPiece.llPiece.color == chess.WHITE)
     if (isWhite and self.pressedSquareId != chess.E1) \
       or ((not isWhite) and self.pressedSquareId != chess.E8):
      raise ValueError('UIE: Unexpected castling move')
     if releasedSquareId > self.pressedSquareId:
      if isWhite:
       rookPos = self.getScenePos(chess.H1)
       rookTargetPos = self.getScenePos(chess.F1)
      else:
       rookPos = self.getScenePos(chess.H8)
       rookTargetPos = self.getScenePos(chess.F8)
     else:
      if isWhite:
       rookPos = self.getScenePos(chess.A1)
       rookTargetPos = self.getScenePos(chess.D1)
      else:
       rookPos = self.getScenePos(chess.A8)
       rookTargetPos = self.getScenePos(chess.D8)
     rookPiece = self.itemAt(rookPos, QtGui.QTransform())
     if isinstance(rookPiece,QtWidgets.QGraphicsRectItem):
      raise ValueError('UIE: QGraphicsRectItem found')
      rookPiece.setPos(self.getScenePos(releasedSquareId))
     rookPiece.setPos(rookTargetPos)
    elif oldBoard.is_en_passant(move):
     pawnSquareID = chess.square(chess.square_file(move.to_square), chess.square_rank(move.from_square))
     pawnItem = self.itemAt(self.getScenePos(pawnSquareID), QtGui.QTransform())
     self.removeItem(pawnItem)
     print('en passant move detected')
    self.pressedPiece.setPos(self.getScenePos(releasedSquareId))
   self.gameNode = self.gameNode.add_variation(move)
   board = self.gameNode.board()
   # showStatus(board)
   self.showMaterial(board)
   self.showTurn(board)
   if self.notifyNewGameNodeSignal is not None:
    self.notifyNewGameNodeSignal.emit(self.gameNode)
   if self.needHint() or self.score:
    self.requestHint.emit(self.fen())
  else:
   self.pressedPiece.setPos(self.getScenePos(releasedSquareId))
  self.pressedPiece = None
  self.draw_warnOfDanger()

