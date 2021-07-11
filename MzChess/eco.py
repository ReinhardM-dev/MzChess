'''A Wrapper for Encyclopaedia of Chess Openings (ECO) (see `fiekas.eco`_)
It makes use of `polyglot`_ books to arrange the games.
 
.. _fiekas.eco: https://github.com/niklasf/eco
.. _polyglot: https://sourceforge.net/projects/codekiddy-chess/files/Books/Polyglot%20books/
'''

from typing import Optional, Union, Dict, List, Any
import os, os.path
import glob
import warnings
from enum import IntEnum, unique

import chess, chess.pgn, chess.polyglot

@unique
class TSVType(IntEnum):
 'Columns of TSV-files'
 ECO = 0
 OPENING = 1
 FEN = 2
 MOVES = 3

class ECODatabase(list):
 '''A Wrapper class for Encyclopaedia of Chess Openings (ECO)

:param ecoDirectory: directory of tsv - files
:param tsvPattern: a glob pattern describing the files to be loaded. ``None`` -> nothing is loaded
 '''
 keys =  ['eco', 'name', 'fen', 'moves']
 
 def __init__(self, 
  ecoDirectory : os.PathLike = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eco'),
  tsvPattern : Optional[str] = '*.tsv') -> None:
  super(ECODatabase, self).__init__()
  self.ecoDirectory = os.path.abspath(ecoDirectory)
  if tsvPattern is None or len(tsvPattern) == 0:
   return
  for tsvFile in glob.glob(os.path.join(self.ecoDirectory, tsvPattern)):
   self.loadTSVFile(tsvFile)
   # print('{} lines read from file {}'.format(len(self), os.path.basename(tsvFile)))

 def loadTSVFile(self, tsvFile : os.PathLike) -> None:
  '''Adds a *tsvFile* to the database 

:param tsvFile: tsv - file to be added
  '''
  if not os.path.isabs(tsvFile):
   tsvFile = os.path.join(self.ecoDirectory, tsvFile)
  if not os.path.isfile(tsvFile):
   raise IOError('ECODatabase/loadTSVFile: ECO file {} not found'.format(tsvFile))
  with open(tsvFile, mode='r') as f:
   isFirst = True
   while True:
    row = f.readline().strip(' \n').split('\t')
    if isFirst:
     if row != self.keys:
      raise IOError('ECODatabase/loadTSVFile: {} is not a valid ECO file'.format(tsvFile))
     isFirst = False
     continue
    if len(row) != 4:
     f.close()
     return
    moveList = list()
    for uciCode in row[3].split(' '):
     moveList.append(chess.Move.from_uci(uciCode))
    self.append((row[0], row[1], row[2], moveList))
 
 def column2IdList(self, key : TSVType) -> Dict[str, List[int]]:
  resultDict = dict()
  for id, tpl in enumerate(self):
   _key = tpl[key]
   if _key not in resultDict:
    resultDict[_key] = list()
   resultDict[_key].append(id)
  return resultDict

 def column2Id(self, column : int) -> Dict[str, int]:
  # standard databases => only fen is unique 
  assert column >= 0 and column < 3
  resultDict = dict()
  for id, tpl in enumerate(self):
   key = tpl[column]
   if key in resultDict:
    warnings.warn('ECODatabase/column2Id: Duplicate key {}'.format(key), RuntimeWarning)
   resultDict[key] = id
  return resultDict
  
 def fen2Id(self) -> Dict[str, int]:
  return self.column2Id(2)

 def column2Count(self, column) -> Dict[str, int]:
  assert column >= 0 and column < 3
  resultDict = dict()
  for tpl in self:
   key = tpl[column]
   if key not in resultDict:
    resultDict[key] = 0
   resultDict[key] += 1
  return resultDict
  
 @staticmethod
 def commonLength(listOLists : List[List[Any]]) -> int:
  n = 0
  while True:
   itemSet = set()
   for valueList in listOLists:
    if len(valueList) < n + 1:
     return n
    itemSet.add(valueList[n])
   if len(itemSet) > 1:
    return n
   n += 1
  return 0
  
 def statistics(self, key : TSVType = TSVType.ECO) -> Dict[str, Dict[str, Union[int, List[int]]]]:
  '''Delivers statistical data. ``key`` one of the 4 columns of a TSV-file, i.e.
  
  * *ECO* : eco code
  * *OPENING* : opening name
  * *FEN* : Forsyth-Edwards-Notation of the starting position
  * *MOVES* : move list

 The values of the returned dictionary are
 
  * *idList* : list of entries in the TSV table
  * *nItems* : len(idlist)
  * *nCommon* : number of common moves
  
:param key: column of a TSV-file (see above)
:returns: return dictionary
  '''
  statisticsDict = dict()
  for columnValue, idList in self.column2IdList(key).items():
   newDict = dict()
   newDict['idList'] = idList
   newDict['nItems'] = len(idList)
   listOfMoveLists = list()
   for id in idList:
     listOfMoveLists.append(self[id][3])
   newDict['nCommon'] = self.commonLength(listOfMoveLists)
   statisticsDict[columnValue] = newDict
  return statisticsDict
 
 @staticmethod
 def sortGameNode(gameNode : chess.pgn.GameNode):
  if len(gameNode.variations) == 0:
   return 1
  if len(gameNode.variations) == 1:
   return ECODatabase.sortGameNode(gameNode.variations[0]) + 1
  nItems2idList = list()
  for n in range(len(gameNode.variations)):
   nItems2idList.append((ECODatabase.sortGameNode(gameNode.variations[n]), n))
  nItems2idList = sorted(nItems2idList, reverse = True, key = lambda el : el[0])
  newVariations = list()
  for nItems, id in nItems2idList:
   newVariations.append(gameNode.variations[id])
  gameNode.variations = newVariations
  return nItems2idList[0][0] + 1
  
 def _createVariation(self, gameNode : chess.pgn.GameNode, nPly : int, idList : List[int], polyglotBook : Optional[chess.polyglot.MemoryMappedReader] = None) -> None:
  move2idDict = dict()
  for id in idList:
   actMoveList = self[id][3]
   if len(actMoveList) == nPly:
    gameNode.comment = '{} : {}'.format(self[id][0], self[id][1])
   else:
    actMove = actMoveList[nPly]
    if actMove not in move2idDict:
     move2idDict[actMove] = list()
    move2idDict[actMove].append(id)
  if polyglotBook is not None:
   w2mDict = dict()
   for entry in polyglotBook.find_all(gameNode.board()):
    if entry.move in move2idDict.keys():
     w2mDict[entry.weight] = entry.move
   moveList = list()
   for weight in sorted(w2mDict.keys(),  reverse = True):
    moveList.append(w2mDict[weight])
   for move in move2idDict.keys():
    if move not in moveList:
     moveList.append(move)
  else:
   moveList = move2idDict.keys()
  for move in moveList:
   newIdList = move2idDict[move]
   newGameNode = gameNode.add_variation(move)
   self._createVariation(newGameNode, nPly+1, newIdList)
  
 def createGame(self, listOfFirstMoves : List[chess.Move], polyglotBook : Optional[chess.polyglot.MemoryMappedReader] = None) -> chess.pgn.Game:
  '''Creates a opening game starting with ``listOfFirstMoves``. The opening variants are implemented as variants
    
:param listOfFirstMoves: list of starting moves
:param polyglotBook: if present, the moves are sorted with respect to frequency of use
:returns: return dictionary
  '''
  title = 'Openings starting with '
  gameNode = chess.pgn.Game()
  for move in listOfFirstMoves:
   title += ' {}'.format(chess.square_name(move.to_square))
   gameNode = gameNode.add_variation(move)
  game = gameNode.game()
  game.comment = title
  game.headers['Site'] = 'ECO Tables'
  game.headers['White'] = 'Niklas Fiekas/White'
  game.headers['Black'] = 'Niklas Fiekas/Black'
  nFirst = len(listOfFirstMoves)
  idList = list()
  for id, tpl in enumerate(self):
   actMoves = tpl[3]
   if len(actMoves) >= nFirst and actMoves[:nFirst] == listOfFirstMoves:
    idList.append(id)
  self._createVariation(gameNode, nFirst, idList, polyglotBook)
  return game
    
if __name__ == "__main__":
 def createOpeningGame(opening, moveList):
  global fileDirectory, eco, polyglotBook
  game = eco.createGame(moveList, polyglotBook = polyglotBook)
  newPgnName = os.path.join(fileDirectory, 'training','openings', '{}.pgn'.format(opening))
  ECODatabase.sortGameNode(game)
  # print(game)
  exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
  f = open(newPgnName, "w", encoding="utf-8")
  pgnString = game.accept(exporter)
  f.write(pgnString)
  f.close()
  print('{} bytes written to {}'.format(len(pgnString), newPgnName))

 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 bookFile = os.path.join(fileDirectory,'books','elo2400.bin')
 polyglotBook = chess.polyglot.open_reader(bookFile)
 eco = ECODatabase()
 fen2IdDict = eco.fen2Id()
 statistics = eco.statistics()
 for ecoCode in sorted(statistics):
  iDict = statistics[ecoCode] 
  print('{:3} : {:3}, {} items'.format(ecoCode, iDict['nCommon'], iDict['nItems'] ))

 createOpeningGame('kingsPawn', [chess.Move.from_uci('e2e4'), chess.Move.from_uci('e7e5')])
 createOpeningGame('sicilianDefense', [chess.Move.from_uci('e2e4'), chess.Move.from_uci('c7c5')])
 createOpeningGame('frenchDefense', [chess.Move.from_uci('e2e4'), chess.Move.from_uci('e7e6')])
 createOpeningGame('caroKannDefense', [chess.Move.from_uci('e2e4'), chess.Move.from_uci('c7c6')])
 createOpeningGame('pircDefense', [chess.Move.from_uci('e2e4'), chess.Move.from_uci('d7d6')])
 createOpeningGame('queensGambit', [chess.Move.from_uci('d2d4'), chess.Move.from_uci('d7d5')])
 createOpeningGame('indianDefense', [chess.Move.from_uci('d2d4'), chess.Move.from_uci('g8f6')])
 createOpeningGame('englishOpening', [chess.Move.from_uci('c2c4')])
 createOpeningGame('retiOpening', [chess.Move.from_uci('g7f6')])
