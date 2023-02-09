MzChess
===========================
A chess GUI using PyQt6 (or alternatively PyQt5) and `chess`_ modules.

Installing
----------

Mz Chess is based on Python 3.7+.

.. warning::
 
 If you’re not on Windows, you are responsible for the installation of the binary PyQt-packages, i.e.

  * *PyQt6*, *PyQt6.QtCharts* (v6.2+)
  * or *PyQt5*, *PyQt5.QtChart*, and - if available - *PyQt5.QtSvg* (v5.11+),

 using a `Linux Package Manager`_, `Homebrew`_ or pip3 in advance. 
 Linux users planning a pip3 installation should consult the `manylinux`_ webpage 
 to see whether their distribution is supported.
 
Then, download and install the latest release:

::

    pip install mzChess

Running
----------

An executable is generated and installed in python's *Scripts* directory. 
So, if this directory is in your search *PATH*, you type simply

::

    mzChess

to start the chess GUI. An extra tool
::

   analysePosition
   
allows to evaluate the position using the Forsyth-Edwards Notation (`FEN`_)
and principles described in the chess programming website (`CPE`_). A little helper

::

   buildFen
   
allows to build position strings using the Forsyth-Edwards Notation (`FEN`_)
and copy them to the clipboard.

If you are under Windows or Linux, you can run 

::

    <python> -c "import MzChess; MzChess.postInstall()"  

to get symbolic links to the tools *mzChess* and *fenBuild* on the desktop 
(*<python>* is the python interpreter used for installation).
Under Windows, the *postInstall* function must be executed as administrator.

.. toctree::
  :maxdepth: 2

  gui
  analysePosition
  buildFen

..
  analysePosition
  buildFen
  utilities

Indices and tables
-----------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _chess: https://pypi.org/project/chess
.. _Linux Package Manager: https://en.wikipedia.org/wiki/List_of_software_package_management_systems
.. _Homebrew: https://docs.brew.sh/
.. _manylinux: https://github.com/pypa/manylinux
.. _CPE: https://www.chessprogramming.org/Evaluation
.. _FEN: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
