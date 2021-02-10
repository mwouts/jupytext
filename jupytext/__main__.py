""" Main for Jupytext

Call with (e.g.)::

    python -m jupytext my_notebook.ipynb --to Rmd
"""

import sys

from .cli import jupytext

if __name__ == "__main__":
    sys.exit(jupytext())
