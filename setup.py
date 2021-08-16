import subprocess
import platform
import shutil
import glob
import sys
import os, os.path

import PyQt5.QtGui

# Try using setuptools first, if it's installed
from setuptools import setup
from packaging import version

package = 'MzChess'
fileDirectory = os.path.dirname(os.path.abspath(__file__))
packageDirectory = os.path.join(fileDirectory, package)
sys.path.insert(0, fileDirectory)

with open(os.path.join(packageDirectory,'readme.rst'), 'r', encoding = 'utf-8') as f:
 long_description = f.read()
 
import MzChess
pkgVersion = MzChess.__version__

leipfontFile = os.path.join(packageDirectory, 'pieces', 'LEIPFONT.ttf')

pyQt5Version = '5.11.0'
if platform.system() == 'Linux':
 # this code helps, if the package manager does not create egg files (e.g. debianos.rename('a.txt', 'b.kml') 10)
 install_requires = list()
 try:
  import PyQt5.QtCore
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

# Required to ensure a clean environment
shutil.rmtree(os.path.join(fileDirectory, 'build'), ignore_errors = True)

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
  entry_points={ 'gui_scripts': 
                         ['buildFen = {}:runFenBuilder'.format(package),
                          'mzChess = {}:runMzChess'.format(package)] }, 
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

app = PyQt5.QtGui.QGuiApplication([])
MzChess.installLeipFont(print)

settingsFile = os.path.join(fileDirectory, 'settings.ini')
if os.path.exists(settingsFile):
 os.remove(settingsFile) 

