'''Annotation support

.. _fiekas.eco: https://github.com/niklasf/eco
'''

from typing import Callable, List, Union, Optional, Tuple
import sys
import os.path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtCore
else:
 from PyQt6 import QtCore

import chess, chess.pgn
from chessengine import ChessEngine, PGNEval_REGEX

class Annotator():
 '''A Annotator class applying 

:param name: name of the annotation engine
:param notifyFunction: print-like function used for notification
 '''

 def __init__(self, name : str,  notifyFunction : Optional[Callable[[str], None]] = None) -> None:
  self.name = name
  self.notifyFunction = notifyFunction
  self.posScNagAV : List[Tuple[float, int, bool]] = list()
  self.negScNagAV : List[Tuple[float, int, bool]] = list()
 
 def _setClass(self, nagCode : int, score : float, addVariant : bool):
  if score > 0:
   newList = [(score, nagCode, addVariant)]
   for scNagAv in self.posScNagAV:
    if scNagAv[1] != nagCode:
     newList.append(scNagAv)
   self.posScNagAV = sorted(newList, reverse = True, key = lambda el : el[1])
  else:
   newList = [(score, nagCode, addVariant)]
   for scNagAv in self.negScNagAV:
    if scNagAv[1] != nagCode:
     newList.append(scNagAv)
   self.negScNagAV = sorted(newList, reverse = False, key = lambda el : el[1])
  
 # ---------------------------------------------------------------

 def setBlunder(self, score : float, addVariant : bool = True) -> None:
  '''Sets the condition for a blunder move (NAG: $4)
  
:param score: score limit (score < 0 expected)
:param addVariant: add a variant in below score
  '''
  if score > 0:
   score = -score
  self._setClass(chess.pgn.NAG_BLUNDER, score, addVariant)

 def setDubiousMove(self, score : float, addVariant : bool = False) -> None:
  '''Sets the condition for a dubious move (NAG: $6)
  
:param score: score limit (score < 0 expected)
:param addVariant: add a variant in below score
  '''
  if score > 0:
   score = -score
  self._setClass(chess.pgn.NAG_DUBIOUS_MOVE, score, addVariant)

 def setPoorMove(self, score : float, addVariant : bool = False) -> None:
  '''Sets the condition for a poor move (NAG: $2)
  
:param score: score limit (score < 0 expected)
:param addVariant: add a variant in below score
  '''
  if score > 0:
   score = -score
  self._setClass(chess.pgn.NAG_MISTAKE, score, addVariant)

 def setBrillantMove(self, score : float, addVariant : bool = False) -> None:
  '''Sets the condition for a brilliant move (NAG: $3)
  
:param score: score limit (score > 0 expected)
:param addVariant: add a variant in below score
  '''
  if score < 0:
   score = -score
  self._setClass(chess.pgn.NAG_BRILLIANT_MOVE, score, addVariant)

 def setSpeculativeMove(self, score : float, addVariant : bool = False) -> None:
  '''Sets the condition for a speculative move (NAG: $5)
  
:param score: score limit (score > 0 expected)
:param addVariant: add a variant in below score
  '''
  if score < 0:
   score = -score
  self._setClass(chess.pgn.NAG_SPECULATIVE_MOVE, score, addVariant)

 def setGoodMove(self, score : float, addVariant : bool = False) -> None:
  '''Sets the condition for a good move (NAG: $1)
  
:param score: score limit (score > 0 expected)
:param addVariant: add a variant in below score
  '''
  if score < 0:
   score = -score
  self._setClass(chess.pgn.NAG_GOOD_MOVE, score, addVariant)
  
 # ---------------------------------------------------------------

 def _nagAv(self, whiteScore : str, lastWhiteScore : str, turn):
  if whiteScore is not None and len(whiteScore) > 0:
   try: 
    score = float(whiteScore)
   except:
    score = 1001 - float(whiteScore[1:])
   try: 
    lastScore = float(lastWhiteScore)
   except:
    lastScore = 1001 - float(lastWhiteScore[1:])
   if not turn:
    score = -score
    lastScore = -lastScore
   if score > 0 and len(self.posScNagAV) > 0:
    for sc, nag, av in self.posScNagAV:
     if lastScore - score > sc:
      return ([nag], av)
   elif score < 0 and len(self.negScNagAV) > 0:
    for sc, nag, av in self.negScNagAV:
     if lastScore - score < sc:
      return ([nag], av)
  return (list(), False)
   
 def _replaceScore(self, comment : str, newWhiteScore : float):
  while True:
   match = PGNEval_REGEX.search(comment)
   if match is None:
    break
   comment = comment.replace(match.group(0),'')
  comment = '[%eval {}] {}'.format(newWhiteScore, comment)
  return comment 

 @staticmethod
 def remove(game : chess.pgn.Game, comments : bool = False, variants : bool = False) -> chess.pgn.Game:
  '''Remove certain items from a game
  
:param game: game to process
:param comments: If True, remove all comments
:param variants: If True, remove all variants
  '''

  gameNode = game
  while gameNode is not None:
   if comments:
    gameNode.comment = ''
   if variants and len(gameNode.variations) > 0:
    gameNode.variations = [gameNode.variations[0]]
   gameNode = gameNode.next()
  return game
  
 def apply(self, 
                game : Union[chess.pgn.Game, chess.pgn.GameNode] = chess.pgn.Game(), 
                scoreListList : List[List[float]] = list(), 
                pvListList : Optional[List[List[List[chess.Move]]]] = None, 
                forceHints : bool = False) -> bool:
  '''Apply the results of AnnotateEngine.run to a game 
  
:param game: game or gameNode where annotation starts (required)
:param scoreListList: for each move a list of scores for each variant, see AnnotateEngine.scoreListList
:param pvListList: for each move a list of lists of moves for each variant, see AnnotateEngine.pvListList
:param forceHints: force the creation of variants independent of the setXX definitions

:return: boolean indicating whether any hints are added
  '''
  
  assert len(scoreListList) > 0, 'Empty scoreListList detected'
  if pvListList is not None:
   if len(pvListList) == 0:
    pvListList = None
   else:
    assert len(scoreListList) == len(pvListList), 'len(scoreListList) == len(pvListList) required'
  if isinstance(game, chess.pgn.Game):
   gameNode = game.next()
   if len(self.name) > 0:
    game.headers['Annotator'] = self.name
  else:
   gameNode = game
  lastWsc = 0
  pvList = None
  anyHintsAdded = False
  for plyID, scoreList in enumerate(scoreListList):
   if gameNode is None:
    break
   if pvListList is not None and plyID > 0:
    pvList = pvListList[plyID - 1]
   else:
    pvList = None
   wsc = scoreList[0]
   nag, av = self._nagAv(wsc, lastWsc, gameNode.turn())
   lastWsc = wsc
   gameNode.nags = nag
   gameNode.comment = self._replaceScore(gameNode.comment, wsc)
   addHints = (av or forceHints) and pvList is not None
   if self.notifyFunction is not None:
    self.notifyFunction('{}. {}: score = {}, nags = {}'.format(plyID, gameNode.move, wsc, nag))
   if addHints:
    anyHintsAdded = True
    for n, score in enumerate(scoreList):
     if self.notifyFunction is not None:
      self.notifyFunction('--> {}'.format(pvList[n]))
     gameNode.parent.add_line(pvList[n])
   gameNode = gameNode.next()
  return anyHintsAdded

class AnnotateEngine(QtCore.QObject):
 '''A wrapper class collecting score and variant (pv) data from an engine 

:param notifyFunction: print-like function used for notification
 '''
 def __init__(self, 
                    notifyFunction : Optional[Callable[[str], None]] = None, 
                    parent : Optional[QtCore.QObject] = None) -> None:
  super(AnnotateEngine, self).__init__(parent)
  self.notifyFunction = notifyFunction

 def setup(self, 
                engine : ChessEngine, 
                hintPLYs : int = 0, 
                multiPV : int = 1) -> None:
  '''Setup for operation

:param engine: engine used for annotation
:param hintPLYs: number of half moves (plys) in variants. Suppress hints by setting hintPLYs == 0 
:param multiPV: number of variants
  '''
  assert hintPLYs >= 0
  assert multiPV > 0
  self.halfMoveID = 0
  self.engine = engine
  self.engine.bestMoveScoreSignal.connect(self._bestMoveScoreAvailable)
  self.hintPLYs = hintPLYs
  self.multiPV = multiPV

 @QtCore.pyqtSlot(chess.Move, str)
 def _bestMoveScoreAvailable(self, move : chess.Move, score : str):
  if len(score) == 0:
   score = None
  if self.notifyFunction is not None:
   if self.gameNode.move is not None:
    san = self.gameNode.san()
   else:
    san = None
   if not self.gameNode.turn():
    moveText = '{}. {}'.format(self.halfMoveID//2 + 1, san)
   else:
    moveText = '... {}'.format(san)
   self.notifyFunction('{}: score = {}'.format(moveText, score))
  self.halfMoveID += 1
  scoreList = list()
  pvList = list()
  if not isinstance(self.engine.playResult.info, list):
   self.engine.playResult.info = [self.engine.playResult.info]
  for hintID, info in enumerate(self.engine.playResult.info):
   if self.hintPLYs > 0:
    if 'pv' in info:
     pvList.append(info['pv'][:self.hintPLYs])
    else:
     pvList.append([])
   scoreList.append(self.engine.getScore(hintID = hintID))
  self.scoreListList.append(scoreList)
  if self.hintPLYs > 0:
   self.pvListList.append(pvList)
  if (self.numberOfPlys is not None and len(self.scoreListList) >= self.numberOfPlys) or not self._startNext():
   return
 
 def _startNext(self, isNew : bool = False) -> bool:
  if not isNew:
   self.gameNode = self.gameNode.next()
  if self.gameNode is None:
   return False
  self.engine.uciNewGame(fen = self.gameNode.board().fen())
  return self.engine.startAnalysis(multiPV = self.multiPV)
  
 def run(self, game : Union[chess.pgn.Game, chess.pgn.GameNode], numberOfPlys : Optional[int] = None) -> bool:
  '''Runs the engine for a whole game or a gameNode

:param game: game or gameNode
:param numberOfPlys: number of half moves to analyse, ``None`` means analysis of the rest of the game
:returns: True, if successful
  '''
  if isinstance(game, chess.pgn.Game):
   self.gameNode = game.next()
  else:
   self.gameNode = game
  self.numberOfPlys = numberOfPlys
  self.scoreListList = list()
  if self.hintPLYs > 0:
   self.pvListList = list()
  else:
   self.pvListList = None
  if not self._startNext(isNew = True):
   return False
  while (self.numberOfPlys is None or len(self.scoreListList) < self.numberOfPlys) and self.gameNode is not None:
   QtCore.QCoreApplication.processEvents()
  return True

if __name__ == "__main__":
 import os, sys
 import pickle
 import argparse
 import configparser
 import chess.pgn
 import configureEngine
 from pgnParse import read_game

 app = QtCore.QCoreApplication(sys.argv)

 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 os.chdir(fileDirectory)
 parser = argparse.ArgumentParser(description='PGN Parser: test')
 
 parser.add_argument("pgnFile", help = "PGN-File")
 parser.add_argument("--encoding",  metavar = 'encoding',  default = 'u', 
   choices=['u', 'utf-8-sig', 'i', 'iso-8859-1', 'a', 'ascii'], 
   help="target of parsing (g - games, h - headers, s - skip every second game, b - board, l - lexical analysis only)")
 parser.add_argument("--gameID", metavar = 'gameID', type = int, default=0, help="ID of the game to be used")
 parser.add_argument("--plyID", metavar = 'plyID', type = int, default=0, help="ID of the game to be used")
 parser.add_argument("--multiPV", metavar = 'multiPV', type = int, default=1, help="ID of the game to be used")
 parser.add_argument("--engine", metavar = 'engine', type = str, help="ID of the game to be used")
 parser.add_argument("-debug", action = 'store_true', default = False, help = "Enable Debugging")

 args = parser.parse_args()
 assert args.pgnFile is not None, 'pgnFile is required'
 encoding = args.encoding[0]
 if encoding == 'u':
  encoding = 'utf-8-sig'
 elif encoding == 'i':
  encoding = 'iso-8859-1'
 elif encoding == 'a':
  encoding = 'ascii'

 settingsFile = os.path.join(fileDirectory, 'settings.ini')
 settings = configparser.ConfigParser(delimiters=['='], allow_no_value=True)
 settings.optionxform = str
 settings.read(settingsFile, encoding = 'utf-8')
 engineDict = configureEngine.loadEngineSettings(settings)
 if args.engine is None:
  selectedEngine = settings['Menu/Engine']['selectedEngine']
 else:
  selectedEngine = args.engine
 assert selectedEngine in engineDict, 'Unexpected engine {} (must be out of {})'.format(selectedEngine,  engineDict)
 executable = engineDict[selectedEngine]

 engine = ChessEngine(executable, limit = chess.engine.Limit(depth = 15),  log = False)
 
 _,  ext = os.path.splitext(args.pgnFile)
 assert ext in ['.ppgn', '.pgn'], 'Unexpected file type {} of {}'.format(ext, args.pgnFile)
 
 if ext == '.ppgn':
  with open(args.pgnFile, mode = 'rb') as f:
   gameList = pickle.load(f)
   game = gameList[args.gameID]
 else:
  pgn = open(args.pgnFile, mode = 'r',  encoding = encoding)
  for n in range(args.gameID + 1):
   game = read_game(pgn)
 
 annotateEngine = AnnotateEngine(notifyFunction = print)
 annotateEngine.setup(engine, hintPLYs = 3, multiPV = args.multiPV)

 if args.plyID <= 0:
  rc = annotateEngine.run(game)
  gameNode = game
  forceHints = False
 else:
  gameNode = game
  for n in range(args.plyID):
   gameNode = gameNode.next()
  rc = annotateEngine.run(gameNode.parent, numberOfPlys = 2)
  forceHints = True
  
 if rc:
  annotator = Annotator(selectedEngine, notifyFunction = print)
  annotator.setBlunder(1.0, addVariant = True)
  annotator.apply(game = gameNode, 
                        scoreListList = annotateEngine.scoreListList, 
                        pvListList = annotateEngine.pvListList, 
                        forceHints = forceHints)
  exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
  pgnString = game.accept(exporter)
  print(pgnString)
  base, _ = os.path.splitext(args.pgnFile)
  with open('{}_new.pgn'.format(base), "w", encoding = 'iso-8859-1') as f:
   f.write(pgnString)
 
 app.exec()
 print('completed')
