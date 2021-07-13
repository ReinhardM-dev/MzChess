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
 
    * *Copy/Paste PGN*, i.e. the actual game is copied to or pasted from the clipboard
    * *Copy/Paste FEN*, i.e. the actual position is copied to or pasted from the clipboard
    * *Promote/Demote Variant* promote/demote the variant selected in the Game TAB
    * *Promote Variant to Main* promote the variant selected in the Game TAB to mainline
    * *Delete Variant* delete the variant selected in the Game TAB

 * *Database* menu with obvious functionality with the exception of
 
    * *Remove Games* removes selected games in the *Database* TAB

 * *Game* menu with obvious functionality with the exception of
 
    * *Select Header Elements ...* opens a dialog to add/remove header elements according to the `PGN`_ standard
    * *Show Move Options* shows by left-button selecting a square the weighted options 
    * *Warn of Danger* shows squares attacked by the opponent 

 * *Engine* menu for handling Universal Chess Interface (`UCI`_) engines with
 
    * *Select Engine* sub-menu to select the engine for hints/scores and annotations
    * *Search Depth* sub-menu to set the search depth of the selected engine
    * *Annotate Last Move* annotates the move leading to actual position
    * *Annotate All* annotates the actual game
    * *# Annotations* defines the number of variants to be suggested in case of a blunder
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
import pickle
import io
import re

import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

import Ui_chessMainWindow
import AboutDialog

import chess, chess.pgn
import MzChess
from MzChess import chessengine, annotateEngine, configureEngine
from MzChess.pgnParse import read_game
import eco 
from specialDialogs import ItemSelector

class ChessMainWindow(PyQt5.QtWidgets.QMainWindow, Ui_chessMainWindow.Ui_MainWindow):
 logSignal = PyQt5.QtCore.pyqtSignal(str)
 notifySignal = PyQt5.QtCore.pyqtSignal(str)
 notifyGameSelectedSignal = PyQt5.QtCore.pyqtSignal(int)
 notifyGameHeadersChangedSignal = PyQt5.QtCore.pyqtSignal(chess.pgn.Headers)

 notifyGameNodeSelectedSignal = PyQt5.QtCore.pyqtSignal(chess.pgn.GameNode)
 notifyGameChangedSignal = PyQt5.QtCore.pyqtSignal(chess.pgn.Game)
 notifyNewGameNodeSignal = PyQt5.QtCore.pyqtSignal(chess.pgn.GameNode)
 fileDialogOptions = PyQt5.QtWidgets.QFileDialog.Options() | PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog
 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 intRe = re.compile(r"^[+-]?[1-9][0-9]*$")
 boolRe = re.compile(r"^(True|False)$")

 def __init__(self, parent = None) -> None:
  super(ChessMainWindow, self).__init__(parent)
  self.setupUi(self)

  icon = PyQt5.QtGui.QIcon()
  icon.addPixmap(PyQt5.QtGui.QPixmap(os.path.join(self.fileDirectory,'schach.png')), PyQt5.QtGui.QIcon.Normal, PyQt5.QtGui.QIcon.Off)
  self.setWindowIcon(icon)
  
  fDB = PyQt5.QtGui.QFontDatabase()
  if 'Chess Leipzig' not in fDB.families():
   PyQt5.QtGui.QFontDatabase.addApplicationFont(os.path.join(self.fileDirectory, 'pieces', 'LEIPFONT.TTF'))

  self.pgm = 'Mz Chess GUI'
  self.version = MzChess.__version__
  self.dateString = MzChess.__date__
  
  # self.helpIndex = PyQt5.QtCore.QUrl.fromLocalFile(os.path.join(os.path.dirname(self.fileDirectory), 'doc_build', 'html', 'index.html'))
  self.helpIndex = PyQt5.QtCore.QUrl('https://reinhardm-dev.github.io/MzChess')

  self.ecoDB = eco.ECODatabase()
  self.ecoFen2IdDict = self.ecoDB.fen2Id()
  self.actionNew_PGN.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_FileDialogNewFolder))
  self.actionOpen_PGN.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_DirOpenIcon))
  self.actionSave_PGN.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_DirHomeIcon))
  self.actionNew_Game.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_FileIcon))
  self.actionSave_Game.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_DialogSaveButton))
  self.actionFlip_Board.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_BrowserReload))
  self.actionNext_Move.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_ArrowRight))
  self.actionPrevious_Move.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_ArrowLeft))

  self.gameOptions = { 
   'showOptions' : (self.actionShow_Options, False), 
   'warnOfDanger' : (self.actionWarn_of_Danger, False), 
   'encoding' : (self.menuEncoding, 'UTF-8')
  }
  self.encodingDict = { 'UTF-8' : 'utf-8-sig', 'ISO 8859/1' : 'iso-8859-1',  'ASCII' : 'ascii'}
  
  self.engineOptions = {
   'selectedEngine' : (self.menuSelect_Engine, None), 
   'searchDepth' : (self.menuSearch_Depth, 15), 
   'blunderLimit' : (self.menuBlunder_Limit, None), 
   'numberOfAnnotations' : (self.menuNumber_of_Annotations, 1), 
   'annotateVariants' : (self.menuAnnotate_Variants, None), 
   'showScores' : (self.actionShow_Scores, False), 
   'showHints' :( self.actionShow_Hints, False) 
   }
  
  self.engineDict = dict()
  self.recentPGN = dict()
  self.eventList = list()
  self.siteList = list()
  self.playerList = list()
  self.optionalHeaderItems = list()

  self.hintEngine = None
  self.mateScore = 100
  self.debugEngine = False
  
  self.settingsFile = os.path.join(self.fileDirectory, 'settings.ini')
  self.settings = configparser.ConfigParser(delimiters=['='], allow_no_value=True)
  self.settings.optionxform = str
  if os.path.isfile(self.settingsFile):
   self.settings.read(self.settingsFile, encoding = 'utf-8')
   self.engineDict = configureEngine.loadEngineSettings(self.settings)
   if 'Recent' in self.settings.sections():
    self.recentPGN = dict(self.settings['Recent'])
   if 'Events' in self.settings.sections():
    self.eventList = self.settings.options('Events')
   if 'Sites' in self.settings.sections():
    self.siteList = self.settings.options('Sites')
   if 'Players' in self.settings.sections():
    self.playerList = self.settings.options('Players')
   if 'OptionalHeaderItems' in self.settings.sections():
    self.optionalHeaderItems = list(self.settings['OptionalHeaderItems'])

  self.menuRecent_PGN.clear()
  if self.recentPGN is None:
   self.recentPGN = dict()
  else:
   actDir = os.path.expanduser('~')
   for rItem in self.recentPGN.keys():
    if rItem is not None and os.path.isfile(rItem):
     if actDir == os.path.expanduser('~'):
      actDir = os.path.dirname(rItem)
     self.menuRecent_PGN.addAction(rItem)
  
  os.chdir(actDir)
  
  self.aboutDialog = AboutDialog.AboutDialog()
  self.aboutDialog.setup(
   pgm = self.pgm, 
   version = self.version, 
   dateString = self.dateString)

  sbText = self.statusBar().font()
  sbText.setPointSize(12)
  
  self.infoLabel = PyQt5.QtWidgets.QLabel()
  self.infoLabel.setAlignment(PyQt5.QtCore.Qt.AlignLeft)
  self.infoLabel.setFont(sbText)
  self.statusBar().addPermanentWidget(self.infoLabel, 150)
  self.engineLabel = PyQt5.QtWidgets.QLabel()
  self.engineLabel.setFont(sbText)
  self.engineLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
  self.engineLabel.setToolTip("Engine in use")
  self.statusBar().addPermanentWidget(self.engineLabel, 50)
  self.hintLabel = PyQt5.QtWidgets.QLabel()
  self.hintLabel.setFont(sbText)
  self.hintLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
  self.hintLabel.setToolTip("Best move/Score[Pawns]")
  self.statusBar().addPermanentWidget(self.hintLabel, 30)
  self.ecoLabel = PyQt5.QtWidgets.QLabel()
  self.ecoLabel.setFont(sbText)
  self.ecoLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
  self.statusBar().addPermanentWidget(self.ecoLabel, 10)
  self.squareLabel = PyQt5.QtWidgets.QLabel()
  self.squareLabel.setFont(sbText)
  self.squareLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
  self.engineLabel.setToolTip("Position")
  self.statusBar().addPermanentWidget(self.squareLabel, 10)

  self.itemSelector = ItemSelector('Header Elements (without 7-tag roster)...', pointSize = 10)
  
  self.loadOptionDict('Menu/Game', self.gameOptions)
  self.resetSelectEngine()
  self.loadOptionDict('Menu/Engine', self.engineOptions)
  self.gameListTableView.setup(self.notifyGameSelectedSignal)
  self.notifyGameSelectedSignal.connect(self.gameSelected)
  self.gameListFile = ''
  self.gameList = list()
  self.gameListChanged = False
  self.gameFile = ''
  self.game = chess.pgn.Game()
  self.gameNode = self.game
  self.gameID = None
  self._gameChanged = False

  self.gameHeaderTableView.setup(
       notifyGameHeadersChangedSignal = self.notifyGameHeadersChangedSignal, 
       eventList = self.eventList, siteList = self.siteList, playerList = self.playerList)
  self.notifyGameHeadersChangedSignal.connect(self.gameHeadersChanged)

  self.boardGraphicsView.setup(
   notifyNewGameNodeSignal = self.notifyNewGameNodeSignal, notifyGameNodeSelectedSignal =self.notifyGameNodeSelectedSignal, 
   materialLabel = self.materialLabel, squareLabel = self.squareLabel, 
   turnFrame= self.turnFrame, hintLabel = self.hintLabel, 
   flipped = False)
  self.gameTreeViewWidget.setup(self.notifyGameNodeSelectedSignal, self.notifyGameChangedSignal)
  self.scorePlotGraphicsView.setup(self.notifyGameNodeSelectedSignal)
  self.notifyGameNodeSelectedSignal.connect(self.gameNodeSelected)
  self.notifyNewGameNodeSignal.connect(self.newGameNode)
  self.notifyGameChangedSignal.connect(self.gameChanged)
  self.notifySignal.connect(self.notify)
  self.logSignal.connect(self.toLog)

 def setup(self) -> None:
  sizes = self.splitter.sizes()
  self.splitter.setSizes([self.boardGraphicsView.height(), sizes[0] + sizes[1] - self.boardGraphicsView.height()])
  self.boardGraphicsView.setDrawOptions(self.actionShow_Options.isChecked())
  self.boardGraphicsView.setGameNode(self.game)
  self.gameTreeViewWidget.setGame(self.game)
  self.gameListTableView.resetDB()
  self.gameHeaderTableView.resetGame()

 def loadOptionDict(self, name : str, n2oDict : Dict[str, Union[PyQt5.QtWidgets.QAction, Tuple[PyQt5.QtWidgets.QMenu, Any]]]) -> Dict[str, Union[int, float]]:
  if name not in self.settings:
   self.settings[name] = dict()
  optionsDict = dict()
  for opt, o2v in n2oDict.items():
   obj, defValue = o2v
   optionsDict[opt] = defValue
   if opt in self.settings[name]:
    optValue = str(self.settings[name][opt])
   else:
    optValue = str(defValue)
   if isinstance(obj, PyQt5.QtWidgets.QAction):
    optionsDict[opt] = (optValue == 'True')
    obj.setChecked(optionsDict[opt])
   elif isinstance(obj, PyQt5.QtWidgets.QMenu):
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
  self.settings[name] = optionsDict

 def resetSelectEngine(self) -> None:
  self.menuSelect_Engine.clear()
  action = self.menuSelect_Engine.addAction('None')
  action.setCheckable(True)
  if 'Menu/Engine' in self.settings.sections():
   if self.settings['Menu/Engine']['selectedEngine'] is None or self.settings['Menu/Engine']['selectedEngine'] not in self.engineDict:
    action.setChecked(True)
   self.menuSelect_Engine.addSeparator()
   for eItem in self.engineDict:
    action = self.menuSelect_Engine.addAction(eItem)
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
 
 @PyQt5.QtCore.pyqtSlot(str)
 def notifyError(self, msg):
  msgList = msg.split('\n')
  dispMsg  = msgList[0]
  if len(msgList) > 1:
   dispMsg += ' ...' 
  self.notify(dispMsg)
  PyQt5.QtWidgets.QApplication.beep()

 def notify(self, str):
  self.infoLabel.setText(str)
  self.infoLabel.update()
  PyQt5.QtWidgets.QApplication.processEvents()

 @PyQt5.QtCore.pyqtSlot(str)
 def toLog(self, msg):
  self.uciTextEdit.moveCursor (PyQt5.QtGui.QTextCursor.End)
  self.uciTextEdit.insertPlainText (msg)
  self.uciTextEdit.moveCursor(PyQt5.QtGui.QTextCursor.End)

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
  self.notify('')
  if self.gameListChanged:
   rc = PyQt5.QtWidgets.QMessageBox.warning(self, 
    'Game database not saved ...', 'Do you like to close anyway ?', 
     PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No, 
     PyQt5.QtWidgets.QMessageBox.No)
   if rc == PyQt5.QtWidgets.QMessageBox.No:
    return False
  self.gameListTableView.resetDB()
  self.gameHeaderTableView.resetGame()
  self.gameListChanged = False
  self.gameList = list()
  self.gameID = None
  return True

 def _allowNewGame(self):
  self.notify('')
  if self._gameChanged:
   rc = PyQt5.QtWidgets.QMessageBox.warning(self, 
    'Game not saved ...', 'Do you like to close anyway ?', 
     PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No, 
     PyQt5.QtWidgets.QMessageBox.No)
   if rc == PyQt5.QtWidgets.QMessageBox.No:
    return False
  self.game = chess.pgn.Game()
  self.game.headers = self._setGameHeader(self.optionalHeaderItems)
  self.gameNode = self.game
  self.boardGraphicsView.setGameNode(self.game)
  self.gameTreeViewWidget.setGame(self.game)
  self.gameHeaderTableView.resetGame()
  self._showEcoCode(self.game, fromBeginning = True)
  self.setChessWindowTitle()
  self._gameChanged = False
  return True
 
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

 def openPGN(self, pgnFile : str, encoding : str):
  if not self._allowNewGameList():
   return
  self.notify('Opening {} ...'.format(os.path.basename(pgnFile)))
  self.gameListFile = os.path.split(pgnFile)[1]
  _,  ext = os.path.splitext(pgnFile)
  if ext == '.ppgn':
   try:
    with open(pgnFile, mode = 'rb') as f:
     self.gameList += pickle.load(f)
     encoding = None
   except:
    self.notifyError('Cannot open PPGN file {}'.format(pgnFile))
    return
  else:
   try:
    pgn = open(pgnFile, mode = 'r', encoding = encoding)
   except:
    self.notifyError('Cannot open PGN file {}'.format(pgnFile))
    return
   n = 1
   while True:
    actGame = read_game(pgn)
    if actGame is None:
     break
    if len(actGame.errors) == 0:
     self.gameList.append(actGame)
    else:
     self.notifyError('Failed to load game #{}'.format(n))
    n += 1
  os.chdir(os.path.dirname(pgnFile))
  self.gameListTableView.setGameList(self.gameList)
  self.settings['Recent'] = {pgnFile : encoding}
  newRecentPGN = {pgnFile : encoding}
  for file, enc in self.recentPGN.items():
   if file != pgnFile:
    newRecentPGN[file] = enc
    self.settings['Recent'][file] = enc
  self.recentPGN = newRecentPGN
  self.saveSettings()
  self.menuRecent_PGN.clear()
  for rItem in self.recentPGN:
   if rItem is not None and os.path.isfile(rItem):
    self.menuRecent_PGN.addAction(rItem)
  os.chdir(os.path.dirname(pgnFile))
  self.notify('')
 
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuEncoding_triggered(self, action):
  self.notify('')
  for actAction in self.menuEncoding.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  self.settings['Menu/Game']['encoding'] = action.text()
  self.saveSettings()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionNew_PGN_triggered(self):
  self.notify('')
  self.on_actionClose_PGN_triggered()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionOpen_PGN_triggered(self):
  self.notify('')
  pgnFile, _ = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self,"Load Game Database ...", "",
        "Pickle Portable Game Notation Files (*.ppgn);;Portable Game Notation Files (*.pgn);;All Files (*)", options = self.fileDialogOptions)
  if pgnFile is not None and len(pgnFile) > 0:
   self.openPGN(pgnFile, self.encodingDict[self.settings['Menu/Game']['encoding']])
   
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuRecent_PGN_triggered(self, action):
  self.notify('')
  fileName = action.text()
  self.openPGN(fileName, self.recentPGN[fileName])
 
 @PyQt5.QtCore.pyqtSlot()
 def on_actionClose_PGN_triggered(self):
  self.notify('')
  if not self._allowNewGameList() or not self._allowNewGame():
   return
  self.gameListTableView.resetDB()
  self.gameHeaderTableView.resetGame()
  self.gameList = list()
  self.gameID = None

 @PyQt5.QtCore.pyqtSlot(PyQt5.QtGui.QCloseEvent)
 def closeEvent(self, ev):
  self.notify('')
  if not self._allowNewGameList() or not self._allowNewGame():
   ev.ignore()
  else:
   ev.accept()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionExit_triggered(self):
  self.notify('')
  if self._allowNewGameList() and self._allowNewGame():
   self.close()
   
 @PyQt5.QtCore.pyqtSlot()
 def on_actionSave_PGN_triggered(self):
  self.notify('')
  if len(self.gameList) == 0:
    self.notifyError('No Game Database available')
    return
  pgnFile, _ = PyQt5.QtWidgets.QFileDialog.getSaveFileName(self,
     "Save Game Database ...", self.gameListFile,
     "Pickle Portable Game Notation Files (*.ppgn);;Portable Game Notation Files (*.pgn);;All Files (*)", options = self.fileDialogOptions)
  if pgnFile is None or len(pgnFile) == 0:
   return
  _,  ext = os.path.splitext(pgnFile)
  if ext == '.ppgn':
   try:
    with open(pgnFile, mode = 'wb') as f:
     pickle.dump(self.gameList, f)
   except:
    self.notifyError('Cannot open PPGN file {}'.format(pgnFile))
    return
   encoding = None
  elif ext == '.pgn':
   try:
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    pgnString = str()
    encoding = self.settings['Menu/Game']['encoding']
    with open(pgnFile, mode = 'w',  encoding = self.encodingDict[encoding]) as f:
     for game in self.gameList:
      pgnString += game.accept(exporter)
      if game != self.gameList[-1]:
       pgnString += '\n\n'
     f.write(pgnString)
   except:
    self.notifyError('Cannot save PGN file {}'.format(pgnFile))
    return
  else:
    self.notifyError('PGN file {} has improper extension (.pgn or .pgn expected)'.format(pgnFile))
  self.updateSettingsList('Recent', self.recentPGN.items(), firstValue = (pgnFile, encoding))
  self.saveSettings()
  self.gameListChanged = False
  self.gameListFile = os.path.split(pgnFile)[1]
  os.chdir(os.path.dirname(pgnFile))
   
 @PyQt5.QtCore.pyqtSlot()
 def on_actionAdd_Game_triggered(self):
  self.notify('')
  if self.gameID is None:
   self.gameID = len(self.gameList)
   self.gameList.append(self.game)
   self.gameListTableView.setGameList(self.gameList)
  else:
   self.gameList[self.gameID] = self.game
  self.gameListChanged = True
   
 @PyQt5.QtCore.pyqtSlot()
 def on_actionRemove_Games_triggered(self):
  self.notify('')
  selectedIndices = self.gameListTableView.selectedIndexes()
  if len(selectedIndices) != 0:
   removeList = list()
   for index in selectedIndices:
    row = index.row()
    removeList.append(row)
    if row == self.gameID:
     self.gameID = None
   newGameList = list()
   for n, game in enumerate(self.gameList):
    if n not in removeList:
     newGameList.append(game)
   self.gameList = newGameList
   self.gameListChanged = True
   self.gameListTableView.setGameList(self.gameList)
  
 @PyQt5.QtCore.pyqtSlot(bool)
 def on_actionNew_Game_triggered(self):
  self._allowNewGame()
  
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuEnd_Game_triggered(self, action):
  self.notify('')
  endGame = self.game.end()
  if endGame.board().is_game_over():
   self.notifyError('You cannot change the game result any more')
   return
  self.game.headers['Result'] = action.text()
  self.boardGraphicsView.setGameNode(self.gameNode)
  self.gameChanged(self.game)
  
 @PyQt5.QtCore.pyqtSlot()
 def on_actionSave_Game_triggered(self):
  self.notify('')
  pgnFile, _ = PyQt5.QtWidgets.QFileDialog.getSaveFileName(self,
     "Save Game ...", self.gameFile,"Portable Game Notation Files (*.pgn);;All Files (*)", options = self.fileDialogOptions)
  if pgnFile is not None and len(pgnFile) > 0:
   try:
    encoding = self.settings['Menu/Game']['encoding']
    f = open(pgnFile, mode = 'w',  encoding = self.encodingDict[encoding])
   except:
    self.notifyError('Cannot open PGN file {}'.format(pgnFile))
    return
   exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
   pgnString = self.game.accept(exporter)
   f.write(pgnString)
   f.close()
   self.updateSettingsList('Recent', self.recentPGN.items(), firstValue = (pgnFile, encoding))
   self.saveSettings()
   self._gameChanged = False
   self.gameFile = os.path.split(pgnFile)[1]
   os.chdir(os.path.dirname(pgnFile))

 # ---------------------------------------------------------------------------

 @PyQt5.QtCore.pyqtSlot(PyQt5.QtGui.QWheelEvent)
 def wheelEvent(self, ev):
  self.notify('')
  numDegrees = ev.angleDelta()
  if numDegrees.y() < 0:
   self.on_actionNext_Move_triggered()
  elif numDegrees.y() > 0:
   self.on_actionPrevious_Move_triggered()
  ev.accept()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionNext_Move_triggered(self):
  self.notify('')
  self.gameNode = self.boardGraphicsView.nextMove()
  self.gameTreeViewWidget.selectNodeItem(self.gameNode)
  self.scorePlotGraphicsView.selectNodeItem(self.gameNode)

 @PyQt5.QtCore.pyqtSlot()
 def on_actionPrevious_Move_triggered(self):
  self.notify('')
  self.gameNode = self.boardGraphicsView.previousMove()
  self.gameTreeViewWidget.selectNodeItem(self.gameNode)
  self.scorePlotGraphicsView.selectNodeItem(self.gameNode)

 @PyQt5.QtCore.pyqtSlot()
 def on_actionNext_Variant_triggered(self):
  self.notify('')
  self.gameTreeViewWidget.selectSubnodeItem(self.gameNode, next = True)

 @PyQt5.QtCore.pyqtSlot()
 def on_actionPrevious_Variant_triggered(self):
  self.notify('')
  self.gameTreeViewWidget.selectSubnodeItem(self.gameNode, next = False)

 @PyQt5.QtCore.pyqtSlot()
 def on_actionPromote_Variant_triggered(self):
  self.notify('')
  if self.gameNode.is_main_variation():
   self.notifyError('You cannot promote from main line nodes')
   return
  self.gameTreeViewWidget.promoteVariant()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionPromote_Variant_to_Main_triggered(self):
  self.notify('')
  if self.gameNode.is_main_variation():
   self.notifyError('You cannot promote from main line nodes')
   return
  self.gameTreeViewWidget.promoteVariant2Main()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionDemote_Variant_triggered(self):
  self.notify('')
  if self.gameNode.is_main_variation():
   self.notifyError('You cannot promote from main line nodes')
   return
  self.gameTreeViewWidget.demoteVariant()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionDelete_Variant_triggered(self):
  self.notify('')
  if self.gameNode.parent is None:
   self.notifyError('Use Game/New to remove a complete game')
   return
  self.gameTreeViewWidget.removeVariant()
  self.gameNode = self.gameNode.parent
  self.boardGraphicsView.setGameNode(self.gameNode)

 @PyQt5.QtCore.pyqtSlot()
 def on_actionUndo_Last_Move_triggered(self):
  self.notify('')
  if self.gameNode is None or self.gameNode.parent is None:
   return
  if not self.gameNode.is_end():
   self.notifyError('Select the end of the mainline or a variant')
   return
  gameNode = self.gameNode
  self.gameNode = self.gameNode.parent
  self.boardGraphicsView.setGameNode(self.gameNode)
  self.gameTreeViewWidget.removeGameNode(gameNode)
  if gameNode.is_mainline():
   self.scorePlotGraphicsView.removeLastNode()
  self.gameNode.remove_variation(gameNode)
  self._gameChanged = True

 def setChessWindowTitle(self):
  self.setWindowTitle('MzChess {}: {} - {}'.format(self.game.headers['Date'], self.game.headers['White'], self.game.headers['Black']))

 # ---------------------------------------------------------------------------

 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuSelect_Engine_triggered(self, action):
  self.notify('')
  oldValue = self.settings['Menu/Engine']['selectedEngine']
  for actAction in self.menuSelect_Engine.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  self.settings['Menu/Engine']['selectedEngine'] = action.text()
  if oldValue is None:
   self.show_HintsScores()
  self.saveSettings()
  
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuSearch_Depth_triggered(self, action):
  self.notify('')
  for actAction in self.menuSearch_Depth.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  tList = action.text().split(' ')
  self.settings['Menu/Engine']['searchDepth'] = str(int(tList[0]))
  self.saveSettings()
  
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuNumber_of_Annotations_triggered(self, action):
  self.notify('')
  for actAction in self.menuBlunder_Limit.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  naValue = action.text()
  self.settings['Menu/Engine']['numberOfAnnotations'] = naValue
  self.saveSettings()

 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuBlunder_Limit_triggered(self, action):
  self.notify('')
  for actAction in self.menuBlunder_Limit.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  blValue = action.text()
  if blValue == 'None':
   blunderLimit = None
  else:
   blunderLimit = -float(blValue.split(' ')[0])
  self.settings['Menu/Engine']['blunderLimit'] = str(blunderLimit)
  self.saveSettings()
   
 @PyQt5.QtCore.pyqtSlot(PyQt5.QtWidgets.QAction)
 def on_menuAnnotate_Variants_triggered(self, action):
  self.notify('')
  for actAction in self.menuAnnotate_Variants.actions():
   actAction.setChecked(False)
  action.setChecked(True)
  avValue = action.text().split(' ')
  if avValue == 'None':
   self.settings['Menu/Engine']['annotateVariants'] = str(None)
  elif avValue == 'All':
   self.settings['Menu/Engine']['annotateVariants'] = str(2^32 - 1)
  else:
   self.settings['Menu/Engine']['annotateVariants'] = str(int(avValue[0]))
  self.saveSettings()

 @PyQt5.QtCore.pyqtSlot()
 def on_actionAnnotate_Last_Move_triggered(self):
  if self.settings['Menu/Engine']['selectedEngine'] is None:
   self.notifyError('No engine selected')
   return
  self.notify('')
  if self.debugEngine:
   logFunction = self.logSignal.emit
  else:
   logFunction = None
  engine = chessengine.ChessEngine(
      self.engineDict[self.settings['Menu/Engine']['selectedEngine']], 
      limit = chess.engine.Limit(depth = self.settings['Menu/Engine']['searchDepth']), 
      log = logFunction)

  aEngine = annotateEngine.AnnotateEngine(notifyFunction = self.notifySignal.emit)
  annotateVariants = self.settings['Menu/Engine']['annotateVariants']
  if annotateVariants is not None and annotateVariants.isdigit():
   annotateVariants = int(annotateVariants)
  else:
   annotateVariants = 0
  aEngine.setup(engine, hintPLYs = annotateVariants, multiPV = int(self.settings['Menu/Engine']['numberOfAnnotations']))
  if aEngine.run(self.gameNode.parent, numberOfPlys = 2):
   annotator = annotateEngine.Annotator(self.settings['Menu/Engine']['selectedEngine'], notifyFunction = self.notifySignal.emit)
   if self.settings['Menu/Engine']['blunderLimit'] is None:
    annotator.setBlunder(-float('inf'), addVariant = False)
   else:
    annotator.setBlunder(float(self.settings['Menu/Engine']['blunderLimit']), addVariant = True)
   annotator.apply(game = self.gameNode, scoreListList = aEngine.scoreListList, pvListList = aEngine.pvListList, forceHints = True)
   self.scorePlotGraphicsView.setGame(self.game)
   self.gameTreeViewWidget.setGame(self.game)
   self.gameHeaderTableView.setGame(self.game)
   self._gameChanged = True
  else:
   self.notifyError('Annotation failed')

 @PyQt5.QtCore.pyqtSlot()
 def on_actionAnnotate_All_triggered(self):
  if self.settings['Menu/Engine']['selectedEngine'] is None:
   self.notifyError('No engine selected')
   return
  self.notify('')
  if self.debugEngine:
   logFunction = self.logSignal.emit
  else:
   logFunction = None
  engine = chessengine.ChessEngine(
      self.engineDict[self.settings['Menu/Engine']['selectedEngine']], 
      limit = chess.engine.Limit(depth = self.settings['Menu/Engine']['searchDepth']), 
      log = logFunction)

  aEngine = annotateEngine.AnnotateEngine(notifyFunction = self.notifySignal.emit)
  annotateVariants = self.settings['Menu/Engine']['annotateVariants']
  if annotateVariants is not None and annotateVariants.isdigit():
   annotateVariants = int(annotateVariants)
  else:
   annotateVariants = 0
  aEngine.setup(engine, hintPLYs = annotateVariants, multiPV = int(self.settings['Menu/Engine']['numberOfAnnotations']))
  if aEngine.run(self.game, numberOfPlys = None):
   annotator = annotateEngine.Annotator(self.settings['Menu/Engine']['selectedEngine'])
   if self.settings['Menu/Engine']['blunderLimit'] is None:
    annotator.setBlunder(-float('inf'), addVariant = False)
   else:
    annotator.setBlunder(float(self.settings['Menu/Engine']['blunderLimit']), addVariant = True)
   self.game = annotator.apply(game = self.game, scoreListList = aEngine.scoreListList, pvListList = aEngine.pvListList)
   self.scorePlotGraphicsView.setGame(self.game)
   self.gameTreeViewWidget.setGame(self.game)
   self.gameHeaderTableView.setGame(self.game)
   self._gameChanged = True
  else:
   self.notifyError('Annotation failed')

 @PyQt5.QtCore.pyqtSlot(bool)
 def on_actionShow_Options_toggled(self, checked):
  self.notify('')
  self.boardGraphicsView.setDrawOptions(checked)
  self.settings['Menu/Game']['showOptions'] = str(checked)
  self.saveSettings()

 @PyQt5.QtCore.pyqtSlot(bool)
 def on_actionWarn_of_Danger_toggled(self, checked):
  self.notify('')
  self.boardGraphicsView.setWarnOfDanger(checked)
  self.settings['Menu/Game']['warnOfDanger'] = str(checked)
  self.saveSettings()

 @PyQt5.QtCore.pyqtSlot(bool)
 def on_actionFlip_Board_toggled(self, checked):
  self.notify('')
  self.boardGraphicsView.setFlipped(checked)
  
 @PyQt5.QtCore.pyqtSlot()
 def on_actionSelect_Header_Elements_triggered(self):
  self.notify('')
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
  self.notify('')
  hintsChecked = self.actionShow_Hints.isChecked()
  scoresChecked = self.actionShow_Scores.isChecked()
  self.settings['Menu/Engine']['showHints'] = str(hintsChecked)
  self.settings['Menu/Engine']['showScores'] = str(scoresChecked)
  self.saveSettings()
  if hintsChecked or scoresChecked:
   if self.settings['Menu/Engine']['searchDepth'] is None:
    self.notifyError('"Engine/Search Depth" undefined.')
   if self.debugEngine:
    logFunction = self.logSignal.emit
   else:
    logFunction = None
   self.hintEngine = chessengine.ChessEngine(
      self.engineDict[self.settings['Menu/Engine']['selectedEngine']], 
      limit = chess.engine.Limit(depth = self.settings['Menu/Engine']['searchDepth']), 
      log = logFunction)
   self.boardGraphicsView.setHint(enableHint = hintsChecked, enableScore = scoresChecked, engine = self.hintEngine)
   self.engineLabel.setText(self.settings['Menu/Engine']['selectedEngine'])
  else:
   self.hintEngine = None
   self.boardGraphicsView.setHint(enableHint = False, enableScore = False, engine = None)
   self.engineLabel.setText('---')

 @PyQt5.QtCore.pyqtSlot(bool)
 def on_actionShow_Hints_toggled(self, checked):
  self.show_HintsScores()
    
 @PyQt5.QtCore.pyqtSlot(bool)
 def on_actionShow_Scores_toggled(self, checked):
  self.show_HintsScores()
  
 @PyQt5.QtCore.pyqtSlot()
 def on_actionConfigureEngine_triggered(self):
  self.notify('')
  configForm = configureEngine.ConfigureEngine()
  newEngineDict = configForm.run(engineDict = self.engineDict, log = self.debugEngine)
  if newEngineDict is not None:
   self.engineDict = newEngineDict
   self.resetSelectEngine()
   configureEngine.saveEngineSettings(self.settings, self.engineDict)
   self.saveSettings()
   
 @PyQt5.QtCore.pyqtSlot(bool)
 def on_actionDebugEngine_toggled(self, checked):
  self.notify('')
  self.debugEngine = checked
  if self.hintEngine is not None:
   if self.debugEngine:
    logFunction = self.logSignal.emit
   else:
    logFunction = None
   self.hintEngine.setLog(logFunction)
  
 @PyQt5.QtCore.pyqtSlot()
 def on_actionAbout_triggered(self):
  self.notify('')
  self.aboutDialog.exec()
 
 @PyQt5.QtCore.pyqtSlot()
 def on_actionHelp_triggered(self):
  self.notify('')
  PyQt5.QtGui.QDesktopServices.openUrl(self.helpIndex)

 # ---------------------------------------------------------------------------

 @PyQt5.QtCore.pyqtSlot() 
 def on_actionCopy_FEN_triggered(self):
  self.notify('')
  fen = self.gameNode.board().fen()
  PyQt5.QtWidgets.QApplication.clipboard().setText(fen)

 @PyQt5.QtCore.pyqtSlot() 
 def on_actionPaste_FEN_triggered(self):
  self.notify('')
  if not self._allowNewGame():
   return
  fen = PyQt5.QtWidgets.QApplication.clipboard().text()
  try:
   board = chess.Board()
   board.set_fen(fen)
  except:
   self.notifyError('Improper FEN')
   return
  self.gameID = None
  self.game = chess.pgn.Game()
  self.gameNode = self.game
  self.game.headers['FEN'] = fen
  self._showEcoCode(self.game, fromBeginning = True)
  self.boardGraphicsView.setGame(self.game)
  self.gameTreeViewWidget.setGame(self.game)
  self.gameHeaderTableView.setGame(self.game)

 @PyQt5.QtCore.pyqtSlot() 
 def on_actionCopy_PGN_triggered(self):
  self.notify('')
  exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
  pgnString = self.game.accept(exporter)
  PyQt5.QtWidgets.QApplication.clipboard().setText(pgnString)

 @PyQt5.QtCore.pyqtSlot() 
 def on_actionPaste_PGN_triggered(self):
  self.notify('')
  if not self._allowNewGame():
   return
  self.gameID = None
  pgnString = PyQt5.QtWidgets.QApplication.clipboard().text()
  pgn = io.StringIO(pgnString)
  self.game = read_game(pgn)
  self.gameNode = self.game
  if len(self.game.errors) != 0:
   self.notifyError('Improper PGN')
   self.game = chess.pgn.Game()
  self._showEcoCode(self.game, fromBeginning = True)
  self.boardGraphicsView.setGame(self.game)
  self.gameTreeViewWidget.setGame(self.game)
  self.gameHeaderTableView.setGame(self.game)
  self.scorePlotGraphicsView.setGame(self.game)
  
 # ---------------------------------------------------------------------------

 @PyQt5.QtCore.pyqtSlot(int)
 def gameSelected(self, gameID):
  if not self._allowNewGame():
   return
  self.gameID = gameID
  self.game = self.gameList[gameID]
  self.gameNode = self.game
  try:
   self.notify('Loading game #{} ...'.format(self.gameID))
   self._showEcoCode(self.game, fromBeginning = True)
   self.boardGraphicsView.setGameNode(self.game)
   self.gameTreeViewWidget.setGame(self.game)
   self.gameHeaderTableView.setGame(self.game)
   self.scorePlotGraphicsView.setGame(self.game)
   self.setChessWindowTitle()
   self.notify('')
  except:
   self.notifyError('UIE: Improper game ="{}"'.format(self.game))

 @PyQt5.QtCore.pyqtSlot(chess.pgn.Headers)
 def gameHeadersChanged(self,  headers):
  self.notify('')
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
  self._gameChanged = True

 @PyQt5.QtCore.pyqtSlot(chess.pgn.GameNode)
 def newGameNode(self, gameNode):
  self.notify('')
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
    self.gameChanged(self.game)

  if gameNode.is_main_variation():
   self.gameTreeViewWidget.addGameNodes(gameNode)
  else:
   self.gameTreeViewWidget.addVariant(gameNode)
  self._gameChanged = True
   
 @PyQt5.QtCore.pyqtSlot(chess.pgn.GameNode)
 def gameNodeSelected(self, gameNode):
  self.notify('')
  self.gameNode = gameNode
  self.boardGraphicsView.setGameNode(self.gameNode)
  self.gameTreeViewWidget.selectNodeItem(self.gameNode)
  self.scorePlotGraphicsView.selectNodeItem(self.gameNode)

 @PyQt5.QtCore.pyqtSlot(chess.pgn.Game)
 def gameChanged(self, game):
  self.notify('')
  self.gameHeaderTableView.setGameResult(game.headers['Result'])
  self.gameTreeViewWidget.setGameResult(game.headers['Result'])
  self.game = game
  self._gameChanged = True
  
class MzClassApplication(PyQt5.QtWidgets.QApplication):
 def __init__(self, argv : List[str], notifyFct : Callable[[str], None] = print) -> None: 
  super(MzClassApplication, self).__init__(argv)
  self.notifyFct = notifyFct

 def notify(self, rec, ev):
  rc = super(MzClassApplication, self).notify(rec, ev)
  self.notifyFct('{} -> Type(Event)= {}, handled = {}'.format(rec, ev.type(),  rc))
  return rc

 # ---------------------------------------------------------------------------

import os,  os.path
import sys

def runMzChess(notifyFct : Optional[Callable[[str], None]] = None):
 os.chdir(os.path.expanduser('~'))
 if notifyFct is not None:
  qApp = MzClassApplication(sys.argv)
 else:
  qApp = PyQt5.QtWidgets.QApplication(sys.argv)
 chessMainWindow = ChessMainWindow()
 chessMainWindow.show()
 chessMainWindow.setup()
 qApp.exec_()

def _runMzChess():
 print('Hello, world')

if __name__ == "__main__":
 runMzChess(print)
