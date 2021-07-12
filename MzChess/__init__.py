__description__ = \
"""
A PyQt5 based chess GUI

Versions:
 1.0.0      first version
 1.0.3      installation running
 1.0.4      bug fixes + end-of-game handling completed
"""
__author__ = "Reinhard Maerz"
__date__ = "2021-07-11"
__version__ = "1.0.5"

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

__all__ = [
 'AboutDialog', 
 'AnnotateEngine', 'Annotator', 
 'ChessMainWindow', 
 'ChessEngine', 
 'ConfigureEngine', 'loadEngineSettings', 'saveEngineSettings', 
 'ConfigureEngineOptions',  
 'ECODatabase', 'TSVType', 
 'GameHeaderView', 'KeyType', 
 'GameListTableModel', 'GameListTableView', 
 'HelpBrowser', 
 'read_game', 'read_board', 'read_headers', 'skip_game', 'PGNLexer', 
 'ScorePlot', 
 'ButtonLine', 'ItemSelector', 'treeWidgetItemPos', 
 'QUCIEdit', 'UCIHighlighter', 
 'warnOfDanger'
]

from .AboutDialog import AboutDialog
from .annotateEngine import AnnotateEngine,  Annotator
from .chessMainWindow import ChessMainWindow
from .chessengine import ChessEngine
from .configureEngine import ConfigureEngine, loadEngineSettings, saveEngineSettings
from .configureEngineOptions import ConfigureEngineOptions
from .eco import ECODatabase, TSVType
from .gameheaderview import GameHeaderView, KeyType
from .gamelisttableview import GameListTableModel, GameListTableView
from .helpDialog import HelpBrowser
from .pgnParse import read_game, read_board, read_headers, skip_game, PGNLexer
from .qboardviewclass import QBoardViewClass, Piece, Game
from .scoreplotgraphicsview import ScorePlot
from .specialDialogs import ButtonLine, ItemSelector, treeWidgetItemPos
from .uciedit import QUCIEdit, UCIHighlighter
from .warnOfDanger import warnOfDanger
