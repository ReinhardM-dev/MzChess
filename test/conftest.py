from typing import List

import sys
import platform
import winreg
import os, os.path
import pytest
import pytestqt.qt_compat


fileDirectory = os.path.dirname(os.path.abspath(__file__)) 
sys.path.insert(0, os.path.dirname(fileDirectory))

import chess, chess.pgn
import MzChess

def pytest_addoption(parser):
 home = homeFolder()
 parser.addoption("--home", action="store", default=home, help="home directory")
 parser.addoption("--pgnFile", action="store", help = "PGN-File or ID of test")
 parser.addoption("--uciEngine", action="store", help = "Executable")
 parser.addoption("--FEN", action="store", help = "FEN")
 parser.addoption("--target",  action="store",  default = 'g', 
   help="target(s) of parsing (g - games, h - headers, s - skip every second game, b - board, l - lexical analysis only)")
 parser.addoption("--encoding",  metavar = 'encoding',  default = 'u', 
   choices=['u', 'utf-8-sig', 'i', 'iso-8859-1', 'a', 'ascii'], 
   help="encoding of pgnFile (u - utf-8-sig, i - iso-8859-1, a - ascii")
 parser.addoption("--compare", action = 'store_true', default = False, help = "If True, compare with chess.pgn.read_game")
 # parser.addoption("--debug", action = 'store_true', default = False, help = "Enable Debugging")

@pytest.helpers.register
def loadPGN(pgnFile : str, encoding : str = 'utf-8-sig') -> List[chess.pgn.Game]:
 global fileDirectory
 if not os.path.isabs(pgnFile): 
  pgnFile = os.path.join(fileDirectory, pgnFile)
 pgn = open(pgnFile, mode = 'r', encoding = encoding)
 pgnList = list()
 while True:
  game = MzChess.read_game(pgn)
  if game is None:
   break
  pgnList.append(game)
 return pgnList

@pytest.helpers.register
def homeFolder() -> str: 
 if platform.system() == 'Windows':
  try:
   handle= winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
   return winreg.QueryValueEx(handle,'Personal')[0] 
  except:
   pass
 return os.path.expanduser('~')
 
@pytest.helpers.register
def findPGNFile(pytestconfig) -> str:
 pgnFile = pytestconfig.getoption("--pgnFile")
 if pgnFile is None:
  raise IOError('pgnFile not specified.')
 try:
  pgnID = int(pgnFile)
  pgnFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_{}.pgn'.format(pgnID)) 
 except:
  if not os.path.isabs(pgnFile): 
   home = pytestconfig.getoption("--home")
   pgnFile = os.path.join(home, pgnFile) 
 return pgnFile

@pytest.helpers.register
def findEncoding(pytestconfig) -> str:
 encoding = pytestconfig.getoption("--encoding")
 if encoding == 'u':
  encoding = 'utf-8-sig'
 elif encoding == 'i':
  encoding = 'iso-8859-1'
 elif encoding == 'a':
  encoding = 'ascii'
 return encoding

@pytest.helpers.register
def findPGNTextIO(pytestconfig) -> List[chess.pgn.Game]:
 pgnFile = pytest.helpers.findPGNFile(pytestconfig)
 encoding = pytest.helpers.findEncoding(pytestconfig)
 pgn = open(pgnFile, mode = 'r', encoding = encoding)
 return pgn

@pytest.helpers.register
def findPGNList(pytestconfig) -> List[chess.pgn.Game]:
 pgnFile = pytest.helpers.findPGNFile(pytestconfig)
 encoding = pytest.helpers.findEncoding(pytestconfig)
 pgnList = pytest.helpers.loadPGN(pgnFile, encoding = encoding)
 if len(pgnList) == 0:
  raise IOError('pgnFile {} not readable or empty.'.format(pgnFile))
 print('pgnFile {} with {} games read.'.format(pgnFile, len(pgnList)))
 return pgnList

@pytest.helpers.register
def exitApp():
 pytestqt.qt_compat.qt_api.QtWidgets.QApplication.exit()

@pytest.fixture(scope="module")
def promoteMateGame():
 return loadPGN('promoteMate.pgn')[0]
