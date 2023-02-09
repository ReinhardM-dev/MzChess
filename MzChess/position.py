from typing import Any, Dict, Callable, Iterable, List, Optional, Tuple, Type, Union
import copy
import math
import chess

class Position(chess.Board):
 # material and simple-position scores in centipawns due to Tomasz Michniewski
 centiPawnMaterialScoreDict = {
   chess.PAWN : 100, 
   chess.KNIGHT : 310, 
   chess.BISHOP : 320, 
   chess.ROOK : 500, 
   chess.QUEEN : 900
  }
  
 centiPawnSimplePositionScoreDict = dict()
 
 centiPawnSimplePositionScoreDict[chess.KING] = \
  [ -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20]
 centiPawnSimplePositionScoreDict[chess.PAWN] = \
  [  0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0 ]
 centiPawnSimplePositionScoreDict[chess.KNIGHT] = \
  [ -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50]
 centiPawnSimplePositionScoreDict[chess.BISHOP] = \
  [ -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20]
 centiPawnSimplePositionScoreDict[chess.ROOK] = \
  [ 0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0]
 centiPawnSimplePositionScoreDict[chess.QUEEN] = \
  [ -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20]
   
 squareSetMethodDict = { 
  'Attacked pieces' : '-attackedPieces', 
  'Attacking pieces' : '+attackingPieces', 
  'Bad bishops' : '-badBishops', 
  'Blocked pawns' : '-blockedPawns', 
  'Controlled central squares' : '+controlledCentralSquares', 
  'Fiancettoed bishops' : '+fiancettoedBishops', 
  'Hanging pieces' : '-hangingPieces', 
  'Isolated pawns' : '-isolatedPawns', 
  'Passed pawns' : '+passedPawns', 
  'Pinned pieces' : '-pinnedPieces', 
  'Reachable Squares' : '0reachableSquares', 
  'Stacked pawns' : '-stackedPawns', 
  'Supported pawns' : '+supportedPawns', 
  'Trapped pieces' : '-trappedPieces', 
  'Undefended pieces' : '-undefendedPieces'
 }
 
 def __init__(self, fen : str = '8/8/8/8/8/8/8/8 w - - 0 1') -> None:
  super(Position, self).__init__()
  self._usePawnScore = False
  self.set_chess960_pos = self._disabledMethod
  self.clear_board = self._disabledMethod
  self.transform = self._disabledMethod
  self.mirror = self._disabledMethod
  self.set_fen(fen)
  
 def _disabledMethod(self, *args):
  raise NameError('Method has been disabled')
  
 def _setup(self):
  self.maxNonPawnScore = self.centiPawnMaterialScoreDict[chess.QUEEN] + 2*(self.centiPawnMaterialScoreDict[chess.ROOK] + self.centiPawnMaterialScoreDict[chess.BISHOP] + self.centiPawnMaterialScoreDict[chess.KNIGHT]) 

  self._bitboards = {chess.WHITE : dict(), chess.BLACK : dict()}
  self._bitboards[chess.WHITE][chess.PAWN] = self.pieces(chess.PAWN, chess.WHITE)
  self._bitboards[chess.BLACK][chess.PAWN] = self.pieces(chess.PAWN, chess.BLACK)
  self._bitboards[chess.WHITE][chess.KNIGHT] = self.pieces(chess.KNIGHT, chess.WHITE)
  self._bitboards[chess.BLACK][chess.KNIGHT] = self.pieces(chess.KNIGHT, chess.BLACK)
  self._bitboards[chess.WHITE][chess.BISHOP] = self.pieces(chess.BISHOP, chess.WHITE)
  self._bitboards[chess.BLACK][chess.BISHOP] = self.pieces(chess.BISHOP, chess.BLACK)
  self._bitboards[chess.WHITE][chess.ROOK] = self.pieces(chess.ROOK, chess.WHITE)
  self._bitboards[chess.BLACK][chess.ROOK] = self.pieces(chess.ROOK, chess.BLACK)
  self._bitboards[chess.WHITE][chess.QUEEN] = self.pieces(chess.QUEEN, chess.WHITE)
  self._bitboards[chess.BLACK][chess.QUEEN] = self.pieces(chess.QUEEN, chess.BLACK)
  self._bitboards[chess.WHITE][chess.KING] = self.pieces(chess.KING, chess.WHITE)
  self._bitboards[chess.BLACK][chess.KING] = self.pieces(chess.KING, chess.BLACK)

  chess.ALL = chess.PIECE_TYPES.stop
  for pieceColor in [chess.WHITE, chess.BLACK]:
   self._bitboards[pieceColor][chess.ALL] = chess.SquareSet()
   for piece in chess.PIECE_TYPES:
    self._bitboards[pieceColor][chess.ALL] |= self._bitboards[pieceColor][piece] 

  self._items = None
  self._pinnedPieces = dict()
  self._badBishops = dict()
  
  self._material = {chess.WHITE : dict(), chess.BLACK : dict()}
  for pieceColor in [chess.WHITE, chess.BLACK]:
   for piece in chess.PIECE_TYPES:
    self._material[pieceColor][piece] = len(self._bitboards[pieceColor][piece])
   
  self._horizontalRay = 64*[None]
  for rank in range(8):
   square = chess.square(0, rank)
   self._horizontalRay[square] = chess.SquareSet([square])
   for file in range(1, 8):
    subSquare = chess.square(file, rank)
    self._horizontalRay[subSquare] = self._horizontalRay[square]
    self._horizontalRay[square].add(subSquare)

  self._verticalRay = 64*[None]
  for file in range(8):
   square = chess.square(file, 0)
   self._verticalRay[square] = chess.SquareSet([square])
   for rank in range(1, 8):
    subSquare = chess.square(file, rank)
    self._verticalRay[subSquare] = self._verticalRay[square]
    self._verticalRay[square].add(subSquare)

  self._diagonalRay = {True: 64*[None], False: 64*[None]}
  for n in range(8):
   file = 0
   square = chess.square(file, n)
   self._diagonalRay[True][square] = chess.SquareSet([square])
   for rank in range(n+1, 8):
    file += 1
    subSquare = chess.square(file, rank)
    self._diagonalRay[True][subSquare] = self._diagonalRay[True][square]
    self._diagonalRay[True][square].add(subSquare)
  for n in range(1, 8):
   rank = 0
   square = chess.square(n, rank)
   self._diagonalRay[True][square] = chess.SquareSet([square])
   for file in range(n+1, 8):
    rank += 1
    subSquare = chess.square(file, rank)
    self._diagonalRay[True][subSquare] = self._diagonalRay[True][square]
    self._diagonalRay[True][square].add(subSquare)

  for n in range(7, -1, -1):
   file = 0
   square = chess.square(file, n)
   self._diagonalRay[False][square] = chess.SquareSet([square])
   for rank in range(n-1, -1, -1):
    file += 1
    subSquare = chess.square(file, rank)
    self._diagonalRay[False][subSquare] = self._diagonalRay[False][square]
    self._diagonalRay[False][square].add(subSquare)
  for n in range(1, 8):
   rank = 7
   square = chess.square(n, rank)
   self._diagonalRay[False][square] = chess.SquareSet([square])
   for file in range(n+1, 8):
    rank -= 1
    subSquare = chess.square(file, rank)
    self._diagonalRay[False][subSquare] = self._diagonalRay[False][square]
    self._diagonalRay[False][square].add(subSquare)

 def __getitem__(self, square : chess.Square) ->  Optional[chess.Piece]:
  '''Detects pieces 
 
 :param square: Square, i.e. location 
 :returns: tuple(pieceColor, piece) or None
  '''
  return self.piece_at(square)
  
 # #################################
 # overloaded methods to ensure object integrity
 # #################################
 
 def set_fen(self, fen : str) -> None:
  super(Position, self).set_fen(fen)
  self._setup()
 
 def push(self, move : chess.Move) -> None:
  super(Position, self).push(move)
  self._setup()
 
 def _set_piece_at(self, square : chess.Square, piece : Optional[chess.Piece], promoted : bool = False) -> None:
  super(Position, self)._set_piece_at(square, piece, promoted)
  self._setup()

 def _remove_piece_at(self, square : chess.Square) -> None:
  super(Position, self)._remove_piece_at(square)
  self._setup()

 # #################################
 # supporting methods
 # #################################

 @property
 def usePawnScore(self) -> bool:
  '''Delivers the score units 
  
  * *True* Pawn-Score
  * *False* CentiPawn-Score
  
 :returns: score units 
  '''
  return self._usePawnScore

 @usePawnScore.setter
 def usePawnScore(self, newUsePawnScore : bool) -> None:
  self._usePawnScore = newUsePawnScore

 def count(self, piece : chess.Piece) -> int:
  '''Delivers the number of pieces of a certain type and color
 
 :param piece: Piece to be counted
 :returns: Number of pieces
  '''
  return self._material[piece.color][piece.piece_type]
  
 def unoccupiedSquares(self) -> chess.SquareSet:
  '''All squares not occupied by any piece
 
 :returns: SquareSet 
  '''
  return chess.SquareSet(chess.BB_ALL & ~self.occupied)

 def diagonalRay(self, square : chess.Square, positiveSlope : bool) -> chess.SquareSet:
  '''Draws a diagonal ray through a square
 
 :param square: Square, i.e. location 
 :param positiveSlope: slope of the ray
 :returns: SquareSet defining the ray
  '''
  assert square in chess.SQUARES
  return self._diagonalRay[positiveSlope][square]

 def horizontalRay(self, square : chess.Square) -> chess.SquareSet:
  '''Draws a horizontal ray through a square
 
 :param square: Square, i.e. location 
 :returns: SquareSet defining the ray
  '''
  assert square in chess.SQUARES
  return self._horizontalRay[square]
  
 def verticalRay(self, square : chess.Square) -> chess.SquareSet:
  '''Draws a vertical ray through a square
 
 :param square: Square, i.e. location 
 :returns: SquareSet defining the ray
  '''
  assert square in chess.SQUARES
  return self._verticalRay[square]
  
 def area(self, llSquare : chess.Square, urSquare : chess.Square) -> chess.SquareSet:
  '''Draws an area between 2 squares
 
 :param llSquare: lower left square, i.e. location 
 :param urSquare: upper right square, i.e. location 
 :returns: SquareSet defining the area
  '''
  assert llSquare in chess.SQUARES and urSquare in chess.SQUARES
  urFile = chess.square_file(urSquare)
  llFile = chess.square_file(llSquare)
  assert urFile >= llFile
  urRank = chess.square_rank(urSquare)
  llRank = chess.square_rank(llSquare)
  assert urRank >= llRank
  rSet = chess.SquareSet()
  for rank in range(llRank, urRank + 1):
   rSet |= self.horizontalRay(chess.square(0, rank))
  fSet = chess.SquareSet()
  for file in range(llFile, urFile + 1):
   fSet |= self.verticalRay(chess.square(file, 0))
  return rSet & fSet
  
 def centerArea(self, extended : bool = False) -> chess.SquareSet:
  '''Draws the center area
 
 :param extended: use 4x4 instead of 2x2 area
 :returns: SquareSet defining the area
  '''
  if extended:
   return self.area(chess.C4, chess.F6)
  else:
   return self.area(chess.D4, chess.E5)

 def shift(self, input : chess.SquareSet, fileShift : int, rankShift : int) -> chess.SquareSet:
  '''Shift a squareSet, positive shifts cause shifts to the right, negative shifts to the left
 
 :param fileShift: file shift (-7 ... +7)
 :param rankShift: rank shift (-7 ... +7)
 :returns: SquareSet defining the shifted  squareSet
  '''
  assert fileShift > -8 and fileShift < 8
  assert rankShift > -8 and rankShift < 8
  rSet = input.copy()
  if fileShift > 0:
   rSet = rSet << fileShift & ~self.area(chess.square(0, 0), chess.square(fileShift - 1, 7))
  elif fileShift < 0:
   rSet = rSet >> -fileShift & ~self.area(chess.square(8 + fileShift, 0), chess.square(7, 7))
  if rankShift > 0:
   rSet = rSet << 8*rankShift
  elif rankShift < 0:
   rSet = rSet >> -8*rankShift
  return rSet

 def northFill(self, input : Union[chess.SquareSet, chess.IntoSquareSet], numberOfLoops : int = 3) -> chess.SquareSet:
  '''Fills a region north to the input, i.e. from white to black 
  For a predictable operation, the squares should have one rank.

.. csv-table:: Ranks populated by fill
   :header: "numberOfLoops", "Maximum #Ranks"
   :widths: 30, 30

   1, 2
   2, 4
   3, 8
   
 :param input: either a chess.SquareSet, chess.IntoSquareSet (square or List[square])
 :param numberOfLoops: number of loops 
 :returns: SquareSet defining the fill
  '''
  if not isinstance(input, chess.SquareSet):
   input = chess.SquareSet(input)
  input |= input <<  8
  if numberOfLoops >= 2:  
   input |= input << 16
  if numberOfLoops == 3:
   input |= input << 32
  return input
  
 def southFill(self, input : Union[chess.SquareSet, chess.IntoSquareSet], numberOfLoops : int = 3) -> chess.SquareSet:
  '''Fills a region north to the input, i.e. from black to white 
  For a predictable operation, the squares should have one rank.

.. csv-table:: Ranks populated by fill
   :header: "numberOfLoops", "Maximum #Ranks"
   :widths: 30, 30

   1, 2
   2, 4
   3, 8
   
 :param input: either a chess.SquareSet, chess.IntoSquareSet (square or List[square])
 :param numberOfLoops: number of loops 
 :returns: SquareSet defining the fill
  '''
  if not isinstance(input, chess.SquareSet):
   input = chess.SquareSet(input)
  input |= input >> 8
  if numberOfLoops >= 3:
   input |= input >> 16
  if numberOfLoops == 3:
   input |= input >> 32
  return input

 def findNN(self, refSquare : chess.Square, squareList : List[chess.Square]) -> List[chess.Square]:
  '''Finds next neighbor squares. refSquare and the elements of squareList are located along a file, rank or ray 

 :param refSquare: reference square
 :param squareList: list of squares to be assessed
 :returns: 1 or 2 squares depending whether squares are on both sides of refSquare
  '''
  minNDistance = 9
  minNSquare = None
  minPDistance = 9
  minPSquare = None
  refSquareRank = chess.square_rank(refSquare)
  refSquareFile = chess.square_file(refSquare)
  for square in squareList:
   delta = chess.square_rank(square) - refSquareRank
   if delta == 0:
    delta = chess.square_file(square) - refSquareFile
   if delta > 0 and delta < minPDistance:
    minPDistance = delta
    minPSquare = square
   if delta < 0 and -delta < minNDistance:
    minNDistance = -delta
    minNSquare = square
  squareList = list()
  if minNSquare is not None:
   squareList.append(minNSquare)
  if minPSquare is not None:
   squareList.append(minPSquare)
  return squareList

 def restrictedRay(self, refSquare : chess.Square, ray : chess.SquareSet, obstaclePieces : chess.SquareSet) -> chess.SquareSet:
  '''Finds next neighbor squares. refSquare and the elements of squareList are located along a file, rank or ray 

 :param refSquare: reference square
 :param ray: square set of the ray
 :param excludeRefSquare: exclude refence square
 :returns: chess.SquareSet
  '''
  assert refSquare in ray
  obstacleList = list(ray & obstaclePieces)
  obstacleList.remove(refSquare)
  if len(obstacleList) == 0:
   return ray & ~chess.SquareSet([refSquare])
  rSet = chess.SquareSet()
  rayList = sorted(ray)
  posRef = rayList.index(refSquare)
  for square in reversed(rayList[:posRef]):
   if square in obstacleList:
    break
   rSet.add(square)
  for square in rayList[posRef+1:]:
   if square in obstacleList:
    break
   rSet.add(square)
  return rSet

 # #################################
 # new methods
 # #################################
  
 def gamePhase(self) -> str:
  '''Delivers the game phase based on the total material of a board
 
 .. csv-table:: 
    :header: "Phase", "Definition"
    :widths: 15, 50
    
    *opening*, not more than 4 knights have been defeated
    *middleGame*, in between opening and end game
    *endGame*, less than 1 rook and 2 knights left
 
 :param board: board showing the position
 :returns: Phase 
  '''
  pawnScore = 0
  for piece in list(self.piece_map().values()):
   if piece.piece_type != chess.KING:
    pawnScore += self.centiPawnMaterialScoreDict[piece.piece_type]
  if pawnScore >= 2 * (self.maxNonPawnScore - 2 * self.centiPawnMaterialScoreDict[chess.KNIGHT]):
   return 'opening'
  if pawnScore <= self.centiPawnMaterialScoreDict[chess.BISHOP] + 4 * self.centiPawnMaterialScoreDict[chess.KNIGHT]:
   return 'endGame'
  return 'middleGame'

 def material(self, pieceColor : chess.Color) -> Dict[chess.PieceType, int]:
  '''Delivers the material counts
 
 :param pieceColor: Color of the piece
 :returns: Dictionary[chess.PieceType, number of pieces]
  '''
  return self._material[pieceColor]
   
 def materialScore(self, pieceColor : chess.Color) -> Union[int, float]:
  '''Delivers the material score
 
 :param pieceColor: Color of the piece
 :returns: score in pawns or centipawns depending on self.usePawnScore
  '''
  score = 0
  weight = [1, 0.01][self.usePawnScore]
  materialBalance = self.materialBalance()
  for pieceType in self.centiPawnMaterialScoreDict.keys():
   score += self.centiPawnMaterialScoreDict[pieceType] * materialBalance[pieceType] * weight
  return score

 def simplePositionScore(self, pieceColor : chess.Color) -> Union[int, float]:
  '''Delivers the simple position score
 
 :param pieceColor: Color of the piece
 :returns: score in pawns or centipawns depending on self.usePawnScore
  '''
  score = 0
  weight = [1, 0.01][self.usePawnScore]
  for pieceType in chess.PIECE_TYPES:
   for square in list(self._bitboards[pieceColor][pieceType]):
    score += self.centiPawnSimplePositionScoreDict[pieceType][square] * weight
  return score

 def materialBalance(self) -> Dict[chess.PieceType, int]:
  '''Delivers the relative material counts from the WHITE point of view
 
 :param pieceColor: Color of the piece
 :returns: Dictionary[PieceType, number of pieces]
  '''
  materialDeltaDict = dict()
  for pieceType in chess.PIECE_TYPES:
   materialDeltaDict[pieceType] = self._material[chess.WHITE][pieceType] - self._material[chess.BLACK][pieceType]
  return materialDeltaDict
 
 def pawnBalance(self) -> int:
  '''Delivers the relative counts of pawns from the WHITE point of view
 
 :returns: Relative counts
  '''
  return self._material[chess.WHITE][chess.PAWN] - self._material[chess.BLACK][chess.PAWN]
  
 def winningProbability(self, k : float = 4.) -> float:
  '''Computes the win probabilty according to the method of Sune Fischer and Pradu Kannan
 
 :returns: Probability
  '''
  return 1./(1. + pow(10, -self.pawnBalance()/k))

 def potentialEnPassantSquares(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects potential en-passant configurations
 
 :param pieceColor: Color of the piece
 :returns: SquareSet
  '''
  if pieceColor == chess.WHITE:
   return self.shift(self._bitboards[chess.WHITE][chess.PAWN] & chess.SquareSet(chess.BB_RANKS[3]) \
         & (self.shift(self._bitboards[chess.BLACK][chess.PAWN], 1, 0) \
           | self.shift(self._bitboards[chess.BLACK][chess.PAWN], -1, 0)), 0, -1)
  return self.shift(self._bitboards[chess.BLACK][chess.PAWN] & chess.SquareSet(chess.BB_RANKS[4]) \
        & (self.shift(self._bitboards[chess.WHITE][chess.PAWN], 1, 0) \
          | self.shift(self._bitboards[chess.WHITE][chess.PAWN], -1, 0)), 0, 1)
         
 def pinnedPieces(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects pinned pieces, i.e. pieces required at the current square to protect the king
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  if pieceColor not in self._pinnedPieces:
   kingSquare = list(self._bitboards[pieceColor][chess.KING])[0]
   kingSquareRank = chess.square_rank(kingSquare)
   kingSquareFile = chess.square_file(kingSquare)
   cAll = copy.copy(self._bitboards[pieceColor][chess.ALL])
   cAll.remove(kingSquare)
   self._pinnedPieces[pieceColor] = chess.SquareSet()   
   ncQueensBishops = self._bitboards[not pieceColor][chess.QUEEN] | self._bitboards[not pieceColor][chess.BISHOP]
   ncQueensRooks = self._bitboards[not pieceColor][chess.QUEEN] | self._bitboards[not pieceColor][chess.ROOK]
   for n in range(4):
    if n < 2:
     positiveSlope = bool(n)
     rSquareList = list(self.diagonalRay(kingSquare, positiveSlope) & ncQueensBishops)
    elif n == 2:
     rSquareList = list(chess.SquareSet(chess.BB_RANKS[kingSquareRank]) & ncQueensRooks)
    else:
     rSquareList = list(chess.SquareSet(chess.BB_FILES[kingSquareFile]) & ncQueensRooks)
    if len(rSquareList) == 0:
     continue
    for nnSquare in self.findNN(kingSquare, rSquareList):
     betweenSet = chess.SquareSet.between(kingSquare, nnSquare) & cAll
     if len(betweenSet) == 1:
      self._pinnedPieces[pieceColor] |= betweenSet
  return self._pinnedPieces[pieceColor]
  
 def undefendedPieces(self, pieceColor : chess.Color, excludeKing : bool = True) -> None:
  '''Detects undefended pieces which may be unattacked by the enemy
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  rSet = chess.SquareSet()
  if excludeKing:
   cAll = self._bitboards[pieceColor][chess.ALL] & ~self._bitboards[pieceColor][chess.KING]
  else:
   cAll = self._bitboards[pieceColor][chess.ALL]
  for square in list(cAll):
   actSet = self.attackers(pieceColor, square) & self._bitboards[pieceColor][chess.ALL]
   if not bool(actSet):
    rSet.add(square)
  return rSet

 def defendedPieces(self, pieceColor : chess.Color) -> None:
  '''Detects defended pieces
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  return self._bitboards[pieceColor][chess.ALL] & ~self.undefendedPieces(pieceColor, excludeKing = False)
  
 def hangingPieces(self, pieceColor : chess.Color):
  '''Detects pieces being undefended and attacked
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  return self.undefendedPieces(pieceColor) & self.attackedPieces(pieceColor)
  
 def reachableSquares(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects reachable, unattacked squares (and give thus an idea of the mobility)
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  rSet = chess.SquareSet()
  pinnedPieces = self.pinnedPieces(pieceColor) | self.defendedPieces(not pieceColor)
  allPieces = self._bitboards[pieceColor][chess.ALL] | self._bitboards[not pieceColor][chess.ALL]
  for square in list(self._bitboards[pieceColor][chess.KING]):
   rSet |= chess.SquareSet(chess.BB_KING_ATTACKS[square]) & ~allPieces
  for square in list(self._bitboards[pieceColor][chess.PAWN] & ~pinnedPieces):
   # rSet |= (chess.SquareSet(chess.BB_PAWN_ATTACKS[pieceColor][square]) & self._bitboards[not pieceColor][chess.ALL])
   if pieceColor == chess.WHITE:
    targetSquare = self._bitboards[pieceColor][chess.PAWN] << 8
    targetSquare |= (self._bitboards[pieceColor][chess.PAWN] & self.area(chess.A2, chess.H2)) << 16 
   else:
    targetSquare = self._bitboards[pieceColor][chess.PAWN] >> 8
    targetSquare |= (self._bitboards[pieceColor][chess.PAWN] & self.area(chess.A7, chess.H7)) >> 16 
   rSet |= targetSquare & ~self.occupied
  for square in list(self._bitboards[pieceColor][chess.KNIGHT] & ~pinnedPieces):
   rSet |= chess.SquareSet(chess.BB_KNIGHT_ATTACKS[square]) & ~allPieces
   
  # self.attackedPieces(not pieceColor)
  for square in list((self._bitboards[pieceColor][chess.QUEEN] | self._bitboards[pieceColor][chess.ROOK]) & ~pinnedPieces):
   rSet |= self.restrictedRay(square, self.horizontalRay(square), allPieces) 
   rSet |= self.restrictedRay(square, self.verticalRay(square), allPieces)
  for square in list((self._bitboards[pieceColor][chess.QUEEN] | self._bitboards[pieceColor][chess.BISHOP]) & ~pinnedPieces):
   rSet |= self.restrictedRay(square, self.diagonalRay(square, True), allPieces)
   rSet |= self.restrictedRay(square, self.diagonalRay(square, False), allPieces)
  
  return rSet & (chess.SquareSet(chess.BB_ALL) & ~self._bitboards[pieceColor][chess.ALL])
  
 def attackedPieces(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects attacked pieces irrespective of defense
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  rSet = chess.SquareSet()
  cAll = self._bitboards[not pieceColor][chess.ALL]
  for square in list(self._bitboards[pieceColor][chess.ALL]):
   actSet = self.attackers(not pieceColor, square) & cAll
   for attacker in list(actSet):
    if attacker not in self.pinnedPieces(pieceColor):
     rSet.add(square)
     break
  return rSet
  
 def trappedPieces(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects trapped pieces
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  allPieces = self._bitboards[pieceColor][chess.ALL] | self.defendedPieces(not pieceColor)
  rSet = chess.SquareSet()
  for square in list(self._bitboards[pieceColor][chess.QUEEN]):
   actSet = chess.SquareSet()
   actSet |= self.restrictedRay(square, self.horizontalRay(square), allPieces) 
   actSet |= self.restrictedRay(square, self.verticalRay(square), allPieces) 
   actSet |= self.restrictedRay(square, self.diagonalRay(square, True), allPieces)
   actSet |= self.restrictedRay(square, self.diagonalRay(square, False), allPieces)
   if not bool(actSet):
    rSet.add(square)
  for square in list(self._bitboards[pieceColor][chess.ROOK]):
   actSet = chess.SquareSet()
   actSet |= self.restrictedRay(square, self.horizontalRay(square), allPieces) 
   actSet |= self.restrictedRay(square, self.verticalRay(square), allPieces) 
   if not bool(actSet):
    rSet.add(square)
  for square in list(self._bitboards[pieceColor][chess.BISHOP]):
   actSet = chess.SquareSet()
   actSet |= self.restrictedRay(square, self.diagonalRay(square, True), allPieces)
   actSet |= self.restrictedRay(square, self.diagonalRay(square, False), allPieces)
   if not bool(actSet):
    rSet.add(square)
  for square in list(self._bitboards[pieceColor][chess.KNIGHT]):
   actSet = chess.SquareSet(chess.BB_KNIGHT_ATTACKS[square]) & ~allPieces
   if not bool(actSet):
    rSet.add(square)
  return rSet
  
 def attackingPieces(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects attacking pieces irrespective of defense of the attacked device
 
  :param pieceColor: Color of the piece
  :returns: SquareSet
  '''
  rSet = chess.SquareSet()
  cAll = self._bitboards[pieceColor][chess.ALL] & ~self.pinnedPieces(pieceColor)
  for square in list(self._bitboards[not pieceColor][chess.ALL]):
   actSet = self.attackers(pieceColor, square) & cAll
   if bool(actSet):
    rSet |= actSet
  return rSet

 def controlledCentralSquares(self, pieceColor : chess.Color, extendedCenter : bool = False ) -> chess.SquareSet:
  '''Detects central squares (D4, E4, D5, E5) contolled by pieceColor
 
  :param pieceColor: Controlling piece color
  :returns: SquareSet
  '''
  rSet = chess.SquareSet()
  centerSquares = [chess.D4, chess.E4, chess.D5, chess.E5]
  if extendedCenter:
   centerSquares += [chess.C3, chess.D3, chess.E3, chess.F3]
   centerSquares += [chess.C4, chess.C5, chess.F4, chess.F5]
   centerSquares += [chess.C6, chess.D6, chess.E6, chess.F6]
  for square in centerSquares:
   n_PCSquares = len(self.attackers(pieceColor, square))
   n_NPCSquares = len(self.attackers(not pieceColor, square))
   if n_NPCSquares > 0:
    if n_PCSquares == 0:
     if self[square] is not None:
      rSet.add(square)
    elif n_PCSquares >  n_NPCSquares:
      rSet.add(square)
  return rSet
 
 def hasBishopPair(self, pieceColor : chess.Color) -> bool:
  '''Checks the number of bishops
 
 :returns: Check result
  '''
  return self.count(chess.Piece(chess.BISHOP, pieceColor)) == 2
  
 def badBishops(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects bishops protecting pawns
 
:param pieceColor: Color of the pieces
:returns: SquareSet
  '''
  if pieceColor not in self._badBishops:
   squareList = list(self._bitboards[pieceColor][chess.BISHOP])
   rSet = chess.SquareSet()
   sAll = self._bitboards[pieceColor][chess.ALL] | self._bitboards[not pieceColor][chess.ALL]
   for bishopSquare in squareList:
    bsSet = chess.SquareSet()
    for positiveSlope in [True, False]:
     pawnSquareList = list(self._diagonalRay[positiveSlope][bishopSquare] & self._bitboards[pieceColor][chess.PAWN])
     for pawnSquare in self.findNN(bishopSquare, pawnSquareList):
      if not bool(chess.SquareSet.between(bishopSquare, pawnSquare) & sAll):
       bsSet.add(pawnSquare)
    if bool(bsSet):
     rSet.add(bishopSquare)
   self._badBishops[pieceColor] = rSet
  return self._badBishops[pieceColor]
  
 def fiancettoedBishops(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects bishops on knight pawn squares
 
:param pieceColor: Color of the pieces
:returns: SquareSet
  '''
  squareList = list(self._bitboards[pieceColor][chess.BISHOP])
  rSet = chess.SquareSet()
  if pieceColor == chess.WHITE:
   for bishopSquare in squareList:
    if bishopSquare == chess.B2 or bishopSquare == chess.G2:
     rSet.add(bishopSquare)
  else:
   for bishopSquare in squareList:
    if bishopSquare == chess.B7 or bishopSquare == chess.G7:
     rSet.add(bishopSquare)
  return rSet
  
 def stackedPawns(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects stacked pawns, i.e. multiple pawns on a single file
 
:param pieceColor: Color of the pieces
:returns: SquareSet
  '''
  bb = self._bitboards[pieceColor][chess.PAWN]
  rSet = chess.SquareSet()
  for fileID, file in enumerate(chess.BB_FILES):
   actSet = bb & file
   n = len(actSet)
   if n > 1:
    rSet |= actSet
  return rSet
  
 def isolatedPawns(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects isolated pawns, i.e. pawns without supporting pawns in the adjacent files
 
:param pieceColor: Color of the pieces
:returns: SquareSet
  '''
  bb = self._bitboards[pieceColor][chess.PAWN]
  pList = list()
  for fileID, file in enumerate(chess.BB_FILES):
   pList.append(bb & file)
  rSet = chess.SquareSet()
  for fileID, file in enumerate(chess.BB_FILES):
   if len(pList[fileID]) != 0 and (fileID == 0 or len(pList[fileID-1]) == 0) and (fileID == len(pList) - 1 or len(pList[fileID+1]) == 0):
    rSet |= pList[fileID]
  return rSet
  
 def blockedPawns(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects blocked pawns, i.e. pawns in ranks 5 and 6 (WHITE) or 3 and 4 (BLACK) blocked by a pawn of opposite color
 
:param pieceColor: Color of the pieces
:returns: SquareSet
  '''
  if pieceColor == chess.WHITE:
   return self._bitboards[chess.WHITE][chess.PAWN] \
         & (self._bitboards[chess.BLACK][chess.PAWN] >> 8) \
         & (chess.BB_RANKS[4] | chess.BB_RANKS[5])
  return self._bitboards[chess.BLACK][chess.PAWN] \
        & (self._bitboards[chess.WHITE][chess.PAWN] << 8) \
        & (chess.BB_RANKS[2] | chess.BB_RANKS[3])

 def supportedPawns(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects supported pawns, i.e. pawns protected by pawns in the adjacent files
 
:param pieceColor: Color of the pieces
:returns: SquareSet
  '''
  if pieceColor == chess.WHITE:
   return self._bitboards[chess.WHITE][chess.PAWN] \
         & (self.shift(self._bitboards[chess.WHITE][chess.PAWN], 1, 1) \
           | self.shift(self._bitboards[chess.WHITE][chess.PAWN], -1, 1))
   return self._bitboards[chess.WHITE][chess.PAWN] \
         & (((self._bitboards[chess.WHITE][chess.PAWN] << 7)  \
           & ~self.verticalRay(chess.A8)) \
         |   ((self._bitboards[chess.WHITE][chess.PAWN] << 9) \
           & ~self.verticalRay(chess.A1))) 
  else:
   return self._bitboards[chess.BLACK][chess.PAWN] \
         & (self.shift(self._bitboards[chess.BLACK][chess.PAWN], 1, -1) \
           | self.shift(self._bitboards[chess.BLACK][chess.PAWN], -1, -1))
   return self._bitboards[chess.BLACK][chess.PAWN] \
         & (((self._bitboards[chess.BLACK][chess.PAWN] >> 7) \
           & ~self.verticalRay(chess.A8)) \
         |   ((self._bitboards[chess.BLACK][chess.PAWN] >> 9) \
           & ~self.verticalRay(chess.A1))) 
        
 def passedPawns(self, pieceColor : chess.Color) -> chess.SquareSet:
  '''Detects passed pawns
    These pawns cannot be attacked by "non-pieceColor" pawns anymore
 
:param pieceColor: Color of the pieces
:returns: SquareSet
  '''
  sign = [-1, 1][pieceColor]
  fillFct = [self.southFill, self.northFill][pieceColor]
  notPawnSet = self._bitboards[not pieceColor][chess.PAWN]

  freeSet = chess.SquareSet()
  for pawn in list(self._bitboards[pieceColor][chess.PAWN]):
   file = chess.square_file(pawn)
   rank = chess.square_rank(pawn) + sign
   squareList = list()
   for actFile in range(max(file - 1, 0), min(file +2, 8)):
    squareList.append(chess.square(actFile, rank))
   actSet = fillFct(squareList)
   if not bool(actSet & notPawnSet):
    freeSet.add(pawn)
  return freeSet

 def summary(self):
  print('Game Phase: ', self.gamePhase())
  print('Material: ')
  whiteMaterial = self.material(chess.WHITE)
  blackMaterial = self.material(chess.BLACK)
  materialBalance = self.materialBalance()
  fmt = ' {:<10} {:^5} {:^5} {}'
  print(fmt.format('PIECE', 'WHITE', 'BLACK', 'DELTA'))
  fmt = ' {:<10} {:^5} {:^5} {:>2}'
  for key in whiteMaterial.keys():
   print(fmt.format(key, whiteMaterial[key], blackMaterial[key], materialBalance[key]))

  print('\nGame Phase: ', self.gamePhase())
  print('Winning Probability: ', self.winningProbability(), ' (for WHITE)')
  print('\nGeneral: ')
  fmt = ' {:<10} {:^5} {:^5}'
  print(fmt.format('SQUARE', 'WHITE', 'BLACK'))
  print(fmt.format('reachable', len(self.reachableSquares(chess.WHITE)), len(self.reachableSquares(chess.BLACK))))
  print(fmt.format('undefended', len(self.undefendedPieces(chess.WHITE)), len(self.undefendedPieces(chess.BLACK))))
  print(fmt.format('hanging', len(self.hangingPieces(chess.WHITE)), len(self.hangingPieces(chess.BLACK))))
  print('\nPawns: ')
  fmt = ' {:<10} {:^5} {:^5}'
  print(fmt.format('PROPERTY', 'WHITE', 'BLACK'))
  print(fmt.format('stacked', len(self.stackedPawns(chess.WHITE)), len(self.stackedPawns(chess.BLACK))))
  print(fmt.format('isolated', len(self.isolatedPawns(chess.WHITE)), len(self.isolatedPawns(chess.BLACK))))
  print(fmt.format('blocked', len(self.blockedPawns(chess.WHITE)), len(self.blockedPawns(chess.BLACK))))
  print(fmt.format('supported', len(self.blockedPawns(chess.WHITE)), len(self.blockedPawns(chess.BLACK))))
  print(fmt.format('passed', len(self.passedPawns(chess.WHITE)), len(self.passedPawns(chess.BLACK))))
  print('\nBishops: ')
  fmt = ' {:<10} {:^5} {:^5}'
  print(fmt.format('PROPERTY', 'WHITE', 'BLACK'))
  print(fmt.format('has pair', self.hasBishopPair(chess.WHITE), self.hasBishopPair(chess.BLACK)))
  print(fmt.format('"bad"', len(self.badBishops(chess.WHITE)), len(self.badBishops(chess.BLACK))))
 
if __name__ == "__main__":
  
 fen = '8/8/7P/P5Pp/1p3P1P/3P4/8/8 w - - 0 1'
 fen = 'rnb1kb1r/4pp1p/1p4p1/3PP3/2q2B2/2N2Q1P/PP3PP1/R3K2R b KQkq - 1 15'
 fen = 'rnb1kb1r/4pp1p/1p4p1/3PP3/2q2B2/1PN2Q1P/P4PP1/R3K2R b KQkq - 15 15'
 fen = 'rnbqkbnr/1pppp1pp/8/pP6/4Pp2/8/P1PP1PPP/RNBQKBNR w KQkq - 1 1'
 board = Position(fen)
 print()
 cArea = board.area(17, 46)
 print(cArea)
 wBoard = board._bitboards[chess.WHITE][chess.PAWN]
 print('-')
 scArea11 = board.shift(wBoard, 1, 1)
 print(scArea11)
 print('-')
 scAreaM11 = board.shift(wBoard, -1, -1)
 print(scAreaM11) 
 print('---')
 print(board.supportedPawns(board.turn))
 print('-')
 print(board.supportedPawns(not board.turn))
 print('---')
 print(board.reachableSquares(board.turn))
 print('-')
 print(board.reachableSquares(not board.turn))
 print('---')
 print(board.potentialEnPassantSquares(board.turn))
 print('-')
 print(board.potentialEnPassantSquares(not board.turn))
 print('---')
 board.summary()

 print(' ...')
 
