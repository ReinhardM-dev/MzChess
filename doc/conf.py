# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
import os

sys.path.insert(0, os.path.abspath('..'))

try:
 from PyQt6 import QtWidgets
except:
 try:
  from PyQt5 import QtWidgets
 except:
  raise ModuleNotFoundError('Neither the required PyQt6.QtWidgets nor PyQt5.QtWidgets installed')

# -- Project information -----------------------------------------------------
# Avoid PyQt statements in the static part, since they are executed by sphinx
import MzChess

project = 'MzChess'
copyright = '2022, Reinhard März'
author = 'Reinhard März'

# The full version, including alpha/beta/rc tags
# The use of importlib.metadata is the only way compliant with sphinx
__version__ = MzChess.__version__
release = 'V' + __version__
version = 'V' + '.'.join(__version__.split('.')[:2])

# -- General configuration ---------------------------------------------------
master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc.typehints', 
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx', 
    'sphinx.ext.githubpages',
]
autosummary_generate = False
autodoc_typehints = 'signature'

autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': '__init__',
    'exclude-members': '__weakref__'
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['Ui_*', '*.txt']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# -- Options for HTML output -------------------------------------------------

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
html_static_path = []

print('conf.py left')
