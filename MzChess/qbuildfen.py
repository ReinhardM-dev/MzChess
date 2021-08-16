from typing import Optional,  Callable,  List
import os
import sys

import Ui_buildFen

import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.QtSvg

import chess, chess.pgn
import MzChess
import AboutDialog
from installLeipFont import installLeipFont

class BuildFenClass(PyQt5.QtWidgets.QMainWindow, Ui_buildFen.Ui_MainWindow):
 '''The *chessboard* is based on Qt's QGraphicsView.
 '''

 def __init__(self, parent = None) -> None:
  super(BuildFenClass, self).__init__(parent)
  self.setupUi(self)

  self.pgm = 'FEN-Builder'
  self.version = MzChess.__version__
  self.dateString = MzChess.__date__

  self.helpIndex = PyQt5.QtCore.QUrl('https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation')
 
  sbText = self.statusBar().font()
  sbText.setPointSize(12)

  self.board = chess.Board()

  self.msgBox = PyQt5.QtWidgets.QMessageBox()
  self.msgBox.setIcon(PyQt5.QtWidgets.QMessageBox.Critical)
  self.msgBox.setWindowTitle("Error ...")

  self.infoLabel = PyQt5.QtWidgets.QLabel()
  self.infoLabel.setAlignment(PyQt5.QtCore.Qt.AlignLeft)
  self.infoLabel.setFont(sbText)
  self.statusBar().addPermanentWidget(self.infoLabel, 150)
 
  sizePolicy = PyQt5.QtWidgets.QSizePolicy(PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Preferred)
  sizePolicy.setHorizontalStretch(0)
  sizePolicy.setVerticalStretch(0)
  sizePolicy.setHeightForWidth(self.castlingGroupBox.sizePolicy().hasHeightForWidth())
  self.castlingGroupBox.setSizePolicy(sizePolicy)
  self.wkCheckBox = self. _addCastlingBox(chess.WHITE, True)
  self.wqCheckBox = self. _addCastlingBox(chess.WHITE, False)
  self.bkCheckBox = self. _addCastlingBox(chess.BLACK, True)
  self.bqCheckBox = self. _addCastlingBox(chess.BLACK, False)
  
  installLeipFont()
  
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

 @PyQt5.QtCore.pyqtSlot(str)
 def notify(self, str : str) -> None:
  self.infoLabel.setText(str)
  self.infoLabel.update()
  PyQt5.QtWidgets.QApplication.processEvents()
  
 def _addCastlingBox(self, color : chess.Color, kingside : bool ) -> None:
  box = PyQt5.QtWidgets.QCheckBox(self.castlingGroupBox)
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

 def _epList(self) -> None: 
  if self.board.turn:
   rank = 4
   sgn = 1
  else:
   rank = 3
   sgn = -1
  square2PieceList = sorted(self.board.piece_map().items())
  lastSquare = None
  lastColor = None
  sqList = list()
  for square, piece in square2PieceList:
   if piece.piece_type == chess.PAWN and chess.square_rank(square) == rank:
    if lastSquare != square - 1 or piece.color == lastColor:
     lastSquare = None
    if lastSquare is None:
     lastSquare = square
     lastColor = piece.color
     continue
    if piece.color == self.board.turn:
     target = chess.square_name(lastSquare+sgn*8)
    else:
     target = chess.square_name(square+sgn*8)
    if target not in sqList:
     sqList.append(target)
  return sqList
 
 def _resetFen(self) -> None:
  self.placementBoard.resetPosition()
  if self.board.turn:
   self.wRadioButton.click()
  else:
   self.bRadioButton.click()
  validWK = self.board.kings & chess.BB_E1 > 0
  self.wkCheckBox.setChecked(validWK and self.board.rooks & chess.BB_H1 > 0)
  self.wqCheckBox.setChecked(validWK and self.board.rooks & chess.BB_A1 > 0)
  validBK = self.board.kings & chess.BB_E8 > 0
  self.bkCheckBox.setChecked(validBK and self.board.rooks & chess.BB_H8 > 0)
  self.bqCheckBox.setChecked(validBK and self.board.rooks & chess.BB_A8 > 0)
  self.enPassantListWidget.clear()
  self.enPassantListWidget.addItem('-')
  for target in self._epList():
   self.enPassantListWidget.addItem(target)
  self.moveSpinBox.setValue(self.board.halfmove_clock)
  self.clockSpinBox.setValue(self.board.fullmove_number)
  self.notify(self.board.fen())

 @PyQt5.QtCore.pyqtSlot()
 def on_actionCopy_triggered(self):
  try:
   MzChess.checkFEN(self.board)
   fen = self.board.fen()
   PyQt5.QtWidgets.QApplication.clipboard().setText(fen)
  except ValueError as err:
   self.notifyError('Improper FEN {}:\n{}'.format(fen, str(err)))
   
 @PyQt5.QtCore.pyqtSlot()
 def on_actionPaste_triggered(self):
  fen = PyQt5.QtWidgets.QApplication.clipboard().text()
  try:
   MzChess.checkFEN(fen, allowIncompleteBoard = True)
   self.board.set_fen(fen)
   self._resetFen()
  except ValueError as err:
   self.notifyError('Improper FEN {}:\n{}'.format(fen, str(err)))

 @PyQt5.QtCore.pyqtSlot()
 def on_fenChanged(self):
  self.notify(self.board.fen())
   
 @PyQt5.QtCore.pyqtSlot()
 def on_actionReset_Board_triggered(self):
  self.board.reset()
  self._resetFen()
  
 @PyQt5.QtCore.pyqtSlot()
 def on_actionClear_Board_triggered(self):
  self.board.clear()
  self._resetFen()
  
 @PyQt5.QtCore.pyqtSlot()
 def on_wRadioButton_clicked(self):
  if self.board.turn != chess.WHITE:
   self.board.turn = chess.WHITE
   self._resetFen()

 @PyQt5.QtCore.pyqtSlot()
 def on_bRadioButton_clicked(self):
  if self.board.turn != chess.BLACK:
   self.board.turn = chess.BLACK
   self._resetFen()
  
 @PyQt5.QtCore.pyqtSlot(bool)
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
  self.board.set_castling_fen(castlingString)
  self.notify(self.board.fen())
  
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QListWidgetItem)
 def on_enPassantListWidget_itemClicked(self, enPassantItem):
  enPassantSqSymbol = enPassantItem.text()
  if enPassantSqSymbol != '-':
   self.board.ep_square = chess.parse_square(enPassantItem.text())
  else:
   self.board.ep_square = None
  self.notify(self.board.fen())

 @PyQt5.QtCore.pyqtSlot(int)
 def on_moveSpinBox_valueChanged(self, moveNumber):
  self.board.fullmove_number = moveNumber
  self.notify(self.board.fen())
  
 @PyQt5.QtCore.pyqtSlot(int)
 def on_clockSpinBox_valueChanged(self, halfmoveClock):
  self.board.halfmove_clock = halfmoveClock
  self.notify(self.board.fen())

 @PyQt5.QtCore.pyqtSlot()
 def on_actionAbout_triggered(self):
  self.notify('')
  self.aboutDialog.exec()
 
 @PyQt5.QtCore.pyqtSlot()
 def on_actionHelp_triggered(self):
  self.notify('')
  PyQt5.QtGui.QDesktopServices.openUrl(self.helpIndex)

class ChessGroupBox(PyQt5.QtWidgets.QGroupBox):
 leipzigEncodeDict = {
   'P' : 'p', 'N' : 'n', 'B' : 'b', 'R' : 'r', 'Q' : 'q', 'K' : 'k',
   'p' : 'o', 'n' : 'm', 'b' : 'v', 'r' : 't', 'q' : 'w', 'k' : 'l',
 }
 colorName = ['black', 'white']

 def __init__(self, parent = None) -> None:
  super(ChessGroupBox, self).__init__(parent)
  self.font = PyQt5.QtGui.QFont()
  self.font.setFamily("Chess Leipzig")
  self.font.setPointSize(24)
  self.gridLayout = PyQt5.QtWidgets.QGridLayout(self)
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
  pushButton = PyQt5.QtWidgets.QPushButton(self)
  pushButton.setMinimumSize(PyQt5.QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setMaximumSize(PyQt5.QtCore.QSize(self.squareSize, self.squareSize))
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
   self.gridLayout.addWidget(pushButton, nPieces // 2, nPieces % 2, 1, -1, PyQt5.QtCore.Qt.AlignCenter)
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
  
 @PyQt5.QtCore.pyqtSlot()
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
  pieceDict = self.buildFenClass.board.piece_map()
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
    
 def _setBrushAndToolTip(self, pushButton : PyQt5.QtWidgets.QPushButton, square : chess.square) -> None:
  if (chess.square_rank(square) + self.flipped) % 2 == chess.square_file(square) % 2:
   pushButton.setStyleSheet("background-color: white; \n;border: none;")  
  else:
   pushButton.setStyleSheet("background-color: lightgray; \n;border: none;")  
  pushButton.setToolTip(chess.square_name(square))
  
 def _addButton(self, square : chess.square ) -> None:
  pushButton = PyQt5.QtWidgets.QPushButton(self)
  pushButton.setMinimumSize(PyQt5.QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setMaximumSize(PyQt5.QtCore.QSize(self.squareSize, self.squareSize))
  pushButton.setFont(self.font)
  pushButton.setText('')
  self._setBrushAndToolTip(pushButton, square)
  pushButton.clicked.connect(self.on_clicked)
  self.gridLayout.addWidget(pushButton, 7 - chess.square_rank(square), chess.square_file(square))
  self.button2SquareList[square] = pushButton
  self.pushButtonList.append(pushButton)

 @PyQt5.QtCore.pyqtSlot()
 def on_clicked(self):
  sendingButton = self.sender()
  square = self.button2SquareList.index(sendingButton)
  pieceDict = self.buildFenClass.board.piece_map()
  piece = self.buildFenClass.selectionBox.selectedPiece
  oldPiece = pieceDict.get(square, None)
  txt = ''
  if piece != oldPiece:
   if piece is None:
    pieceDict.pop(square, None)
   else:
    pieceDict[square] = piece
    txt = self.leipzigEncodeDict[piece.symbol()]
  try:
   newBoard = chess.Board(self.buildFenClass.board.fen())
   newBoard.set_piece_map(pieceDict)
   MzChess.checkFEN(newBoard, allowIncompleteBoard = True)
   sendingButton.setText(txt)
   self.buildFenClass.board.set_piece_map(pieceDict)
   self.buildFenClass.notify(self.buildFenClass.board.fen())
  except ValueError as err:
   self.buildFenClass.notifyError('Improper placemenent @ {}:\n{}'.format(chess.square_name(square), str(err)))
   
def showStatus(board):
 print('fen = {}'.format(board.fen()))
 for row in range(8):
  for col in range(8):
   chessSquare = chess.square(col, row)
   piece = board.piece_at(chessSquare)
   if piece is not None:
    print(' square = {}, name = {}, symbol = {}'.format(
     chessSquare, chess.square_name(chessSquare), piece.symbol()))
 for n, move in enumerate(board.move_stack):
  print('{}. {}'.format(n, move.uci()))

class MzClassApplication(PyQt5.QtWidgets.QApplication):
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
  qApp = PyQt5.QtWidgets.QApplication(sys.argv)
 chessMainWindow = BuildFenClass()
 chessMainWindow.show()
 chessMainWindow.setup()
 qApp.exec_()

def _runFenBuilder():
 print('Hello, world')

if __name__ == "__main__":
 runFenBuilder(print)
