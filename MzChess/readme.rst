MzChess: a chess GUI using PyQt5 and `chess`_ modules
==========================================================

The chess GUI allows for:

 * play standard chess games
 * configure the game header
 * load and/or save games and/or databases with many games
 * configure and run Universal Chess Interface (`UCI`_) engines
 * detects Encyclopaedia of Chess Openings (`ECO`_)
 * annotates games or single moves
 * shows score graphs
 * allows to monitor scores and move hints continously (for training purposes)
 * allows to warn on danger (for training purposes)
 * allows to show move options (for training purposes)

It supports the following game formats:

 * Portable Game Notation (`PGN`_) standard
 * Pickled PGN (*PPNG*), an internal format for rapid loading

Installing
--------------

If you’re on Linux, you should install
the binary packages *PyQt5*, *PyQt5.QtChart*, and - if available - *PyQt5.QtSvg* using
the `Linux Package Manager`_ to avoid a compilation of the huge sources. 
Then, download and install the latest release:

::

    pip install mzChess
    
Running the GUI
-----------------------

An executable is generated and installed in python's *Scripts* directory. 
So, if this directory is in your search *PATH*, you type simply

::

    mzChess

to start the GUI

.. _chess: https://pypi.org/project/chess
.. _UCI: http://wbec-ridderkerk.nl/html/UCIProtocol.html
.. _PGN: https://github.com/fsmosca/PGN-Standard
.. _ECO: https://github.com/niklasf/chess-openings
.. _Linux Package Manager: https://packaging.python.org/guides/installing-using-linux-tools/
