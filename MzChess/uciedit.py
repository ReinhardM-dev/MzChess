import re
import sys, os.path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtGui
else:
 from PyQt6 import QtWidgets, QtGui

class UCIHighlighter(QtGui.QSyntaxHighlighter):
 sendKeywords = ['uci', 'debug', 'isready', 'register', 'ucinewgame', 'position', 'go', 'ponderhit', 'quit']
 receiveKeywords = ['id', 'uciok', 'isready', 'readyok', 'bestmove', 'registration', 'copyprotection', 'info', 'option']
 infoKeywords = ['depth', 'score', 'pv']
 
 def __init__(self, parent=None) -> None:
  super(UCIHighlighter, self).__init__(parent)
  sendFmt = self._charFormat(color = 'black', isBold = True,  isItalic = False)
  sendPattern = re.compile('(?<![a-z])({})(?![a-z])'.format('|'.join(self.sendKeywords)))
  receiveFmt = self._charFormat(color = 'blue', isBold = True,  isItalic = False)
  receivePattern = re.compile('(?<![a-z])({})(?![a-z])'.format('|'.join(self.receiveKeywords)))
  infoFmt = self._charFormat(color = 'green', isBold = True,  isItalic = False)
  infoPattern = re.compile('(?<![a-z])({})(?![a-z])'.format('|'.join(self.infoKeywords)))
  
  self.rules = [
   (sendPattern, sendFmt), 
   (receivePattern, receiveFmt), 
   (infoPattern, infoFmt)]

 def _charFormat(self, color : str = 'black', isBold : bool = False,  isItalic : bool = False) -> QtGui.QTextCharFormat:
  charFormat = QtGui.QTextCharFormat()
  _color = QtGui.QColor()
  _color.setNamedColor(color)
  charFormat.setForeground(_color)
  if isBold:
   charFormat.setFontWeight(QtGui.QFont.Weight.Bold)
  if isItalic:
   charFormat.setFontItalic(True)
  return charFormat
  
 def highlightBlock(self, text):
  for expr, charFormat in self.rules:
   for match in expr.finditer(text):
    self.setFormat(match.start(), match.end() - match.start(), charFormat)
  

class QUCIEdit(QtWidgets.QTextEdit):
 def __init__(self, parent = None) -> None:
  super(QUCIEdit, self).__init__(parent)
  
  self.uciHighlighter = UCIHighlighter(self.document())

if __name__ == "__main__":
 data = '''
ChessEngine/_toStdin: stdin> ucinewgame, readyok = TrueChessEngine/_toStdin: stdin> position fen r2qkbnr/pp2pppp/2n5/3P4/2pP4/2N2B2/PPP2PPP/R1BQK2R b KQkq - 0 7, readyok = TrueChessEngine/_toStdin: stdin> setoption name MultiPV value 1, readyok = TrueChessEngine/_toStdin: stdin> setoption name UCI_AnalyseMode value false, readyok = TrueChessEngine/_toStdin: stdin> go depth 15, readyok = TrueChessEngine/_fromStdout: stdout< info string NNUE evaluation using nn-82215d0fd0df.nnue enabled
ChessEngine/_fromStdout: stdout< info depth 1 seldepth 1 multipv 1 score cp -435 nodes 86 nps 86000 tbhits 0 time 1 pv c6b4
info depth 2 seldepth 2 multipv 1 score cp -415 nodes 120 nps 120000 tbhits 0 time 1 pv c6b4 a2a3
'''

 app = QtWidgets.QApplication([])
 editor = QUCIEdit()
 editor.setPlainText(data)
 editor.show()
 app.exec()
