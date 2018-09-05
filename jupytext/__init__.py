"""R markdown notebook format for Jupyter

Use this module to read or write Jupyter notebooks as Markdown documents,
R markdown documents, Python or R scripts (methods 'read', 'reads', 'write',
'writes')

Use the TextFileContentsManager to open Rmd and Jupyter notebooks in Jupyter

Use the 'jupytext' conversion script to convert Jupyter notebooks from/to
R Markdown notebooks.
"""

from .jupytext import readf, writef, writes, reads, NOTEBOOK_EXTENSIONS
from .file_format_version import FILE_FORMAT_VERSION

try:
    from .rmarkdownexporter import RMarkdownExporter
    from .srcexporter import PyNotebookExporter
    from .srcexporter import RNotebookExporter
    from .srcexporter import JlNotebookExporter
except ImportError as err:
    RMarkdownExporter = PyNotebookExporter = JlNotebookExporter =\
        RNotebookExporter = str(err)

try:
    from .contentsmanager import TextFileContentsManager
except ImportError as err:
    TextFileContentsManager = str(err)

__all__ = ['readf', 'writef', 'writes', 'reads',
           'NOTEBOOK_EXTENSIONS', 'FILE_FORMAT_VERSION',
           'RMarkdownExporter', 'PyNotebookExporter', 'RNotebookExporter',
           'TextFileContentsManager']
