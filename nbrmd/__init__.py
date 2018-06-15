"""R markdown notebook format for Jupyter

Use this module to read or write Jupyter notebooks as Rmd documents (methods 'read', 'reads', 'write', 'writes')

Use the 'pre_save_hook' method (see its documentation) to automatically dump your Jupyter notebooks as a Rmd file, in addition
to the ipynb file.

Use the 'nbrmd' conversion script to convert Jupyter notebooks from/to R markdown notebooks.
"""

from .nbrmd import read, reads, write, writes
from .jupyter_hook import pre_save_hook