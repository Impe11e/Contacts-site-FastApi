import sys
import os

sys.path.append(os.path.abspath('..'))
project = 'Rest API'
copyright = '2025, Impe11e'
author = 'Impe11e'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
