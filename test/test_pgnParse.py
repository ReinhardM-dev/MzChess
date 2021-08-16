from typing import Callable, TextIO, List

import pytest
import os, os.path

import MzChess
import chess

def test_FEN(pytestconfig):
 specifiedFEN = pytestconfig.getoption('FEN')
 if specifiedFEN is None:
  pytest.skip('FEN not specified')
  return
 MzChess.checkFEN(specifiedFEN)

def test_pgnLexer(pytestconfig):
 if 'l' not in pytestconfig.getoption('target'):
  pytest.skip('Lexer test not activated')
  return
 pgn = pytest.helpers.findPGNTextIO(pytestconfig)
 lexer = MzChess.PGNLexer(bufsize = 4096, debug =  pytestconfig.getoption('debug'), optimize = False)
 tok = lexer.newGame(pgn)
 lexer.dumps(tok = tok, notify = print)

def test_readGame(pytestconfig):
 def runNode(readFct : Callable, f : TextIO,  gameID : int):
  try:
   node = readFct(f)
   print('node #{}, fct = {} -> {}'.format(gameID, readFct, repr(node)))
  except Exception as error:
   node = None
   print('node #{}: fct = {} failed -> {}'.format(gameID,readFct, error))
  return node
  
 def cmpGameNodes(chessNode, newNode):
  if isinstance(chessNode, bool) or isinstance(newNode, bool):
   context = 'Skipped game: chess.pgn: {}, MzChess = {}'.format(chessNode, newNode)
   assert chessNode == newNode, context
  elif isinstance(chessNode, chess.pgn.Headers) or isinstance(newNode, chess.pgn.Headers):
   context = 'Headers: chess.pgn: {}, MzChess = {}'.format(chessNode, newNode)
   assert chessNode == newNode, context
  elif isinstance(chessNode, chess.Board) or isinstance(newNode, chess.Board):
   context = 'Board: chess.pgn: {}, MzChess = {}'.format(chessNode.fen(), newNode.fen())
   assert chessNode.fen() == newNode.fen(), context
  else:
   if isinstance(chessNode, chess.pgn.Game) and isinstance(newNode, chess.pgn.Game):
    context = 'Game Headers: chess.pgn: {}, MzChess = {}'.format(chessNode.headers, newNode.headers)
    assert chessNode.headers == newNode.headers, context
   else:
    context = 'Move: chess.pgn: {}, MzChess = {}'.format(repr(chessNode), repr(newNode))
    assert chessNode.move.uci() == newNode.move.uci(), context
   assert chessNode.comment == newNode.comment, 'Comment: chess.pgn: "{}", MzChess = "{}" => {}'.format(chessNode.comment, newNode.comment, context)
   assert chessNode.nags == newNode.nags, 'Nags: chess.pgn: {}, MzChess = {} => {}'.format(sorted(chessNode.nags), sorted(newNode.nags), context)
   assert len(chessNode.variations) == len(newNode.variations), 'nVariations: chess.pgn: {}, MzChess = {} => {}'.format(len(chessNode.variations), len(newNode.variations), context)
   for subNode1, subNode2 in zip(chessNode.variations, newNode.variations):
    cmpGameNodes(subNode1, subNode2)
    
 # ===============================================================================

 targets = pytestconfig.getoption('target')
 anyExecuted = False
 for target in targets:
  pgn = pytest.helpers.findPGNTextIO(pytestconfig)
  newRead2 = None
  oldRead2 = None
  if target == 'g':
   newRead1 = MzChess.read_game
   oldRead1 = chess.pgn.read_game
  elif target == 'h':
   newRead1 = MzChess.read_headers
   oldRead1 = chess.pgn.read_headers
  elif target == 'b':
   newRead1 = MzChess.read_board
   oldRead1 = MzChess.read_board2
  elif target == 's':
   newRead1 = MzChess.read_game
   oldRead1 = chess.pgn.read_game
   newRead2 = MzChess.skip_game
   oldRead2 = chess.pgn.skip_game
  else:
   continue
  
  anyExecuted = True
  gameList = list()
  print('Parse games using new read_game ----------------------------')
  gameID = 0
  log = list()
  node = False
  while node is not None:
   gameID += 1
   node = runNode(newRead1, pgn, gameID)
   gameList.append(node)
   if newRead2 is not None:
    runNode(newRead2, pgn, gameID)
  gameID -= 1
  if newRead2 is not None:
   gameID *= 2
  log.append('MzChess.read_game: {} games read'.format(gameID))
  del gameList[-1]
  if pytestconfig.getoption('compare') and len(gameList) > 0:
   pgn.seek(0)
   pgnGameList = list()
   print('Parse games using chess.pgn.read_game ----------------------------')
   gameID = 0
   nErrors = 0
   node = False
   while node is not None:
    gameID += 1
    node = runNode(oldRead1, pgn, gameID)
    pgnGameList.append(node)
    if oldRead2 is not None:
     runNode(oldRead2, pgn, gameID)
   gameID -= 1
   if oldRead2 is not None:
    gameID *= 2
   log.append('chess.read_game: {} games read'.format(gameID - 1))
   del pgnGameList[-1]
   if len(gameList) != len(pgnGameList):
    print('len(gameList) = {} != len(pgnGameList) = {}'.format(len(gameList), len(pgnGameList)))
   print('Comparing games ----------------------------')
   gameID = 0
   for node, chessNode in zip(gameList, pgnGameList):
    gameID += 1
    txt = 'game #{}: {}'.format(gameID, repr(node))
    try:
     cmpGameNodes(chessNode, node)
     print(' {} succeeded'.format(txt))
    except AssertionError as msg:
     nErrors += 1
     print(' {} failed \n -> {}'.format(txt, msg))
   print('Comparison failed for {} of {} games --------'.format(nErrors, gameID))
  print('\n'.join(log)) 
  
  if not anyExecuted:
   pytest.skip('read_game tests not activated')

