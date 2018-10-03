"""Jupytext's version number"""

import os

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'VERSION')) as version_file:
    JUPYTEXT_VERSION = version_file.read().strip()
