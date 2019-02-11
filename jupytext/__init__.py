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

def _jupyter_nbextension_paths():
    """Allows commands like
     jupyter nbextension install --py jupytext
     jupyter nbextension enable --py jupytext
     jupyter labextension install jupyterlab-jupytext"""
    return [dict(
        section="notebook",
        # the path is relative to the `jupytext` directory
        src="nbextension",
        # directory in the `nbextension/` namespace
        dest="jupytext",
        # _also_ in the `nbextension/` namespace
        require="jupytext/index")]


__all__ = ['readf', 'writef', 'writes', 'reads',
           'NOTEBOOK_EXTENSIONS', 'guess_format', 'get_format_implementation',
           'TextFileContentsManager', '__version__']
