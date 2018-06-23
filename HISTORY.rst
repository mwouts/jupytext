.. :changelog:

Release History
---------------

dev
+++

0.2.1 (2018-06-24)
+++++++++++++++++++

**Improvements**
- Support for editing markdown files in Jupyter
- New pre-save hook `update_selected_formats` that saves to formats in metadata 'nbrmd_formats'
- Rmd cell options directly mapped to cell metadata

**BugFixes**
- ContentManager compatible with Python 2.7

0.2.0 (2018-06-21)
+++++++++++++++++++

**Improvements**
- The package provides a ``RmdFileContentsManager`` for direct edit of R markdown files in Jupyter
- Notebook metadata and cell options are preserved


0.1.1 (2018-06-19)
+++++++++++++++++++

**Improvements**
- ``nbrmd`` prints the result of conversion to stdout, unless flag ``-i`` is provided
- Notebooks with R code chunks are supported

0.1 (2018-06-18)
+++++++++++++++++++

- Initial version with the ``nbrmd`` converter and Jupyter ``pre_save_hook``

