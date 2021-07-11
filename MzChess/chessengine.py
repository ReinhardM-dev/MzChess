'''A Qt-compatible interface similar to `chess.engine`_ 
 
.. _chess.engine: https://pypi.org/project/chess
'''

import os,  os.path
import time
import re
from typing import Any, Dict, Callable, Iterable, List, Optional, Tuple, Type, Union

import PyQt5.QtCore

import chess
import chess.engine

PGNCmd_REGEX = re.compile(r'\[(%[a-z]*)?[ ]+([^\n\t \]]+)\]')
PGNEval_REGEX = re.compile(r'\[(%|%eval)[ ]+([^\n\t \]]+)\]')

class ChessEngine(PyQt5.QtCore.QObject):
 '''A Universal Chess Interface (`UCI`_) engine using (`QProcess`_)

:param engine2Option: a pair of a path to the executable and *dict* of the changed options
:param limit: a limit definition for the engine (see `chess.engine.Limit`_)
:param timeout_msec: timeout for the engine to respond (should be at least 1000)
:param log: log for the engine's commands 
:param ChessEngine.bestMoveScoreSignal: ``pyqtSignal`` emitted when a best move is available
 
.. _UCI: http://wbec-ridderkerk.nl/html/UCIProtocol.html
.. _QProcess: https://doc.qt.io/qt-5/qprocess.html
.. _chess.engine.Limit: https://python-chess.readthedocs.io/en/latest/engine.html
 '''
 bestMoveScoreSignal : PyQt5.QtCore.pyqtSignal = PyQt5.QtCore.pyqtSignal(chess.Move, str)

 def __init__(self, engine2Option : Tuple[os.PathLike, Dict[str, Union[str, int, bool, None]]], 
   limit : chess.engine.Limit = chess.engine.Limit(depth = 10), 
   timeout_msec : int = 1000, 
   log : Optional[Callable[[str], None]] = None, 
   parent : Optional[PyQt5.QtCore.QObject] = None) -> None:
  super(ChessEngine, self).__init__(parent)
  executable, optionsDict = engine2Option
  if not (os.path.isfile(executable) and os.access(executable, os.X_OK )):
   raise IOError('ChessEngine: {} is not an executable'.format(executable))
  self.limit = limit
  self.setLog(log)
  self.timeout_msec = max(int(timeout_msec), 10)
  self.stdoutLines = list()
  self.p = PyQt5.QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
  self.p.readyReadStandardOutput.connect(self._fromStdout)
  self.p.readyReadStandardError.connect(self._fromStdout)
  self.stdout = ''
  self.stdoutLines = list()
  self.p.start(executable, PyQt5.QtCore.QIODevice.ReadWrite | PyQt5.QtCore.QIODevice.Text)
  while not self.p.waitForStarted(msecs = self.timeout_msec):
   self._log('ChessEngine: slow write, {} msec elapsed'.format(self.timeout_msec))
  self.readyok = True
  self._toStdin('uci')
  start = int(round(time.time() * 1000))
  loop = 1
  while 'idDict' not in vars(self) or 'optionsDict' not in vars(self):
   PyQt5.QtCore.QCoreApplication.processEvents()
   elapsed = int(round(time.time() * 1000)) - start
   if elapsed > 3*self.timeout_msec:
    self._log('ChessEngine: long wait for uci response, {}x looped, {} msec elapsed'.format(loop, elapsed))
    break
   loop += 1
  if self.isReady():
   for name, value in optionsDict.items():
    self.uciSetOption(name, value)
  self.isrunning = False
  self.playResult = None
  self.board = chess.Board()

 def setLog(self, log : Optional[Callable[[str], None]] = None) -> None:
  '''Sets the log for engine's commands

:param log: log for the engine's commands, default = None  
  '''
  if isinstance(log, bool):
   if log:
    self.notify = print
   else:
    self.notify = None
  else:
   self.notify = log

 def getScore(self, hintID : int = 0) -> Optional[int]:
  '''Delivers the score for a hint, if available

:param hintID: hint, i.e. alternative to be used (0 for best move)
:returns: score in centipawns or ``None``
  '''
  if   'info' not in vars(self.playResult) \
    or hintID >= len(self.playResult.info) \
    or 'score' not in self.playResult.info[hintID]:
   return None
  score = self.playResult.info[hintID]['score'].white()
  if isinstance(score, chess.engine.Cp):
   score = '{:+.1f}'.format(0.01 * score.score())
  elif score is not None:
   score = str(score)
  return score
  
 def _log(self, txt : str) -> None:
  if self.notify is not None:
   self.notify(txt)

 def _fromStdout(self) -> None:
  if 'stdout' not in vars(self):
   self.stdout = ''
  try:
   self.stdout += bytes(self.p.readAllStandardOutput()).decode('utf-8')
  except:
   return
  if not self.stdout.endswith('\n'):
   return
  self.stdoutLines += self.stdout.strip("\n").split("\n")
  self._log('ChessEngine/_fromStdout: stdout< {}'.format(self.stdout))
  self.stdout = ''
  if self.stdoutLines[-1] == 'uciok':
   self._parseHeader()
   self.readyok = True
   self.stdoutLines = list()
  elif self.stdoutLines[-1] == 'readyok':
   self.readyok = True
   self.stdoutLines = list()
  elif self.stdoutLines[-1].startswith('bestmove'):
   self._parseResult()
   score = self.getScore(hintID = 0)
   self.readyok = True
   self.stdoutLines = list()
   if len(self.playResult.info) == 1: 
    self.playResult.info = self.playResult.info[0]
   if self.playResult.move is not None:
    self.bestMoveScoreSignal.emit(self.playResult.move, score)
   elif score is not None:
    self.bestMoveScoreSignal.emit(chess.Move.null(), score)

 def _fromStderr(self) -> None:
  stderr = bytes(self.p.readAllStandardError()).decode('utf-8').strip("\n")
  self._log('ChessEngine/_fromStderr:???????????????\n <stderr: {} \n???????????????'.format(stderr))

 def _toStdin(self, txt : str) -> None:
  self._log('ChessEngine/_toStdin: stdin> {}, readyok = {}'.format(txt, self.readyok))
  if not self.readyok:
   return False
  self.readyok = False
  self.stdoutLines = list()
  self.p.write("{}\n".format(txt).encode('utf-8'))
  while not self.p.waitForBytesWritten(msecs = self.timeout_msec):
   self._log('ChessEngine/_toStdin: slow write, {} msec elapsed'.format(self.timeout_msec))
  return True
 
 def isReady(self) -> bool:
  '''Checks whether the engine is able to receive commands

:returns: boolean indicating the response
  '''
  return self.p.state() == PyQt5.QtCore.QProcess.Running and self.readyok
  
 #  Parser --------------------------------------------------------------------------------------

 def _parseHeader(self) -> None:
  self.idDict = dict()
  self.optionsDict = dict()
  for line in self.stdoutLines:
   tokens = line.split(" ")
   report = tokens.pop(0)
   if report == 'id':
    key = tokens.pop(0)
    if key != 'name' and key != 'author':
     raise ValueError("UIE: Unknown {} in header (expected name or author)".format(key))
    self.idDict[key] = ' '.join(tokens)
   elif report == 'option':
    self._parseOption(tokens)
   elif len(report.strip(' ')) > 0 and report != 'uciok':
    self._log("Extra line '{}'".format(line))

 def _parseOption(self, tokens) -> None:
  optDict = dict()
  minValue = None 
  maxValue = None
  name = None
  vtype = None
  while tokens:
   key = tokens.pop(0)
   if key == 'name':
    nameList = list()
    while tokens:
     part = tokens[0]
     if part in  ['type', 'default', 'min', 'max', 'var']:
      break
     tokens.pop(0)
     nameList.append(part)
    name = ' '.join(nameList)
   elif key == 'type':
    vtype = tokens.pop(0)
    if vtype not in ['check', 'spin', 'combo', 'button', 'string']:
     raise ValueError("UIE: Unexpected option type '{}'".format(vtype))
    if vtype == 'combo':
     optDict['varList'] = list()
    optDict[key] = vtype
   elif key == 'default':
    value = tokens.pop(0)
    if vtype == 'spin':
     optDict[key] = int(value)
    elif value == 'check':
     optDict[key] = value == 'true'
    else:
     optDict[key] = value
   elif key == 'min':
    minValue =  int(tokens.pop(0)) 
   elif key == 'max':
    maxValue =  int(tokens.pop(0)) 
   elif key == 'var':
    if 'varList' not in optDict:
     raise ValueError("UIE: var found, not type 'combo' ?!?")
    optDict['varList'].append(tokens.pop(0))
   elif key == 'string':
    if len(tokens) > 0:
     value = tokens.pop(0)
    else:
     value = ''
    if value == '<empty>':
     value = ''
    optDict[key] = value
  if name is None or vtype is None:
   raise ValueError("UIE: name and/or type record missing")
  if vtype == 'spin' and minValue is not None and maxValue is not None:
   optDict['range'] = range(minValue, maxValue+1)
  self.optionsDict[name] = optDict

 def _parseResult(self) -> None:
  depth = 0
  if self.playResult is None or 'move' in vars(self.playResult):
   self.playResult = chess.engine.PlayResult(None, None, draw_offered = None, resigned = None)
   self.playResult.info = list()
  for line in reversed(self.stdoutLines):
   tokens = line.split(" ")
   report = tokens.pop(0)
   if report == 'info':
    actInfo, newDepth = self._parseInfoline(tokens, depth)
    if newDepth is None or len(actInfo) == 0 or 'score' not in actInfo:
     continue
    if newDepth < depth:
     self.playResult.info = list(reversed(self.playResult.info))
     break
    depth = newDepth
    self.playResult.info.append(actInfo)
   elif report == 'bestmove':
    try:
     self.playResult.move = chess.Move.from_uci(tokens.pop(0))
    except:
     self.playResult.move = None
    if len(tokens) > 0 and tokens.pop(0) == 'ponder':
     try:
      self.playResult.ponder = chess.Move.from_uci(tokens.pop(0))
     except:
      self.playResult.ponder = None 

 def _parseInfoline(self, tokens, depth) -> Tuple[Dict[str, Any], int]:
   info = dict()
   actDepth = None
   while tokens:
    parameter = tokens.pop(0)
    if parameter == "string":
     info["string"] = " ".join(tokens)
     return dict(), depth
    elif parameter == "depth":
     actDepth = int(tokens.pop(0))
     info[parameter] = actDepth
    elif parameter in ["seldepth", "nodes", "multipv", "currmovenumber", "hashfull", "nps", "tbhits", "cpuload"]:
     info[parameter] = int(tokens.pop(0))  # type: ignore
    elif parameter == "time":
     info["time"] = int(tokens.pop(0)) // 1000.0
    elif parameter == "ebf":
     info["ebf"] = float(tokens.pop(0))
    elif parameter == "score":
     kind = tokens.pop(0)
     value = tokens.pop(0)
     if tokens and tokens[0] in ["lowerbound", "upperbound"]:
      info[tokens.pop(0)] = True  # type: ignore
     if kind == "cp":
      info["score"] = chess.engine.PovScore(chess.engine.Cp(int(value)), self.board.turn)
     elif kind == "mate":
      info["score"] = chess.engine.PovScore(chess.engine.Mate(int(value)), self.board.turn)
     else:
      raise ValueError("UIE: Unknown score kind {} in info (expected cp or mate)".format(kind))
    elif parameter == "currmove":
     info["currmove"] = chess.Move.from_uci(tokens.pop(0))
    elif parameter == "currline":
     cpunr = int(tokens.pop(0))
     currline = list()
     for n in range(cpunr):
      currline.append(tokens.pop(0))
     info["currline"] = currline
    elif parameter == "refutation":
     info["refutation"] = []
     while tokens:
      try:
       move = chess.Move.from_uci(tokens[0])
       tokens.pop(0)
       info["refutation"].append(move)
      except:
       break
    elif parameter == "pv":
     info["pv"] = list()
     while tokens:
      try:
       move = chess.Move.from_uci(tokens[0])
       tokens.pop(0)
       info["pv"].append(move)
      except:
       break
    elif parameter == "wdl":
     info["wdl"] = chess.engine.PovWdl(chess.engine.Wdl(int(tokens.pop(0)), int(tokens.pop(0)), int(tokens.pop(0))), self.board.turn)
   return info, actDepth

 #  Methods for use  --------------------------------------------------------------------------------------

 def uciNewGame(self, fen : Optional[str] = None, moves : List[chess.Move] = []) -> bool:
  '''Wrapper for the UCI *ucinewgame* command

:param fen: starting position in Forsyth-Edwards-Notation (FEN)
:param moves: list of moves to be applied
:returns: boolean indicating the success
  '''
  self.playResult = None
  if not self._toStdin('ucinewgame'):
   return False
  builder = ["position"]
  if fen is not None:
   self.board.set_fen(fen)
   builder.append("fen")
   builder.append(fen)
  else:
   self.board.set_fen(chess.STARTING_FEN)
   builder.append("startpos")
  for move in moves:
   builder.append(move.uci())
  self.readyok = True
  self._toStdin(' '.join(builder))
  self.readyok = True
  return True

 def uciSetOption(self, name : str, value : Union[bool, int,  str, None]) -> bool:
  '''Wrapper for the UCI *setoption* command

:param name: name of the option
:param value: value, type depends on name
:returns: boolean indicating the success
  '''
  if name not in self.optionsDict:
   raise ValueError('ChessEngine/setOption: {} is not a valid option name'.format(name))
  optDict = self.optionsDict[name]
  optType = optDict['type']
  builder = ['setoption']
  builder.append('name')
  builder.append(name)
  builder.append('value')
  if optType == 'button' and value is not None:
    raise ValueError('ChessEngine/setOption: option name {} expects no value'.format(name))
  elif optType == 'check':
   if not isinstance(value, bool):
    raise ValueError('ChessEngine/setOption: option name {} expects an boolean value'.format(name))
   builder.append(['false', 'true'][value])
  elif optType == 'spin':
   if isinstance(value, str):
    value = int(value)
   if 'range' in optDict and value not in optDict['range']:
    raise ValueError('ChessEngine/setOption: option name {}: value {} not in range {}'.format(name, value, optDict['range']))
   builder.append(str(value))
  elif optType == 'combo':
   if not isinstance(value, str):
    raise ValueError('ChessEngine/setOption: option name {} expects an string value'.format(name))
   if 'varList' in optDict and value not in optDict['varList']:
    raise ValueError('ChessEngine/setOption: option name {}: value {} not in list {}'.format(name, value, optDict['varList']))
   builder.append(value)
  elif Type == 'string':
   if not isinstance(value, str):
    raise ValueError('ChessEngine/setOption: option name {} expects an string value'.format(name))
   if len(value) == 0:
    value == '<empty>'
   builder.append(value)
  if self._toStdin(' '.join(builder)):
   self.readyok = True
  return self.readyok

 def uciGo(self, search_moves : Optional[Iterable[chess.Move]] = None, ponder : bool = False, infinite : bool = False) -> bool:
  '''Wrapper for the UCI *go* command

:param search_moves: list of moves to be searched
:param ponder: suggest a response to the *best-move*
:param infinite: improve the *best-move* continuously
:returns: boolean indicating the success
  '''
  builder = ["go"]
  if ponder:
   builder.append("ponder")
  if self.limit.white_clock is not None:
   builder.append("wtime")
   builder.append(str(max(1, int(self.limit.white_clock * 1000))))
  if self.limit.black_clock is not None:
   builder.append("btime")
   builder.append(str(max(1, int(self.limit.black_clock * 1000))))
  if self.limit.white_inc is not None:
   builder.append("winc")
   builder.append(str(int(self.limit.white_inc * 1000)))
  if self.limit.black_inc is not None:
   builder.append("binc")
   builder.append(str(int(self.limit.black_inc * 1000)))
  if self.limit.remaining_moves is not None and int(self.limit.remaining_moves) > 0:
   builder.append("movestogo")
   builder.append(str(int(self.limit.remaining_moves)))
  if self.limit.depth is not None:
   builder.append("depth")
   builder.append(str(max(1, int(self.limit.depth))))
  if self.limit.nodes is not None:
   builder.append("nodes")
   builder.append(str(max(1, int(self.limit.nodes))))
  if self.limit.mate is not None:
   builder.append("mate")
   builder.append(str(max(1, int(self.limit.mate))))
  if self.limit.time is not None:
   builder.append("movetime")
   builder.append(str(max(1, int(self.limit.time * 1000))))
  if infinite:
   builder.append("infinite")
  if search_moves is not None:
   builder.append("searchmoves")
   builder.extend(move.uci() for move in search_moves)
  if not self._toStdin(' '.join(builder)):
   return False

  if infinite:
   self.isrunning = True
   self.readyok = True
  return True

 def uciStop(self) -> bool:
  '''Wrapper for the UCI *stop* command to stop an infinite *go*

:returns: boolean indicating the success
  '''
  if not self.isrunning:
   return False
  return self._toStdin('stop')

 def uciQuit(self) -> None:
  'Terminate the engine'
  self._toStdin('quit')

 #  chess.engine like calls  --------------------------------------------------------------------------------------

 def startPlay(self) -> bool:
  '''Emits *uciGO* in *play* mode, i.e.g
  
  * *UCI_AnalyseMode = off*
  * *MultiPV = 1*, i.e. no alternative move suggestions

:returns: boolean indicating the success
  '''
  if 'MultiPV' in self.optionsDict:
   if not self.uciSetOption('MultiPV', 1):
    return False
  if 'UCI_AnalyseMode' in self.optionsDict:
   if not self.uciSetOption('UCI_AnalyseMode', False):
    return False
  return self.uciGo()

 def startAnalysis(self, multiPV : int = 1) -> bool:
  '''Emits *uciGO* in *analyse* mode, i.e.
  
  * *UCI_AnalyseMode = off*
  * *MultiPV =* ``multiPV``

:param multiPV: number of alternative move suggestions
:returns: boolean indicating the success
  '''
  if 'MultiPV' in self.optionsDict:
   if not self.uciSetOption('MultiPV', max(1, multiPV)):
    return False
  if 'UCI_AnalyseMode' in self.optionsDict:
   if not self.uciSetOption('UCI_AnalyseMode', True):
    return False
  return self.uciGo()

 def setELO(self, elo : Union[int, str]) -> bool:
  if not ('UCI_Elo' in self.optionsDict and 'UCI_LimitStrength' in self.optionsDict):
   return False
  eloDict = self.optionsDict['UCI_Elo']
  if elo == 'max':
   elo =eloDict['range'].stop - 1
  elif elo == 'min':
   elo = eloDict['range'].start
  if elo not in eloDict['range']:
   raise ValueError('ChessEngine: elo {} not in {}'.format(elo, eloDict['range']))
  if not self.uciSetOption('UCI_Elo', elo):
   return False
  if not self.uciSetOption('UCI_LimitStrength', True):
   return False
  self.readyok = True
  return True
  
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

if __name__ == "__main__":
 
 os.chdir('C:/Users/Reinh/chess_engines')
 stockfish12 = 'stockfish_12_win_x64_bmi2/stockfish_20090216_x64_bmi2.exe'
 togaII4 = 'TogaII40/Windows/TogaII_40_intelPGO_x64.exe'
 komodo12 = 'komodo-12.1.1_5a8fc2/Windows/komodo-12.1.1-64bit-bmi2.exe'
 fritz17 = 'Fritz17/Fritz17.exe'
 lcZero26 = 'lc0-v0.26.3-windows-gpu-opencl/lc0.exe'
 raubfischGTZ23 = 'RaubfischX44_and_GTZ23/GTZ23/RaubfischGTZ23_nn_sl-bmi2.exe'
 
 executable = stockfish12

 def waitForData(engine):
  for i in range(100):
   PyQt5.QtCore.QThread.msleep(engine.timeout_msec)
   PyQt5.QtCore.QCoreApplication.processEvents()
   if engine.isReady():
    return
   print('----> waiting {} * {} ms'.format(i, engine.timeout_msec))

 def printPlayResult(engine):
  playResult = engine.playResult
  rootBoard = chess.Board(engine.board.fen())
  print('{} : {}'.format('best move', playResult.move))
  if playResult.ponder is not None:
   print('{} : {}'.format('expected response', playResult.ponder))
  if isinstance(playResult.info, dict):
   infoList = [playResult.info]
  else:
   infoList = playResult.info
  for i, infoDict in enumerate(infoList):
   print('info #{}'.format(i+1))
   for key, value in infoDict.items(): 
    if key == 'pv':
     pvString = ''
     for n, moveList in enumerate(value):
      if not isinstance(moveList, list):
       moveList = [moveList]
      for move in moveList: 
       rootBoard.push(move)
       uciMove = move.uci()
       if rootBoard.is_checkmate():
        uciMove += '#'
       elif rootBoard.is_check():
        uciMove += '+'
       if engine.board.turn:
        if n == 0:
         pvString += '1.{}'.format(uciMove)
        elif n % 2 == 0:
         pvString += ' {}.{}'.format(n//2+1, uciMove)
        else:
         pvString += ' {}'.format(uciMove)
       else:
        if n == 0:
         pvString += '1...{}'.format(uciMove)
        elif n % 2 == 1:
         pvString += ' {}.{}'.format((n+1)//2+1, uciMove)
        else:
         pvString += ' {}'.format(uciMove)
       print('{} : {}'.format(key, pvString))
    elif value is not None: 
     print('{} : {}'.format(key, value))

 def runChessEngine():
  global executable
  fenList = [
  "3rr3/2p3p1/4N3/3b4/1p3P2/2PBB3/kPQ3PP/3R2K1 w - - 0 1", 
  "rn3r1k/pp4pp/2p1Q2N/q2np3/4N2P/2PP4/PP3P2/R3K2R w KQ - 0 1", 
  "r2rkn2/1R1N2p1/2p1B2p/4p1PP/p1P2b2/5P2/P3K3/1R6 w - - 0 1", 
  "2r4k/p2R4/1p2P3/5p2/3PbbpP/BP6/P1r5/4Q1K1 b - - 0 1"
  ]
  engine = ChessEngine(executable, limit = chess.engine.Limit(depth = 15),  log = True)
  waitForData(engine)
  for item in sorted(engine.idDict):
   print(' {} : {}'.format(item, engine.idDict[item]))
  print('Options:')
  for opt in sorted(engine.optionsDict):
   print(' {} : {}'.format(opt, engine.optionsDict[opt]))
  for fen in fenList:
   engine.uciNewGame(fen = fen)
   print('------------------------- startPlay -------------------------')
   engine.startPlay()
   waitForData(engine)
   printPlayResult(engine)
   print('----------------------- startAnalysis -----------------------')
   engine.startAnalysis(multiPV = 1)
   waitForData(engine)
   printPlayResult(engine)

 import sys
 from eco import ECODatabase 
 def scoreECOTable():
  global executable, basename, depth
  filename = '{}.tsv'.format(basename)
  print('Scoring {} -------------'.format(filename))
  eco = ECODatabase(tsvPattern = filename)
  fenList = eco.fen2Id().keys()
  engine = ChessEngine(executable, 
   limit = chess.engine.Limit(depth = depth),  
   timeout_msec = 300, 
   log = True)
  waitForData(engine)
  nTotal = len(fenList)
  fen2score = ['\t'.join(['fen',executable])]
  scmin, scmean, scmax = sys.maxsize//2, 0, -(sys.maxsize//2)
  for n, fen in enumerate(fenList):
   engine.startAnalysis(multiPV = 1)
   waitForData(engine)
   score = int(str(engine.playResult.info['score'].relative))
   scmin = min(scmin, score)
   scmean += score/nTotal
   scmax = max(scmax, score)
   fen2score.append('\t'.join([fen, str(score)]))
   print(' {} of {} completed'.format(n+1, nTotal))
  print('Scores {} <= {:.1f} <= {}'.format(scmin, scmean, scmax))

  fscFile = os.path.join(eco.ecoDirectory, '{}.fsc'.format(basename))
  with open(fscFile, mode='w') as f:
   f.write('\n'.join(fen2score))
  print('Result filed @ {}'.format(fscFile))

 app = PyQt5.QtCore.QCoreApplication(sys.argv)

 PyQt5.QtCore.QTimer.singleShot(10, runChessEngine)
 # PyQt5.QtCore.QTimer.singleShot(10, scoreECOTable)
 
 app.exec_()
 print('completed')
