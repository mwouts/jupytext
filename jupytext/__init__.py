"""R markdown notebook format for Jupyter

Use this module to read or write Jupyter notebooks as Markdown documents,
R markdown documents, Python or R scripts (methods 'read', 'reads', 'write',
'writes')

Use the TextFileContentsManager to open Text notebooks in Jupyter

Use the 'jupytext' conversion script to convert Jupyter notebooks from/to
R Markdown notebooks.
"""

from .jupytext import readf, writef, writes, reads
from .formats import NOTEBOOK_EXTENSIONS, guess_format, get_format

try:
    from .contentsmanager import TextFileContentsManager
except ImportError as err:
    class TextFileContentsManager:
        """A class that raises the previous ImportError"""
        err = err

        def __init__(self):
            raise self.err

__all__ = ['readf', 'writef', 'writes', 'reads',
           'NOTEBOOK_EXTENSIONS', 'guess_format', 'get_format',
           'TextFileContentsManager']
