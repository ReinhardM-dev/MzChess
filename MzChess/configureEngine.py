'''
Configuration of Engines
================================

This dialog allows to add/remove/configure engines

|ConfigureEngine| 

Configuration of the Engine's Options
===========================================

By pressing the *Details* button the *Configure Engine Options* dialog is started.
Please consult the engine's documentation (e.g. `stockfish`_ or `here`_) before changing any options.

|ConfigureEngineOptions| 

.. |ConfigureEngine| image:: configureEngine.png
  :width: 400
  :alt: Configure Engine
.. |ConfigureEngineOptions| image:: configureEngineOptions.png
  :width: 400
  :alt: Configure Engine Options
.. _stockfish: https://github.com/official-stockfish/Stockfish
.. _here: https://www.chessprogramming.org/Engines
'''
from typing import List, Dict, Callable, Union, Optional, Any
import os, os.path
import platform
import copy

import configparser
import re

import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

from chessengine import ChessEngine
from configureEngineOptions import ConfigureEngineOptions 

import Ui_configureEngine

intRe = re.compile(r"^[+\-]?[0-9]+$")
boolRe = re.compile(r"^(True|False)$")

def loadEngineSettings(settings : configparser.ConfigParser) -> Dict[str, List[Any]]:
 engineDict = dict()
 for section in settings.sections():
  partList = section.split('/')
  isEngineSection = (len(partList) == 2 and partList[0] == 'Engine')
  if  isEngineSection:
   key = partList[1]
   optionsDict = dict()
   executable = None
   for opt in settings[section]:
    value = settings[section][opt]
    if opt == 'executable':
     executable = value
    elif intRe.match(value) is not None:
     optionsDict[opt] = int(value)
    elif boolRe.match(value) is not None:
     optionsDict[opt] = bool(value)
    else:
     optionsDict[opt] = value
   if executable is not None:
    engineDict[key] = [executable, optionsDict]
 return engineDict

def saveEngineSettings(settings : configparser.ConfigParser, engineDict : Dict[str, List[Any]]) -> None:
 for section in settings.sections():
  partList = section.split('/')
  if len(partList) == 2 and partList[0] == 'Engine':
   settings.remove_section(section)
 for opt in engineDict:
  executable, optionsDict = engineDict[opt]
  key = 'Engine/{}'.format(opt)
  settings[key] = optionsDict
  settings[key]['executable'] = executable

class ConfigureEngine(PyQt5.QtWidgets.QDialog, Ui_configureEngine.Ui_Dialog):
 fileDialogOptions = PyQt5.QtWidgets.QFileDialog.Options() \
                        | PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog
 fileDialogFilters = PyQt5.QtCore.QDir.AllDirs \
                      | PyQt5.QtCore.QDir.Files \
                      | PyQt5.QtCore.QDir.NoDotAndDotDot \
                      | PyQt5.QtCore.QDir.Hidden

 def __init__(self, parent : Optional[PyQt5.QtCore.QObject] = None):
  super(ConfigureEngine, self).__init__(parent)
  self.setupUi(self)
  self.engineDict = dict()
  self.log = False
  self.directories = list()
  self.engineTableWidget.horizontalHeader().setStretchLastSection(True)
  self.engineTableWidget.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
  self.browsePushButton.setIcon(self.style().standardIcon(PyQt5.QtWidgets.QStyle.SP_DialogSaveButton))
  self.engineDetails = dict()

 @PyQt5.QtCore.pyqtSlot(str)
 def notifyError(self, msg):
  msgBox = PyQt5.QtWidgets.QMessageBox()
  msgBox.setIcon(PyQt5.QtWidgets.QMessageBox.Critical)
  msgBox.setText(msg)
  msgBox.setWindowTitle("Error")
  msgBox.exec()

 def _fillForm(self):
  self.engineTableWidget.setRowCount(len(self.engineDict))
  for row, n2ec in enumerate(self.engineDict.items()):
   name, ec = n2ec
   executable = ec[0]
   if not (os.path.isfile(executable) and os.access(executable, os.X_OK )):
    executable = 'not found'
   else:
    self.directories.append(os.path.dirname(executable))
   self.engineTableWidget.setCellWidget(row, 0, PyQt5.QtWidgets.QLabel(name))
   self.engineTableWidget.setCellWidget(row, 1, PyQt5.QtWidgets.QLabel(executable))
  self.executableLineEdit.setText('')
  self.nameLineEdit.setText('')

 def run(self, engineDict : Dict[str, List[Any]] = dict(),  log : Union[Callable, bool] = False) -> Dict[str, List[Any]]:
  self.engineDict = copy.deepcopy(engineDict)
  self.log = log
  self._fillForm()
  self.isChanged = False
  self.selectedRow = None
  if self.exec():
   return self.engineDict
  else:
   return engineDict
  
 def ignoreIsChanged(self) -> None:
  if self.isChanged:
   msgBox = PyQt5.QtWidgets.QMessageBox()
   msgBox.setIcon(PyQt5.QtWidgets.QMessageBox.Critical)
   msgBox.addButton(PyQt5.QtWidgets.QMessageBox.No)
   msgBox.addButton(PyQt5.QtWidgets.QMessageBox.Yes)
   msgBox.setText('Ignore ?')
   msgBox.setWindowTitle("Unsaved content detected")
   rc = msgBox.exec()
   return rc
  else:
   return True

 def checkEngine(self, executable : str) -> Optional[ChessEngine]:
  try:
   engine = ChessEngine([executable, dict()], log = self.log)
   isOK = engine.isReady()
  except:
   isOK = False
  if not isOK:
   msgBox = PyQt5.QtWidgets.QMessageBox()
   msgBox.setIcon(PyQt5.QtWidgets.QMessageBox.Critical)
   msgBox.addButton(PyQt5.QtWidgets.QMessageBox.Ok)
   msgBox.setText('{} is not an UCI engine'.format(executable))
   msgBox.setWindowTitle("Error")
   msgBox.exec()
   return None
  return engine
 
 @PyQt5.QtCore.pyqtSlot()
 def on_detailsPushButton_clicked(self):
  executable = self.executableLineEdit.text()   
  if len(executable) == 0:
   self.notifyError('Executable undefined')
   return
  name = self.nameLineEdit.text()
  engine = self.checkEngine(executable)
  if engine is not None:
   dialog = ConfigureEngineOptions()
   newEngineDetails = dialog.run(engine.optionsDict, changedOptions = self.engineDetails, name = name)
   if newEngineDetails != self.engineDetails:
    self.engineDetails = newEngineDetails
    self.isChanged = True

 @PyQt5.QtCore.pyqtSlot()
 def on_browsePushButton_clicked(self):
  fDialog = PyQt5.QtWidgets.QFileDialog()
  fDialog.setFileMode(PyQt5.QtWidgets.QFileDialog.ExistingFile)
  fDialog.setOptions(self.fileDialogOptions)
  fDialog.setFilter(self.fileDialogFilters)
  fDialog.setWindowTitle("Load Engine Executable ...")
  if len(self.directories) > 0:
   fDialog.setHistory(self.directories)
  if len(self.executableLineEdit.text()) > 0:
   head, tail = os.path.split(self.executableLineEdit.text())
   fDialog.setDirectory(head)
   fDialog.selectFile(tail)
  if platform.system() == 'Windows':
   fDialog.setNameFilter("Executables (*.exe);;All Files (*)")
  else:
   fDialog.setNameFilter("All Files (*)")
  if fDialog.exec():
   executable = fDialog.selectedFiles()[0]
   self.engineDetails = dict()
   if self.checkEngine(executable) is not None:
    self.executableLineEdit.setText(executable)
    self.isChanged = True

 @PyQt5.QtCore.pyqtSlot(int, int)
 def on_engineTableWidget_cellClicked(self, row, column):
  if not self.ignoreIsChanged():
   return  
  name = self.engineTableWidget.cellWidget(row, 0).text()
  self.nameLineEdit.setText(name)
  self.executableLineEdit.setText(self.engineDict[name][0])
  self.engineDetails = self.engineDict[name][1]
  self.selectedRow = row

 @PyQt5.QtCore.pyqtSlot(str)
 def on_nameLineEdit_textEdited(self, newName):
  self.isChanged = True

 @PyQt5.QtCore.pyqtSlot(str)
 def on_executableLineEdit_textEdited(self, newExecutable):
  if self.checkEngine(newExecutable) is None:
   self.executableLineEdit.setText('')
   self.engineDetails = dict()
  self.isChanged = True

 @PyQt5.QtCore.pyqtSlot()
 def on_savePushButton_clicked(self):
  name = self.nameLineEdit.text()
  executable = self.executableLineEdit.text()
  if not self.isChanged:
   return
  if len(executable) == 0:
   self.notifyError('Executable undefined')
   return
  self.engineDict[name] = [executable, self.engineDetails]
  self._fillForm()
  self.isChanged = False
 
 @PyQt5.QtCore.pyqtSlot()
 def on_removePushButton_clicked(self):
  if not self.ignoreIsChanged():
   return
  key = self.engineTableWidget.cellWidget(self.selectedRow, 0).text()
  self.engineDict.pop(key, None)
  self.engineTableWidget.removeRow(self.selectedRow)
  self.selectedRow = None
  
 @PyQt5.QtCore.pyqtSlot()
 def on_cancelPushButton_clicked(self):
  self.done(False)
  
 @PyQt5.QtCore.pyqtSlot()
 def on_okPushButton_clicked(self):
  if self.ignoreIsChanged():
   self.done(True)

if __name__ == "__main__":
 import os,  os.path
 import sys
 import configparser

 qApp=PyQt5.QtWidgets.QApplication(sys.argv)   

 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 os.chdir(fileDirectory)
 
 settingsFile = os.path.join(fileDirectory, 'settings.ini')
 settings = configparser.ConfigParser(delimiters=['='], allow_no_value=True)
 settings.optionxform = str
 settings.read(settingsFile, encoding = 'utf-8')
 engineDict = loadEngineSettings(settings)

 configureEngine = ConfigureEngine()
 print(engineDict)
 for name in engineDict:
  engineDict[name] = [engineDict[name], dict()] 
 configureEngine.show()
 newEngineDict = configureEngine.run(engineDict = engineDict, log = True)
 print('------- new')
 print(newEngineDict)
 qApp.exec_()
