import subprocess
import platform
import shutil
import glob
import sys
import os, os.path

# Try using setuptools first, if it's installed
from setuptools import setup
from packaging import version

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

pyQt5Version = '5.11.0'
if platform.system() == 'Linux':
 # this code helps, if the package manager does not create egg files (e.g. debian 10)
 install_requires = list()
 try:
  import PyQt5.QtCore
  import PyQt5.QtGui
  import PyQt5.QtWidgets
  foundPyQt5Version = PyQt5.QtCore.PYQT_VERSION_STR
 except:
  foundPyQt5Version = '0.0.0'
 if version.parse(pyQt5Version) > version.parse(foundPyQt5Version):
  install_requires = ['PyQt5>={}'.format(pyQt5Version)]
 try:
  import PyQt5.QtSvg
 except:
  print('Install PyQt5.QtSvg using your Linux Package Manager')
  quit()
 try:
  import PyQt5.QtChart
 except:
  install_requires.append('PyQtChart>={}'.format(pyQt5Version))
else:
 install_requires = ['PyQt5>={}'.format(pyQt5Version), 'PyQtChart>={}'.format(pyQt5Version)]

install_requires += ['chess>=1.4', 'ply>=3.11']

# Need to add all dependencies to setup as we go!
setup(name = package,
  url = 'https://github.com/ReinhardM-dev/MzChess', 
  version = pkgVersion,
  packages = [package],
  options={'bdist_wheel':{'universal':True}},
  package_data = {package: 
    ['*.txt', '*.ui', '*.gpl3', '*.rst', '*.png',  
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
  install_requires = install_requires,
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

