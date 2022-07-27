from typing import Dict, Tuple, Any
import pytest

inverseLeipzigEncodeDict = dict()

from PyQt6 import QtCore

import chess, chess.pgn
import MzChess

@pytest.fixture()
def app(qtbot):
 global inverseLeipzigEncodeDict
 inverseLeipzigEncodeDict = dict()
 for key, lKey in MzChess.Game.leipzigEncodeDict.items():
  inverseLeipzigEncodeDict[lKey] = key
 mzChess = MzChess.ChessMainWindow()
 mzChess.show()
 mzChess.setup()
 qtbot.addWidget(mzChess)
 return mzChess

def materialBudget(board : chess.Board) -> str:
 pieceMap = board.piece_map()
 whiteCountList = 7 * [0]
 blackCountList = 7 * [0]
 for piece in list(pieceMap.values()):
  if piece.color == chess.WHITE:
   whiteCountList[piece.piece_type] += 1
  else:
   blackCountList[piece.piece_type] += 1
 pieceText =''
 for pieceType in range(5, 0,-1):
  delta = whiteCountList[pieceType] - blackCountList[pieceType]
  if delta == 0:
   continue
  if delta > 0:
   pieceText += delta * chess.Piece(pieceType, chess.WHITE).symbol()
  else:
   pieceText += abs(delta) * chess.encodePiece(pieceType, chess.BLACK).symbol()
 return pieceText
  
def makeMove(app, qtbot, 
                      move : chess.Move, 
                      breakAfterPress : bool = False, 
                      breakAfterRelease : bool = False, 
                      relDeltaPercent : Tuple[bool, QtCore.QPoint] = (False, QtCore.QPoint()),  
                      expectedResultDict : Dict[str, Any] = dict()) -> None:
 global inverseLeipzigEncodeDict
 gv = app.boardGraphicsView.viewport()
 gameScene = app.boardGraphicsView.game
 if relDeltaPercent[0]:
  delta = (0.01 * gameScene.pieceSize) * relDeltaPercent[1]
 else:
  delta = QtCore.QPoint()
 fromPoint = gameScene.getScenePos(move.from_square).toPoint() + delta
 qtbot.mousePress(gv, QtCore.Qt.MouseButton.LeftButton, pos = app.boardGraphicsView.mapFromScene(fromPoint))
 if breakAfterPress:
  breakpoint()
 if relDeltaPercent[0]:
  delta = QtCore.QPoint()
 else:
  delta = (0.01 * gameScene.pieceSize) * relDeltaPercent[1]
 toPoint = gameScene.getScenePos(move.to_square).toPoint() + delta
 qtbot.mouseRelease(gv, QtCore.Qt.MouseButton.LeftButton, pos = app.boardGraphicsView.mapFromScene(toPoint))
 QtCore.QCoreApplication.processEvents()
 if breakAfterRelease:
  breakpoint()
 if 'FEN' in expectedResultDict:
  assert expectedResultDict['FEN'] == app.gameNode.board().fen()
 if 'Material' in expectedResultDict:
  pieceText =''
  for char in gameScene.materialLabel.text():
   pieceText += inverseLeipzigEncodeDict[char]
  for char in 'QRBKPqrbkp':
   assert expectedResultDict['Material'].count(char) == pieceText.count(char)
 if 'Color' in expectedResultDict:
  board = app.gameNode.board()
  if board.is_game_over():
   next = None
  else:
   next = board.turn
  assert expectedResultDict['Color'] == next
 
def runPromoteMate(app, qtbot, promoteMateGame : chess.pgn.Game) -> None:
 app.actionNew_Game.triggered.emit()
 expectedResultDict = dict()
 gameNode = promoteMateGame.next()
 print('You must promote a queen for this example.')
 while gameNode is not None:
  board = gameNode.board()
  expectedResultDict['Material'] = materialBudget(board)
  expectedResultDict['FEN'] = board.fen()
  if gameNode.board().is_game_over():
   expectedResultDict['Color'] = None
  else:
   expectedResultDict['Color'] = gameNode.turn()
  makeMove(app, qtbot, gameNode.move, 
                        breakAfterPress = app.actionShow_Options.isChecked(), 
                        breakAfterRelease = app.actionWarn_of_Danger.isChecked(), 
                        expectedResultDict = expectedResultDict)
  gameNode = gameNode.next()

def test_promoteMate1(app, qtbot, promoteMateGame : chess.pgn.Game) -> None:
 app.actionFlip_Board.setChecked(False)
 app.actionShow_Options.setChecked(True)
 app.actionWarn_of_Danger.setChecked(False)
 runPromoteMate(app, qtbot, promoteMateGame)
 
def test_promoteMate2(app, qtbot, promoteMateGame : chess.pgn.Game) -> None:
 app.actionFlip_Board.setChecked(True)
 app.actionShow_Options.setChecked(False)
 app.actionWarn_of_Danger.setChecked(True)
 runPromoteMate(app, qtbot, promoteMateGame)
 
def mouseOp(app, qtbot, analyzePress : bool) -> None:
 app.actionNew_Game.triggered.emit()
 mouseOpStr = ('mouseReleaseEvent', 'mousePressEvent')
 nPoints = 3
 expectedResultDict = {'FEN' : 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1'}
 gameScene = app.boardGraphicsView.game
 squarePos = gameScene.getScenePos(chess.parse_square('e2'))
 print('{}: pos(e2) = {}'.format(mouseOpStr[analyzePress], squarePos))
 expectedResultDict = {}
 for nx in range(nPoints):
  for ny in range(nPoints):
   relDeltaPercent = QtCore.QPoint((100 * nx) // nPoints, (100 * ny) // nPoints)
   delta = (0.01 * gameScene.pieceSize) * relDeltaPercent
   print('{}: actPos = {}'.format((nx, ny), squarePos + delta))
   makeMove(app, qtbot, chess.Move.from_uci('e2e4'), 
                   breakAfterPress = False, 
                   breakAfterRelease = False, 
                   relDeltaPercent = (analyzePress, relDeltaPercent), 
                   expectedResultDict = expectedResultDict)
   app.actionUndo_Last_Move.triggered.emit()

def test_mousePress(app, qtbot, promoteMateGame : chess.pgn.Game) -> None:
 mouseOp(app, qtbot, False)

def test_mouseRelease(app, qtbot, promoteMateGame : chess.pgn.Game) -> None:
 mouseOp(app, qtbot, False)

def test_exitMzChess():
 pytest.helpers.exitApp()
