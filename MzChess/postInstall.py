#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module implementing the post install tasks not done by 'pip install'.
"""

import sys
import os, os.path
import platform
import shutil

def postInstall():
 osName = platform.system()
 home = os.path.expanduser('~')
 scripts = ['mzChess',  'buildFen']
 scriptIcons = ['schach.png',  'schach.png']
   
 if osName == 'Windows':
  import ctypes
  if ctypes.windll.shell32.IsUserAnAdmin() != 1:
   raise PermissionError('Admin privileges required to run this script.')
  scriptsDir = os.path.join(os.path.dirname(sys.executable), 'Scripts')
  desktopDir = os.path.join(home, 'Desktop')
  for script in scripts:
   src = os.path.join(scriptsDir,'{}.exe'.format(script))
   scriptTgt = os.path.join(scriptsDir, script)
   tgt = os.path.join(desktopDir, script)
   if os.path.exists(scriptTgt):
    os.remove(scriptTgt)
   os.symlink(src, scriptTgt)
   if os.path.exists(tgt):
    os.remove(tgt)
   shutil.move(scriptTgt, tgt)
 elif osName == 'Linux':
  import MzChess
  packageDir = os.path.dirname(MzChess.__file__)
  desktopDir = os.path.join(home, '.local', 'share', 'applications')
  iconsDir = os.path.join(home, '.local', 'share', 'icons')
  hasDeskopFileInstall = True
  for script, icon in zip(scripts, scriptIcons):
   iconPath = os.path.join(packageDir, icon)
   shutil.copy(iconPath, iconsDir, follow_symlinks = False)
   scriptPath = shutil.which(script)
   src = os.path.join(packageDir, '{}.desktop'.format(script))
   tgt = os.path.join(home, '{}.desktop'.format(script))
   with open(src, "r", encoding="utf-8") as f:
    text = f.read()
   text = text.format(scriptPath = scriptPath)
   with open(tgt, "w", encoding="utf-8") as f:
    f.write(text)
   if os.system('desktop-file-install --delete-original --dir={} {}'.format(desktopDir, tgt)) == -1:
    os.chmod(tgt, 0o644)
    shutil.move(tgt, desktopDir)
    hasDeskopFileInstall = False
  if not hasDeskopFileInstall:
   raise OSError('desktop-file-install failed, .desktop files manually moved to {}'.format(desktopDir))
 else:
  raise OSError('OS "{}" is not supported'.format(osName))

if __name__ == "__main__":
 postInstall()

