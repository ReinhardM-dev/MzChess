from typing import Optional,  Callable
import subprocess
import platform
import shutil
import glob

def installLeipFont(notify : Optional[Callable[[str], None]] = None) -> None:
 import sys, os, os.path
 sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 import MzChess
 
 if MzChess.useQt5():
  from PyQt5 import QtGui
  families = QtGui.QFontDatabase().families()
 else:
  from PyQt6 import QtGui
  families = QtGui.QFontDatabase.families()
 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 leipfontFile = os.path.join(fileDirectory, 'pieces', 'LEIPFONT.ttf')
 if platform.system() == 'Linux_':
  fontFileList = map(lambda x : x.split(':')[0], subprocess.getstatusoutput('fc-list')[1].split('\n'))
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
   if notify is not None:
    notify('Chess font {} added'.format(leipfontFile))
  elif notify is not None:
   notify('Chess font {} already installed'.format(leipfontFile))
 else:
  if 'Chess Leipzig' not in families:
   assert QtGui.QFontDatabase.addApplicationFont(leipfontFile) != -1, "installLeipFont: Could not add 'Chess Leipzig' font"
   if notify is not None:
    notify('Chess font {} added'.format(leipfontFile))
  elif notify is not None:
   notify('Chess font {} already installed'.format(leipfontFile))
