"""R markdown notebook format for Jupyter

Use this module to read or write Jupyter notebooks as R Markdown documents
(methods 'read', 'reads', 'write', 'writes')

Use the jupyter pre-save hooks (see the documentation) to automatically
dump your Jupyter notebooks as a Rmd file, in addition to the ipynb file
(or the opposite)

Use the 'nbrmd' conversion script to convert Jupyter notebooks from/to
R Markdown notebooks.
"""

from .nbrmd import readf, writef, writes, reads, notebook_extensions, readme
from .hooks import *

try:
    from .rmarkdownexporter import RMarkdownExporter
except ImportError as e:
    RMarkdownExporter = str(e)

try:
    from .cm import RmdFileContentsManager
except ImportError as e:
    RmdFileContentsManager = str(e)
