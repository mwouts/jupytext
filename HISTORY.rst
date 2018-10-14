.. :changelog:

Release History
---------------

0.8.2 (2018-10-15)
++++++++++++++++++++++

**Improvements**

- Round trip conversion testing with ``jupytext --test`` was improved (#99)
- Round trip conversion tested on Jake Vanderplas' Python for Data Science Handbook.

**BugFixes**

- Nested lists and dictionaries are now supported in notebook metadata
- Final empty code cell supported in Sphinx representation

0.8.1 (2018-10-11)
++++++++++++++++++++++

**BugFixes**

- Sphinx format tested on ``World population`` notebook (#97)
- Mirror test made stronger on this occasion!
- Markdown representation recognize Julia, Scheme and C++ code cells as such
- Light representation of Scheme and C++ notebooks fixed (#61)

0.8.0 (2018-10-10)
++++++++++++++++++++++

**Improvements**

- All ``jupytext`` related metadata goes to a ``jupytext`` section (#91). Please make sure your collaborators use the same version of Jupytext, as the new version can read previous metadata, but not the opposite.
- Notebooks extensions can be prefixed with any prefix of at most three chars (#87).
- Export of the same notebook to multiple formats is now supported. To export to all python formats, plus ``.ipynb`` and ``.md``, use ``"jupytext": {"formats": "ipynb,pct.py:percent,lgt.py:light,spx.py:sphinx,md"},``.
- README includes a short section on how to extend ``light`` and ``percent`` formats to more languages (#61).
- Jupytext's contents manager accepts the ``auto`` extension in ``default_jupytext_formats`` (#93).
- All Jupyter magics are escaped in ``light`` scripts and R markdown documents. Escape magics in other formats with a ``comment_magics`` metadata (true or false), or with the contents manager ``comment_magics`` global flag (#94).

**BugFixes**

- Trusting notebooks made functional again.
- Command line ``jupytext`` returns a meaningful error when no argument is given.
- Fixed global pairing configuration (#95).

0.7.2 (2018-10-01)
++++++++++++++++++++++

**Improvements**

- ``light`` and ``percent`` formats made available for scheme and cpp notebooks. Adding more formats is straightforward - just add a new entry to _SCRIPT_EXTENSIONS in languages.py, a sample notebook and a mirror test (#61)
- Format name is automatically appended to extension in ``jupytext_formats`` when notebook is loaded/saved.

**BugFixes**

- Notebooks extensions can only be prefixed with ``.nb`` (#87)


0.7.1 (2018-09-24)
++++++++++++++++++++++

**BugFixes**

- Markdown cells header in sphinx gallery format may have a space between first # and following.

0.7.0 (2018-09-23)
++++++++++++++++++++++

**Improvements**

- Header for cells in ``percent`` format is more robust: use ``[markdown]`` and ``[raw]`` to identify cell types. Cell type comes after the cell title. (#59)

0.7.0-rc0 (2018-09-22)
++++++++++++++++++++++

**Improvements**

- Jupytext can read and write notebooks as Hydrogen/VScode/Spyder/PyCharm compatible scripts (cells starting with ``# %%``) (#59)
- Jupytext can read and write notebooks as Sphinx-gallery compatible scripts (#80)
- Metadata are supported for all cell types in light python and percent formats (#66). Due to this, light python format version is now 1.3. Light python notebooks in versions 1.1 and 1.2 are still readable.
- Command line ``jupytext`` has a ``from`` argument, and now accepts notebook from the standard input.

**BugFixes**

- Fix merging of input and output notebooks (#83)
- Removed extra new line on stdout in command line ``jupytext`` (#84)

0.6.5 (2018-09-13)
+++++++++++++++++++

**Improvements**

- Code lines that start with a quotation mark in Jupyter are commented in the corresponding Python and Julia scripts (#73)
- Update pypy, add flake8 tests on Travis CI (#74)

**BugFixes**

- Import notebook.transutils before notebook.services.contents.filemanager (#75)

0.6.4 (2018-09-12)
+++++++++++++++++++

**Improvements**

- Jupytext will not load paired notebook when text representation is out of date (#63)
- Package tested against Python 3.7 (#68)

**BugFixes**

- Allow unicode characters in notebook path (#70)
- Read README.md as unicode in ``setup.py`` (#71)

0.6.3 (2018-09-07)
+++++++++++++++++++

**Improvements**

- Lighter cell markers for Python and Julia scripts (#57). Corresponding file format version at 1.2. Scripts in previous version 1.1 can still be opened.
- New screenshots for the README.

**BugFixes**

- Command line conversion tool ``jupytext`` fixed on Python 2.7 (#46)

0.6.2 (2018-09-05)
+++++++++++++++++++

**Improvements**

- Initial support for Jupyter notebooks as Julia scripts (#56)
- Command line conversion tool ``jupytext`` has explicit ``to`` and ``output`` options (#46)
- Round trip test with ``jupytext --test`` improved (#54)
- Improved README (#51)


**BugFixes**

- testfixtures now in requirements (#55)
- Empty code cells are now preserved (#53)

0.6.1 (2018-08-31)
+++++++++++++++++++

**Improvements**

- Package and conversion script renamed from ``nbrmd`` to ``jupytext``.

0.6.0 (2018-08-31)
+++++++++++++++++++

**Improvements**

- Cell parsing and exporting done in two specialized classes. This is way easier to read. Pylint score at 9.9 !
- Python file format updated to 1.1: default end of cell for python scripts is one blank space. Two blank spaces are allowed as well. Now you can reformat code in Python IDE without breaking notebook cells (#38).
- Added support for plain markdown files (#40, #44).
- Demonstration notebooks more user friendly (#45).
- Command line tool simpler to use (#46).
- Start code patterns present in Jupyter cells are escaped.
- Default ``nbrmd_format`` is empty (mwouts/nbsrc/#5): no Jupyter notebook is created on disk when the user opens a Python or R file and saves it from Jupyter, unless the users asks for it by setting ``nbrmd_format``.

**BugFixes**

- Fixed message in the ``nbsrc`` script (#43)
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
- Explicit file format version, set at 1.0, to avoid overriding ipynb files by accident (#36)


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
- Extensions can be prefixed, like ``.nb.py``, (mwouts/nbsrc#5)
- When a file with an extension not associated to 'ipynb' is opened and saved, no 'ipynb' file is created (mwouts/nbsrc#5)
- Extensions can now be a sequence of groups. For instance, ``nbrmd_formats="ipynb,nb.py;script.ipynb,py"`` will create an ``ipynb`` file when a ``nb.py`` is opened (and conversely), and a ``script.ipynb`` file when a ``py`` file is opened (mwouts/nbsrc#5)
- ``nbsrc`` script was moved to the ``nbrmd`` package. The ``nbsrc`` package now only contains the documentation (mwouts/nbsrc#3)


0.4.6 (2018-07-26)
+++++++++++++++++++

- Ping pypi - previous version still not available


0.4.5 (2018-07-26)
+++++++++++++++++++

**BugFixes**

- Removed dependency of ``setup.py`` on ``yaml``

0.4.4 (2018-07-26)
+++++++++++++++++++

**BugFixes**

- Package republished with ``python setup.py sdist bdist_wheel`` to fix missing dependencies

0.4.3 (2018-07-26)
+++++++++++++++++++

**Improvements**

- Multiline comments now supported #25
- Readme refactored, notebook demos available on binder #23

**BugFixes**

- ContentsManager can be imported even if ``notebook.transutils`` is not available, for compatibility with older python distributions.
- Fixed missing cell metadata #27
- Documentation tells how to avoid creating ``.ipynb`` files #16

0.4.2 (2018-07-23)
+++++++++++++++++++

**Improvements**

- Added test for R notebooks
- Added pylint badge, imports now in correct order
- New ``active`` cell metadata that allows cell activation only for desired extensions (currently available for Rmd and ipynb extensions only)

0.4.1 (2018-07-20)
+++++++++++++++++++

**BugFixes**

- Indented python code will not start a new cell #20
- Fixed parsing of Rmd cell metadata #21

0.4.0 (2018-07-18)
+++++++++++++++++++

**Improvements**

- ``.py`` format for notebooks is lighter and pep8 compliant

**BugFixes**

- Default nbrmd config not added to notebooks (#17)
- ``nbrmd_formats`` becomes a configurable traits (#16)
- Removed ``nbrmd_sourceonly_format`` metadata. Source notebook is current notebook when not ``.ipynb``, otherwise the first notebook format in ``nbrmd_formats`` (not ``.ipynb``) that is found on disk

0.3.0 (2018-07-17)
+++++++++++++++++++

**Improvements**

- Introducing support for notebooks as python ``.py`` or R scripts ``.R``

0.2.6 (2018-07-13)
+++++++++++++++++++

**Improvements**

- Introduced ``nbrmd_sourceonly_format`` metadata
- Inputs are loaded from ``.Rmd`` file when a matching ``.ipynb`` file is opened.

**BugFixes**

- Trusted notebooks remain trusted (#12)

0.2.5 (2018-07-11)
+++++++++++++++++++

**Improvements**

- Outputs of existing ``.ipynb`` versions are combined with matching inputs of R markdown version, as suggested by @grst (#12)

**BugFixes**

- Support for unicode text in python 2.7 (#11)


0.2.4 (2018-07-05)
+++++++++++++++++++

**Improvements**

- nbrmd will always open notebooks, even if header of code cells are not terminated. Merge conflicts can thus be solved in Jupyter directly.
- New metadata 'main language' that preserves the notebook language.

**BugFixes**

- dependencies included in ``setup.py``
- pre_save_hook work with non-empty ``notebook_dir`` (#9)

0.2.3 (2018-06-28)
+++++++++++++++++++

**Improvements**

- Screenshots in README

**BugFixes**

- RMarkdown exporter for nbconvert fixed on non-recent python
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
- New pre-save hook ``update_selected_formats`` that saves to formats in metadata 'nbrmd_formats'
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

- Initial version with the nbrmd`` converter and Jupyter ``pre_save_hook``
