"""Read and write Jupyter notebooks as text files"""

from .async_contentsmanager import (
    AsyncTextFileContentsManager,
    build_async_jupytext_contents_manager_class,
)
from .formats import NOTEBOOK_EXTENSIONS, get_format_implementation, guess_format
from .jupytext import read, reads, write, writes
from .sync_contentsmanager import (
    TextFileContentsManager,
    build_sync_jupytext_contents_manager_class,
)
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
    "AsyncTextFileContentsManager",
    "build_sync_jupytext_contents_manager_class",
    "build_async_jupytext_contents_manager_class",
    "__version__",
]
