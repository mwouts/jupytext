"""R markdown notebook format for Jupyter

Use this module to read or write Jupyter notebooks as Markdown documents,
R markdown documents, Python or R scripts (methods 'read', 'reads', 'write',
'writes')

Use the TextFileContentsManager to open Rmd and Jupyter notebooks in Jupyter

Use the 'jupytext' conversion script to convert Jupyter notebooks from/to
R Markdown notebooks.
"""

from .jupytext import readf, writef, writes, reads
from .formats import NOTEBOOK_EXTENSIONS
from .header import INSERT_AND_CHECK_VERSION_NUMBER

try:
    from .textexporter import RMarkdownExporter, MarkdownExporter, \
        LightPythonExporter, LightJuliaExporter, RKnitrSpinExporter

except ImportError as err:
    RMarkdownExporter = MarkdownExporter = LightPythonExporter = \
        LightJuliaExporter = RKnitrSpinExporter = str(err)

try:
    from .contentsmanager import TextFileContentsManager
except ImportError as err:
    TextFileContentsManager = str(err)

__all__ = ['readf', 'writef', 'writes', 'reads',
           'NOTEBOOK_EXTENSIONS',
           'RMarkdownExporter', 'MarkdownExporter', 'LightPythonExporter',
           'LightJuliaExporter', 'RKnitrSpinExporter',
           'TextFileContentsManager']
