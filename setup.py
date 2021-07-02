import subprocess
import platform
import shutil
import glob
import sys
import os, os.path

# Try using setuptools first, if it's installed
from setuptools import setup

package = 'MzChess'
fileDirectory = os.path.dirname(os.path.abspath(__file__))
packageDirectory = os.path.join(fileDirectory, package)
# os.chdir(fileDirectory)
sys.path.insert(0, packageDirectory)

with open(os.path.join(packageDirectory,'readme.rst'), 'r', encoding = 'utf-8') as f:
 long_description = f.read()
 
import MzChess
pkgVersion = MzChess.__version__

leipfontFile = os.path.join(packageDirectory, 'pieces', 'LEIPFONT.ttf')

# Need to add all dependencies to setup as we go!
setup(name = package,
  url = 'https://github.com/ReinhardM-dev/MzChess', 
  version = pkgVersion,
  packages = [package],
  options={'bdist_wheel':{'universal':True}}, 
  package_data = {'': 
    ['*.txt', '*.md', '*.ui', '*.gpl3', 
     'books/*.txt', 
     'eco/*.fsc', 'eco/*.tsv', 'eco/*.txt', 'eco/*.md', 'eco/bin/*',
     'pieces/*.svg', 'pieces/*.ttf', 
     'training/*/*.pgn'] }, 
  description = 'A Chess GUI using PyQt5',
  long_description = long_description, 
  long_description_content_type="text/x-rst",
  entry_points={ 'gui_scripts': ['mzChess = {}.chessMainWindow:runMzChess'.format(package)] }, 
  author  ='Reinhard Maerz',
  python_requires = '>=3.7', 
  install_requires = ['PyQt5>=5.7', 'PyQtChart>=5.7', 'chess>=1.4', 'ply>=3.11'],
  setup_requires=['wheel'], 
  classifiers = [
    'Programming Language :: Python', 
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Development Status :: 4 - Beta', 
    'Natural Language :: English', 
    'Topic :: Games/Entertainment :: Board Games'])
  
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
  print('Chess font {} installed'.format(leipfontFile))
 else:
  print('Chess font {} already installed'.format(leipfontFile))
else:
 import PyQt5.QtGui
 app = PyQt5.QtGui.QGuiApplication([])
 fDB = PyQt5.QtGui.QFontDatabase()
 if 'Chess Leipzig' not in fDB.families():
  PyQt5.QtGui.QFontDatabase.addApplicationFont(leipfontFile)
  print('Chess font {} installed'.format(leipfontFile))
 else:
  print('Chess font {} already installed'.format(leipfontFile))
 
settingsFile = os.path.join(fileDirectory, 'settings.ini')
if os.path.exists(settingsFile):
 os.remove(settingsFile) 

