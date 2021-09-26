__description__ = \
"""
A PyQt5 based chess GUI

Versions:
 1.0.0      first version
 1.0.3      installation running
 1.0.4      bug fixes + end-of-game handling completed
 1.0.6      documentation on github.io + ico added
 1.0.8      setup corrected
 1.1.0      FEN-builder added and bug fixes
 1.2.0      tests established and bug fixes
 1.2.1      variant bug fixes
"""
__author__ = "Reinhard Maerz"
__date__ = "2021-08-28"
__version__ = "1.2.1"

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

__all__ = [
 'AboutDialog', 
 'AnnotateEngine', 'Annotator', 
 'ChessMainWindow', 'runMzChess', 
 'BuildFenClass', 'runFenBuilder', 
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
 'warnOfDanger'
]

from .AboutDialog import AboutDialog
from .annotateEngine import AnnotateEngine,  Annotator
from .chessMainWindow import ChessMainWindow, runMzChess
from .qbuildfen import BuildFenClass, SelectionBox, PlacementBoard, runFenBuilder
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
