"""Read and write Jupyter notebooks as text files"""

from .jupytext import readf, writef, writes, reads
from .formats import NOTEBOOK_EXTENSIONS, guess_format, get_format_implementation
from .version import __version__

try:
    from .contentsmanager import TextFileContentsManager
except ImportError as err:
    class TextFileContentsManager:
        """A class that raises the previous ImportError"""
        err = err

        def __init__(self):
            raise self.err

__all__ = ['readf', 'writef', 'writes', 'reads',
           'NOTEBOOK_EXTENSIONS', 'guess_format', 'get_format_implementation',
           'TextFileContentsManager', '__version__']
