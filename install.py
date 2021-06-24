import subprocess
import platform
import shutil
import glob
import os, os.path
fileDirectory = os.path.dirname(os.path.abspath(__file__))
leipfontFile = os.path.join(fileDirectory, 'pieces', 'LEIPFONT.ttf')

if platform.system() == 'Linux':
 hasPyQt5 = False
 try:
  import PyQt5.QtCore
  import PyQt5.QtGui
  import PyQt5.QtWidgets
  hasPyQt5 = True
 except:
  print('Install PyQt5 Base package from your LINUX distribution')
 if hasPyQt5:
  try:
   import PyQt5.QtSvg
  except:
   print('Install PyQt5.QtSvg from your LINUX distribution')
  try:
   import PyQt5.QtChart
  except:
   print('Install PyQt5.QtChart from your LINUX distribution')
 subprocess.run(['python3', '-m', 'pip', 'install', 'chess'])
 fontFileList = map(lambda x : x.split(":")[0], subprocess.getstatusoutput('fc-list')[1].split("\n"))
 hasLEIPFONT = False
 for fileName in fontFileList:
  if os.path.basename(leipfontFile) in fileName:
   hasLEIPFONT = True
 if not hasLEIPFONT:
  fontDir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'fonts')
  if not os.path.isdir(fontDir):
   os.mkdir(fontDir)
  for file in glob.glob(leipfontFile):
   shutil.copyfile(file, os.path.join(fontDir, file))
  os.system('fc-cache -f -v')
else:
 subprocess.run(['pip', 'install', 'PyQt5'])
 subprocess.run(['pip', 'install', 'PyQtChart'])
 subprocess.run(['pip', 'install', 'chess'])
 fDB = PyQt5.QtGui.QFontDatabase()
 if 'Chess Leipzig' not in fDB.families():
  PyQt5.QtGui.QFontDatabase.addApplicationFont(leipfontFile)
 
settingsFile = os.path.join(fileDirectory, 'settings.ini')
if os.path.exists(settingsFile):
 os.remove(settingsFile) 
