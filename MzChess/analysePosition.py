'''
Position-Analyser
================================
|PositionAnalyser| 

The Position-Analyser is an extra tool which can be started from the main window of the chess GUI.
It allows to analyse the position using some properties shown in the chess programming website (`CPE`_).
It consists of the *Board* displaying the current position and the several properties of the position with the:

    * *Attacked pieces* 
    * *Attacking pieces*
    * *Bad bishops*, i.e. bishops whose mobility is restricted by own pawns
    * *Blocked pawns*, i.e. pawns blocked by a pawn of opposite color
    * *Controlled central squares*, i.e. control over the center squares (E4, E5, D4, D5)
    * *Fiancettoed bishops*, i.e. bishops on knight pawn squares
    * *Hanging pieces*, i.e. pieces being undefended and attacked
    * *Isolated pawns*, i.e. pawns without supporting pawns in the adjacent files
    * *Passed pawns*, i.e. pawns which cannot be attacked by pawns of opposite color anymore
    * *Pinned pieces*, i.e. pieces required at the current square to protect the king
    * *Reachable Squares*, is an indicator of the piece mobility
    * *Stacked pawns*, i.e. multiple pawns on a single file
    * *Supported pawns*, i.e. pawns protected by pawns in the adjacent files
    * *Trapped pieces*, i.e. pieces that cannot move anymore
    * *Undefended pieces*, i.e. pieces which are not defended irrespective whether they are attacked
    
By selecting a color for a property, the corresponding pieces are highlighted on the board. The highlight color

    * *green* for positive properties
    * *yellow* for neutral properties
    * *red* for negative properties
    
indicates the valuation of the position.
    
.. |PositionAnalyser| image:: positionAnalyser.png
  :width: 800
  :alt: Analyse Position Window
.. _CPE: https://www.chessprogramming.org/Evaluation
'''

from typing import Optional,  Callable, Tuple,  List
import sys, os, os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
 from PyQt6 import QtWidgets, QtGui, QtCore
 from PyQt6 import uic
except:
 try:
  from PyQt5 import QtWidgets, QtGui, QtCore
  from PyQt5 import uic
 except:
  raise ModuleNotFoundError('Neither the required PyQt6 nor PyQt5 modules installed')

import chess, chess.pgn
import MzChess
import AboutDialog
from installLeipFont import installLeipFont

class AnalysePositionClass(QtWidgets.QMainWindow):
 '''The *chessboard* is based on Qt's QGraphicsView.
 '''

 def __init__(self, parent = None) -> None:
  super(AnalysePositionClass, self).__init__(parent)
  installLeipFont()
  fileDirectory = os.path.dirname(os.path.abspath(__file__))
  uic.loadUi(os.path.join(fileDirectory, 'analysePosition.ui'), self)

  self.pgm = 'Position Analyser'
  self.version = MzChess.__version__
  self.dateString = MzChess.__date__

  self.helpIndex = QtCore.QUrl('https://www.chessprogramming.org/Evaluation')
 
  sbText = self.statusBar().font()
  sbText.setPointSize(12)

  self.position = MzChess.Position()

  self.msgBox = QtWidgets.QMessageBox()
  self.msgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
  self.msgBox.setWindowTitle("Error ...")

  self.moveLabel = QtWidgets.QLabel()
  self.moveLabel.setFont(sbText)
  self.moveLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.moveLabel.setToolTip("Total Moves/Half-moves since the last capture or pawn move")
  self.statusBar().addWidget(self.moveLabel, 50)
  self.scoreLabel = QtWidgets.QLabel()
  self.scoreLabel.setFont(sbText)
  self.scoreLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.scoreLabel.setToolTip("Material Score/Simple Position Score [centipawn]")
  self.statusBar().addWidget(self.scoreLabel, 50)
  self.winLabel = QtWidgets.QLabel()
  self.winLabel.setFont(sbText)
  self.winLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.winLabel.setToolTip("Probability for WHITE to win")
  self.statusBar().addWidget(self.winLabel, 20)
 
  self.aboutDialog = AboutDialog.AboutDialog()
  self.aboutDialog.setup(
   pgm = self.pgm, 
   version = self.version, 
   dateString = self.dateString)

 def setup(self) -> None:
  self.placementBoard.setup(self.materialLabel, self.turnFrame)
  self.propertyTableWidget.setup(self.placementBoard)

 def notifyError(self, str : str) -> None:
  self.msgBox.setText(str)
  self.msgBox.exec()

 @QtCore.pyqtSlot(str)
 def notify(self, str : str) -> None:
  self.infoLabel.setText(str)
  self.infoLabel.update()
  QtWidgets.QApplication.processEvents()
  
 @QtCore.pyqtSlot()
 def on_actionCopy_triggered(self):
  try:
   fen = self.position.fen(en_passant = 'fen')
   QtWidgets.QApplication.clipboard().setText(fen)
  except ValueError as err:
   self.notifyError('Improper FEN {}:\n{}'.format(fen, str(err)))
   return
   
 @QtCore.pyqtSlot()
 def on_actionPaste_triggered(self):
  self.setFen(QtWidgets.QApplication.clipboard().text())
  
 def setFen(self, fen : str) -> None:
  try:
   self.position.set_fen(fen)
   self.placementBoard.setPosition(self.position)
   self.propertyTableWidget.setPosition(self.position)
   self.moveLabel.setText('{}/{}'.format(self.position.fullmove_number, self.position.halfmove_clock))
   self.scoreLabel.setText('{}/{}'.format(self.position.materialScore(chess.WHITE), self.position.simplePositionScore(chess.WHITE)))
   self.winLabel.setText('{}%'.format(int(100*self.position.winningProbability())))
  except ValueError as err:
   self.notifyError('Improper FEN {}:\n{}'.format(fen, str(err)))
   return

 @QtCore.pyqtSlot()
 def on_actionAbout_triggered(self):
  self.aboutDialog.exec()
 
 @QtCore.pyqtSlot()
 def on_actionHelp_triggered(self):
  QtGui.QDesktopServices.openUrl(self.helpIndex)
  

class ChessGroupBox(QtWidgets.QGroupBox):
 leipzigEncodeDict = {
   'P' : 'p', 'N' : 'n', 'B' : 'b', 'R' : 'r', 'Q' : 'q', 'K' : 'k',
   'p' : 'o', 'n' : 'm', 'b' : 'v', 'r' : 't', 'q' : 'w', 'k' : 'l',
 }
 colorName = ['black', 'white']

 def __init__(self, parent = None) -> None:
  super(ChessGroupBox, self).__init__(parent)
  self.font = QtGui.QFont()
  self.font.setFamily("Chess Leipzig")
  self.font.setPointSize(24)
  self.gridLayout = QtWidgets.QGridLayout(self)
  self.gridLayout.setContentsMargins(5, 5, 5, 5)
  self.squareSize = 40
  
class PlacementBoard(ChessGroupBox):
 whiteSquare = "background-color: white; \n;border: none;"
 blackSquare = "background-color: lightgray; \n;border: none;"
 goodSquare = "background-color: green; \n;border: none;"
 badSquare = "background-color: red; \n;border: none;"
 neutralSquare = "background-color: yellow; \n;border: none;"

 def __init__(self, parent = None) -> None:
  super(PlacementBoard, self).__init__(parent)
  self.materialLabel = None
  self.turnFrame = None
  self.gridLayout.setSpacing(0)
  self.button2SquareList = 64 * [None]
  self.flipped = False
 
 def setup(self, materialLabel : QtWidgets.QLabel, turnFrame : QtWidgets.QFrame ) -> None:
  self.turnFrame = turnFrame
  self.materialLabel = materialLabel
  self.position = MzChess.Position()
  self.pushButtonList = list()
  for square in range(64):
   self._addButton(square)
  
 def setFlipped(self, flipped : bool):
  if self.flipped != flipped:
   for square in range(32):
    flippedSquare = square ^ 0x38
    tmp = self.button2SquareList[flippedSquare]
    self.button2SquareList[flippedSquare] = self.button2SquareList[square]
    self.button2SquareList[square] = tmp
    self._setBrushAndToolTip(self.button2SquareList[square], square)
    self._setBrushAndToolTip(self.button2SquareList[flippedSquare], flippedSquare)
    
 def _setBrushAndToolTip(self, pushButton : QtWidgets.QPushButton, square : chess.square) -> None:
  if (chess.square_rank(square) + self.flipped) % 2 == chess.square_file(square) % 2:
   pushButton.setStyleSheet(self.blackSquare)  
  else:
   pushButton.setStyleSheet(self.whiteSquare)  
  pushButton.setToolTip(chess.square_name(square))
  
 def _addButton(self, square : chess.square ) -> None:
  pushButton = QtWidgets.QPushButton(self)
  pushButton.setMinimumSize(QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setMaximumSize(QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setFont(self.font)
  pushButton.setText('')
  self._setBrushAndToolTip(pushButton, square)
  pushButton.installEventFilter(self)
  self.gridLayout.addWidget(pushButton, 7 - chess.square_rank(square), chess.square_file(square))
  self.button2SquareList[square] = pushButton
  self.pushButtonList.append(pushButton)
 
 def setPosition(self, position : MzChess.Position) -> None:
  self.position = position
  for square in chess.SQUARES:
   piece = self.position[square]
   if piece is not None:
    self.pushButtonList[square].setText(self.leipzigEncodeDict[piece.symbol()])
   else:
    self.pushButtonList[square].setText('')
  self._showMaterial()
  self._showTurn()

 def _showMaterial(self) -> None:
  if self.materialLabel is None:
   return
  self.materialLabel.setFont(QtGui.QFont("Chess Leipzig", 20))
  encodePiece = lambda piece_type, color : self.leipzigEncodeDict[chess.Piece(piece_type, color).symbol()]
  pieceMap = self.position.piece_map()
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
    piece_text += delta * encodePiece(piece_type, chess.WHITE)
   else:
    piece_text += abs(delta) * encodePiece(piece_type, chess.BLACK)
  self.materialLabel.setText(piece_text)

 def _showTurn(self) -> None:
  if self.turnFrame is None:
   return
  self.gameIsOver = self.position.is_game_over()
  border = ' border-color: black; border-style: solid; border-width: 1px;'
  if self.gameIsOver:
   if self.position.is_checkmate():
    self.turnFrame.setStyleSheet('background-color: red;' + border)
   else:
    self.turnFrame.setStyleSheet('background-color: yellow;' + border)
  elif self.position.turn:
   self.turnFrame.setStyleSheet('background-color: white;' + border)
  else:
   self.turnFrame.setStyleSheet('background-color: black;')

 def highlightSquareSet(self, highlightSquareSetTuple : Optional[Tuple[str, chess.SquareSet]]) -> None:
  if highlightSquareSetTuple is not None:
   highlightKey, squareSet = highlightSquareSetTuple
   if highlightKey is not None:
    if highlightKey == '+':
     highlightedSquare = self.goodSquare
    elif highlightKey == '-':
     highlightedSquare = self.badSquare
    else:
     highlightedSquare = self.neutralSquare
  else:
   squareSet = chess.SquareSet()
  for square in chess.SQUARES:
   if square in squareSet:
    self.pushButtonList[square].setStyleSheet(highlightedSquare)
   elif (chess.square_rank(square) + self.flipped) % 2 == chess.square_file(square) % 2:
    self.pushButtonList[square].setStyleSheet(self.blackSquare)  
   else:
    self.pushButtonList[square].setStyleSheet(self.whiteSquare)  

 def eventFilter(self, pushButton : QtCore.QObject, ev : QtCore.QEvent) -> bool:
  evType = ev.type()
  
  if pushButton in self.pushButtonList \
   and (evType == QtCore.QEvent.Type.MouseButtonPress \
    or    evType == QtCore.QEvent.Type.MouseButtonRelease):
   square = self.pushButtonList.index(pushButton)
   piece = self.position[square]
   if not (piece is None or square in self.position.pinnedPieces(piece.color)):
    if evType == QtCore.QEvent.Type.MouseButtonPress:
     attackedSquares = list(self.position.attacks(square) & ~self.position._bitboards[piece.color][chess.ALL])
     defendedSquares = self.position.defendedPieces(not piece.color)
     for actSquare in attackedSquares:
      if actSquare in defendedSquares or self.position.is_attacked_by(not piece.color, actSquare):
       highlightedSquare = self.badSquare
      else:
       highlightedSquare = self.goodSquare
      self.pushButtonList[actSquare].setStyleSheet(highlightedSquare)
     print('MouseButtonPress, square = {}'.format(square))
    elif evType == QtCore.QEvent.Type.MouseButtonRelease:
     self.highlightSquareSet(None)
     print('MouseButtonRelease, square = {}'.format(square))
  return super(PlacementBoard, self).eventFilter(pushButton, ev)
   
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

class PositionPropertyTable(QtWidgets.QTableWidget):
 
 def __init__(self, parent = None) -> None:
  super(PositionPropertyTable, self).__init__(parent)
  self.setColumnCount(3)
  self.selectionModel().currentChanged.connect(self.on_currentChanged)
  hHeader = self.horizontalHeader()
  hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
  hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Fixed)
  hHeader.resizeSection(1, 50)
  hHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Fixed)
  hHeader.resizeSection(2, 50)
  
 def setup(self, placementBoard : PlacementBoard)-> None:
  self.placementBoard = placementBoard
  
 def setPosition(self, position : Optional[MzChess.Position]) -> None:
  self.clearContents()
  if position is None:
   return
  self.setRowCount(len(position.squareSetMethodDict))
  for row, key in enumerate(position.squareSetMethodDict):
   method = getattr(position, position.squareSetMethodDict[key][1:])
   highlightedKey = position.squareSetMethodDict[key][0]
   keyItem = QtWidgets.QTableWidgetItem(key)
   keyItem.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
   self.setItem(row, 0, keyItem)
   for column, color in enumerate([chess.WHITE, chess.BLACK]):
    item = QtWidgets.QTableWidgetItem(str(len(method(color))))
    item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
    item.setData(QtCore.Qt.ItemDataRole.UserRole, (highlightedKey, method(color)))
    self.setItem(row, column +1, item)
  self.show()
    
 def on_currentChanged(self, index : QtCore.QModelIndex) -> None:
  if index.isValid():
   item = self.itemFromIndex(index)
   self.placementBoard.highlightSquareSet(item.data(QtCore.Qt.ItemDataRole.UserRole))

class MzClassApplication(QtWidgets.QApplication):
 def __init__(self, argv : List[str], notifyFct : Callable[[str], None] = print) -> None: 
  super(MzClassApplication, self).__init__(argv)
  self.notifyFct = notifyFct

 def notify(self, rec, ev):
  rc = super(MzClassApplication, self).notify(rec, ev)
  #self.notifyFct('{} -> Type(Event)= {}, handled = {}'.format(rec, ev.type(),  rc))
  return rc

def runAnalysePosition(notifyFct : Optional[Callable[[str], None]] = None):
 os.chdir(os.path.expanduser('~'))
 if notifyFct is not None:
  qApp = MzClassApplication(sys.argv)
 else:
  qApp = QtWidgets.QApplication(sys.argv)
 chessMainWindow = AnalysePositionClass()
 chessMainWindow.show()
 chessMainWindow.setup()
 if len(sys.argv) > 1:
  chessMainWindow.setFen(sys.argv[1])
 qApp.exec()

if __name__ == "__main__":
 runAnalysePosition(print)

