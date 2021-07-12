MzChess
===========================
A chess GUI using PyQt5 and `chess`_ modules.

Installing
----------

If you’re on Linux, you should install
the binary packages *PyQt5*, *PyQt5.QtChart*, and - if available - *PyQt5.QtSvg* using
the `Linux Package Manager`_ to avoid a compilation of the huge sources. 
Then, download and install the latest release:

::

    pip install mzChess
    
Running
----------

An executable is generated and installed in python's *Scripts* directory. 
So, if this directory is in your search *PATH*, you type simply

::

    mzChess

to start the GUI

Contents
-----------

.. toctree::
  :maxdepth: 2

  gui
  utilities

Indices and tables
-----------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _chess: https://pypi.org/project/chess
.. _Linux Package Manager: https://en.wikipedia.org/wiki/List_of_software_package_management_systems
