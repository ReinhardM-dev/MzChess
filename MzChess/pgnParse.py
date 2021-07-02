'''A new-Parser for Portable Game Notation (`PGN`_) files for `chess.pgn`_ items
 
.. _chess.pgn: https://pypi.org/project/chess
.. _PGN: https://github.com/fsmosca/PGN-Standard
'''

from typing import Optional, Type, Callable, List, TextIO
import os, os.path
import re

import chess.pgn
import ply.lex

class PGNLexer(object):
 '''A Lexer for Portable Game Notation (PGN) files (see `ply`_)
tracking line number, gameID, position (in game) 

:param bufsize: size of the token buffer (min: 4096). The buffer is refilled at bufsize/4 
:param debug: run the lexer in debug mode
:param kwargs: other keyword arguments of ply.lex.lex 
 
.. _ply: https://ply.readthedocs.io/en/latest/
 '''
 states = ( ('comment','exclusive'),  ('tag', 'exclusive') )
 tokens = ( 'TAGNAME', 'TAGVALUE', 'ENDOFGAME', 'MOVENUMBER', 'SANPLY', 
                'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK', 'NAG',
                'COMMENT', 'LINECOMMENT')
 nagDict = { '?' : 2,  '??' : 4, '?!' : 6, '!' : 1,  '!!' : 3, '!?' : 5, 
                  '+=' :  14, '=+' : 15, '+/-' : 16, '+-' : 18, '+--' : 20,
                  '-/+' : 17, '-+' : 19, '--+' : 21,  '=' : 10, '~' : 13, 'N' : 146, 'D' : 220}
 
 def __init__(self, bufsize : int = 2147483647, debug : bool = False, **kwargs) -> None:
  assert bufsize >= 4096
  self.bufsize = bufsize
  self.lexer = ply.lex.lex(module = self, debug = debug, **kwargs)
  self.gameID = 0
  self.data = None
  self.f = None

 def newGame(self, f : TextIO) -> ply.lex.LexToken:
  '''Prepared the lexer to deliver tokens for a game 
  
:param f: file handle opened in text mode 
:returns: the first token of the game
  '''
  if f.tell() == 0 or f is not self.f:
   lexer.lineno = 1
   lexer.gameID = 0
   self.f = f
   self.data = self.f.read(self.bufsize).lstrip("\ufeff")
  self.gameID += 1
  self.lexer.input(self.data)
  return self.token()
  
 def endGame(self) -> None:
  'Ends running through a new game'
  self.data = self.data[self.lexer.lexpos:]
  self.lexer.input(self.data)
  self._loadBuffer()

 def _loadBuffer(self):
  if len(self.data) == self.bufsize and len(self.data) - self.lexer.lexpos < self.bufsize // 4:
   self.data += self.f.read(self.bufsize)
   self.data = self.data[self.lexer.lexpos:]
   self.lexer.input(self.data)

 def token(self) -> ply.lex.LexToken:
  self._loadBuffer()
  return self.lexer.token()
  
 def dumps(self, tok : Optional[ply.lex.LexToken] = None, notify : Optional[Callable[[str], None]] = None) -> None:
  msgList = list()
  if tok is None:
   tok = self.token()
  while tok is not None:
   if notify is not None:
    notify('({}({}): {}/{})'.format(tok.type, tok.value, tok.lineno, tok.lexpos))
   msgList.append('({}({}): {}/{})'.format(tok.type, tok.value, tok.lineno, tok.lexpos))
   tok = self.token()
  return '\n'.join(msgList)
  
 def endOfGamePattern(self) -> re.Pattern:
  '''Returns the compiled *t_ENDOFGAME* pattern
  
:returns: compiled *t_ENDOFGAME* pattern
  '''
  return re.compile(self.t_ENDOFGAME) 

 def _raise_error(self, rootCause : str,  t : ply.lex, warn = False) -> None:
  if isinstance(t.value, str):
   txt = t.value[:20]
  else:
   txt = repr(t.value)
  if warn:
   print("LEXER/{}: '{} ...' @ Line: {}, Game {}, Pos: {}".format(rootCause, txt, t.lineno, self.gameID,  t.lexpos))
  else:
   raise SyntaxError("LEXER/{}: '{} ...' @ Line: {}, Game {}, Pos: {}".format(rootCause, txt, t.lineno, self.gameID,  t.lexpos))
 
 # ---------------------------------------------------------------------------------- 
 
 # Completely ignored characters
 t_ignore = ' \t\x0c'
 t_tag_ignore = ' \t\x0c'
 t_comment_ignore = '\x0c'
 t_ENDOFGAME = r'(1\-0|0\-1|1/2\-1/2|\*)'

 # Newlines
 def t_NEWLINE(self, t):
  r'\n+'
  t.lexer.lineno += t.value.count("\n")

 def t_tag_NEWLINE(self, t):
  r'\n+'
  t.lexer.lineno += t.value.count("\n")

 t_tag_TAGNAME = r'[A-Z][A-Za-z0-9]*'
 t_LPAREN = r'\('
 t_RPAREN = r'\)'

 def t_tag_TAGVALUE(self, t): 
  r'\"(\\\"|[^"])*\"'
  t.value = t.value[1:-1]
  return t

 def t_SANPLY(self, t):
  r'(([NBKRQ]?[a-h]?[1-8]?)?[\:x]?[a-h][1-8](=[QRBN])?[+#]?|O-O(-O)?|0-0(-0)?|0{4}|@{4}|Z0|--(?![+\-]))'
  t.value = t.value.replace('x', '').replace(':', '')
  t.value = t.value.replace('+', '').replace('#', '')
  if t.value == '@@@@' or t.value == 'Z0':
   t.value = '0000'
  return t

 def t_LBRACK(self, t):
  r'\['
  t.lexer.begin('tag')
 
 def t_tag_RBRACK(self, t):
  r'\]'
  t.lexer.begin('INITIAL')

 def  t_MOVENUMBER(self, t):
  r'([1-9][0-9]*\.*|\.+)(?!-)'
  pass
  
 def t_NAG(self, t):
  r'(\$[1-9][0-9]{0,2}(?![0-9])|(--\+|\+--|-/\+|\+/-|-\+|-\+|\+-|-\+|\+=|=\+)(?![=+\-])|(\?[?!]|![?!])(?![?!])|[?!=~DN](?![?!=~DN]))'
  if t.value[0] != '$':
   if t.value not in self.nagDict:
    self._raise_error("Illegal NAG symbol", t, warn = True)
    t.value = 0
   else:
    t.value = self.nagDict[t.value]
  else:
   t.value = int(t.value[1:])
   if t.value >= 140:
    self._raise_error("Illegal NAG string", t, warn = True)
    t.value = 0
  return t  
  
 def t_comment_COMMENT(self, t):
  r'[^{}]+'
  t.lexer.lineno += t.value.count("\n")
  return t

 def t_LBRACE(self, t):
  r'\{'
  t.lexer.begin('comment')
 
 def t_comment_RBRACE(self, t):
  r'\}'
  t.lexer.begin('INITIAL')
 
 def t_tag_LINECOMMENT(self, t):
  r';[^\n]*'
  pass

 def t_LINECOMMENT(self, t):
  r';[^\n]*'
  pass

  # -----------------------------------------------------------------------

 def  t_TAGNAME (self, t):
  r'\['
  self._raise_error("Illegal tagname", t)

 def t_TAGVALUE(self, t):
  r'\]'
  self._raise_error("Illegal tagname", t)

 def t_RBRACK(self, t):
  r'\]'
  self._raise_error("Unexpected ]")

 def t_COMMENT(self, t):
  r'\{'
  self._raise_error("Illegal comment string", t)
 
 def t_RBRACE(self, t):
  r'\}'
  self._raise_error("Unexpected }")

 def t_error(self, t):
  self._raise_error("Illegal character", t)

 def t_tag_error(self, t):
  self._raise_error("Illegal tag character", t)

 def t_comment_error(self, t):
  self._raise_error("Illegal comment character", t)

# ==================================================================

lexer : PGNLexer = PGNLexer()
'''The global instance of the lexer'''

def _checkToken(tok : ply.lex.LexToken, expectedType : str) -> None:
 global lexer
 if tok is None:
  raise SyntaxError('Parser: {} marker missing'.format(expectedType))
 elif tok.type != expectedType:
  raise SyntaxError('Parser: Unexpected token "{}" = {} ... (expected "{}") @ Line {}, Game {}, Pos {}'.format(
                            tok.type, str(tok.value)[:10], expectedType, tok.lineno, lexer.gameID, tok.lexpos))

def _skipGameBody() -> None:
 global lexer
 data = lexer.lexer.lexdata[lexer.lexer.lexpos:]
 actPos = 0

 if len(data) == 0:
  return lexer.lexer.lexpos
 
 endOfGameID = 0
 brackID = -1

 patternList = list()
 patternList.append(lexer.endOfGamePattern())
 patternList.append(re.compile(r'\{[^{}]*\}'))
 patternList.append(re.compile(r';[^\n]*\n'))

 matchDict = dict()
 for id in range(3):  
  match = patternList[id].search(data)
  if match is not None:
   span = match.span()
   # print('Setup: {}/{}: {}'.format(id, actPos + span[1], data[actPos + span[0]:actPos + span[1]]))
   matchDict[actPos + span[0]] = (id, actPos + span[1])

 newBrackPos = data[actPos:].find('[')
 if newBrackPos >= 0:
  brackPos = actPos + newBrackPos
 else:
  brackPos = 2147483647
 while len(matchDict) > 0:
  minPos = sorted(matchDict)[0]
  id, endPos = matchDict[minPos]
  if brackPos < minPos:
   id = brackID
   endPos = minPos +1
   break
  if id == endOfGameID:
   break
  del matchDict[minPos]
  idList = [id]
  keys = list(matchDict.keys())
  for pos in keys:
   if pos < endPos:
    id, _ = matchDict[pos]
    del matchDict[pos]
    idList.append(id)
  actPos = endPos
  for id in idList:
   match = patternList[id].search(data[actPos:])
   if match is not None:
    span = match.span()
    # print('{}/{}: {}'.format(id, actPos + span[1], data[actPos + span[0]:actPos + span[1]]))
    matchDict[actPos + span[0]] = (id, actPos + span[1])
  newBrackPos = data[actPos:].find('[')
  if newBrackPos >= 0:
   brackPos = actPos + newBrackPos
  else:
   brackPos = 2147483647
    
 lexer.lexer.lineno += data[:endPos].count('\n')
 lexer.lexer.lexpos += endPos - (id == brackID)
 if id == endOfGameID:
  return None
 if len(matchDict) == 0:
  raise SyntaxError("SkipBody: Parsing ended by EOF")
 elif id == brackID:
  raise SyntaxError("SkipBody: Parsing ended by new header")
 else:
  raise SyntaxError("SkipBody: Parsing ended inside a comment")
 return None
 
def _readComments(visitor : chess.pgn.BaseVisitor, tok : ply.lex.LexToken) -> ply.lex.LexToken:
 global lexer
 comment = ''
 while tok is not None and tok.type == 'COMMENT':
  if len(comment) != 0:
   comment += '\n'
  comment += tok.value
  tok = lexer.token()
  visitor.visit_comment(comment.strip())
 return tok

def _read_variants(visitor : chess.pgn.BaseVisitor[chess.pgn.ResultT], board_stack : List[chess.Board], tok : ply.lex.LexToken, semanticError : str) -> ply.lex.LexToken:
 global lexer
 while tok is not None and tok.type == 'LPAREN':
  visitor.begin_variation()
  board = board_stack[-1].copy()
  board.pop()
  board_stack.append(board)
  tok = lexer.token()
  tok = _readComments(visitor, tok)
  tok, semanticError = _read_gameNodes(visitor, board_stack, tok, semanticError)
  _checkToken(tok, 'RPAREN')
  visitor.end_variation()
  board_stack.pop()
  tok = lexer.token()
 return tok, semanticError

def _read_gameNodes(visitor : chess.pgn.BaseVisitor[chess.pgn.ResultT], board_stack : List[chess.Board],  tok : ply.lex.LexToken, semanticError : str) -> ply.lex.LexToken:
 global lexer
 while tok is not None and tok.type == 'SANPLY':
  try:
   move =  board_stack[-1].parse_san(tok.value)
  except:
   move = chess.Move.null()
   if semanticError == '':
    semanticError = 'Parser: Improper SAN {} @ Line {}, Game {}, Pos {}'.format(tok.value, tok.lineno, lexer.gameID, tok.lexpos)
  visitor.visit_move(board_stack[-1], move)
  board_stack[-1].push(move)
  visitor.visit_board(board_stack[-1])
  tok = lexer.token()
  while tok is not None and tok.type == 'NAG':
    visitor.visit_nag(tok.value)
    tok = lexer.token()
  tok = _readComments(visitor, tok)
  if tok is not None and tok.type == 'LPAREN':
   tok, semanticError = _read_variants(visitor, board_stack, tok, semanticError)
 return tok, semanticError

def read_game(f : TextIO, Visitor : Type[chess.pgn.BaseVisitor[chess.pgn.ResultT]] = chess.pgn.GameBuilder) -> Optional[chess.pgn.ResultT]:
 """Reads a game from an open handle PGN-file in text mode.
 
By using text mode, the parser does not need to handle encodings. 
The file must be opened using the correct encoding, usually 
  
  * 'utf-8-sig': UTF-8 with optional BOM,
  * 'ascii': 7-bit ASCII,
  * 'iso-8859-1': ISO 8859/1 (Latin 1), rarely used but suggested by PGN standard.
  
Please note: *read_game* uses a private buffer.

As an extension of the PGN Standard, read_game accepts

  * null move extensions of the Standard Algebraic Notation (SAN) (0000|@@@@|Z0)
  * NAG symbols for annotations (?|??|?!|!|!!|!?)
  * NAG symbols for positions (+=|=+|+/-|+-|+--|-/+|-+|--+|=|~')
  * NAG symbols for novelty (N) and display(D)
  * Improper end of a game (see below)
    
The parser is configured by using the Visitor object leading to different *ResultT* nodes
  
  * chess.pgn.GameBuilder delivers a chess.pgn.Game object
  * chess.pgn.HeadersBuilder delivers a chess.pgn.Headers object 
  * chess.pgn.BoardBuilder delivers a chess.Board object 
  * chess.pgn.SkipVisitor delivers a boolean indicating whether a game could be successfully skipped 

The end of a game is determined by either
   
  * the game termination marker (1-0|0-1|1/2-1/2|*),
  * the end of file (EOF) occured during parsing,
  * or the start of a new header.
   
The last 2 alternatives are reported as an error, but parsing succeeds.

:param f: file handle opened in text mode 
:param Visitor: Visitor object, i.e. chess.pgn.BaseVisitor and one of the derived classes 
    
:returns: the expected *ResultT* object or ``None`` if parsing failed.
 """
 global lexer
 assert issubclass(Visitor, chess.pgn.BaseVisitor), 'Visitor ({}) must a subclass of chess.pgn.BaseVisitor'.format(type(Visitor)) 
 try:
  tok = lexer.newGame(f)
 except Exception as error:
  raise IOError('Lexer: {}'.format(error))
 if tok is None:
  return None
 visitor = Visitor()
 skipping_game = visitor.begin_game() is chess.pgn.SKIP
 headers = visitor.begin_headers()
 if headers is None:
  headers = chess.pgn.Headers()
 while tok.type == 'TAGNAME':
  tagName = tok.value
  tok = lexer.token()
  _checkToken(tok, 'TAGVALUE')
  visitor.visit_header(tagName, tok.value)
  tok = lexer.token()
 skipping_game  |= visitor.end_headers() is chess.pgn.SKIP
 tok = _readComments(visitor, tok)
 if skipping_game:
  try:
   _skipGameBody()
   lexer.endGame()
  except Exception as error:
   visitor.handle_error(error)
  visitor.end_game()
  return visitor.result()
 try:
  board_stack = [headers.board()]
  visitor.visit_board(board_stack[-1])
  tok, semanticError = _read_gameNodes(visitor,board_stack, tok, '')
  gameIsOver = board_stack[-1].is_game_over(claim_draw = False)
  if gameIsOver:
   if board_stack[-1].is_checkmate():
    if board_stack[-1].turn:
     tok.value = '0-1'
    else:
     tok.value = '1-0'
   else:
    tok.value = '1/2-1/2'
  if tok is not None and tok.type == 'TAGNAME':
   lexer.lexer.lexpos -= 1
  elif semanticError != '':
   if tok.type == 'ENDOFGAME':
    visitor.visit_result(tok.value)
   raise SyntaxError(semanticError)
  elif tok is not None:
   _checkToken(tok, 'ENDOFGAME')
   visitor.visit_result(tok.value)
   if (not gameIsOver) and headers['Result'] != tok.value:
    raise SyntaxError("Parser: game.headers['Result'] ({}) != endOfGame ({})".format(headers['Result'], tok.value))
 except Exception as error:
  try:
   visitor.handle_error(error)
  except Exception as error:
   chess.pgn.LOGGER.exception(error)
  visitor.end_game()
 lexer.endGame()
 return visitor.result()
 
def read_headers(handle : TextIO) -> Optional[chess.pgn.Headers]:
 '''Convenience function representing *read_game(handle, Visitor = chess.pgn.HeadersBuilder)*

 :param f: file handle opened in text mode 
 :returns: a *chess.pgn.Headers* object or ``None`` if parsing failed.
 '''
 return read_game(handle, Visitor = chess.pgn.HeadersBuilder)
 
def read_board(handle : TextIO) -> Optional[chess.Board]:
 '''Convenience function representing *read_game(handle, Visitor = chess.pgn.BoardBuilder)*

 :param f: file handle opened in text mode 
 :returns: a *chess.Board* object or ``None`` if parsing failed.
 '''
 return read_game(handle, Visitor = chess.pgn.BoardBuilder)

def skip_game(handle : TextIO) -> bool:
 '''Convenience function representing *read_game(handle, Visitor = chess.pgn.SkipVisitor)*

 :param f: file handle opened in text mode 
 :returns: a *bool* indicating whether parsing was successful.
 '''
 return bool(read_game(handle, Visitor = chess.pgn.SkipVisitor))

# ==================================================================
 
if __name__ == "__main__":
 import argparse
 from time import time

 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 parser = argparse.ArgumentParser(description='PGN Parser: test')
 parser.add_argument("pgnFile", help = "PGN-File (required)")
 parser.add_argument("--target",  metavar = 'target',  default = 'g', 
   choices=['g', 'game', 'h' ,'headers', 's', 'skip', 'b', 'board', 'l', 'lex'], 
   help="target of parsing (g - games, h - headers, s - skip every second game, b - board, l - lexical analysis only)")
 parser.add_argument("--encoding",  metavar = 'encoding',  default = 'u', 
   choices=['u', 'utf-8', 'i', 'iso-8859-1', 'a', 'ascii'], 
   help="target of parsing (g - games, h - headers, s - skip every second game, b - board, l - lexical analysis only)")
 parser.add_argument("-compare", action = 'store_true', default = False, help = "If True, compare with chess.pgn.read_game")
 parser.add_argument("-debug", action = 'store_true', default = False, help = "Enable Debugging")
 
 args = parser.parse_args()
 assert args.pgnFile is not None, 'pgnFile is required'
 target = args.target[0]
 encoding = args.encoding[0]
 if encoding == 'u':
  encoding = 'utf-8-sig'
 elif encoding == 'i':
  encoding = 'iso-8859-1'
 elif encoding == 'a':
  encoding = 'ascii'

 def read_board2(handle : TextIO) -> Optional[chess.Board]:
  return chess.pgn.read_game(handle, Visitor = chess.pgn.BoardBuilder)
 
 def runBoard(node, n = 100):
  if node is not None:
   for i in range(n):
    node.board()

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
   context = 'Skipped game: chess.pgn: {}, new chess = {}'.format(chessNode, newNode)
   assert chessNode == newNode, context
  elif isinstance(chessNode, chess.pgn.Headers) or isinstance(newNode, chess.pgn.Headers):
   context = 'Headers: chess.pgn: {}, new chess = {}'.format(chessNode, newNode)
   assert chessNode == newNode, context
  elif isinstance(chessNode, chess.Board) or isinstance(newNode, chess.Board):
   context = 'Board: chess.pgn: {}, new chess = {}'.format(chessNode.fen(), newNode.fen())
   assert chessNode.fen() == newNode.fen(), context
  else:
   if isinstance(chessNode, chess.pgn.Game) and isinstance(newNode, chess.pgn.Game):
    context = 'Game Headers: chess.pgn: {}, new chess = {}'.format(chessNode.headers, newNode.headers)
    assert chessNode.headers == newNode.headers, context
   else:
    context = 'Move: chess.pgn: {}, new chess = {}'.format(repr(chessNode), repr(newNode))
    assert chessNode.move.uci() == newNode.move.uci(), context
   assert chessNode.comment == newNode.comment, 'Comment: chess.pgn: "{}", new chess = "{}" => {}'.format(chessNode.comment, newNode.comment, context)
   assert chessNode.nags == newNode.nags, 'Nags: chess.pgn: {}, new chess = {} => {}'.format(sorted(chessNode.nags), sorted(newNode.nags), context)
   assert len(chessNode.variations) == len(newNode.variations), 'nVariations: chess.pgn: {}, new chess = {} => {}'.format(len(chessNode.variations), len(newNode.variations), context)
   for subNode1, subNode2 in zip(chessNode.variations, newNode.variations):
    cmpGameNodes(subNode1, subNode2)

 print('File: {}'.format(os.path.abspath(args.pgnFile)))
 try:
  pgn = open(args.pgnFile, mode = 'r', encoding = encoding)
 except:
  raise IOError("Cannot open file '{}' for reading".format(args.pgnFile))
 
 if target == 'l':
  lexer = PGNLexer(bufsize = 4096, debug = args.debug, optimize = False)
  tok = lexer.newGame(pgn)
  start = time()
  lexer.dumps(tok = tok, notify = print)
  end = time()
  print('PGNLex: {:.1f} msec'.format(1000*(end-start)))
 else:
  newRead2 = None
  oldRead2 = None
  if target == 'g':
   newRead1 = read_game
   oldRead1 = chess.pgn.read_game
  elif target == 'h':
   newRead1 = read_headers
   oldRead1 = chess.pgn.read_headers
  elif target == 'b':
   newRead1 = read_board
   oldRead1 = read_board2
  elif target == 's':
   newRead1 = read_game
   oldRead1 = chess.pgn.read_game
   newRead2 = skip_game
   oldRead2 = chess.pgn.skip_game
   
  gameList = list()
  print('Parse games using new read_game ----------------------------')
  gameID = 0
  log = list()
  node = False
  start = time()
  while node is not None:
   gameID += 1
   node = runNode(newRead1, pgn, gameID)
   gameList.append(node)
   if newRead2 is not None:
    runNode(newRead2, pgn, gameID)
  end = time()
  gameID -= 1
  if newRead2 is not None:
   gameID *= 2
  log.append('new read_game: {} games read, elapsed {:.1f} msec/game'.format(gameID, 1000*(end-start)/max(gameID, 1)))
  del gameList[-1]
  if args.compare and len(gameList) > 0:
   pgn.seek(0)
   pgnGameList = list()
   print('Parse games using chess.pgn.read_game ----------------------------')
   gameID = 0
   nErrors = 0
   node = False
   start = time()
   while node is not None:
    gameID += 1
    node = runNode(oldRead1, pgn, gameID)
    pgnGameList.append(node)
    if oldRead2 is not None:
     runNode(oldRead2, pgn, gameID)
   end = time()
   gameID -= 1
   if oldRead2 is not None:
    gameID *= 2
   log.append('chess read_game: {} games read, elapsed {:.1f} msec/game'.format(gameID - 1, 1000*(end-start)/max(gameID, 1)))
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
  print('completed')
