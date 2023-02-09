from typing import Optional, Callable, Dict 
import chess, chess.pgn

def warnOfDanger(originalBoard : chess.Board, log : Optional[Callable[[str], None]] = None,  depth : int = 0) -> Optional[Dict[chess.Square, int]]:
 ''' Warns, if certain pieces are in danger
 
Basis are the material scores from the attackers point of view, 
i.e. positive scores show an advantage of the attacker

:param originalBoard: input board to be analysed
:returns: a dictionary of square/score pairs
  '''
 pieceScoreDict = {
  chess.PAWN : 1, 
  chess.KNIGHT : 3.2, 
  chess.BISHOP : 3.2, 
  chess.ROOK : 5, 
  chess.QUEEN : 9, 
  chess.KING : 1000
 }
 fen = originalBoard.fen(en_passant = 'fen')
 if originalBoard.is_game_over():
  return None
 if log is not None and depth > 0:
  log(' move: {} (next_isWhite = {}, fen = {} ------------------------------'.format((gameNode.ply()+1)/2, originalBoard.turn, fen))
 square2ScoreDict : Dict[chess.Square, int] = dict()
 if originalBoard.is_check():
  square2ScoreDict[originalBoard.king(originalBoard.turn)] = - pieceScoreDict[chess.KING]
  if log is not None:
   log(' check detected!') 
  return square2ScoreDict
 originalBoard.push(chess.Move.null())
 for piece in chess.PIECE_TYPES:
  sList = list(originalBoard.pieces(piece, not originalBoard.turn))
  for sSquare in sList:
   board = originalBoard.copy()
   scoreList = list()
   sign = -1
   if log is not None and depth > 0:
    log('  square = {}, piece = {}'.format(chess.square_name(sSquare), chess.piece_name(piece))) 
   # 1. assign material scores to each attack and reply
   while True:
    minScore = 10000
    minSquare = None
    for actSquare in board.attackers(board.turn, sSquare):
     actPiece = board.piece_type_at(actSquare)
     # 2. promote to queen, if applicable
     if actPiece == chess.PAWN and \
         ((board.turn and chess.square_rank(sSquare) == 7) \
       or ((not board.turn) and chess.square_rank(sSquare) == 0)):
      promotion = chess.QUEEN
     else:
      promotion = None
     if chess.Move(actSquare, sSquare, promotion) in board.legal_moves:
      if minScore > pieceScoreDict[actPiece]:
       minScore = pieceScoreDict[actPiece]
       minSquare = actSquare
      if log is not None and depth > 0:
       log(' isAttacker = {}, square = {}, piece = {}'.format(sign == 1, chess.square_name(actSquare), chess.piece_name(board.piece_type_at(actSquare))))
     elif log is not None and depth > 0:
       log(' isAttacker = {}, square = {}, piece = {}, illegal move detected'.format(originalBoard.turn != board.turn, chess.square_name(actSquare), chess.piece_name(board.piece_type_at(actSquare))))
    if minScore == 10000:
     break
    scoreList.append(sign*minScore)
    board.push(chess.Move(minSquare, sSquare, promotion))
    sign = -sign
   # 2. no attackers
   if len(scoreList) >= 1:
    square2ScoreDict[sSquare] = pieceScoreDict[originalBoard.piece_type_at(sSquare)]
    if len(scoreList) > 1: 
     square2ScoreDict[sSquare] += sum(scoreList[:-1])
    if log is not None:
     log(' square = {}, totScore = {}'.format(chess.square_name(sSquare), square2ScoreDict[sSquare]))
 return square2ScoreDict

if __name__ == "__main__":
 import io
 from pgnParse import read_game

 def createGame(file):
  with open(file, mode = 'r',  encoding = 'utf-8') as f:
   newData = f.read()

  pgn = io.StringIO(newData)
  game = read_game(pgn)
  return game

 ps = "C:/Users/Reinh/OneDrive/Dokumente/Schach/ps210105.pgn"
 game = createGame(ps)
 gameNode = game.next()
 ply = 2
 while gameNode is not None:
  print(' move {}: {} ------------------------------'.format(ply/2, gameNode.move.uci()))
  square2ScoreDict = warnOfDanger(gameNode.board(), log = print, depth = 0)
  gameNode = gameNode.next()
  if len(square2ScoreDict) > 0:
   print(' square2ScoreDict: ------------------------------')
   for square, score in square2ScoreDict.items():
    print('  {}: {}'.format(chess.square_name(square), score))
  ply += 1
 print('completed ------------------------------')
