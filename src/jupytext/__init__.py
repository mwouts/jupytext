"""Read and write Jupyter notebooks as text files"""

from .formats import NOTEBOOK_EXTENSIONS, get_format_implementation, guess_format
from .jupytext import read, reads, write, writes
from .reraise import reraise
from .version import __version__

try:
    from .contentsmanager import build_jupytext_contents_manager_class
except ImportError as err:
    build_jupytext_contents_manager = reraise(err)

try:
    from .contentsmanager import TextFileContentsManager
except ImportError as err:
    TextFileContentsManager = reraise(err)

__all__ = [
    "read",
    "write",
    "writes",
    "reads",
    "NOTEBOOK_EXTENSIONS",
    "guess_format",
    "get_format_implementation",
    "TextFileContentsManager",
    "build_jupytext_contents_manager_class",
    "__version__",
]
