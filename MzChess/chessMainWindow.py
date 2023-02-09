'''
Main Window of the Chess GUI
================================
|MainWindow| 

The main Window consists of 4 parts:

 * On the left, the *game board* with the *material* and *next turn* labels. The *next turn* may 4 colors ``white``, ``black``, ``red`` (mate), ``yellow`` (draw)
 * On the right, the TAB widget with the
    
    * *Game* tree widget displaying the body of the actual game
    * *Headers* list widget displaying the header of the actual game
    * *Database* list widget displaying all loaded games
    * *Score* plot displaying engine and material scores
    * *Log* edit displaying communication with the engine in use
    
 * On the bottom, the status bar with the labels

    * *info/error* displaying information or errors
    * *engine* displaying the engine in use
    * *hint/score* displaying the hint and score computed by the engine
    * *ECO code* displaying the eco code of the current opening, the hint shows the full opening string
    * *square* displaying the square under the cursor within the board

Main Window Menu
================================
On the top, the menu with

 * *File* menu handling files in the Portable Game Notation (`PGN`_) and pickled PGN (*PPNG*) formats

    * *Encoding* sub-menu to set encoding for opening/saveing PNG-format
    * *Open DB ...* action to open a PPGN- or PGN-file and replace the current database
    * *Recent* sub-menu with the recent PPGN- or PGN-files
    * *Append to DB ...* action to open a PPGN- or PGN-file and append to the current database
    * *Save DB ...* action to save the whole database as a PPGN- or PGN-file 
    * *Save Game ...* action to save the actual game as a PGN-file 
    * *Exit* action to terminate the GUI

 * *Edit* menu with obvious functionality with the exception of
 
    * *Copy Game*, i.e. the actual game PGN is copied to the clipboard
    * *Copy FEN*, i.e. the actual position is copied to the clipboard
    * *Promote/Demote Variant* promote/demote the variant selected in the Game TAB
    * *Promote Variant to Main* promote the variant selected in the Game TAB to mainline
    * *Delete Variant* delete the variant selected in the Game TAB
    * *Undo Current Action* deletes the end move of a sequence (main line or variant)

 * *Database* menu with obvious functionality with the exception of
 
    * *Remove Games* removes selected games in the *Database* TAB
    * *Move Games>Up/Down*  moves a selected game up and down in the *Database*
    * *Paste Game*, i.e. the actual game PGN from the clipboard and added to the *Database*
    * *Paste FEN*, i.e. the actual position is pasted from the clipboard and added to the *Database*

 * *Game* menu with obvious functionality with the exception of
 
    * *Select Header Elements ...* opens a dialog to add/remove header elements according to the `PGN`_ standard
    * *Show Move Options* shows by left-button selecting a square the weighted options 
    * *Warn of Danger* shows squares attacked by the opponent 

 * *Engine* menu for handling Universal Chess Interface (`UCI`_) engines with
 
    * *Select Engine* sub-menu to select the engine for hints/scores and annotations
    * *Search Depth* sub-menu to set the search depth of the selected engine
    * *Score Current Move* annotates the move leading to actual position
    * *Annotate All* annotates the actual game or variant
    * *# Annotations* defines the number of variants to be suggested in case of a blunder
    * *Blunder Limit* defines the limit to add a variant
    * *Annotate Variants* defines the number of half moves (PLY) to be shown in variants 
    * *Show Scores* toggle actions enables the *score* part of the *hint/score* label of the status bar
    * *Show Hints* toggle actions enables the *hint* part of the *hint/score* label of the status bar
    * *Configure ...* opens a dialog to add/remove/configure engines
    * *Debug* logs the communication with engine in the *Log* TAB

Keyboard and Mouse Contol
================================

To allow for a user-friendly usage, the game can be controlled by keyboard and/or mouse:

.. csv-table:: Game Control by Keyboard/Mouse/Mouse Wheel
   :header: "Key/Wheel", "Board", "Game-TAB", "Description"
   :widths: 30, 10, 10, 50
   
   :kbd:`up` | :kbd:`scroll-up`       , :kbd:`✔`, :kbd:`✔`, goto last move
   :kbd:`down` | :kbd:`scroll-down`, :kbd:`✔`, :kbd:`✔`, goto next move
   :kbd:`left`                               ,              , :kbd:`✔`, step into variant
   :kbd:`right`                             ,              , :kbd:`✔`, step out of a variant
   :kbd:`home`                            ,              , :kbd:`✔`, goto initial move
   :kbd:`end`                              ,              , :kbd:`✔`, goto end-of-game
   :kbd:`mouse-left-press`            , :kbd:`✔`,              , begin move
   :kbd:`mouse-left-release`          , :kbd:`✔`,              , end move
   :kbd:`Control-P`                      ,              , :kbd:`✔`, promote variant
   :kbd:`Control-D`                      ,              , :kbd:`✔`, demote variant
   :kbd:`Control-R`                      ,              , :kbd:`✔`, remove variant
   :kbd:`Control-M`                      ,              , :kbd:`✔`, promote variant to mainline
   :kbd:`Control-W`                      ,              , :kbd:`✔`, toggle warn of danger

In addition, several *standard* key strokes are supported:

.. csv-table:: Other Key-Codes
   :header: "Key", "Description"
   :widths: 30, 50

   :kbd:`Control-Z`                       , undo last move
   :kbd:`Control-F`                       , flip board
   :kbd:`Control-C`                       , copy game (PGN) to clipboard
   :kbd:`Control-V`                       , paste game (PGN) from clipboard
   :kbd:`Control-Shift-C`               , copy position (FEN) to clipboard
   :kbd:`Control-Shift-V`               , paste position (FEN) from clipboard

.. |MainWindow| image:: mainWindow.png
  :width: 800
  :alt: Main Window
.. _PGN: https://github.com/fsmosca/PGN-Standard
.. _UCI: http://wbec-ridderkerk.nl/html/UCIProtocol.html
'''

from typing import Optional, Callable, Dict, List, Tuple, Union, Any
import configparser
import os, os.path
import copy
import platform
import pickle
import io
import re
try:
 from PyQt6 import QtWidgets, QtGui, QtCore
 from PyQt6.QtGui import QAction
 from PyQt6 import uic
 import PyQt6.QtSvgWidgets
 import PyQt6.QtCharts
except:
 try:
  from PyQt5 import QtWidgets, QtGui, QtCore
  from PyQt5.QtWidgets import QAction
  from PyQt5 import uic
  import PyQt5.QtSvg
  import PyQt5.QtChart
 except:
  raise ModuleNotFoundError('Neither the required PyQt6 nor PyQt5 modules are completely installed')

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess, chess.pgn
import MzChess
from MzChess import read_game

import AboutDialog

class ChessMainWindow(QtWidgets.QMainWindow):
 logSignal = QtCore.pyqtSignal(str)
 notifySignal = QtCore.pyqtSignal(str)
 notifyGameSelectedSignal = QtCore.pyqtSignal(int)
 notifyGameListHeaderChangedSignal = QtCore.pyqtSignal(list)
 notifyGameListChangedSignal = QtCore.pyqtSignal()
 notifyGameHeadersChangedSignal = QtCore.pyqtSignal(chess.pgn.Headers)

 notifyGameNodeSelectedSignal = QtCore.pyqtSignal(chess.pgn.GameNode)
 notifyGameNodeChangedSignal = QtCore.pyqtSignal(chess.pgn.GameNode, tuple)
 notifyNewGameNodeSignal = QtCore.pyqtSignal(chess.pgn.GameNode)
 hintDict = { 'None' :  '0',  'White' : '1',  'Black' : '2',  'All' : '3' }
 hintList = [ 'None', 'White',  'Black',  'All' ]
 fileDialogOptions = QtWidgets.QFileDialog.Option.DontUseNativeDialog
 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 intRe = re.compile(r"^[+-]?[1-9][0-9]*$")
 boolRe = re.compile(r"^(True|False)$")

 def __init__(self, parent = None) -> None:
  super(ChessMainWindow, self).__init__(parent)
  MzChess.installLeipFont()
  uic.loadUi(os.path.join(self.fileDirectory, 'chessMainWindow.ui'), self)
  # self.setupUi(self)

  icon = QtGui.QIcon()
  icon.addPixmap(QtGui.QPixmap(os.path.join(self.fileDirectory,'schach.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
  self.setWindowIcon(icon)
  
  self.pgm = MzChess.__name__
  self.version = MzChess.__version__
  self.dateString = MzChess.__date__
  
  # self.helpIndex = QtCore.QUrl.fromLocalFile(os.path.join(os.path.dirname(self.fileDirectory), 'doc_build', 'html', 'index.html'))
  self.helpIndex = QtCore.QUrl('https://reinhardm-dev.github.io/MzChess')

  self.ecoDB = MzChess.ECODatabase()
  self.ecoFen2IdDict = self.ecoDB.fen2Id()
  self.toolBar = QtWidgets.QToolBar()
  self._setIcon(self.actionSaveDB, QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton)
  self.toolBar.addSeparator()
  self._setIcon(self.actionAddGame, QtWidgets.QStyle.StandardPixmap.SP_FileIcon)
  self._setIcon(self.actionFlipBoard, QtWidgets.QStyle.StandardPixmap.SP_BrowserReload)
  self.toolBar.addSeparator()
  self._setIcon(self.actionNextMove, QtWidgets.QStyle.StandardPixmap.SP_ArrowDown)
  self._setIcon(self.actionPreviousMove, QtWidgets.QStyle.StandardPixmap.SP_ArrowUp)
  self._setIcon(self.actionNextVariant, QtWidgets.QStyle.StandardPixmap.SP_ArrowForward)
  self._setIcon(self.actionPreviousVariant, QtWidgets.QStyle.StandardPixmap.SP_ArrowBack)
  self._setIcon(self.actionPromoteVariant, QtWidgets.QStyle.StandardPixmap.SP_MediaSeekBackward)
  self._setIcon(self.actionDemoteVariant, QtWidgets.QStyle.StandardPixmap.SP_MediaSeekForward)
  self._setIcon(self.actionPromoteVariant2Main, QtWidgets.QStyle.StandardPixmap.SP_MediaSkipBackward)
  self._setIcon(self.actionDeleteVariant, QtWidgets.QStyle.StandardPixmap.SP_DialogCloseButton)
  self.toolBar.addSeparator()
  self._setIcon(self.actionUndo, QtWidgets.QStyle.StandardPixmap.SP_BrowserStop)
  self.addToolBar(self.toolBar)
  
  self.gameOptions = { 
   'showOptions' : (self.actionShowOptions, False), 
   'warnOfDanger' : (self.actionWarnOfDanger, False), 
   'encoding' : (self.menuEncoding, 'UTF-8')
  }
  self.encodingDict = { 'UTF-8' : 'utf-8-sig', 'ISO 8859/1' : 'iso-8859-1',  'ASCII' : 'ascii'}
  
  self.engineOptions = {
   'selectedEngine' : (self.menuSelectEngine, None), 
   'searchDepth' : (self.menuSearchDepth, 15), 
   'numberOfAnnotations' : (self.menuNumberOfAnnotations, 1), 
   'annotateVariants' : (self.menuAnnotateVariants, None), 
   'showScores' : (self.actionShowScores, False), 
   }
  
  #  'blunderLimit' : (self.menuBlunderLimit, -float('inf')), 
  self.gameListHeaders = ['Date',  'White',  'Black',  'Result']
  
  self.engineDict = dict()
  self.recentPGN = dict()
  self.eventList = list()
  self.siteList = list()
  self.playerList = list()
  self.optionalHeaderItems = list()

  self.hintEngine = None
  self.mateScore = 100
  self.debugEngine = False
  
  if platform.system() == 'Windows':
   self.settingsDir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'MzChess')
  else:
   self.settingsDir = os.path.join(os.path.expanduser('~'), '.config', 'MzChess')
  if not os.path.isdir(self.settingsDir):
   os.mkdir(self.settingsDir, 0o755)
  self.settingsFile = os.path.join(self.settingsDir, 'settings.ini')
  self.recoverFile = os.path.join(self.settingsDir, 'recover.ppgn')
  self.settings = configparser.ConfigParser(delimiters=['='], allow_no_value=True)
  self.settings.optionxform = str
  self.recentPGN = dict()
  self.engineDict = dict()
  self.eventList = list()
  self.siteList = list()
  self.playerList = list()
  self.optionalHeaderItems = list()
  if os.path.isfile(self.settingsFile):
   self.settings.read(self.settingsFile, encoding = 'utf-8')
   self.engineDict = MzChess.loadEngineSettings(self.settings)
   if 'Recent' in self.settings.sections():
    for recentDB, enc in dict(self.settings['Recent']).items():
     if os.path.exists(recentDB):
      self.recentPGN[recentDB] = enc
   if 'GameListHeaders' in self.settings.sections():
    self.gameListHeaders = self.settings.options('GameListHeaders')
   if 'Events' in self.settings.sections():
    self.eventList = self.settings.options('Events')
   if 'Sites' in self.settings.sections():
    self.siteList = self.settings.options('Sites')
   if 'Players' in self.settings.sections():
    self.playerList = self.settings.options('Players')
   if 'OptionalHeaderItems' in self.settings.sections():
    self.optionalHeaderItems = list(self.settings['OptionalHeaderItems'])
   if self.settings['Menu/Engine']['selectedEngine'] not in self.engineDict:
    self.settings['Menu/Engine']['selectedEngine'] = None
    self.settings['Menu/Engine']['showHints'] = '0'
    self.settings['Menu/Engine']['showScores'] = False
   
  self.menuRecentDB.clear()
  if self.recentPGN is None:
   self.recentPGN = dict()
  else:
   actDir = os.path.expanduser('~')
   for rItem in self.recentPGN.keys():
    if rItem is not None and os.path.isfile(rItem):
     if actDir == os.path.expanduser('~'):
      actDir = os.path.dirname(rItem)
     self.menuRecentDB.addAction(rItem)
  
  os.chdir(actDir)
  
  self.aboutDialog = AboutDialog.AboutDialog()
  self.aboutDialog.setup(
   pgm = self.pgm, 
   version = self.version, 
   dateString = self.dateString)

  sbText = self.statusBar().font()
  sbText.setPointSize(12)
  
  self.moveLabel = QtWidgets.QLabel()
  self.moveLabel.setFont(sbText)
  self.moveLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.moveLabel.setToolTip("Total Moves/Half-moves since the last capture or pawn move")
  self.statusBar().addWidget(self.moveLabel, 20)
  self.infoLabel = QtWidgets.QLabel()
  self.infoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
  self.infoLabel.setFont(sbText)
  self.statusBar().addWidget(self.infoLabel, 130)
  self.engineLabel = QtWidgets.QLabel()
  self.engineLabel.setFont(sbText)
  self.engineLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.engineLabel.setToolTip("Engine in use")
  self.statusBar().addWidget(self.engineLabel, 50)
  self.hintLabel = QtWidgets.QLabel()
  self.hintLabel.setFont(sbText)
  self.hintLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.hintLabel.setToolTip("Best move/Score[centipawn]")
  self.statusBar().addWidget(self.hintLabel, 30)
  self.ecoLabel = QtWidgets.QLabel()
  self.ecoLabel.setFont(sbText)
  self.ecoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.statusBar().addWidget(self.ecoLabel, 10)
  self.squareLabel = QtWidgets.QLabel()
  self.squareLabel.setFont(sbText)
  self.squareLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
  self.squareLabel.setToolTip("Position")
  self.statusBar().addWidget(self.squareLabel, 10)

  self.itemSelector = MzChess.ItemSelector('Header Elements (without 7-tag roster)...', pointSize = 10)
  
  self.loadOptionDict('Menu/Game', self.gameOptions)
  self.resetSelectEngine()
  self.loadOptionDict('Menu/Engine', self.engineOptions)
  blunderLimit = float(self.settings['Menu/Engine'].get('blunderLimit', '-inf'))
  for action in self.menuBlunderLimit.actions():
   tList = action.text().split(' ')
   action.setChecked((len(tList) == 1 and blunderLimit == -float('inf')) \
                        or  (len(tList) == 2 and blunderLimit == -float(tList[0])))
  hintValue = int(self.settings['Menu/Engine'].get('showHints', 0))
  for actAction in self.menuShowHints.actions():
   if actAction.text() == self.hintList[hintValue]:
    actAction.setChecked(True)
  self.gameListTableView.setup(notifyDoubleClickSignal = self.notifyGameSelectedSignal, 
                                          notifyHeaderChangedSignal = self.notifyGameListHeaderChangedSignal, 
                                          notifyListChangedSignal = self.notifyGameListChangedSignal)
  self.gameListTableView.gameHeaderKeys = self.gameListHeaders
  self.notifyGameSelectedSignal.connect(self.gameSelected)
  self.notifyGameListHeaderChangedSignal.connect(self.gameListHeaderChanged)
  self.notifyGameListChangedSignal.connect(self.gameListChanged)
  self.pgnFile = None
  self.gameListFile = ''
  self.gameList = list()
  self.gameListChanged = False
  self.gameFile = ''
  self.game = chess.pgn.Game()
  self.gameNode = self.game
  self.gameID = None
  self.undoListList = list()
  self.redoListList = list()
  self._addGame(game = None, isNew = True)
  self.setChessWindowTitle()
  self.gameSelected(0)
 
  self.gameHeaderTableView.setup(
       notifyGameHeadersChangedSignal = self.notifyGameHeadersChangedSignal, 
       eventList = self.eventList, siteList = self.siteList, playerList = self.playerList)
  self.notifyGameHeadersChangedSignal.connect(self.gameHeadersChanged)

  self.boardGraphicsView.setup(
   notifyNewGameNodeSignal = self.notifyNewGameNodeSignal, notifyGameNodeSelectedSignal =self.notifyGameNodeSelectedSignal, 
   materialLabel = self.materialLabel, squareLabel = self.squareLabel, 
   turnFrame= self.turnFrame, hintLabel = self.hintLabel, 
   flipped = False)
  self.gameTreeViewWidget.setup(self.notifyGameNodeSelectedSignal, self.notifyGameNodeChangedSignal)
  self.scorePlotGraphicsView.setup(self.notifyGameNodeSelectedSignal)
  self.notifyGameNodeSelectedSignal.connect(self.gameNodeSelected)
  self.notifyGameNodeChangedSignal.connect(self.gameNodeChanged)
  self.notifyNewGameNodeSignal.connect(self.newGameNode)
  self.notifySignal.connect(self.notify)
  self.logSignal.connect(self.toLog)

  self.show_HintsScores()


 def setup(self) -> None:
  sizes = self.splitter.sizes()
  self.splitter.setSizes([self.boardGraphicsView.height(), sizes[0] + sizes[1] - self.boardGraphicsView.height()])
  self.boardGraphicsView.setDrawOptions(self.actionShowOptions.isChecked())
  self.boardGraphicsView.setGameNode(self.game)
  self.gameTreeViewWidget.setGame(self.game)
  self.gameListTableView.resetDB()
  self.gameHeaderTableView.resetGame()

 def loadOptionDict(self, name : str, n2oDict : Dict[str, Union[QAction, Tuple[QtWidgets.QMenu, Any]]]) -> Dict[str, Union[int, float]]:
  if name not in self.settings:
   self.settings[name] = dict()
  optionsDict = dict()
  for opt, o2v in n2oDict.items():
   obj, defValue = o2v
   optionsDict[opt] = defValue
   optValue = self.settings[name].get(opt, defValue)
   if isinstance(obj, QAction):
    optionsDict[opt] = (optValue == 'True')
    obj.setChecked(optionsDict[opt])
   elif isinstance(obj, QtWidgets.QMenu):
    for action in obj.actions():
     tListString = action.text()
     if len(tListString) == 0:
      continue
     tList = tListString.split(' ')
     if self.intRe.match(tList[0]) is not None:
      actionValue = int(tList[0])
     elif tList[0] == 'All':
      actionValue = 2^32 - 1
     elif tList[0] == 'None':
      actionValue = None
     else:
      try:
       actionValue = float(tList[0])
      except:
       actionValue = tListString
     if str(actionValue) == optValue or '{}.0'.format(actionValue) == optValue:
      action.setChecked(True)
      optionsDict[opt] = actionValue
     else:
      action.setChecked(False)
  for tag, value in optionsDict.items():
   self.settings[name][tag] = str(value)
   
 def resetSelectEngine(self) -> None:
  self.menuSelectEngine.clear()
  action = self.menuSelectEngine.addAction('None')
  action.setCheckable(True)
  if 'Menu/Engine' in self.settings.sections():
   if self.settings['Menu/Engine']['selectedEngine'] is None or self.settings['Menu/Engine']['selectedEngine'] not in self.engineDict:
    action.setChecked(True)
   self.menuSelectEngine.addSeparator()
   for eItem in self.engineDict:
    action = self.menuSelectEngine.addAction(eItem)
    action.setCheckable(True)
    if self.settings['Menu/Engine']['selectedEngine'] == eItem:
     action.setChecked(True)

 def updateSettingsList(self, section : str, valueList : List[Union[str, Tuple[str, str]]] = list(), firstValue : Union[str, Tuple[str, str], None] = None) -> None:
  if section not in self.settings.sections():
   self.settings.add_section(section)
  newDict = dict()
  if len(valueList) > 0:
   newDict = dict(self.settings[section])
  if isinstance(firstValue, tuple):
   key = firstValue[0]
   value = firstValue[1]
  else:
   key = firstValue
   value = None
  keys = list()
  if key is not None:
   newDict[key] = value
   self.settings.remove_option(section, key)
   keys = [key]
  if len(valueList) == 0:
   keys += self.settings.options(section)
  self.settings.remove_section(section)
  self.settings.add_section(section)
  for key in keys:
   if key in newDict:
    value = newDict[key]
   self.settings[section][key] = value
  for kv in valueList:
   if isinstance(kv, tuple):
    self.settings[section][kv[0]] = kv[1]
   else:
    self.settings[section][kv] = None
  
 def saveSettings(self) -> None:
  with open(self.settingsFile, 'w', encoding = 'utf-8') as f:
   self.settings.write(f)

 # --------------------------------------------------------------------------------------------------
 
 @QtCore.pyqtSlot(str)
 def notifyError(self, str : str) -> None:
  msgBox = QtWidgets.QMessageBox()
  msgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
  msgBox.setText(str)
  msgBox.setWindowTitle("Error ...")
  msgBox.exec()

 def setInfoLabel(self):
  if self.game in self.gameList:
   self.gameID = self.gameList.index(self.game)
  else:
   if self.gameID > 0:
    self.gameID = 0
   self.game = self.gameList[self.gameID]
  if self.gameID >= len(self.undoListList)-1:
   self.undoListList = list()
   self.redoListList = list()
   for n in range(len(self.gameList)):
    self.undoListList.append(list())
    self.redoListList.append(list())
  self.infoLabel.setText('game #{} of {} ({} moves): {} = {}'.format(self.gameID, len(self.gameList), 
   self.gameList[self.gameID].end().board().fullmove_number, self.gameListHeaders[0], self.game.headers[self.gameListHeaders[0]]))
  self.infoLabel.update()
  QtWidgets.QApplication.processEvents()

 def setMoveLabel(self, board):
  self.moveLabel.setText('{}/{}'.format(board.fullmove_number, board.halfmove_clock))
  self.moveLabel.update()
  QtWidgets.QApplication.processEvents()

 def notify(self, str):
  self.statusBar().showMessage(str, 3000)
  
 @QtCore.pyqtSlot(str)
 def toLog(self, msg):
  self.uciTextEdit.moveCursor (QtGui.QTextCursor.MoveOperation.End)
  self.uciTextEdit.insertPlainText (msg)
  self.uciTextEdit.moveCursor(QtGui.QTextCursor.MoveOperation.End)

 def _setIcon(self, action, stdIcon, toToolbar = True):
  action.setIcon(self.style().standardIcon(stdIcon))
  if toToolbar:
   self.toolBar.addAction(action)

 def _showEcoCode(self, gameNode, fromBeginning = False):
  if fromBeginning:
   actNode = gameNode.game().next()
   self.ecoCode = '---'
   self.ecoDescription = ''
  else:
   actNode = gameNode
  id = -1
  while actNode is not None:
   fen = ' '.join(actNode.board().fen().split(' ')[:-2])
   if fen in self.ecoFen2IdDict:
    id = self.ecoFen2IdDict[fen]
   actNode = actNode.next()
  if id >= 0:
   self.ecoCode = self.ecoDB[id][0]
   self.ecoDescription = self.ecoDB[id][1]
   gameNode.game().headers['Opening'] = self.ecoDescription
   gameNode.game().headers['ECO'] = self.ecoCode
   self.ecoLabel.setText(self.ecoCode)
   self.ecoLabel.setToolTip(self.ecoDescription)

 def _allowNewGameList(self):
  if self.gameListChanged:
   rc = QtWidgets.QMessageBox.warning(self, 
    'Game database not saved ...', 'Do you like to close anyway ?', 
     QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, 
     QtWidgets.QMessageBox.StandardButton.No)
   if rc == QtWidgets.QMessageBox.StandardButton.No:
    return False
  self.gameListChanged = False
  self.gameID = None
  self.undoListList = list()
  self.redoListList = list()
  self.gameList = list()
  self.pgnFile = None

  self._addGame(game = None, isNew = True)
  return True

 def _addGame(self, game = None, isNew = False):
  if game is not None:
   self.game = game
  else:
   self.game = chess.pgn.Game()
   self.game.headers = self._setGameHeader(self.optionalHeaderItems)
  self.gameNode = self.game
  self.gameID = len(self.gameList)
  self.gameList.append(self.game)
  self.undoListList.append(list())
  self.undoListList[self.gameID] = list()
  self.redoListList.append(list())
  self.redoListList[self.gameID] = list()
  self.gameListTableView.setGameList(self.gameList)
  self._showEcoCode(self.game, fromBeginning = True)
  self.gameSelected(self.gameID)
  if not isNew:
   self.setChessWindowTitle()

 def _setGameHeader(self, optionalHeaderItems : List[str]) -> chess.pgn.Headers:
  selectedItems =  list(chess.pgn.Headers()) + optionalHeaderItems
  newHeaders = chess.pgn.Headers()
  for el in selectedItems:
   if el in self.game.headers:
    newHeaders[el] = self.game.headers[el]
   else:
    newHeaders[el] = self.gameHeaderTableView.stdKey2ValueTypeDict[el][0]
  self.optionalHeaderItems = optionalHeaderItems
  return newHeaders

 # ---------------------------------------------------------------------------

 def openPGN(self, pgnFile : str, encoding : str = None):
  if not self._allowNewGameList():
   return
  self.notify('Opening {} ...'.format(os.path.basename(pgnFile)))
  self.gameListFile = os.path.split(pgnFile)[1]
  _,  ext = os.path.splitext(pgnFile)
  if ext == '.ppgn':
   try:
    with open(pgnFile, mode = 'rb') as f:
     self.gameList = pickle.load(f)
     encoding = None
   except:
    self.notifyError('Cannot open PPGN file {}'.format(pgnFile))
    return
  elif ext == '.pgn':
   try:
    pgn = open(pgnFile, mode = 'r', encoding = encoding)
   except:
    self.notifyError('Cannot open PGN file {}'.format(pgnFile))
    return
   n = 1
   self.gameList = list()
   while True:
    actGame = read_game(pgn)
    if actGame is None:
     break
    if len(actGame.errors) == 0:
     self.gameList.append(actGame)
    else:
     self.notifyError('Failed to load game #{}'.format(n))
     return
    n += 1
  else:
   self.notifyError('Cannot handle file with extension "{}"'.format(ext))
   return
  if len(self.gameList) < 1:   
   self.notifyError('No game loaded')
   return
  with open(self.recoverFile, mode = 'wb') as f:
   pickle.dump(self.gameList, f)
  self.gameListTableView.setGameList(self.gameList)
  self.gameSelected(0)
  self.settings['Recent'] = {pgnFile : encoding}
  newRecentPGN = {pgnFile : encoding}
  for file, enc in self.recentPGN.items():
   if file != pgnFile:
    newRecentPGN[file] = enc
    self.settings['Recent'][file] = enc
  self.recentPGN = newRecentPGN
  self.saveSettings()
  self.menuRecentDB.clear()
  for rItem in self.recentPGN:
   if rItem is not None and os.path.isfile(rItem):
    self.menuRecentDB.addAction(rItem)
  if pgnFile != self.recoverFile:
   os.chdir(os.path.dirname(pgnFile))
   self.pgnFile = pgnFile
  self.setChessWindowTitle()
 
 @QtCore.pyqtSlot(QAction)
 def on_menuEncoding_triggered(self, action):
  for actAction in self.menuEncoding.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  self.settings['Menu/Game']['encoding'] = action.text()
  self.saveSettings()

 @QtCore.pyqtSlot()
 def on_actionOpenDB_triggered(self):
  pgnFile, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Load Game Database ...", "",
        "Pickle Portable Game Notation Files (*.ppgn);;Portable Game Notation Files (*.pgn);;All Files (*)", options = self.fileDialogOptions)
  if pgnFile is not None and len(pgnFile) > 0:
   self.openPGN(pgnFile, self.encodingDict[self.settings['Menu/Game']['encoding']])
   
 @QtCore.pyqtSlot()
 def on_actionRecoverDB_triggered(self):
  if not os.path.exists(self.recoverFile):
   self.notifyError('Recovery database not existing')
   return
  self.openPGN(self.recoverFile)
   
 @QtCore.pyqtSlot()
 def on_actionGameUp_triggered(self):
  if self.gameListTableView.on_menuMoveGame_triggered(self.actionGameUp):
   self.setInfoLabel()
   self.setChessWindowTitle()

 @QtCore.pyqtSlot()
 def on_actionCloseDB_triggered(self):
  if not self._allowNewGameList():
   return
  self.notify('Closing database ...')
  self.setChessWindowTitle()

 @QtCore.pyqtSlot(QtGui.QCloseEvent)
 def closeEvent(self, ev):
  if not self._allowNewGameList():
   ev.ignore()
  else:
   if self.hintEngine is not None:
    self.hintEngine.kill(True)
   ev.accept()

 @QtCore.pyqtSlot()
 def on_actionExit_triggered(self):
  if self._allowNewGameList():
   self.close()

 def saveDB(self, forceAppend : bool = False, saveCurrent : bool = False):
  if len(self.gameList) == 0:
    self.notifyError('No Game Database available')
    return

  if forceAppend:
   mode = 'a'
  else:
   mode = 'w'
  if saveCurrent and self.pgnFile is not None:
   pgnFile = self.pgnFile
  else:
   pgnFile, _ = QtWidgets.QFileDialog.getSaveFileName(self,
     "Save Game Database ...", self.gameListFile,
     "Portable Game Notation Files (*.ppgn *.pgn)", options = self.fileDialogOptions)
   if pgnFile is None or len(pgnFile) == 0:
    return
  _,  ext = os.path.splitext(pgnFile)
  if len(ext) == 0:
   ext = '.pgn'
   self.notify('Saving database to PGN file {}.pgn ...'.format(pgnFile))
  else:
   self.notify('Saving database to file {} ...'.format(pgnFile))
  if ext == '.ppgn':
   if mode == 'a':
    self.notifyError('Cannot append to PPGN file {}'.format(pgnFile))
    return
   try:
    with open(pgnFile, mode = 'wb') as f:
     pickle.dump(self.gameList, f)
   except:
    self.notifyError('Cannot open PPGN file {}'.format(pgnFile))
    return
   encoding = None
  elif ext == '.pgn':
   try:
    encoding = self.settings['Menu/Game']['encoding']
    pgnString = str()
    for game in self.gameList:
     exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
     pgnString += game.accept(exporter)
     if game != self.gameList[-1]:
      pgnString += '\n\n'
    with open(pgnFile, mode = mode,  encoding = self.encodingDict[encoding]) as f:
     f.write(pgnString)
   except:
    self.notifyError('Cannot save PGN file {}'.format(pgnFile))
    return
  else:
    self.notifyError('PGN file {} has improper extension (.pgn or .pgn expected)'.format(pgnFile))
    return
  self.updateSettingsList('Recent', self.recentPGN.items(), firstValue = (pgnFile, encoding))
  self.saveSettings()
  with open(self.recoverFile, mode = 'wb') as f:
   pickle.dump(self.gameList, f)
  self.gameListFile = os.path.split(pgnFile)[1]
  os.chdir(os.path.dirname(pgnFile))
  self.pgnFile = pgnFile
  self.undoListList = list()
  self.redoListList = list()
  self.setChessWindowTitle()

 @QtCore.pyqtSlot()
 def on_actionAppend2DB_triggered(self):
  self.notify('Appending database ...')
  self.saveDB(forceAppend = True, saveCurrent = False)
  
 @QtCore.pyqtSlot()
 def on_actionSaveDB_triggered(self):
  self.saveDB(forceAppend = False, saveCurrent = True)
   
 @QtCore.pyqtSlot()
 def on_actionSaveDBAs_triggered(self):
  self.saveDB(forceAppend = False, saveCurrent = False)

 @QtCore.pyqtSlot()
 def on_actionAddGame_triggered(self):
  self.notify('Adding game #{} ...'.format(self.gameID))
  self._addGame()
   
 @QtCore.pyqtSlot()
 def on_actionRemoveGames_triggered(self):
  if self.gameListTableView.on_actionRemoveGames_triggered():
   if self.game in self.gameList:
    self.setInfoLabel()
   else:
    self.gameSelected(0)
   self.setChessWindowTitle()

 @QtCore.pyqtSlot()
 def on_actionGameDown_triggered(self):
  if self.gameListTableView.on_menuMoveGame_triggered(self.actionGameDown):
   self.setInfoLabel()
   self.setChessWindowTitle()
 
 @QtCore.pyqtSlot(QAction)
 def on_menuRecentDB_triggered(self, action):
  fileName = action.text()
  self.openPGN(fileName, self.recentPGN[fileName])
 
 @QtCore.pyqtSlot(QAction)
 def on_menuEndGame_triggered(self, action):
  endGame = self.game.end()
  if endGame.board().is_game_over():
   self.notifyError('You cannot change the game result any more')
   return
  self.game.headers['Result'] = action.text()
  self.boardGraphicsView.setGameNode(self.gameNode)
  self.gameChanged(self.game)
  
 @QtCore.pyqtSlot()
 def on_actionSaveGame_triggered(self):
  pgnFile, _ = QtWidgets.QFileDialog.getSaveFileName(self,
     "Save Game ...", self.gameFile,"Portable Game Notation Files (*.pgn);;All Files (*)", options = self.fileDialogOptions)
  if pgnFile is not None and len(pgnFile) > 0:
   try:
    encoding = self.settings['Menu/Game']['encoding']
    f = open(pgnFile, mode = 'w',  encoding = self.encodingDict[encoding])
   except:
    self.notifyError('Cannot open PGN file {}'.format(pgnFile))
    return
   self.notify('Saving game #{} ...'.format(self.gameID))
   exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
   pgnString = self.game.accept(exporter)
   f.write(pgnString)
   f.close()
   self.updateSettingsList('Recent', self.recentPGN.items(), firstValue = (pgnFile, encoding))
   self.saveSettings()
   self.gameFile = os.path.split(pgnFile)[1]
   os.chdir(os.path.dirname(pgnFile))

 # ---------------------------------------------------------------------------

 @QtCore.pyqtSlot(QtGui.QWheelEvent)
 def wheelEvent(self, ev):
  numDegrees = ev.angleDelta()
  if numDegrees.y() < 0:
   self.on_actionNextMove_triggered()
  elif numDegrees.y() > 0:
   self.on_actionPreviousMove_triggered()
  ev.accept()

 @QtCore.pyqtSlot()
 def on_actionNextMove_triggered(self):
  self.gameNode = self.boardGraphicsView.nextMove()
  self.gameTreeViewWidget.selectNodeItem(self.gameNode)
  self.scorePlotGraphicsView.selectNodeItem(self.gameNode)
  self.setMoveLabel(self.gameNode.board())

 @QtCore.pyqtSlot()
 def on_actionPreviousMove_triggered(self):
  self.gameNode = self.boardGraphicsView.previousMove()
  self.gameTreeViewWidget.selectNodeItem(self.gameNode)
  self.scorePlotGraphicsView.selectNodeItem(self.gameNode)
  self.setMoveLabel(self.gameNode.board())

 @QtCore.pyqtSlot()
 def on_actionNextVariant_triggered(self):
  self.gameTreeViewWidget.selectSubnodeItem(self.gameNode, next = True)

 @QtCore.pyqtSlot()
 def on_actionPreviousVariant_triggered(self):
  self.gameTreeViewWidget.selectSubnodeItem(self.gameNode, next = False)

 @staticmethod
 def variantHead(gameNode):
  if gameNode is None:
   return (None, None)
  parentNode = gameNode.parent
  while parentNode is not None and len(parentNode.variations) < 2:
   gameNode = parentNode
   parentNode = gameNode.parent
  return (parentNode, gameNode)
 
 def promoteVariant(self, toMain):
  headParentNode, headNode = self.variantHead(self.gameNode)
  oldVariations = copy.copy(headParentNode.variations)
  oldID = oldVariations.index(headNode)
  if headParentNode is None or oldID == 0:
    self.notifyError('You cannot promote main line nodes')
    return
  if toMain or oldID < 2:
   self.gameTreeViewWidget.moveVariant2Main(headParentNode, oldID)
   headParentNode.promote_to_main(headNode)
  else:
   self.gameTreeViewWidget.moveVariant(headParentNode, oldID, True)
   headParentNode.promote(headNode)
  self.undoListList[self.gameID].append(('variations', [(headParentNode, oldVariations)]))
  self.gameNodeSelected(self.gameNode)
  if self.gameNode.is_mainline():
   self.scorePlotGraphicsView.setGame(self.game)
   self.scorePlotGraphicsView.selectNodeItem(self.gameNode)
  self.setChessWindowTitle()
  
 @QtCore.pyqtSlot()
 def on_actionPromoteVariant_triggered(self):
  self.promoteVariant(False)

 @QtCore.pyqtSlot()
 def on_actionPromoteVariant2Main_triggered(self):
  self.promoteVariant(True)

 @QtCore.pyqtSlot()
 def on_actionDemoteVariant_triggered(self):
  headParentNode, headNode = self.variantHead(self.gameNode)
  oldVariations = copy.copy(headParentNode.variations)
  oldID = oldVariations.index(headNode)
  isMainline = headNode.is_mainline()
  if headParentNode is None \
   or oldID == len(headParentNode.variations) - 1:
    self.notifyError('You cannot demote last line nodes')
    return
  if oldID > 0:
   self.gameTreeViewWidget.moveVariant(headParentNode, oldID, False)
  else:
   self.gameTreeViewWidget.moveVariant2Main(headParentNode, 1)
  headParentNode.demote(headNode)
  self.undoListList[self.gameID].append(('variations', [(headParentNode, oldVariations)]))
  if False:
   self.gameTreeViewWidget.setGame(self.game)
  self.gameNodeSelected(self.gameNode)
  if isMainline:
   self.scorePlotGraphicsView.setGame(self.game)
   self.scorePlotGraphicsView.selectNodeItem(self.gameNode)
  self.setChessWindowTitle()
  
 @QtCore.pyqtSlot()
 def on_actionDeleteVariant_triggered(self):
  headParentNode, headNode = self.variantHead(self.gameNode)
  if headParentNode is None:
   self.notifyError('Use "Database/Remove Games" to remove a complete game')
   return
  oldVariations = copy.copy(headParentNode.variations)
  oldID = oldVariations.index(headNode)
  isMainline = headNode.is_mainline()
  if oldID > 0:
   self.gameTreeViewWidget.moveVariant(headParentNode, oldID, None)
  else:
   self.gameTreeViewWidget.moveVariant2Main(headParentNode, None)
  headParentNode.remove_variation(headNode)
  self.undoListList[self.gameID].append(('variations', [(headParentNode, oldVariations)]))
  if False:
   self.gameTreeViewWidget.setGame(self.game)
  if isMainline:
   self.scorePlotGraphicsView.setGame(self.game)
  self.gameNodeSelected(headParentNode)
  self.setChessWindowTitle()

 @QtCore.pyqtSlot()
 def on_actionDeleteAllVariants_triggered(self):
  while not self.gameNode.is_mainline():
   self.gameNode = self.gameNode.parent
  gameNodeValueDict = dict()
  for gameNode in self.game.mainline():
   if len(gameNode.variations) > 1:
    gameNodeValueDict[gameNode] = copy.copy(gameNode.variations)
    del gameNode.variations[:1]
  if len(gameNodeValueDict) > 0:
   gameNodeValueList = [gameNodeValueDict.pop(self.gameNode, str())]
   gameNodeValueList += gameNodeValueDict.items()
   self.undoListList[self.gameID].append(('nags', gameNodeValueList))
   self.gameNodeSelected(self.gameNode)
   self.setChessWindowTitle()
 
 @staticmethod
 def _deleteGameNodesLenGtZero(gameNode, attr, clearedAttr, gameNodeValueDict = dict()):
  attrValue = getattr(gameNode, attr)
  if len(attrValue) > 0:
   gameNodeValueDict[gameNode] = attrValue
   setattr(gameNode, attr, clearedAttr)
  for subNode in gameNode.variations:
   ChessMainWindow._deleteGameNodesLenGtZero(subNode, attr, clearedAttr, gameNodeValueDict)
  return gameNodeValueDict
   
 @QtCore.pyqtSlot()
 def on_actionDeleteAllNAGs_triggered(self):
  gameNodeValueDict = self._deleteGameNodesLenGtZero(self.game, 'nags', set())
  if len(gameNodeValueDict) != 0:
   gameNodeValueList = [(self.game, gameNodeValueDict.pop(self.game, set()))]
   gameNodeValueList += gameNodeValueDict.items()
   self.undoListList[self.gameID].append(('nags', gameNodeValueList))
   self.gameTreeViewWidget.setGame(self.game)
   self.setChessWindowTitle()
   
 @QtCore.pyqtSlot()
 def on_actionDeleteAllComments_triggered(self):
  gameNodeValueDict = self._deleteGameNodesLenGtZero(self.game, 'comment', str())
  if len(gameNodeValueDict) != 0:
   gameNodeValueList = [(self.game, gameNodeValueDict.pop(self.game, str()))]
   gameNodeValueList += gameNodeValueDict.items()
   self.undoListList[self.gameID].append(('comment', gameNodeValueList))
   self.gameTreeViewWidget.setGame(self.game)
   self.setChessWindowTitle()
   
 @QtCore.pyqtSlot()
 def on_actionUndoCurrentMove_triggered(self):
  if self.gameNode is None or self.gameNode.parent is None:
   return
  if not self.gameNode.is_end():
   self.notifyError('Select the end of the mainline or a variant')
   return
  gameNode = self.gameNode
  if len(gameNode.parent.variations) > 1:
   self.notifyError('Cannot undo move, node owns variants')
   return
  self.gameNode = self.gameNode.parent
  self.boardGraphicsView.setGameNode(self.gameNode)
  self.gameTreeViewWidget.removeGameNode(gameNode)
  if gameNode.is_mainline():
   self.scorePlotGraphicsView.removeLastNode()
  self.gameNode.remove_variation(gameNode)
  self.setChessWindowTitle()

 @QtCore.pyqtSlot()
 def on_actionUndo_triggered(self):
  if self.gameID is None or len(self.undoListList[self.gameID]) == 0:
   return
  item = self.undoListList[self.gameID].pop(-1)
  if isinstance(item, chess.pgn.GameNode):
   self.redoListList[self.gameID].append(item)
   gameNode = item
   parent = gameNode.parent
   self.gameTreeViewWidget.removeGameNode(gameNode)
   if gameNode.is_mainline():
    self.scorePlotGraphicsView.removeLastNode()
   parent.remove_variation(gameNode)
   self.gameNodeSelected(parent)
  elif isinstance(item, tuple):
   attr, gameNodeValueList = item
   gameNode = gameNodeValueList[0][0]
   if attr == 'headers':
    self.redoListList[self.gameID].append((attr, (gameNode, getattr(self.game, attr))))
    setattr(self.game, attr, gameNodeValueList[0][1])
   else:
    redoGameNodeValueList = list()
    if attr == 'variations':
     for headParentNode, savedVariations in gameNodeValueList:
      redoGameNodeValueList.append((headParentNode, getattr(headParentNode, attr)))
      variantDeleted = len(headParentNode.variations) < len(savedVariations)
      mainlineChanged = headParentNode.variations[0] != savedVariations[0]
      promotedToMain = mainlineChanged and not variantDeleted
      if not (promotedToMain or variantDeleted):
       for firstId, gameNode in enumerate(savedVariations):
        if headParentNode.variations[firstId] != savedVariations[firstId]:
         self.gameTreeViewWidget.moveVariant(headParentNode, firstId, False)
         headParentNode.variations = savedVariations
         break
      else:
       gameNode.variations = savedVariations
       self.gameSelected(self.gameID)
    elif attr == 'game':
     self.redoListList[self.gameID].append((attr, [(self.gameNode, pickle.dumps(self.game))]))
     self.game = pickle.dumps(gameNodeValueList[0][1])
    else:
     for node, oldAttrValue in gameNodeValueList:
      redoGameNodeValueList.append((node, getattr(node, attr)))
      setattr(node, attr, oldAttrValue)
     self.gameSelected(self.gameID)
    self.redoListList[self.gameID].append((attr, redoGameNodeValueList))
    self.gameNodeSelected(gameNode)
  else:
   raise ValueError('UIE: Undo item type {} not expected'.format(type(item)))
  if self.gameNode == self.game:
   self.scorePlotGraphicsView.setGame(self.game)
  self.gameTreeViewWidget.setGame(self.game)
  self.setChessWindowTitle()

 @QtCore.pyqtSlot()
 def on_actionRedo_triggered(self):
  if self.gameID is None or len(self.redoListList[self.gameID]) == 0:
   return
  item = self.redoListList[self.gameID].pop(-1)
  if isinstance(item, chess.pgn.GameNode):
   item.parent.variations.append(item)
   self.newGameNode(item)
   self.gameNodeSelected(item)
  elif isinstance(item, tuple):
   attr, gameNodeValueList = item
   gameNode = gameNodeValueList[0][0]
   if attr == 'headers':
    self.undoListList[self.gameID].append((attr, (gameNode, getattr(self.game, attr))))
    setattr(self.game, attr, gameNodeValueList[0][1])
   else:
    redoGameNodeValueList = list()
    if attr == 'variations':
     for headParentNode, savedVariations in gameNodeValueList:
      redoGameNodeValueList.append((headParentNode, getattr(headParentNode, attr)))
      variantDeleted = len(headParentNode.variations) < len(savedVariations)
      mainlineChanged = headParentNode.variations[0] != savedVariations[0]
      promotedToMain = mainlineChanged and not variantDeleted
      if not (promotedToMain or variantDeleted):
       for firstId, gameNode in enumerate(savedVariations):
        if headParentNode.variations[firstId] != savedVariations[firstId]:
         self.gameTreeViewWidget.moveVariant(headParentNode, firstId, False)
         headParentNode.variations = savedVariations
         break
      else:
       headParentNode.variations = savedVariations
       self.gameTreeViewWidget.setGame(self.game)
    else:
     for node, oldAttrValue in gameNodeValueList:
      redoGameNodeValueList.append((node, getattr(node, attr)))
      setattr(node, attr, oldAttrValue)
    self.undoListList[self.gameID].append((attr, redoGameNodeValueList))
    self.gameNodeSelected(gameNode)
  else:
   raise ValueError('UIE: Undo item type {} not expected'.format(type(item)))
  if self.gameNode == self.game:
   self.scorePlotGraphicsView.setGame(self.game)
  self.gameTreeViewWidget.setGame(self.game)
  self.setChessWindowTitle()

 def setChessWindowTitle(self):
  self.gameListChanged = False 
  for undoList in self.undoListList:
   self.gameListChanged = self.gameListChanged or len(undoList) > 0
   if self.gameListChanged:
    break
  title = 'MzChess - '
  if self.pgnFile is not None:
   title += os.path.basename(self.pgnFile)
  else:
   title += '<UNKNOWN>'
  if self.gameListChanged:
   title += ' *'
  self.setWindowTitle(title)

 # ---------------------------------------------------------------------------

 @QtCore.pyqtSlot(QAction)
 def on_menuSelectEngine_triggered(self, action):
  oldValue = self.settings['Menu/Engine']['selectedEngine']
  for actAction in self.menuSelectEngine.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  self.settings['Menu/Engine']['selectedEngine'] = action.text()
  if oldValue is None:
   self.show_HintsScores()
  self.saveSettings()
  
 @QtCore.pyqtSlot(QAction)
 def on_menuSearchDepth_triggered(self, action):
  for actAction in self.menuSearchDepth.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  tList = action.text().split(' ')
  self.settings['Menu/Engine']['searchDepth'] = str(int(tList[0]))
  self.saveSettings()
  
 @QtCore.pyqtSlot(QAction)
 def on_menuNumberOfAnnotations_triggered(self, action):
  for actAction in self.menuBlunderLimit.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  naValue = action.text()
  self.settings['Menu/Engine']['numberOfAnnotations'] = naValue
  self.saveSettings()

 @QtCore.pyqtSlot(QAction)
 def on_menuBlunderLimit_triggered(self, action):
  for actAction in self.menuBlunderLimit.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  blValue = action.text()
  if blValue == 'None':
   blunderLimit = -float('inf')
  else:
   blunderLimit = -float(blValue.split(' ')[0])
  self.settings['Menu/Engine']['blunderLimit'] = str(blunderLimit)
  self.saveSettings()
   
 @QtCore.pyqtSlot(QAction)
 def on_menuAnnotateVariants_triggered(self, action):
  for actAction in self.menuAnnotateVariants.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  avValue = action.text().split(' ')[0]
  if avValue == 'None':
   self.settings['Menu/Engine']['annotateVariants'] = str(None)
  elif avValue == 'All':
   self.settings['Menu/Engine']['annotateVariants'] = str(2^32 - 1)
  else:
   self.settings['Menu/Engine']['annotateVariants'] = str(int(avValue))
  self.saveSettings()

 @QtCore.pyqtSlot()
 def on_actionAnnotateCurrentMove_triggered(self):
  if self.settings['Menu/Engine']['selectedEngine'] is None:
   self.notifyError('No engine selected')
   return
  if self.debugEngine:
   logFunction = self.logSignal.emit
  else:
   logFunction = None
  engine = MzChess.ChessEngine(
      self.engineDict[self.settings['Menu/Engine']['selectedEngine']], 
      limit = chess.engine.Limit(depth = self.settings['Menu/Engine']['searchDepth']), 
      log = logFunction)

  aEngine = MzChess.AnnotateEngine(notifyFunction = self.notifySignal.emit)
  annotateVariants = self.settings['Menu/Engine']['annotateVariants']
  if annotateVariants is not None and annotateVariants.isdigit():
   annotateVariants = int(annotateVariants)
  else:
   annotateVariants = 0
  self.notify('Scoring move {} of game #{} ...'.format(self.gameNode.move.uci(), self.gameID))
  aEngine.setup(engine, hintPLYs = annotateVariants, multiPV = int(self.settings['Menu/Engine']['numberOfAnnotations']))
  if aEngine.run(self.gameNode, numberOfPlys = 1):
   annotator = MzChess.Annotator(self.settings['Menu/Engine']['selectedEngine'], notifyFunction = self.notifySignal.emit)
   annotator.setBlunder(-float('inf'), addVariant = False)
   oldAttrValue = self.gameNode.comment
   annotator.apply(game = self.gameNode, scoreListList = aEngine.scoreListList, pvListList = None)
   self.undoListList[self.gameID].append(('comment', [(self.gameNode, oldAttrValue)]))
   if self.gameNode == self.game:
    self.scorePlotGraphicsView.setGame(self.game)
   self.gameTreeViewWidget.setGame(self.game)
   # self.gameHeaderTableView.setGame(self.game)
   self.gameNodeSelected(self.gameNode)
   self.setChessWindowTitle()
  else:
   self.notifyError('Annotation failed')
   return

 @QtCore.pyqtSlot()
 def on_actionAnnotateAll_triggered(self):
  if self.settings['Menu/Engine']['selectedEngine'] is None:
   self.notifyError('No engine selected')
   return
  
  if self.debugEngine:
   logFunction = self.logSignal.emit
  else:
   logFunction = None
  engine = MzChess.ChessEngine(
      self.engineDict[self.settings['Menu/Engine']['selectedEngine']], 
      limit = chess.engine.Limit(depth = self.settings['Menu/Engine']['searchDepth']), 
      log = logFunction)

  aEngine = MzChess.AnnotateEngine(notifyFunction = self.notifySignal.emit)
  annotateVariants = self.settings['Menu/Engine']['annotateVariants']
  if annotateVariants is not None and annotateVariants.isdigit():
   annotateVariants = int(annotateVariants.split(' ')[0])
  else:
   annotateVariants = 0
  gameNode = self.gameNode
  while gameNode.parent:
   if gameNode.parent.variations[0] != gameNode:
    break
   gameNode = gameNode.parent
  if gameNode == self.game:
   self.notify('Annotating game #{} ...'.format(self.gameID))
  else:
   self.notify('Annotating variant {} of #{} ...'.format(gameNode, self.gameID))
  aEngine.setup(engine, hintPLYs = annotateVariants, multiPV = int(self.settings['Menu/Engine']['numberOfAnnotations']))
  if aEngine.run(gameNode, numberOfPlys = None):
   annotator = MzChess.Annotator(self.settings['Menu/Engine']['selectedEngine'])
   addVariant = self.settings['Menu/Engine']['blunderLimit'] != '-inf'
   annotator.setBlunder(float(self.settings['Menu/Engine']['blunderLimit']), addVariant = addVariant)
   undoGameNodeValueList = list()
   for actGameNode in gameNode.mainline():
    if actGameNode.comment != '':
     undoGameNodeValueList.append((actGameNode, gameNode.comment))
   hintsAdded = annotator.apply(game = gameNode, scoreListList = aEngine.scoreListList, pvListList = aEngine.pvListList)
   if hintsAdded:
    self.undoListList[self.gameID].append(('game', [(self.gameNode, pickle.dumps(self.game))]))
   else:
    self.undoListList[self.gameID].append(('comment', [(self.gameNode, undoGameNodeValueList)]))
   if gameNode == self.game:
    self.scorePlotGraphicsView.setGame(self.game)
   self.gameTreeViewWidget.setGame(self.game)
   # self.gameHeaderTableView.setGame(self.game)
   self.gameNodeSelected(self.gameNode)
   self.setChessWindowTitle()
  else:
   self.notifyError('Annotation failed')
   return

 @QtCore.pyqtSlot(bool)
 def on_actionShowOptions_toggled(self, checked):
  self.boardGraphicsView.setDrawOptions(checked)
  self.settings['Menu/Game']['showOptions'] = str(checked)
  self.saveSettings()

 @QtCore.pyqtSlot(bool)
 def on_actionWarnOfDanger_toggled(self, checked):
  self.boardGraphicsView.setWarnOfDanger(checked)
  self.settings['Menu/Game']['warnOfDanger'] = str(checked)
  self.saveSettings()

 @QtCore.pyqtSlot(bool)
 def on_actionFlipBoard_toggled(self, checked):
  self.boardGraphicsView.setFlipped(checked)
  
 @QtCore.pyqtSlot()
 def on_actionSelectHeaderElements_triggered(self):
  headerElements = self.gameHeaderTableView.headerElements(withoutSevenTagRoster = True)
  self.itemSelector.setContent(headerElements, self.optionalHeaderItems)
  if not self.itemSelector.exec():
   return None
  self.game.headers = self._setGameHeader(self.itemSelector.selectedItems() )
  self.gameHeaderTableView.setGame(self.game)
  self.updateSettingsList('OptionalHeaderItems', self.optionalHeaderItems)
  self.saveSettings()
   
 def show_HintsScores(self):
  if self.settings['Menu/Engine']['selectedEngine'] is None:
   self.notifyError('No engine selected')
   return
  
  scoresChecked = self.actionShowScores.isChecked()
  hintsChecked = int(self.settings['Menu/Engine'].get('showHints', 0))
  self.settings['Menu/Engine']['showScores'] = str(scoresChecked)
  self.saveSettings()
  if hintsChecked > 0 or scoresChecked:
   if self.settings['Menu/Engine']['searchDepth'] is None:
    self.notifyError('"Engine/Search Depth" undefined.')
    return
   if self.debugEngine:
    logFunction = self.logSignal.emit
   else:
    logFunction = None
   self.hintEngine = MzChess.ChessEngine(
      self.engineDict[self.settings['Menu/Engine']['selectedEngine']], 
      limit = chess.engine.Limit(depth = self.settings['Menu/Engine']['searchDepth']), 
      log = logFunction)
   self.boardGraphicsView.setHint(enableHint = hintsChecked, enableScore = scoresChecked, engine = self.hintEngine)
   self.engineLabel.setText(self.settings['Menu/Engine']['selectedEngine'])
  else:
   self.hintEngine = None
   self.boardGraphicsView.setHint(enableHint = 0, enableScore = False, engine = None)
   self.engineLabel.setText('---')

 @QtCore.pyqtSlot(QAction)
 def on_menuShowHints_triggered(self, action):
  for actAction in self.menuShowHints.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  naValue = self.hintDict[action.text()]
  self.settings['Menu/Engine']['showHints'] = naValue
  self.show_HintsScores()
    
 @QtCore.pyqtSlot(bool)
 def on_actionShowScores_toggled(self, checked):
  self.show_HintsScores()
  
 @QtCore.pyqtSlot()
 def on_actionConfigureEngine_triggered(self):
  configForm = MzChess.ConfigureEngine()
  newEngineDict = configForm.run(engineDict = self.engineDict, log = self.debugEngine)
  if newEngineDict is not None:
   self.engineDict = newEngineDict
   self.resetSelectEngine()
   MzChess.saveEngineSettings(self.settings, self.engineDict)
   self.saveSettings()
   
 @QtCore.pyqtSlot(bool)
 def on_actionDebugEngine_toggled(self, checked):
  self.debugEngine = checked
  if self.hintEngine is not None:
   if self.debugEngine:
    logFunction = self.logSignal.emit
   else:
    logFunction = None
   self.hintEngine.setLog(logFunction)
  
 @QtCore.pyqtSlot()
 def on_actionAbout_triggered(self):
  self.aboutDialog.exec()
 
 @QtCore.pyqtSlot()
 def on_actionHelp_triggered(self):
  QtGui.QDesktopServices.openUrl(self.helpIndex)

 # ---------------------------------------------------------------------------

 @QtCore.pyqtSlot() 
 def on_actionCopyFEN_triggered(self):
  self.notify('Copying current position of game #{} to clipboard ...'.format(self.gameID))
  fen = self.gameNode.board().fen(en_passant = 'fen')
  QtWidgets.QApplication.clipboard().setText(fen)

 @QtCore.pyqtSlot() 
 def on_actionPasteFEN_triggered(self):
  fen = QtWidgets.QApplication.clipboard().text()
  try:
   MzChess.checkFEN(fen)
  except ValueError as err:
   self.notifyError('Improper FEN {}:\n{}'.format(fen, str(err)))
   return
  self.notify('Pasting position from clipboard to game #{} ...'.format(len(self.gameList)))
  board = chess.Board(fen)
  game = chess.pgn.Game()
  game.headers = self.game.headers
  game.headers["Result"] = "*" 
  game.setup(board)
  game.headers.pop("SetUp", None) # remove non-standard header element used by chess package
  self._addGame(game) 
 
 @QtCore.pyqtSlot() 
 def on_actionFENBuilder_triggered(self):
  self.fenBuilder = QtCore.QProcess()
  self.fenBuilder.start(sys.executable, [os.path.join(self.fileDirectory,'qbuildfen.py')], QtCore.QIODevice.OpenModeFlag.NotOpen)
  
 @QtCore.pyqtSlot() 
 def on_actionAnalysePosition_triggered(self):
  self.analysePositionBuilder = QtCore.QProcess()
  self.analysePositionBuilder.start(sys.executable, [os.path.join(self.fileDirectory,'analysePosition.py'), self.gameNode.board().fen()], QtCore.QIODevice.OpenModeFlag.NotOpen)
  
 @QtCore.pyqtSlot() 
 def on_actionCopyGame_triggered(self):
  self.notify('Copying game #{} to clipboard ...'.format(self.gameID))
  exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
  pgnString = self.game.accept(exporter)
  QtWidgets.QApplication.clipboard().setText(pgnString)

 @QtCore.pyqtSlot() 
 def on_actionPasteGame_triggered(self):
  pgnString = QtWidgets.QApplication.clipboard().text()
  pgn = io.StringIO(pgnString)
  game = read_game(pgn)
  if len(game.errors) != 0:
   self.notifyError('Improper PGN')
   return
  self.notify('Pasting game from clipboard to game #{} ...'.format(self.gameID + 1))
  self._addGame(game)
  
 # ---------------------------------------------------------------------------

 @QtCore.pyqtSlot(int)
 def gameSelected(self, gameID):
  if gameID != self.gameID or True:
   self.gameID = gameID
   self.game = self.gameList[gameID]
   self.gameNode = self.game
   self.notify('Loading game #{} ...'.format(self.gameID))
  try:
   self._showEcoCode(self.game, fromBeginning = True)
   self.boardGraphicsView.setGameNode(self.game)
   self.gameTreeViewWidget.setGame(self.game)
   self.gameHeaderTableView.setGame(self.game)
   self.scorePlotGraphicsView.setGame(self.game)
   self.setInfoLabel()
   self.setMoveLabel(self.gameNode.board())
  except:
   self.notifyError('UIE: Improper game ="{}"'.format(self.game))
   return

 @QtCore.pyqtSlot(list)
 def gameListHeaderChanged(self, gameListHeader):
  self.gameListHeader = gameListHeader
  self.updateSettingsList('GameListHeaders', self.gameListHeader)
  self.saveSettings()

 @QtCore.pyqtSlot()
 def gameListChanged(self):
  self.setInfoLabel()
  self.setChessWindowTitle()

 @QtCore.pyqtSlot(chess.pgn.Headers)
 def gameHeadersChanged(self,  headers):
  self.undoListList[self.gameID].append(('headers', [(self.gameNode, self.game.headers)]))
  if 'Comment' in headers:
   self.game.comment = headers['Comment']
   del headers['Comment']
  else:
   self.game.comment = ''
  if '?' not in headers["White"] and headers["White"] not in self.playerList:
   self.updateSettingsList('Players', self.playerList, firstValue = headers["White"])
  if '?' not in headers["Black"] and headers["Black"] not in self.playerList:
   self.updateSettingsList('Players', self.playerList, firstValue = headers["Black"])
  if '?' not in headers["Event"] and headers["Event"] not in self.eventList:
   self.updateSettingsList('Events', self.eventList, firstValue = headers["Event"])
  if '?' not in headers["Site"] and headers["Site"] not in self.siteList:
   self.updateSettingsList('Sites', self.siteList, firstValue = headers["Site"])
  self.saveSettings()
  self.game.headers = headers
  self.setChessWindowTitle()

 @QtCore.pyqtSlot(chess.pgn.GameNode)
 def newGameNode(self, gameNode):
  self.gameNode = gameNode
  self._showEcoCode(self.game, fromBeginning = False)
  if gameNode.is_mainline():
   self.scorePlotGraphicsView.addGameNodes(gameNode)
   self.scorePlotGraphicsView.selectNodeItem(gameNode)
   if 'PlyCount' in self.game.headers:
    self.game.headers['PlyCount'] = str(gameNode.board().ply())
    self.gameHeaderTableView.setPlyCount(self.game.headers['PlyCount'])
   board = self.gameNode.board()
   if self.gameNode.is_end() and board.is_game_over():
    if board.is_checkmate():
     if board.turn == chess.WHITE:
      self.game.headers['Result'] = '0-1'
     else:
      self.game.headers['Result'] = '1-0'
    else:
     self.game.headers['Result'] = '1/2-1/2'

  if gameNode.is_main_variation():
   self.gameTreeViewWidget.addGameNodes(gameNode)
  else:
   self.gameTreeViewWidget.addVariant(gameNode)
  self.gameChanged(self.game)
  self.setInfoLabel()
  self.setMoveLabel(self.gameNode.board())
  self.undoListList[self.gameID].append(self.gameNode)
   
 @QtCore.pyqtSlot(chess.pgn.GameNode)
 def gameNodeSelected(self, gameNode):
  self.gameNode = gameNode
  self.boardGraphicsView.setGameNode(self.gameNode)
  self.gameTreeViewWidget.selectNodeItem(self.gameNode)
  if self.gameNode.is_mainline():
   self.scorePlotGraphicsView.selectNodeItem(self.gameNode)
  self.setMoveLabel(self.gameNode.board())

 @QtCore.pyqtSlot(chess.pgn.Game)
 def gameChanged(self, game):
  self.gameHeaderTableView.setGameResult(game.headers['Result'])
  self.gameTreeViewWidget.setGameResult(game.headers['Result'])
  self.game = game
  self.setChessWindowTitle()
  
 @QtCore.pyqtSlot(chess.pgn.GameNode, tuple)
 def gameNodeChanged(self, gameNode, attrTuple):
  attr, oldAttrValue = attrTuple
  self.undoListList[self.gameID].append((attr, [(gameNode, oldAttrValue)]))
  self.setChessWindowTitle()

class MzClassApplication(QtWidgets.QApplication):
 def __init__(self, argv : List[str], notifyFct : Callable[[str], None] = print) -> None: 
  super(MzClassApplication, self).__init__(argv)
  self.notifyFct = notifyFct

 def notify(self, rec, ev):
  rc = super(MzClassApplication, self).notify(rec, ev)
  self.notifyFct('{} -> Type(Event)= {}, handled = {}'.format(rec, ev.type(),  rc))
  return rc

 # ---------------------------------------------------------------------------

import os,  os.path
# We must create the QtWidgets.QApplication here to avoid Sphinx issues

def runMzChess(notifyFct : Optional[Callable[[str], None]] = None):
 global qApp
 os.chdir(os.path.expanduser('~'))
 if notifyFct is not None:
  qApp = MzClassApplication(sys.argv)
 else:
  qApp = QtWidgets.QApplication(sys.argv)
 chessMainWindow = ChessMainWindow()
 chessMainWindow.show()
 chessMainWindow.setup()
 qApp.exec()

def _runMzChess():
 print('Hello, world')

if __name__ == "__main__":
 runMzChess(None)
