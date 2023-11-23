""" Main for Jupytext_config

Call with (e.g.)::

    python -m jupytext_config list-default-viewer
"""

import sys

from .jupytext_config import main

if __name__ == "__main__":
    sys.exit(main())
