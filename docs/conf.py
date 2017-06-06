#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is execfile()d with the current directory set to its
# containing dir.

import sys
import os

# -- General configuration ------------------------------------------------

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
version = '1.0'  # The short X.Y version.
release = version  # The full version, including alpha/beta/rc tags.

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Python Project'
copyright = '2017, Tim Diels'
author = 'Tim Diels'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['build']

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'python_project.tex', 'Python Project Documentation',
     'Tim Diels', 'manual'),
]

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'python_project', 'Python Project Documentation',
     [author], 1)
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'python_project', 'Python Project Documentation',
     author, 'python_project', 'Python project structure documentation.',
     'Miscellaneous'),
]
