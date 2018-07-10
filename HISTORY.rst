.. :changelog:

Release History
---------------

dev
+++

0.2.5 (2018-07-11)
+++++++++++++++++++

**Improvements**

- Outputs of existing `.ipynb` versions are combined with matching inputs
 of R markdown version, as suggested by @grst (#12)

**BugFixes**

- Support for unicode text in python 2.7 (#11)


0.2.4 (2018-07-05)
+++++++++++++++++++

**Improvements**

- nbrmd will always open notebooks, even if header of code cells are not terminated. Merge conflicts can thus be
solved in Jupyter directly.
- New metadata 'main language' that preserves the notebook language.

**BugFixes**

- dependencies included in `setup.py`
- pre_save_hook work with non-empty `notebook_dir` (#9)

0.2.3 (2018-06-28)
+++++++++++++++++++

**Improvements**

- Screenshots in README

**BugFixes**

- rmarkdown exporter for nbconvert fixed on non-recent python
- Tests compatible with other revisions of nbformat >= 4.0
- Tests compatible with older pytest versions


0.2.2 (2018-06-28)
+++++++++++++++++++

**Improvements**

- RMarkdown exporter for nbconvert
- Parsing of R options robust to parenthesis
- Jupyter cell tags are preserved

**BugFixes**

- requirements.txt now included in pypi packages

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

