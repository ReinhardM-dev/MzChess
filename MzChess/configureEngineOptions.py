from typing import Dict, Optional, Any
import os,  os.path

import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

import Ui_configureEngineOptions

class ConfigureEngineOptions(PyQt5.QtWidgets.QDialog, Ui_configureEngineOptions.Ui_Dialog):
 fileDialogOptions = PyQt5.QtWidgets.QFileDialog.Options() | PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog
 fileDialogFilters = PyQt5.QtCore.QDir.AllDirs \
                      | PyQt5.QtCore.QDir.Files \
                      | PyQt5.QtCore.QDir.NoDotAndDotDot \
                      | PyQt5.QtCore.QDir.Hidden
 readOnlyOptions = ['UCI_Chess960', 'UCI_AnalyseMode', 'MultiPV']
 checkState = {'false' : PyQt5.QtCore.Qt.Unchecked, '0' : PyQt5.QtCore.Qt.Unchecked, 
                      'true' :  PyQt5.QtCore.Qt.Checked,  '1' : PyQt5.QtCore.Qt.Unchecked}

 def __init__(self, parent = None):
  super(ConfigureEngineOptions, self).__init__(parent)
  self.setupUi(self)
  self.tableWidget.setColumnCount(3)  
  self.tableWidget.setHorizontalHeaderLabels(['','Option', 'Value'])
  self.tableWidget.horizontalHeader().setStretchLastSection(True)
  self.tableWidget.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
  self.buttonBox.accepted.connect(self.accept)
  self.buttonBox.rejected.connect(self.reject)
 
 def run(self, engineOptionsDict : Dict[str, Dict[str, Any]], 
                   changedOptions : Dict[str, Any] = dict(), 
                   name : str = ''):
  if len(name) == 0:                  
   self.setWindowTitle('Configure Engines Options')
  else:
   self.setWindowTitle('Configure Options: {}'.format(name))
  self.tableWidget.setRowCount(len(engineOptionsDict))
  test = PyQt5.QtWidgets.QLabel()
  maxWidth = 0
  self.engineOptionsDict = engineOptionsDict
  self.optionsDict = dict()
  for key, value in changedOptions.items():
   self._toOptionsDict(key,  value)
  self.itemList = list()
  self.btnList = list()
  for row, key2Opts in enumerate(engineOptionsDict.items()):
   key, optDict = key2Opts
   maxWidth = max(maxWidth, test.fontMetrics().size(PyQt5.QtCore.Qt.TextSingleLine, key).width())
   nameLabel = PyQt5.QtWidgets.QLabel(str(key))
   self.btnList.append(None)
   type = optDict['type']
   if 'default' in optDict:
    if key in self.optionsDict:
     value = self.optionsDict[key]
    else:
     value = optDict['default'] 
   if type == 'check':
    item = PyQt5.QtWidgets.QCheckBox()
    item.setCheckState(self.checkState[value])
    item.stateChanged.connect(self.on_checkBox_stateChanged)
   elif type == 'spin':
    item = PyQt5.QtWidgets.QSpinBox()
    itemRange = optDict['range']
    item.setMinimum(itemRange.start)
    item.setMaximum(itemRange.stop - 1)
    item.setValue(int(value))
    item.valueChanged.connect(self.on_spinBox_changed)
   elif type == 'combo':
    item = PyQt5.QtWidgets.QComboBox()
    varList = optDict['varList']
    item.addItems(varList)
    item.setCurrentIndex(varList.index(value))
    item.currentTextChanged.connect(self.on_comboBox_changed)
   elif type == 'button':
    item = PyQt5.QtWidgets.QLabel('<no parameter>')
   elif type == 'string':
    if 'file' in key.lower() or 'path' in key.lower():
     browsePushButton = PyQt5.QtWidgets.QPushButton(self)
     browsePushButton.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_DialogSaveButton))
     self.tableWidget.setCellWidget(row, 0, browsePushButton)
     browsePushButton.clicked.connect(self.on_browsePushButton_clicked)
    self.btnList[-1] = browsePushButton
    item = PyQt5.QtWidgets.QLineEdit()
    item.setText(value)
    item.editingFinished.connect(self.on_string_editingFinished)
   else:
    raise ValueError('ConfigureEngineOptions/run: improper type = {}'.format(type))
   if self.btnList[-1] is None:
    self.tableWidget.setCellWidget(row, 0, PyQt5.QtWidgets.QLabel(''))
   self.tableWidget.setCellWidget(row, 1, nameLabel)
   self.tableWidget.setCellWidget(row, 2, item)
   self.itemList.append(item)
  self.tableWidget.horizontalHeader().resizeSection(1, maxWidth)
  self.tableWidget.horizontalHeader().resizeSection(0, self.tableWidget.rowHeight(0))
  self.optionsDict = dict()
  self.tableWidget.update()
  PyQt5.QtCore.QCoreApplication.processEvents()
  if self.exec():
   return self.optionsDict
  else:
   return changedOptions
   
 def _toOptionsDict(self, key,  value):
  if self.engineOptionsDict[key]['default'] != value:
   self.optionsDict[key] = value
  else:
   self.optionsDict.pop(key, None)
 
 @PyQt5.QtCore.pyqtSlot(int)
 def on_checkBox_stateChanged(self, state):
  item = self.sender()  
  row = self.itemList.index(item)
  key = self.tableWidget.cellWidget(row, 1).text()
  if state == PyQt5.QtCore.Qt.Checked:
   value = 'true'
  else:
   value = 'false'
  self._toOptionsDict(key,  value)
   
 @PyQt5.QtCore.pyqtSlot(int)
 def on_spinBox_changed(self, value):
  item = self.sender()  
  row = self.itemList.index(item)
  key = self.tableWidget.cellWidget(row, 1).text()
  self._toOptionsDict(key,  value)

 @PyQt5.QtCore.pyqtSlot(str)
 def on_comboBox_changed(self, value):
  item = self.sender()  
  row = self.itemList.index(item)
  key = self.tableWidget.cellWidget(row, 1).text()
  self._toOptionsDict(key,  value)

 @PyQt5.QtCore.pyqtSlot()
 def on_string_editingFinished(self):
  item = self.sender()  
  row = self.itemList.index(item)
  key = self.tableWidget.cellWidget(row, 1).text()
  value = item.text()
  self._toOptionsDict(key,  value)
   
 @PyQt5.QtCore.pyqtSlot()
 def on_browsePushButton_clicked(self):
  item = self.sender()  
  row = self.btnList.index(item)
  keyLabel = self.tableWidget.cellWidget(row, 1)
  key = keyLabel.text()
  valueLabel = self.tableWidget.cellWidget(row, 2)
  value = valueLabel.text()
  fDialog = PyQt5.QtWidgets.QFileDialog()
  fDialog.setOptions(self.fileDialogOptions)
  fDialog.setFilter(self.fileDialogFilters)
  if 'file' in key.lower(): 
   fDialog.setFileMode(PyQt5.QtWidgets.QFileDialog.ExistingFile)
   fDialog.setWindowTitle("Set File ...")
   if len(value) > 0:
    head, tail = os.path.split(value)
    fDialog.setDirectory(head)
    fDialog.selectFile(tail)
  else:
   fDialog.setFileMode(PyQt5.QtWidgets.QFileDialog.Directory)
   fDialog.setWindowTitle("Set Directory ...")
   if len(value) > 0:
    head, tail = os.path.split(value)
    fDialog.setDirectory(head)
  if fDialog.exec():
   value = fDialog.selectedFiles()[0]
   valueLabel = self.tableWidget.cellWidget(row, 2)
   valueLabel.setText(value)
   self._toOptionsDict(key,  value)
 
 @PyQt5.QtCore.pyqtSlot()
 def on_cancelPushButton_clicked(self):
  self.done(False)
  
 @PyQt5.QtCore.pyqtSlot()
 def on_okPushButton_clicked(self):
  self.done(True)


if __name__ == "__main__":
 import sys
 os.chdir('C:/Users/Reinh/chess_engines')
 stockfish12 = 'stockfish_12_win_x64_bmi2/stockfish_20090216_x64_bmi2.exe'
 togaII4 = 'TogaII40/Windows/TogaII_40_intelPGO_x64.exe'
 komodo12 = 'komodo-12.1.1_5a8fc2/Windows/komodo-12.1.1-64bit-bmi2.exe'
 fritz17 = 'Fritz17/Fritz17.exe'
 lcZero26 = 'lc0-v0.26.3-windows-gpu-opencl/lc0.exe'
 raubfischGTZ23 = 'RaubfischX44_and_GTZ23/GTZ23/RaubfischGTZ23_nn_sl-bmi2.exe'

 executable = stockfish12
 engineOptionsDict = {
 'Debug Log File': {'type': 'string', 'default': ''}, 
 'Contempt': {'type': 'spin', 'default': 24, 'range': range(-100, 101)}, 
 'Analysis Contempt': {'varList': ['Off', 'White', 'Black', 'Both'], 'type': 'combo', 'default': 'Both'}, 
 'Threads': {'type': 'spin', 'default': 1, 'range': range(1, 513)}, 
 'Hash': {'type': 'spin', 'default': 16, 'range': range(1, 33554433)}, 
 'Clear Hash': {'type': 'button'}, 
 'Ponder': {'type': 'check', 'default': 'false'}, 
 'MultiPV': {'type': 'spin', 'default': 1, 'range': range(1, 501)}, 
 'Skill Level': {'type': 'spin', 'default': 20, 'range': range(0, 21)}, 
 'Move Overhead': {'type': 'spin', 'default': 10, 'range': range(0, 5001)}, 
 'Slow Mover': {'type': 'spin', 'default': 100, 'range': range(10, 1001)}, 
 'nodestime': {'type': 'spin', 'default': 0, 'range': range(0, 10001)}, 
 'UCI_Chess960': {'type': 'check', 'default': 'false'}, 
 'UCI_AnalyseMode': {'type': 'check', 'default': 'false'}, 
 'UCI_LimitStrength': {'type': 'check', 'default': 'false'}, 
 'UCI_Elo': {'type': 'spin', 'default': 1350, 'range': range(1350, 2851)}, 
 'UCI_ShowWDL': {'type': 'check', 'default': 'false'}, 
 'SyzygyPath': {'type': 'string', 'default': '<empty>'}, 
 'SyzygyProbeDepth': {'type': 'spin', 'default': 1, 'range': range(1, 101)}, 
 'Syzygy50MoveRule': {'type': 'check', 'default': 'true'}, 
 'SyzygyProbeLimit': {'type': 'spin', 'default': 7, 'range': range(0, 8)}, 
 'Use NNUE': {'type': 'check', 'default': 'true'}, 
 'EvalFile': {'type': 'string', 'default': 'nn-82215d0fd0df.nnue'}} 

 changedOptions = { 'UCI_Elo' : 1410, 'Ponder' :  'true'}

 app = PyQt5.QtWidgets.QApplication([])
 dialog = ConfigureEngineOptions()
 dialog.run(engineOptionsDict, changedOptions = changedOptions)
 
 sys.exit(app.exec_())
