.. :changelog:

Release History
---------------

dev
+++

0.6.2 (2018-09-??)
+++++++++++++++++++

**Improvements**

- Initial support for Jupyter notebooks as Julia scripts (#56)
- round trip test with `jupytext --test` improved (#54)

**BugFixes**

- testfixtures now in requirements (#55)
- TODO: empty code cells are now preserved (#53)

0.6.1 (2018-08-31)
+++++++++++++++++++

**Improvements**

- Package and conversion script renamed from `nbrmd` to `jupytext`.

0.6.0 (2018-08-31)
+++++++++++++++++++

**Improvements**

- Cell parsing and exporting done in two specialized classes. This is way
easier to read. Pylint score at 9.9 !
- Python file format updated to 1.1: default end of cell for python scripts is
one blank space. Two blank spaces are allowed as well. Now you can reformat
code in Python IDE without breaking notebook cells (#38).
- Added support for plain markdown files (#40, #44).
- Demonstration notebooks more user friendly (#45).
- Command line tool simpler to use (#46).
- Start code patterns present in Jupyter cells are escaped.
- Default `nbrmd_format` is empty (mwouts/nbsrc/#5): no Jupyter notebook
is created on disk when the user opens a Python or R file and saves it from
Jupyter, unless the users asks for it by setting `nbrmd_format`.

**BugFixes**

- Fixed message in the `nbsrc` script (#43)
- Technical metadata don't appear any more in scripts unless required (#42)
- Code cells that are fully commented remain code cells after round trip (#41)

0.5.4 (2018-08-24)
+++++++++++++++++++

**Improvements**

- R to Rmd conversion compares well to knitr::spin (#26)
- Increased coverage to 98%


0.5.3 (2018-08-22)
+++++++++++++++++++

**BugFixes**

- Read and write version to the same metadata (#36)


0.5.2 (2018-08-22)
+++++++++++++++++++

**Improvements**

- Classical jupyter extensions (autoreload, rmagics) are also escaped (#35)
- Explicit file format version, set at 1.0, to avoid overriding ipynb
files by accident (#36)


0.5.1 (2018-08-21)
+++++++++++++++++++

**BugFixes**

- Source only notebooks can be trusted.

0.5.0 (2018-08-21)
+++++++++++++++++++

**Improvements**

- Jupyter magic commands escaped when exported (#29)
- 'endofcell' option for explicit (optional) end-of-cell marker (#31)
- 'active' cell option now supported for .py and .R export (#30)
- Raw cells now preserved when exported to .py or .R (#32)
- Extensions can be prefixed, like `.nb.py`, (mwouts/nbsrc#5)
- When a file with an extension not associated to 'ipynb' is opened and saved,
no 'ipynb' file is created (mwouts/nbsrc#5)
- Extensions can now be a sequence of groups. For instance,
`nbrmd_formats="ipynb,nb.py;script.ipynb,py"` will create an `ipynb` file
when a `nb.py` is opened (and conversely), and a `script.ipynb` file when a
`py` file is opened (mwouts/nbsrc#5)
- `nbsrc` script was moved to the `nbrmd` package. The `nbsrc` package now only
contains the documentation (mwouts/nbsrc#3)


0.4.6 (2018-07-26)
+++++++++++++++++++

- Ping pypi - previous version still not available


0.4.5 (2018-07-26)
+++++++++++++++++++

**BugFixes**

- Removed dependency of `setup.py` on `yaml`

0.4.4 (2018-07-26)
+++++++++++++++++++

**BugFixes**

- Package republished with `python setup.py sdist bdist_wheel` to fix missing
dependencies

0.4.3 (2018-07-26)
+++++++++++++++++++

**Improvements**

- Multiline comments now supported #25
- Readme refactored, notebook demos available on binder #23

**BugFixes**

- ContentsManager can be imported even if `notebook.transutils` is not
available, for compatibility with older python distributions.
- Fixed missing cell metadata #27
- Documentation tells how to avoid creating `.ipynb` files #16

0.4.2 (2018-07-23)
+++++++++++++++++++

**Improvements**

- Added test for R notebooks
- Added pylint badge, imports now in correct order
- New `active` cell metadata that allows cell activation only for desired
extensions (currently available for Rmd and ipynb extensions only)

0.4.1 (2018-07-20)
+++++++++++++++++++

**BugFixes**

- Indented python code will not start a new cell #20
- Fixed parsing of Rmd cell metadata #21

0.4.0 (2018-07-18)
+++++++++++++++++++

**Improvements**

- `.py` format for notebooks is lighter and pep8 compliant

**BugFixes**

- Default nbrmd config not added to notebooks (#17)
- `nbrmd_formats` becomes a configurable traits (#16)
- Removed `nbrmd_sourceonly_format` metadata. Source notebook is current notebook
when not `.ipynb`, otherwise the first notebook format in `nbrmd_formats` (not
`.ipynb`) that is found on disk

0.3.0 (2018-07-17)
+++++++++++++++++++

**Improvements**

- Introducing support for notebooks as python `.py` or R scripts `.R`

0.2.6 (2018-07-13)
+++++++++++++++++++

**Improvements**

- Introduced `nbrmd_sourceonly_format` metadata
- Inputs are loaded from `.Rmd` file when a matching `.ipynb` file is
opened.

**BugFixes**

- Trusted notebooks remain trusted (#12)

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

