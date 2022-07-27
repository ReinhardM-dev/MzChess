from typing import Callable, TextIO, List

import pytest

import os, os.path
from PyQt6 import QtCore

import MzChess
import chess

def runUciEngine(executable : str, fenList : List[str]) -> None:
 print('runUciEngine: {}\n fenList = {}'.format(executable, fenList))
 def waitForData(engine):
  for i in range(100):
   QtCore.QThread.msleep(engine.timeout_msec)
   QtCore.QCoreApplication.processEvents()
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
 
 # =====================================================================

 engine = MzChess.ChessEngine((executable,  dict()) , limit = chess.engine.Limit(depth = 15),  log = print)
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
 engine.kill()
 pytest.helpers.exitApp()

def test_uciEngine(qtbot, pytestconfig):
 fen = pytestconfig.getoption("--FEN")
 if fen is not None:
  fenList = [fen]
 else:
  fenList = [
  "3rr3/2p3p1/4N3/3b4/1p3P2/2PBB3/kPQ3PP/3R2K1 w - - 0 1", 
  "rn3r1k/pp4pp/2p1Q2N/q2np3/4N2P/2PP4/PP3P2/R3K2R w KQ - 0 1", 
  "r2rkn2/1R1N2p1/2p1B2p/4p1PP/p1P2b2/5P2/P3K3/1R6 w - - 0 1", 
  "2r4k/p2R4/1p2P3/5p2/3PbbpP/BP6/P1r5/4Q1K1 b - - 0 1"
  ]
 uciEngine = pytestconfig.getoption("--uciEngine")
 if uciEngine is None:
  pytest.skip('uciEngine not specified')
  return
 if not os.path.isabs(uciEngine): 
  home = pytestconfig.getoption("--home")
  uciEngine = os.path.join(home, uciEngine) 
 if not os.path.exists(uciEngine):
  raise IOError('Engine {} not found'.format(uciEngine))
  return
 runUciEngine(uciEngine, fenList)
 return

