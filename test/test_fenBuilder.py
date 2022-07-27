import pytest
from pytestqt.qt_compat import qt_api

from PyQt6 import QtCore, QtWidgets

import chess
import MzChess

@pytest.fixture
def app(qtbot):
 fenBuilder = MzChess.BuildFenClass()
 fenBuilder.show()
 fenBuilder.setup()
 qtbot.addWidget(fenBuilder)
 return fenBuilder
 
def assertCheckedButton(selectionBox : MzChess.SelectionBox, button : QtWidgets.QPushButton) -> None:
 isChecked = button.isChecked()
 for actButton in selectionBox.button2PieceDict:
  if actButton is button:
   assert isChecked
  else:
   assert not actButton.isChecked()
   
def handleNotifyError(app, qtbot, expectedMessage : str):
 print('Notify Error expected, press OK to continue ...')
 assert isinstance(app.msgBox, QtWidgets.QMessageBox), 'QMessageBox expected, {} got'.format(app.msgBox)
 assert app.msgBox.text() == expectedMessage
 okButton = app.msgBox.button(QtWidgets.QMessageBox.StandardButton.Ok)
 assert isinstance(okButton, QtWidgets.QPushButton)
 if app.msgBox.isVisible():
  qtbot.mouseClick(okButton, QtCore.Qt.MouseButton.LeftButton, delay=1)

def test_selectionBox(app, qtbot):
 assert app.selectionBox.selectedPiece is None
 print('test_selectionBox: check mouse clicks')
 for button, piece in app.selectionBox.button2PieceDict.items():
  qtbot.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)
  assert app.selectionBox.selectedButton is button
  assert app.selectionBox.selectedPiece is piece
  assertCheckedButton(app.selectionBox, button)
 return
 print('test_selectionBox: check shortcuts')
 for s in 'KQRBNP':
  qtbot.keyClicks(app.selectionBox, s)
  assert app.selectionBox.selectedPiece == chess.Piece.from_symbol(s.lower())
  qtbot.keyClicks(app.selectionBox, 'Shift+' + s)
  assert app.selectionBox.selectedPiece == chess.Piece.from_symbol(s)

def test_placementBoard(app, qtbot):
 assert app.selectionBox.selectedPiece is None
 app.wkCheckBox.setChecked(False)
 app.wqCheckBox.setChecked(False)
 app.bkCheckBox.setChecked(False)
 app.bqCheckBox.setChecked(False)
 for button in app.placementBoard.pushButtonList:
  qtbot.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)
 button =  app.selectionBox.getButton(chess.Piece.from_symbol('P'))
 qtbot.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)
 qtbot.mouseClick(app.placementBoard.pushButtonList[0], QtCore.Qt.MouseButton.LeftButton)
 handleNotifyError(app, qtbot, 'Improper placemenent @ a1:\nPawn on rank (row) 1 or 8.')

def test_exitFenBuilder():
 pytest.helpers.exitApp()
