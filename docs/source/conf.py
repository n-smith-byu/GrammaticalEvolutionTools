# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath so that Sphinx finds it.

import os
import sys
from pathlib import Path

# Assuming your Python package 'my_package' is inside a 'src' directory
# that is located one level up from your 'docs' folder,
# and 'conf.py' is inside 'docs/source'.
# This path points to 'my_awesome_project/src/'
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GrammaticalEvolutionTools'
copyright = '2025, Nick Smith'
author = 'Nick Smith'
release = '0.0.1' # The full version, including alpha/beta/rc tags


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',       # For pulling docstrings from code
    'sphinx.ext.napoleon',      # For parsing NumPy/Google style docstrings
    'sphinx.ext.viewcode',      # For adding links to source code
    'sphinx.ext.intersphinx',   # For linking to other projects' docs (e.g., Python, NumPy)
    'sphinx.ext.todo',          # If you use .. todo:: directives
    'sphinx.ext.duration',      # Measures build times
    'sphinx.ext.doctest',       # Tests code examples in doctests
    'sphinx.ext.autosummary',   # Generates summary tables for API
    # 'sphinx.ext.mathjax',     # Uncomment if you have LaTeX math
    # 'sphinx.ext.githubpages', # Uncomment if deploying to GitHub Pages
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Napoleon Configuration --------------------------------------------------
# Options for sphinx.ext.napoleon, which parses NumPy/Google style docstrings

napoleon_google_docstring = False  # Keep False if primarily using NumPy style
napoleon_numpy_docstring = True    # Set to True for NumPy-style docstrings
napoleon_include_init_with_doc = False # Usually handled by autodoc if __init__ has a docstring
napoleon_include_private_with_doc = True # Set to True to document private members (e.g., _my_method)
napoleon_include_special_with_doc = True # Set to True to document special methods (e.g., __str__)
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False         # True for :ivar: False for :attribute:
napoleon_use_param = True         # True for :param: False for :type:
napoleon_preprocess_types = False # Keep False, let autodoc handle type hints
napoleon_type_aliases = None
napoleon_attr_annotations = True  # Important for recognizing type hints in attributes

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme' # Recommended theme for modern look and features

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Intersphinx Configuration -----------------------------------------------
# This allows you to link to documentation of other projects (e.g., Python standard library)
# To use this, uncomment the 'sphinx.ext.intersphinx' extension above.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    # Add other projects as needed
}

# -- Todo Extension Configuration --------------------------------------------
# If you enable 'sphinx.ext.todo', you can use the .. todo:: directive.
# Setting todo_include_todos to True will display the content of these directives.
todo_include_todos = True