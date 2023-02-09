'''
|BuildFEN| 

The FEN-Builder is an extra tool which can be started from the main window of the chess GUI.
It allows to populate all items of the position by using the Forsyth-Edwards Notation (`FEN`_).
It consists of 7 parts:

    * *Board* displaying the current position
    * *Pieces* displaying the pieces to be placed and the X piece for deletion
    * *Next to Move* indicating the next player to move
    * *Castling* indicating the rights to castle
    * *En Passant* displaying the target square of an en passant move
    * *Move* indicating the number of full-moves of the current game
    * *Clock* indicating the number of half-moves since the last capture or pawn advance, see fifty-move rule (`FMR`_)
    
.. |BuildFEN| image:: buildFEN.png
  :width: 800
  :alt: Build FEN Window
.. _FEN: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
.. _FMR: https://en.wikipedia.org/wiki/Fifty-move_rule
'''

from typing import Optional,  Callable,  List
import sys, os, os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MzChess import Position

try:
 from PyQt6 import QtWidgets, QtGui, QtCore
 from PyQt6 import uic
 import PyQt6.QtSvgWidgets
 import PyQt6.QtCharts
except:
 try:
  from PyQt5 import QtWidgets, QtGui, QtCore
  from PyQt5 import uic
  import PyQt5.QtSvg
  import PyQt5.QtChart
 except:
  raise ModuleNotFoundError('Neither the required PyQt6 nor PyQt5 modules installed')

import chess, chess.pgn
import MzChess
import AboutDialog
from installLeipFont import installLeipFont

class BuildFenClass(QtWidgets.QMainWindow):
 '''The *chessboard* is based on Qt's QGraphicsView.
 '''

 def __init__(self, parent = None) -> None:
  super(BuildFenClass, self).__init__(parent)
  installLeipFont()
  fileDirectory = os.path.dirname(os.path.abspath(__file__))
  uic.loadUi(os.path.join(fileDirectory, 'buildFen.ui'), self)

  self.pgm = 'FEN-Builder'
  self.version = MzChess.__version__
  self.dateString = MzChess.__date__

  self.helpIndex = QtCore.QUrl('https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation')
 
  sbText = self.statusBar().font()
  sbText.setPointSize(12)

  self.position = MzChess.Position()

  self.msgBox = QtWidgets.QMessageBox()
  self.msgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
  self.msgBox.setWindowTitle("Error ...")

  self.infoLabel = QtWidgets.QLabel()
  self.infoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
  self.infoLabel.setFont(sbText)
  self.statusBar().addPermanentWidget(self.infoLabel, 150)
 
  sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
  sizePolicy.setHorizontalStretch(0)
  sizePolicy.setVerticalStretch(0)
  sizePolicy.setHeightForWidth(self.castlingGroupBox.sizePolicy().hasHeightForWidth())
  self.castlingGroupBox.setSizePolicy(sizePolicy)
  if True:
   self.wkCheckBox.toggled.connect(self.on_castlingCheckBox_toggled)
   self.wqCheckBox.toggled.connect(self.on_castlingCheckBox_toggled)
   self.bkCheckBox.toggled.connect(self.on_castlingCheckBox_toggled)
   self.bqCheckBox.toggled.connect(self.on_castlingCheckBox_toggled)
  else:
   self.wkCheckBox = self. _addCastlingBox(chess.WHITE, True)
   self.wqCheckBox = self. _addCastlingBox(chess.WHITE, False)
   self.bkCheckBox = self. _addCastlingBox(chess.BLACK, True)
   self.bqCheckBox = self. _addCastlingBox(chess.BLACK, False)
  
  self.aboutDialog = AboutDialog.AboutDialog()
  self.aboutDialog.setup(
   pgm = self.pgm, 
   version = self.version, 
   dateString = self.dateString)

 def setup(self) -> None:
  self.selectionBox.setup()
  self.placementBoard.setup(self)
  self._resetFen()
  
 def notifyError(self, str : str) -> None:
  self.msgBox.setText(str)
  self.msgBox.exec()

 @QtCore.pyqtSlot(str)
 def notify(self, str : str) -> None:
  self.infoLabel.setText(str)
  self.infoLabel.update()
  QtWidgets.QApplication.processEvents()
  
 def _addCastlingBox(self, color : chess.Color, kingside : bool ) -> None:
  box = QtWidgets.QCheckBox(self.castlingGroupBox)
  box.toggled.connect(self.on_castlingCheckBox_toggled)
  if color == chess.BLACK:
   box.setStyleSheet('background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);')
  if kingside:
   box.setText('O-O')
  else:
   box.setText('O-O-O')
  box.setChecked(False)
  self.castlingGroupBox.layout().addWidget(box)
  return box

 def _resetFen(self) -> None:
  self.placementBoard.resetPosition()
  if self.position.turn:
   self.wRadioButton.click()
  else:
   self.bRadioButton.click()
  validWK = self.position.kings & chess.BB_E1 > 0
  self.wkCheckBox.setChecked(validWK and self.position.rooks & chess.BB_H1 > 0)
  self.wqCheckBox.setChecked(validWK and self.position.rooks & chess.BB_A1 > 0)
  validBK = self.position.kings & chess.BB_E8 > 0
  self.bkCheckBox.setChecked(validBK and self.position.rooks & chess.BB_H8 > 0)
  self.bqCheckBox.setChecked(validBK and self.position.rooks & chess.BB_A8 > 0)
  self.moveSpinBox.setValue(self.position.halfmove_clock)
  self.clockSpinBox.setValue(self.position.fullmove_number)
  self.notify(self.position.fen())
  epSquares = list(self.position.potentialEnPassantSquares(self.position.turn))
  self.enPassantListWidget.clear()
  self.enPassantListWidget.addItem('-')
  selIndex = 0
  for index,  square in enumerate(epSquares):
   self.enPassantListWidget.addItem(chess.square_name(square))
   if square == self.position.ep_square:
    selIndex = index + 1
  self.enPassantListWidget.setCurrentRow(selIndex)
  self.notify(self.position.fen())

 @QtCore.pyqtSlot()
 def on_actionCopy_triggered(self):
  try:
   MzChess.checkFEN(self.position, allowIncompleteBoard = True)
   fen = self.position.fen(en_passant = 'fen')
   QtWidgets.QApplication.clipboard().setText(fen)
  except ValueError as err:
   self.notifyError('Improper FEN {}:\n{}'.format(fen, str(err)))
   return
   
 @QtCore.pyqtSlot()
 def on_actionPaste_triggered(self):
  fen = QtWidgets.QApplication.clipboard().text()
  try:
   MzChess.checkFEN(fen, allowIncompleteBoard = True)
   self.position.set_fen(fen)
   self._resetFen()
  except ValueError as err:
   self.notifyError('Improper FEN {}:\n{}'.format(fen, str(err)))
   return

 @QtCore.pyqtSlot()
 def on_actionResetBoard_triggered(self):
  self.position.reset()
  self._resetFen()
  
 @QtCore.pyqtSlot()
 def on_actionClearBoard_triggered(self):
  self.position.clear()
  self._resetFen()
  
 @QtCore.pyqtSlot()
 def on_wRadioButton_clicked(self):
  if self.position.turn != chess.WHITE:
   self.position.turn = chess.WHITE
   self._resetFen()

 @QtCore.pyqtSlot()
 def on_bRadioButton_clicked(self):
  if self.position.turn != chess.BLACK:
   self.position.turn = chess.BLACK
   self._resetFen()
  
 @QtCore.pyqtSlot(bool)
 def on_castlingCheckBox_toggled(self, checked):
  if    'wkCheckBox' not in vars(self) \
    or 'wqCheckBox' not in vars(self) \
    or 'bkCheckBox' not in vars(self) \
    or 'bqCheckBox' not in vars(self):
    return
  castlingString = ''
  if self.wkCheckBox.isChecked():
   castlingString += 'K'
  if self.wqCheckBox.isChecked():
   castlingString += 'Q'
  if self.bkCheckBox.isChecked():
   castlingString += 'k'
  if self.bqCheckBox.isChecked():
   castlingString += 'q'
  if len(castlingString) == 0:
   castlingString = '-'
  self.position.set_castling_fen(castlingString)
  self.notify(self.position.fen(en_passant = 'fen'))
  
 @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
 def on_enPassantListWidget_itemClicked(self, enPassantItem):
  fenList = self.position.fen().split(' ')
  fenList[3] = enPassantItem.text()
  self.position.set_fen(' '.join(fenList))
  self.notify(self.position.fen(en_passant = 'fen'))

 @QtCore.pyqtSlot(int)
 def on_moveSpinBox_valueChanged(self, moveNumber):
  self.position.fullmove_number = moveNumber
  self.notify(self.position.fen(en_passant = 'fen'))
  
 @QtCore.pyqtSlot(int)
 def on_clockSpinBox_valueChanged(self, halfmoveClock):
  self.position.halfmove_clock = halfmoveClock
  self.notify(self.position.fen(en_passant = 'fen'))

 @QtCore.pyqtSlot()
 def on_actionAbout_triggered(self):
  self.notify('')
  self.aboutDialog.exec()
 
 @QtCore.pyqtSlot()
 def on_actionHelp_triggered(self):
  self.notify('')
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
  
class SelectionBox(ChessGroupBox):

 def __init__(self, parent = None) -> None:
  super(SelectionBox, self).__init__(parent)
  self.button2PieceDict = dict()
  self.selectedPiece = None
  self.selectedButton = None

 def setup(self):
  self.pushButtonList = list()
  for s in 'KkQqRrBbNnPp':
   self._addButton(chess.Piece.from_symbol(s))
  self._addButton(None)
  
 def getButton(self, piece = Optional[chess.Piece]):
  for button, actPiece in self.button2PieceDict.items():
   if actPiece == piece:
    return button
   
 def _addButton(self, piece : Optional[chess.Piece] ) -> None:
  pushButton = QtWidgets.QPushButton(self)
  pushButton.setMinimumSize(QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setMaximumSize(QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setCheckable(True)
  pushButton.setFont(self.font)
  nPieces = len(self.button2PieceDict)
  self.button2PieceDict[pushButton] = piece
  if piece is None:
   pushButton.setChecked(True)
   pushButton.setText('x')
   pushButton.setShortcut('x')   
   pushButton.setToolTip('remove piece')
   self.selectedButton = pushButton
   self.gridLayout.addWidget(pushButton, nPieces // 2, nPieces % 2, 1, -1, QtCore.Qt.AlignmentFlag.AlignCenter)
  else:
   pushButton.setChecked(False)
   pushButton.setText(self.leipzigEncodeDict[piece.symbol()])
   if piece.color:
    sc = 'Shift+'
   else:
    sc = ''
   sc += piece.symbol().upper()
   pushButton.setShortcut(sc)   
   pushButton.setToolTip('{} {}'.format(self.colorName[piece.color], chess.piece_name(piece.piece_type)))
   self.gridLayout.addWidget(pushButton, nPieces // 2, nPieces % 2)
  pushButton.clicked.connect(self.on_clicked)
  pushButton.clicked.connect(self.on_clicked)
  self.pushButtonList.append(pushButton)
  
 @QtCore.pyqtSlot()
 def on_clicked(self):
  self.selectedButton.setChecked(False)
  self.selectedButton = self.sender()
  self.selectedPiece = self.button2PieceDict[self.selectedButton]
  self.sender().setChecked(True)

class PlacementBoard(ChessGroupBox):

 def __init__(self, parent = None) -> None:
  super(PlacementBoard, self).__init__(parent)
  self.gridLayout.setSpacing(0)
  self.button2SquareList = 64 * [None]
  self.flipped = False
 
 def setup(self, buildFenClass : BuildFenClass):
  self.buildFenClass = buildFenClass
  self.pushButtonList = list()
  for square in range(64):
   self._addButton(square)
  
 def resetPosition(self):
  pieceDict = self.buildFenClass.position.piece_map()
  for square, pushButton in enumerate(self.button2SquareList):
   if square in pieceDict:
    pushButton.setText(self.leipzigEncodeDict[pieceDict[square].symbol()])
   else:
    pushButton.setText('') 

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
   pushButton.setStyleSheet("background-color: lightgray; \n;border: none;")  
  else:
   pushButton.setStyleSheet("background-color: white; \n;border: none;")  
  pushButton.setToolTip(chess.square_name(square))
  
 def _addButton(self, square : chess.square ) -> None:
  pushButton = QtWidgets.QPushButton(self)
  pushButton.setMinimumSize(QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setMaximumSize(QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setFont(self.font)
  pushButton.setText('')
  self._setBrushAndToolTip(pushButton, square)
  pushButton.clicked.connect(self.on_clicked)
  self.gridLayout.addWidget(pushButton, 7 - chess.square_rank(square), chess.square_file(square))
  self.button2SquareList[square] = pushButton
  self.pushButtonList.append(pushButton)

 @QtCore.pyqtSlot()
 def on_clicked(self):
  sendingButton = self.sender()
  square = self.button2SquareList.index(sendingButton)
  pieceDict = self.buildFenClass.position.piece_map()
  piece = self.buildFenClass.selectionBox.selectedPiece
  oldPiece = pieceDict.get(square, None)
  txt = ''
  if piece != oldPiece:
   if piece is None:
    pieceDict.pop(square, None)
   else:
    pieceDict[square] = piece
    txt = self.leipzigEncodeDict[piece.symbol()]
  else:
   return
  try:
   newBoard = MzChess.Position(self.buildFenClass.position.fen(en_passant = 'fen'))
   newBoard.set_piece_map(pieceDict)
   MzChess.checkFEN(newBoard, allowIncompleteBoard = True)
   sendingButton.setText(txt)
   self.buildFenClass.position.set_piece_map(pieceDict)
   self.buildFenClass._resetFen()
  except ValueError as err:
   self.buildFenClass.notifyError('Improper placement @ {}:\n{}'.format(chess.square_name(square), str(err)))
   return
   
def showStatus(position):
 print('fen = {}'.format(position.fen(en_passant = 'fen')))
 for row in range(8):
  for col in range(8):
   chessSquare = chess.square(col, row)
   piece = position.piece_at(chessSquare)
   if piece is not None:
    print(' square = {}, name = {}, symbol = {}'.format(
     chessSquare, chess.square_name(chessSquare), piece.symbol()))
 for n, move in enumerate(position.move_stack):
  print('{}. {}'.format(n, move.uci()))

class MzClassApplication(QtWidgets.QApplication):
 def __init__(self, argv : List[str], notifyFct : Callable[[str], None] = print) -> None: 
  super(MzClassApplication, self).__init__(argv)
  self.notifyFct = notifyFct

 def notify(self, rec, ev):
  rc = super(MzClassApplication, self).notify(rec, ev)
  #self.notifyFct('{} -> Type(Event)= {}, handled = {}'.format(rec, ev.type(),  rc))
  return rc

def runFenBuilder(notifyFct : Optional[Callable[[str], None]] = None):
 os.chdir(os.path.expanduser('~'))
 if notifyFct is not None:
  qApp = MzClassApplication(sys.argv)
 else:
  qApp = QtWidgets.QApplication(sys.argv)
 chessMainWindow = BuildFenClass()
 chessMainWindow.show()
 chessMainWindow.setup()
 qApp.exec()

def _runFenBuilder():
 print('Hello, world')

if __name__ == "__main__":
 runFenBuilder(print)
