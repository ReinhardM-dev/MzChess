__description__ = \
"""
A PyQt6 based chess GUI

Versions:
 1.0.0      first version
 1.0.3      installation running
 1.0.4      bug fixes + end-of-game handling completed
 1.0.6      documentation on github.io + ico added
 1.0.8      setup corrected
 1.1.0      FEN-builder added and bug fixes
 1.2.0      tests established and bug fixes
 1.2.1      variant bug fixes
 1.2.2      bug fixes
 1.2.3      bug fixes
 1.3.0      migrated to uic.loadUI
 1.4.0      migrated to PyQt6, Open/Save issues removed
 1.5.0      migrated to combined PyQt6/PyQt5 operation
 2.0.0      migrated to setup.cfg 
              postInstall.py added
              flexible gamelisttableview implemented
              detailed hint mechanism added
 2.0.1      long_description_content_type migrated to text/markdown
 2.1.0      GUI streamlined
              recover database added
              numerous bug fixes
 2.2.0      ChessMainWindow.saveDB improved
              Game moving in database implemented
              fullmove_number, halfmove_clock info in statusbar provided
              Game info in statusbar improved
              Square info in statusbar improved
 2.2.1      bug fix
 2.2.2      bug fix
 2.3.0      undo/redo functions implemented
              bug fixes for annotation machinery
 2.4.0      position analyser implemented
              documentation issue corrected
              bug fix in scoreplot 
"""
__author__ = "Reinhard Maerz"
__date__ = "2023-02-09"
__version__ = "2.4.0"

__all__ = [
 'AboutDialog', 
 'AnnotateEngine', 'Annotator', 
 'ChessMainWindow', 'runMzChess', 
 'BuildFenClass', 'runFenBuilder', 
 'AnalysePositionClass', 'runAnalysePosition', 
 'installLeipFont'
 'ChessEngine', 
 'ConfigureEngine', 'loadEngineSettings', 'saveEngineSettings', 
 'ConfigureEngineOptions',  
 'ECODatabase', 'TSVType', 
 'GameHeaderView', 'KeyType', 
 'GameListTableModel', 'GameListTableView', 
 'HelpBrowser', 
 'checkFEN','read_game', 'read_board', 'read_headers', 'skip_game', 'PGNLexer', 
 'QBoardViewClass', 'Piece', 'Game', 
 'ScorePlot', 
 'ButtonLine', 'ItemSelector', 'treeWidgetItemPos', 
 'QUCIEdit', 'UCIHighlighter', 
 'warnOfDanger', 
 'Position'
]

import os.path, sys
import chess
def useQt5():
 try:
  import PyQt6.QtSvgWidgets
  import PyQt6.QtCharts
  return False
 except:
  import PyQt5.QtSvg
  import PyQt5.QtChart
  return True

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from postInstall import postInstall
from .AboutDialog import AboutDialog
from .annotateEngine import AnnotateEngine,  Annotator
from .installLeipFont import installLeipFont
from .chessengine import ChessEngine
from .configureEngine import ConfigureEngine, loadEngineSettings, saveEngineSettings
from .configureEngineOptions import ConfigureEngineOptions
from .eco import ECODatabase, TSVType
from .gameheaderview import GameHeaderView, KeyType
from .gamelisttableview import GameListTableModel, GameListTableView
from .helpDialog import HelpBrowser
from .pgnParse import checkFEN, read_game, read_board, read_headers, skip_game, PGNLexer
from .qboardviewclass import QBoardViewClass, Piece, Game
from .scoreplotgraphicsview import ScorePlot
from .specialDialogs import ButtonLine, ItemSelector, treeWidgetItemPos
from .uciedit import QUCIEdit, UCIHighlighter
from .warnOfDanger import warnOfDanger
from .position import Position
# from .analysePosition import AnalysePositionClass, PlacementBoard, runAnalysePosition
from .qbuildfen import BuildFenClass, SelectionBox, PlacementBoard, runFenBuilder 
from .chessMainWindow import ChessMainWindow, runMzChess

mateScore = 10000
piecePawnScoreDict = {
 chess.PAWN : 100, 
 chess.KNIGHT : 320, 
 chess.BISHOP : 330, 
 chess.ROOK : 500, 
 chess.QUEEN : 900
}
