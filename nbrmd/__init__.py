"""R markdown notebook format for Jupyter

Use this module to read or write Jupyter notebooks as R Markdown documents
(methods 'read', 'reads', 'write', 'writes')

Use the RmdFileContentsManager to open Rmd and Jupyter notebooks in Jupyter

Use the 'nbrmd' conversion script to convert Jupyter notebooks from/to
R Markdown notebooks.
"""

from .nbrmd import read, reads, readf, write, writes, writef

try:
    from .rmarkdownexporter import RMarkdownExporter
except ImportError as e:
    RMarkdownExporter = str(e)

try:
    from .cm import RmdFileContentsManager
except ImportError as e:
    RmdFileContentsManager = str(e)
