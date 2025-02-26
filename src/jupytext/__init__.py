"""Read and write Jupyter notebooks as text files"""

from .formats import NOTEBOOK_EXTENSIONS, get_format_implementation, guess_format
from .jupytext import read, reads, write, writes
from .reraise import reraise
from .version import __version__

try:
    from .sync_contentsmanager import build_sync_jupytext_contents_manager_class
except ImportError as err:
    build_sync_jupytext_contents_manager_class = reraise(err)

try:
    from .sync_contentsmanager import TextFileContentsManager
except ImportError as err:
    TextFileContentsManager = reraise(err)

try:
    from .async_contentsmanager import build_async_jupytext_contents_manager_class
except ImportError as err:
    build_async_jupytext_contents_manager_class = reraise(err)

try:
    from .async_contentsmanager import AsyncTextFileContentsManager
except ImportError as err:
    AsyncTextFileContentsManager = reraise(err)

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
