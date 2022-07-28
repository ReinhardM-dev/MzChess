import platform
import shutil
import sys
import os, os.path

# Try using setuptools first, if it's installed
from setuptools import setup
from packaging import version

package = 'MzChess'
fileDirectory = os.path.dirname(os.path.abspath(__file__))
packageDirectory = os.path.join(fileDirectory, package)
sys.path.insert(0, packageDirectory)

with open(os.path.join(packageDirectory,'readme.rst'), 'r', encoding = 'utf-8') as f:
 long_description = f.read()
 
import MzChess
pkgVersion = MzChess.__version__

leipfontFile = os.path.join(packageDirectory, 'pieces', 'LEIPFONT.ttf')

if platform.system() == 'Linux':
 # On Linux systems PyQt must be installed using a package manager
 install_requires = list()
 try:
  import PyQt6.QtCore
  foundPyQtVersion = PyQt6.QtCore.PYQT_VERSION_STR
  if version.parse(foundPyQtVersion) < version.parse('6.2'): 
   print('Upgrade to PyQt6>=6.2 using your Linux Package Manager')
  try:
   import PyQt6.QtSvgWidgets
  except:
   print('Install PyQt6.QtSvgWidgets using your Linux Package Manager')
   quit()
  try:
   import PyQt6.QtCharts
  except:
   print('Install PyQt6.QtCharts using your Linux Package Manager')
   quit()
# check PyQt5
 except:
  import PyQt5.QtCore
  foundPyQtVersion = PyQt5.QtCore.PYQT_VERSION_STR
  if version.parse(foundPyQtVersion) < version.parse('5.11'): 
   print('Upgrade to PyQt6>=6.2 or PyQt5>=5.11 using your Linux Package Manager')
  try:
   import PyQt5.QtSvg
  except:
   print('Install PyQt5.QtSvg using your Linux Package Manager')
   quit()
  try:
   import PyQt5.QtCharts
  except:
   print('Install PyQt5.QtCharts using your Linux Package Manager')
   quit()
else:
 pyQt6Version = '6.2.0'
 install_requires = ['PyQt6>={}'.format(pyQt6Version), 'PyQt6-Charts>={}'.format(pyQt6Version)]

install_requires += ['chess>=1.4', 'ply>=3.11']

# Required to ensure a clean environment
shutil.rmtree(os.path.join(fileDirectory, 'build'), ignore_errors = True)

# Need to add all dependencies to setup as we go!
setup(name = package,
  url = 'https://github.com/ReinhardM-dev/MzChess', 
  project_urls={ 'Documentation': 'https://reinhardm-dev.github.io/MzChess' }, 
  version = pkgVersion,
  packages = [package],
  options={'bdist_wheel':{'universal':True}},
  package_data = {package: 
    ['*.txt', '*.ui', '*.gpl3', '*.rst', '*.png',  
     'books/*.txt', 
     'eco/*.fsc', 'eco/*.tsv', 'eco/*.txt', 'eco/*.md', 'eco/bin/*',
     'pieces/*.svg', 'pieces/*.ttf', 
     'training/*/*.pgn'] }, 
  description = 'A Chess GUI using PyQt6',
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


