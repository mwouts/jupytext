"""Read and write Jupyter notebooks as text files"""

from .contentsmanager import (
    TextFileContentsManager,
    build_jupytext_contents_manager_class,
)
from .formats import NOTEBOOK_EXTENSIONS, get_format_implementation, guess_format
from .jupytext import read, reads, write, writes
from .version import __version__

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
