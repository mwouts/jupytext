"""R markdown notebook format for Jupyter

Use this module to read or write Jupyter notebooks as R Markdown documents
(methods 'read', 'reads', 'write', 'writes')

Use the RmdFileContentsManager to open Rmd and Jupyter notebooks in Jupyter

Use the 'nbrmd' conversion script to convert Jupyter notebooks from/to
R Markdown notebooks.
"""

from .nbrmd import readf, writef, writes, reads, NOTEBOOK_EXTENSIONS
from .file_format_version import FILE_FORMAT_VERSION

try:
    from .rmarkdownexporter import RMarkdownExporter
    from .srcexporter import PyNotebookExporter
    from .srcexporter import RNotebookExporter
except ImportError as err:
    RMarkdownExporter = PyNotebookExporter = RNotebookExporter = str(err)

try:
    from .contentsmanager import RmdFileContentsManager
except ImportError as err:
    RmdFileContentsManager = str(err)

__all__ = ['readf', 'writef', 'writes', 'reads',
           'NOTEBOOK_EXTENSIONS', 'FILE_FORMAT_VERSION',
           'RMarkdownExporter', 'PyNotebookExporter', 'RNotebookExporter',
           'RmdFileContentsManager']
