'''
Game Header Editor
=====================

The game header editor is a 2-column table which assigns to values to header elements.
The `PGN`_ standard lists the supported header elements. 
The header elements of 7-tag roster, 
i.e. *Event*, *Site*, *Date*, *Round*, *White*, *Black* and *Result*, are mandatory.

The *Game/Select Header Elements ...* menu entry opens a dialog to add/remove header elements.

|HeaderEditor|

Depending on the type, the values are edited using a *text*, *date* and *time* editors.
To avoid inconsistent header data, the following header elements are readonly:

* *Result*, *Annotator*, *PlyCount*
* any kind of opening information, i.e. *Opening*, *Variation*, *SubVariation*, *ECO*, *NIC*


.. |HeaderEditor| image:: headerEditor.png
  :width: 800
  :alt: Header Editor
.. _PGN: https://github.com/fsmosca/PGN-Standard
'''
from typing import Optional, List, Tuple, Any
import copy
import datetime
from enum import IntEnum, unique
import sys,  os.path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtCore
else:
 from PyQt6 import QtWidgets, QtCore

import chess, chess.pgn

@unique
class KeyType(IntEnum):
 STR = 0
 INT = 1
 LABEL = 2
 DATE = 3
 TIME = 4
 EVENT = 5
 SITE = 6
 PLAYER = 7
 TITLE = 8

class GameHeaderView(QtWidgets.QTableWidget):
 '''Game Header Editor object
 '''
 stdKey2ValueTypeDict = {
   # seven tag roster
   "Event" : ("?", KeyType.EVENT),
   "Site" : ("?", KeyType.SITE),
   "Date" : ("????.??.??", KeyType.DATE),
   "Round" : ("?", KeyType.STR),
   "White" : ("?", KeyType.PLAYER),
   "Black" : ("?", KeyType.PLAYER),
   "Result" : ("*", KeyType.LABEL), 
   # player related information 
   "WhiteTitle" : ("", KeyType.TITLE), 
   "BlackTitle" : ("", KeyType.TITLE), 
   "WhiteElo" : ("", KeyType.INT), 
   "BlackElo" : ("", KeyType.INT), 
   "WhiteUSCF" : ("", KeyType.INT), 
   "BlackUSCF" : ("", KeyType.INT), 
   "WhiteNA" : ("", KeyType.STR), 
   "BlackNA" : ("", KeyType.STR), 
   # event related information 
   "EventDate" : ("", KeyType.DATE),
   "EventSponsor" : ("", KeyType.STR),
   "Section" : ("", KeyType.STR),
   "Stage" : ("", KeyType.STR),
   "Board" : ("", KeyType.INT),
   # opening information 
   "Opening" : ("", KeyType.LABEL), 
   "Variation" : ("", KeyType.LABEL), 
   "SubVariation" : ("", KeyType.LABEL), 
   "ECO" : ("", KeyType.LABEL), 
   "NIC" : ("", KeyType.LABEL), 
   # time
   "Time" : ("??:??:??", KeyType.TIME),
   "UTCTime" : ("??:??:??", KeyType.TIME),
   "UTCDate" : ("????.??.??", KeyType.DATE),
   # time control
   "TimeContol" : ("?", KeyType.STR), 
   # alternative starting positions
   "FEN" : (chess.STARTING_FEN, KeyType.LABEL), 
   # game termination
   "Termination" : ("", KeyType.STR), 
   # miscellaneous
   "Annotator" : ("", KeyType.LABEL), 
   "PlyCount" : ("0", KeyType.LABEL)}
 gameResult = ["1-0", "0-1", "1/2-1/2", "*"]

 def __init__(self, parent = None) -> None:
  super(GameHeaderView, self).__init__(parent)
  self.notifyGameHeadersChangedSignal = None
  self.gameResultLabel = None
  self.eventList = ['?']
  self.siteList = ['?']
  self.playerList = ['?']
  
 def setup(self, notifyGameHeadersChangedSignal  : Optional[QtCore.pyqtSignal] = None, 
                 eventList : List[str] = list(), siteList : List[str] = list(), playerList : List[str] = list()) -> None:
  self.eventList = ['?'] + eventList
  self.siteList = ['?'] + siteList
  self.playerList = ['?'] + playerList
  self.notifyGameHeadersChangedSignal = notifyGameHeadersChangedSignal
  self.resetGame()
 
 @staticmethod
 def headerElements(withoutSevenTagRoster : bool = False) -> List[str]:
  '''Get game header elements

:param withoutSevenTagRoster: returns only the optional header elements
:returns: list of header elements
  '''
  if not withoutSevenTagRoster:
   hElements = GameHeaderView.stdKey2ValueTypeDict.keys()
  else:
   hElements = list()
   for el in GameHeaderView.stdKey2ValueTypeDict.keys():
    if el not in chess.pgn.Headers():
     hElements.append(el)
  return hElements

 def _createCompleteEdit(self, selList : List[str], value : Any) -> QtWidgets.QLineEdit:
  completer = QtWidgets.QCompleter(selList)
  completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
  completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
  completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.InlineCompletion)
  item = QtWidgets.QLineEdit(str(value))
  item.setCompleter(completer)
  item.editingFinished.connect(self.on_editingFinished)
  return item

 def _showTable(self, keyValueTypeList : List[Tuple[str, str, KeyType]]) -> None:
  self.horizontalHeader().hide()
  self.verticalHeader().hide()
  self.setRowCount(len(keyValueTypeList))
  self.setColumnCount(2)
  for row, self.defaultKeyValueType in enumerate(keyValueTypeList):
   key, value, type = self.defaultKeyValueType
   item = QtWidgets.QLabel(str(key))
   self.setCellWidget(row, 0, item)
  test = QtWidgets.QLabel()
  zeroWidth = test.fontMetrics().size(QtCore.Qt.TextFlag.TextSingleLine, '0').width()
  self.setColumnWidth(0, 20*zeroWidth)
  
  self.itemList = list()
  for row, self.defaultKeyValueType in enumerate(keyValueTypeList):
   key, value, type = self.defaultKeyValueType
   if type == KeyType.STR:
    item = QtWidgets.QLineEdit(str(value))
    item.editingFinished.connect(self.on_editingFinished)
   elif type == KeyType.LABEL:
    item = QtWidgets.QLabel(str(value))
    item.setStyleSheet("background-color : white; color : gray;")
    if key == 'PlyCount':
     self.plyCountLabel = item
    elif key == 'Result':
     self.gameResultLabel = item
   elif type == KeyType.DATE:
    try:
     datetime.date.fromisoformat(value.replace('.','-'))
     date = QtCore.QDate.fromString(value, "yyyy.MM.dd")
    except:
     date = QtCore.QDate.currentDate()
     self.gameHeaders[key] = date.toString('yyyy.MM.dd')
    item = QtWidgets.QDateEdit(date)
    item.dateChanged.connect(self.on_dateChanged)
   elif type == KeyType.TIME:
    try:
     _time = QtCore.QTime.fromString(value, "hh:mm:ss")
    except:
     _time = QtCore.QTime.currentTime()
    item = QtWidgets.QTimeEdit(_time)
    item.timeChanged.connect(self.on_timeChanged)
   elif type == KeyType.INT:
    item = QtWidgets.QSpinBox()
    item.setMaximum(4000)
    item.setSpecialValueText('-')
    item.valueChanged.connect(self.on_spinBox_changed)
   elif type == KeyType.EVENT:
    item = self._createCompleteEdit(self.eventList, value)
   elif type == KeyType.SITE:
    item = self._createCompleteEdit(self.siteList, value)
   elif type == KeyType.PLAYER:
    item = self._createCompleteEdit(self.playerList, value)
   else:
    continue
   
   self.itemList.append(item)
   self.setCellWidget(row, 1, item)
  self.update()
  
 def _getHeaders(self) -> chess.pgn.Headers:
  return self.gameHeaders

 def resetGame(self) -> None:
  '''Resets editor to standard header
  '''
  self.setGame(chess.pgn.Game())

 def setPlyCount(self, newCount : int) -> None:
  '''Sets the 'PlyCount' header element, if selected 

:param newCount: actual number of halfmoves
  '''
  if self.plyCountLabel is not None:
   self.gameHeaders['PlyCount'] = newCount
   self.plyCountLabel.setText(str(newCount))

 def setGameResult(self, result : str) -> None:
  '''Sets the 'Result' header element

:param result: one out of *1-0*, *0-1*, *1/2-1/2*, *\**
  '''
  if result not in self.gameResult:
   result = self.gameResult[3]
  self.gameHeaders['Result'] = result
  self.gameResultLabel.setText(result)

 def setGame(self, game : chess.pgn.Game) -> None:
  '''Edit the header of a game. It corrects the following header elements
  
  * *Result*
  * *FEN*, if available
  * *PlyCount*, if available

:param game: game to be edited
  '''
  self.clear()
  self.gameHeaders = copy.deepcopy(game.headers)
  for key, defValue in chess.pgn.Headers().items():
   if key not in self.gameHeaders:
    self.gameHeaders[key] = defValue
  if 'FEN' in self.gameHeaders:
   self.gameHeaders['FEN'] = game.board().fen()
  if self.gameHeaders['Result'] not in self.gameResult:
   value = self.gameResult[3]
  plyCount = 0
  gameNode = game
  while gameNode is not None:
   plyCount += 1
   gameNode = gameNode.next()
  if 'PlyCount' in self.gameHeaders:
   self.gameHeaders['PlyCount'] = str(plyCount)
  keyValueTypeList = list()
  for key, value in self.gameHeaders.items():
   if key in self.stdKey2ValueTypeDict:
    type = self.stdKey2ValueTypeDict[key][1]
   else:
    key = '??? {} ???'.format(key)
    type = KeyType.STR
   keyValueTypeList.append((key, value, type))
  self._showTable(keyValueTypeList)
 
 def _getKV(self) -> Tuple[int, str, QtWidgets.QLineEdit]:
  item = self.sender()
  row = self.itemList.index(item)
  key = self.cellWidget(row, 0).text()
  return key, self.cellWidget(row, 1)
  
 @QtCore.pyqtSlot()
 def on_editingFinished(self):
  key, valueItem = self._getKV()
  text = valueItem.text().strip(' \t\n')
  self.gameHeaders[key] = text
  self._emitHeader()
  
 @QtCore.pyqtSlot(QtCore.QDate)
 def on_dateChanged(self, date):
  key, _ = self._getKV()
  self.gameHeaders[key] = date.toString('yyyy.MM.dd')
  self._emitHeader()

 @QtCore.pyqtSlot(QtCore.QTime)
 def on_timeChanged(self, _time):
  key, _ = self._getKV()
  self.gameHeaders[key] = _time.toString('hh:mm:ss')
  self._emitHeader()

 @QtCore.pyqtSlot(int)
 def on_spinBox_changed(self, value):
  key, _ = self._getKV()
  if value != 0:
   self.gameHeaders[key] = str(value)
  else:
   self.gameHeaders[key] = ''
  self._emitHeader()
   
 def _emitHeader(self) -> None:
  for key, value in self.gameHeaders.items():
   if len(value) == 0:
    del self.gameHeaders[key]
  if self.notifyGameHeadersChangedSignal is not None:
   self.notifyGameHeadersChangedSignal.emit(self.gameHeaders)
  
if __name__ == "__main__":
 import io, sys
 from pgnParse import read_game

 if True:
  newData = """[Event "matein2"]
[Site "problem solved"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Time "??:??:??"]
[FEN "1k6/Rp1K4/1P5P/8/P7/3pP3/1p1P4/8 w - - 0 1"]
  
1.h7 b1=Q! $20 {[% -4.80]} 2.h8=R# *"""
 else:
  ps = "C:/Users/Reinh/OneDrive/Dokumente/Schach/ps.pgn"
  with open(ps, mode = 'r',  encoding = 'utf-8') as f:
   newdata = f.read()
 
 pgn = io.StringIO(newData)
 game = read_game(pgn)
 app = QtWidgets.QApplication([])
 tbl = GameHeaderView()
 tbl.setup(
   eventList = ["Wöchentliche Schachmeisterschaften"], 
   siteList = ["München GER", "Internet"], 
   playerList = ["März, Reinhard", "Schlüter, Paul"])
 tbl.setGame(game)
 tbl.resize(360,240)
 tbl.show()
 sys.exit(app.exec_())
