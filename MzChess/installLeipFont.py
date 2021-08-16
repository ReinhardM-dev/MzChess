from typing import Optional,  Callable
import subprocess
import platform
import shutil
import glob
import os, os.path
import PyQt5.QtGui

def installLeipFont(notify : Optional[Callable[[str], None]] = None) -> None:
 fileDirectory = os.path.dirname(os.path.abspath(__file__))
 leipfontFile = os.path.join(fileDirectory, 'pieces', 'LEIPFONT.ttf')
 if platform.system() == 'Linux':
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
  fDB = PyQt5.QtGui.QFontDatabase()
  if 'Chess Leipzig' not in fDB.families():
   PyQt5.QtGui.QFontDatabase.addApplicationFont(leipfontFile)
   if notify is not None:
    notify('Chess font {} added'.format(leipfontFile))
  elif notify is not None:
   notify('Chess font {} already installed'.format(leipfontFile))
