'''
Score Chart
=============

|ScoreChart|

The score chart shows the material score (blue) representing material budget where 
the pieces represent as usual the values

* :math:`s_{pawn} = 1`
* :math:`s_{knight} = 3`
* :math:`s_{bishop} = 3`
* :math:`s_{rook} = 5`
* :math:`s_{queen} = 9`

If available, the scores emitted by a chess engine (red) are also shown.
The engine annotations require command tags according to `PGNExt`_ supplement, i.e. tags like [%eval *score*] or [%  *score*]
*score* is the score [centipawn]. 

The handling of positions close to mate vary from GUI to GUI. This GUI delivers for
a mate in *n* moves a score of

 * *mateScore - n*, if black is facing a mate in $n$
 * *n -mateScore*, if white is facing a mate in $n$

with :math:`mateScore = 100`.

The actual position of the game and the corresponding score values are indicated in the score graph.
It is updated when it changes.

It is possible to control the zoom of the *Score* axis. The GUI with an ongoing zoom process is shown here.

.. csv-table:: Zoom control by mouse
   :header: "Key", "Description"
   :widths: 30, 50

   :kbd:`mouse-left-press`       , begin zoom
   :kbd:`mouse-left-release`     , end zoom
   :kbd:`mouse-right-release`   , reset zoom

.. |ScoreChart| image:: scoreplotgraphicsview.png
  :width: 800
  :alt: Score Chart
.. _PGNExt: https://github.com/mliebelt/pgn-spec-commented/blob/main/pgn-spec-supplement.md
'''

from typing import Optional

import math
import sys, os, os.path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import MzChess

if MzChess.useQt5():
 from PyQt5 import QtWidgets, QtGui, QtCore
 from PyQt5 import QtChart as QtCharts
 from PyQt5.QtWidgets import QShortcut
else:
 from PyQt6 import QtCharts, QtWidgets, QtGui, QtCore
 from PyQt6.QtGui import QShortcut

import chess, chess.pgn
from chessengine import PGNEval_REGEX

class ScorePlot(QtCharts.QChartView):
 '''Score plot object
 '''
 seriesPens = {
  'Material' : QtGui.QPen(QtGui.QBrush(QtCore.Qt.GlobalColor.blue), 1), 
  'Engine' : QtGui.QPen(QtGui.QBrush(QtCore.Qt.GlobalColor.red), 1), 
  None : QtGui.QPen(QtGui.QBrush(QtCore.Qt.GlobalColor.gray), 2, QtCore.Qt.PenStyle.DotLine)}
  
 axesPen = QtGui.QPen(QtGui.QBrush(QtCore.Qt.GlobalColor.blue), 2)
 axesBrush = QtGui.QBrush(QtCore.Qt.GlobalColor.black)

 QtGui.QColor(QtCore.Qt.GlobalColor.blue)

 def __init__(self, parent : Optional[QtCore.QObject] = None) -> None:
  super(ScorePlot, self).__init__(parent)
  self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
  self.setRubberBand(QtCharts.QChartView.RubberBand.VerticalRubberBand)
 
 def setup(self, notifyGameNodeSelectedSignal : Optional[QtCore.pyqtSignal] = None):
  '''Set up of the score
  
:param notifyGameNodeSelectedSignal: signal to be emitted if a game node is selected
  '''
  if 'xAxis' in vars(self):
   return
  self.notifyGameNodeSelectedSignal = notifyGameNodeSelectedSignal 
  if self.notifyGameNodeSelectedSignal is not None:
   scUp = QShortcut(self)
   scUp.setKey(QtCore.Qt.Key.Key_Up)
   scUp.activated.connect(self.on_sc_activated)
   scDown = QShortcut(self)
   scDown.setKey(QtCore.Qt.Key.Key_Down)
   scDown.activated.connect(self.on_sc_activated)
 
 def _setupChart(self, notifyGameNodeSelectedSignal : Optional[QtCore.pyqtSignal] = None):
  self._createChart()
  self.xAxis = self._addAxis(QtCore.Qt.AlignmentFlag.AlignBottom, title = 'Move')
  self.yAxis = self._addAxis(QtCore.Qt.AlignmentFlag.AlignLeft, title = 'Score [centipawn]')
  self.materialSeries = self._addSeries('Material', isLineSeries = True)
  self.engineSeries = self._addSeries('Engine', isLineSeries = True)
  self.selectedGameNode = None
  self.vLine = self._addSeries(None, isLineSeries = True)
  self.vLine.setPointsVisible(True)
  self.vLine.setPointLabelsVisible(True)
  self.vLine.setPointLabelsClipping(False)
  self.vLine.setPointLabelsFormat('@xPoint')
  vLineMarkers = self.chart.legend().markers(self.vLine)
  vLineMarkers[0].setVisible(False)
  self.meLabels = self._addSeries(None, isLineSeries = False)
  self.meLabels.setMarkerSize(10)
  self.meLabels.setPointsVisible(True)
  self.meLabels.setPointLabelsVisible(True)
  self.meLabels.setPointLabelsClipping(False)
  self.meLabels.setPointLabelsFormat('@yPoint')
  meLabelMarkers = self.chart.legend().markers(self.meLabels)
  meLabelMarkers[0].setVisible(False)
  self.resetChart()

 @staticmethod
 def minQtVersion(major : int, minor : int, patch : int = 0) -> bool:
  '''Checks whether the actual Qt-version is smaller or equal than the specified version
  
:param major: specified major version number
:param minor: specified minor version number
:param patch: specified patch number
:returns: True, if the actual Qt-version is smaller or equal than the specified version
  '''
  qtMajor, qtMinor, qtPatch = list(map(int, QtCore.QT_VERSION_STR.split('.')))
  return not (qtMajor < major \
              or (qtMajor == major and qtMinor < minor) \
              or (qtMajor == major and qtMinor == minor and qtPatch <= patch))
              
 def interval(self, minV : float, maxV : float) -> int:
  assert maxV > minV
  if maxV - minV < 1000:
   return 100
  if maxV - minV < 10000:
   return 1000
  return 100
  
 def _createChart(self, 
   bColor = QtCore.Qt.GlobalColor.lightGray, 
   paColor = QtCore.Qt.GlobalColor.white, 
   legendPosition = QtCore.Qt.AlignmentFlag.AlignBottom) -> None:
  self.chart = QtCharts.QChart()
  self.chart.setBackgroundBrush(bColor)
  self.chart.setPlotAreaBackgroundBrush(paColor)
  self.chart.setPlotAreaBackgroundVisible(True)
  self.chart.legend().setVisible(True)
  self.chart.legend().setAlignment(legendPosition)
  self.setChart(self.chart)

 def _addSeries(self, name : Optional[str] = None, isLineSeries : bool = True) -> QtCharts.QLineSeries:
  if isLineSeries:
   series = QtCharts.QLineSeries(self.chart)
   if name is not None:
    series.setName(name)
   series.setPen(self.seriesPens[name])
  else:
   series = QtCharts.QScatterSeries(self.chart)
   series.setPen(self.axesPen)
  self.chart.addSeries(series)
  series.attachAxis(self.xAxis)
  series.attachAxis(self.yAxis)
  return series

 def _addTextLabel(self) -> QtWidgets.QGraphicsSimpleTextItem:
  label = self.scene().addSimpleText('')
  label.hide()
  return label

 def _addAxis(self, alignment : QtCore.Qt.AlignmentFlag, title: str = '') -> QtCharts.QValueAxis:
  axis = QtCharts.QValueAxis()
  axis.setLinePen(self.axesPen)
  axis.setLabelsBrush(self.axesBrush)
  axis.setGridLineVisible(True)
  axis.setMinorTickCount(5)
  if self.minQtVersion(5, 12):
   axis.setTickType(QtCharts.QValueAxis.TickType.TicksDynamic)
   axis.setTickAnchor(0)
  if len(title) > 0: 
   axis.setTitleText(title)
  self.chart.addAxis(axis, alignment)
  return axis
  
 def _setRange(self, axis : QtCharts.QValueAxis, minV : int, maxV : int ) -> None:
  assert maxV > minV, '{} > {} required'.format(maxV, minV)
  if maxV - minV < 5:
   delta = 1
  elif maxV - minV < 10:
   delta = 2
  elif maxV - minV < 50:
   delta = 10
  elif maxV - minV < 100:
   delta = 20
  elif maxV - minV < 500:
   delta = 100
  elif maxV - minV < 1000:
   delta = 200
  elif maxV - minV < 5000:
   delta = 500
  elif maxV - minV < 10000:
   delta = 1000
  else:
   delta = 10000
  axis.setRange(minV, maxV)
  if self.minQtVersion(5, 12):
   axis.setTickInterval(delta)
  else:
   minV = (minV // delta) * delta
   maxV = (maxV // delta + 1) * delta
   axis.setMin(minV)
   axis.setMax(maxV)
   axis.setTickCount(int((maxV-minV) // delta) + 1)
   
 def _move(self, ply : int) -> float:
  return (ply + 1) / 2

 def resetChart(self) -> None:
  '''Clears the chart
  '''
  self.engineDict = dict()
  self.minY = float('inf')
  self.maxY = -float('inf')
  self.xAxis.setRange(0, 1)
  self.yAxis.setRange(-100, 100)
  self.materialSeries.clear()
  self.engineSeries.clear()
  self.vLine.clear()
  self.meLabels.clear()
  return

 def copyAsBitmap(self, width : int = None) -> None:
  '''Copies the chart as a bitmap to clipboard
  
:param width: width of the bitmap (Def: current width of the bounding box)
  '''
  sourceRect = self.sceneBoundingRect().toRect()
  if width is None:
   width = sourceRect.width()
  width = int(width)
  height = int(sourceRect.height() * width / sourceRect.width())
  bgColor = self.scene().views()[0].backgroundBrush().color().toRgb()
  plt = QtGui.QImage(width, height,  QtGui.QImage.Format.Format_RGB32)
  plt.fill(bgColor)
  painter = QtGui.QPainter()
  painter.begin(plt)
  painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
  self.render(painter)
  painter.end()
  clipboard = QtWidgets.QApplication.clipboard()
  clipboard.setImage(plt)

 def selectNodeItem(self, gameNode : chess.pgn.GameNode) -> None:
  '''Selects a game node
  
:param gameNode: game node to be selected
  '''
  if gameNode is None or gameNode.parent is None or not gameNode.is_mainline() or self.materialSeries.count() == 0:
   return
  relPly = gameNode.ply() - gameNode.game().ply() - 1
  assert relPly < self.materialSeries.count()
  self.selectedGameNode = gameNode
  self.vLine.clear()
  self.meLabels.clear()
  xValue = self.materialSeries.at(relPly).x()
  self.vLine.append(xValue, self.yAxis.min())
  self.vLine.append(xValue, 100000)
  self.vLine.show()
  self.meLabels.append(self.materialSeries.at(relPly))
  if relPly in self.engineDict:
   relPly = self.engineDict[relPly]
   self.meLabels.append(self.engineSeries.at(relPly))
  self.meLabels.show()

 def addGameNodes(self, gameNode :  chess.pgn.GameNode) -> None:
  '''Adds 1 or more nodes, parent node of first node must exist in the editor
  
:param gameNode: game node to be added (must be main_variation !!)
  '''
  if gameNode is None or not gameNode.is_mainline():
   return
  if 'materialSeries' not in vars(self):
   self._setupChart()
  self.chart.show()
  ply = gameNode.ply()
  xMin = (gameNode.game().ply() + 1) / 2
  engineData = list()
  materialData = list()
  nMaterial = self.materialSeries.count()
  nEngine = self.engineSeries.count()
  while gameNode is not None:
   pieceMap = gameNode.board().piece_map()
   pawnScore = 0
   for piece in list(pieceMap.values()):
    if piece.piece_type != chess.KING:
     if piece.color == chess.WHITE:
      pawnScore += MzChess.piecePawnScoreDict[piece.piece_type]
     else:
      pawnScore -= MzChess.piecePawnScoreDict[piece.piece_type]
   materialData.append(QtCore.QPointF((ply + 1)/2, pawnScore))
   self.minY = min(self.minY, pawnScore)
   self.maxY = max(self.maxY, pawnScore)
   match = PGNEval_REGEX.search(gameNode.comment)
   if match is not None and (match.group(1) == '%' or match.group(1) == '%eval'):
    engineScore = match.group(2)
    if engineScore != 'None':
     try:
      engineScore = float(engineScore)
     except:
      engineScore = float(engineScore[1:])
      engineScore = math.copysign(1,engineScore) * (MzChess.mateScore - abs(engineScore))
     engineData.append(QtCore.QPointF((ply + 1)/2, engineScore))
     self.engineDict[nMaterial] = nEngine
     self.minY = min(self.minY, engineScore)
     self.maxY = max(self.maxY, engineScore)
     nEngine += 1
   gameNode = gameNode.next()
   nMaterial += 1
   ply += 1

  if self.minY > self.maxY:
   return
   
  if len(materialData) > 0:
   self.materialSeries.append(materialData)
   if len(engineData) > 0:
    self.engineSeries.append(engineData)

  self._setRange(self.xAxis, xMin, max(ply / 2, 2))
  if self.minY < self.maxY:
   self._setRange(self.yAxis, self.minY, self.maxY)
  else:
   self._setRange(self.yAxis, self.minY - 50, self.minY + 50)
  
  self.update()

 def removeLastNode(self) -> None:
  if self.materialSeries.count() == 0:
   return
  
  ply = self.materialSeries.count() - 1
  mMove = self.materialSeries.at(ply).x()
  self.materialSeries.remove(ply)
  ply += 2
  self.minY = float('inf')
  self.maxY = -float('inf')
  for n in range(self.materialSeries.count()):
   pawnScore = self.materialSeries.at(n).y()
   self.minY = min(self.minY, pawnScore)
   self.maxY = max(self.maxY, pawnScore)
  if self.engineSeries.count() > 0:
   lastID = self.engineSeries.count() - 1
   eMove = self.engineSeries.at(lastID).x()
   if mMove == eMove:
    self.engineSeries.remove(lastID)
   for n in range(self.engineSeries.count()):
    pawnScore = self.engineSeries.at(n).y()
    self.minY = min(self.minY, pawnScore)
    self.maxY = max(self.maxY, pawnScore)

  if self.minY > self.maxY:
   return

  self._setRange(self.xAxis, 1, max(ply / 2, 2))
  if self.minY != self.maxY:
   self._setRange(self.yAxis, self.minY, self.maxY)
  else:
   self._setRange(self.yAxis, self.minY - 0.5, self.minY + 0.5)

  self.update()
  
 def setGame(self, game : chess.pgn.Game) -> None:
  '''Sets a new game
  
:param game: game node to be set
  '''
  gameNode = game.next()
  if gameNode is None:
   if 'chart' in vars(self):
    self.chart.hide()
   return
  self.addGameNodes(gameNode)
  if 'Annotator' in game.headers:
   self.engineSeries.setName(game.headers['Annotator'])
  else:
   self.engineSeries.setName('Engine')
  self.selectNodeItem(gameNode)
 
 @QtCore.pyqtSlot()
 def on_sc_activated(self):
  if self.selectedGameNode is not None:
   sendingSC = self.sender()
   if sendingSC.key() == QtCore.Qt.Key.Key_Down:
    newGameNode = self.selectedGameNode.next()
   else:
    newGameNode = self.selectedGameNode.parent
   if newGameNode is not None:
    self.notifyGameNodeSelectedSignal.emit(newGameNode)

 @QtCore.pyqtSlot(QtGui.QMouseEvent)
 def mouseReleaseEvent(self, e):
  plies = self.materialSeries.count()
  if plies == 0:
   return
  super(ScorePlot, self).mouseReleaseEvent(e)
  if e.button() == QtCore.Qt.MouseButton.RightButton:
   self.chart.zoomReset()

  self._setRange(self.xAxis, 1, plies / 2)
  self._setRange(self.yAxis, self.yAxis.min(), self.yAxis.max())
  self.selectNodeItem(self.selectedGameNode)


if __name__ == "__main__":
 import io, sys
 from pgnParse import read_game


 class _My(QtWidgets.QMainWindow):
  def __init__(self, game):
   super().__init__()
   self.setWindowTitle('self.chart Formatting Demo')
   self.plot = ScorePlot(self)
   self.setCentralWidget(self.plot)
   self.resize(1200, 800)
  
  def setup(self):  
   self.plot.setup()
   self.plot.setGame(game)
   gameNode = game
   for i in range(10):
    gameNode = gameNode.next()
   self.plot.selectNodeItem(gameNode)
     
 
 ps = "C:/Users/Reinh/OneDrive/Dokumente/Schach/ps210105.pgn"
 with open(ps, mode = 'r',  encoding = 'utf-8') as f:
  newData = f.read()

 pgn = io.StringIO(newData)
 game = read_game(pgn)
 app = QtWidgets.QApplication([])
 plotWindow = _My(game)
 plotWindow.show()
 plotWindow.setup()
 sys.exit(app.exec())



