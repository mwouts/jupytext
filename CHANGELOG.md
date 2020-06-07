1.5.0 (2020-06-07)
------------------

**Added**
- Jupytext can use a local or global [configuration file](https://github.com/mwouts/jupytext/blob/master/docs/config.md) (#508)
- Jupytext can pair notebooks in trees. Use e.g. `notebooks///ipynb,scripts///py:percent` if you want to replicate the tree of notebooks under `notebooks` in a folder named `scripts` (#424)
- The extension for Jupyter Notebook has a _New Text Notebook_ menu that creates text-only notebooks (#443)
- Groovy and Java are now supported, thanks to Przemek Wesołek (#500)
- The Coconut language is also supported, thanks to Thurston Sexton (#532)
- Resource files with `.resource` extension from the Robot Framework are supported, thanks to Hiski Valli (#535)
- Jupytext is tested in `pip` and `conda` environments, on Linux, Mac OS and Windows, using Github actions (#487)
- Jupytext uses pre-commit checks and automatic reformatting with `pre-commit`, `black` and `flake8` (#483)
- Documentation improvements:
  - Mention that the YAML header can be created with either `--set-kernel`, `--set-formats`, or both (#485)
  - Mention that one should use double quotes, not single quotes, around `jupytext --check` commands like `"pytest {}"` on Windows (#475)
  - Improved error message when a file is in a version that can't be read by Jupytext (#531)

**Fixed**
- Skip the `jupytext --execute` tests when the warning _Timeout waiting for IOPub output_ occurs, which is the case intermittently on Windows (#489)
- Fixed wrong paired paths when syncing with the --pre-commit flag (#506)


1.4.2 (2020-04-05)
------------------

**Added**
- Added an example with custom notebook metadata (#469)
- Added an example with custom cell tags (#478)

**Changed**
- The outputs from the `.ipynb` file are matched with the input cells from the text file with less strict rules. In this version, a search and replace on the text file will not remove the outputs any more (#464).
- Update parsing of myst notebooks to new (markdown-it based) parser (please upgrade to `myst-parser` to version `~0.8`) (#473)
- Use `os.path.samefile` when searching for the kernel that corresponds to the current environment (`--set-kernel -`)

**Fixed**
- Fixed the CLI example for not commenting out magic commands: `--opt comment_magics=false`. In addition, most of the `jupytext` commands in `using-cli.md` are now tested! (#465)
- `jupytext.read` and `jupytext.write` now give more meaningful errors when the format information is incorrect (#462)
- Multiline comments starting or ending with quadruple quotes should not cause issues anymore (#460)
- Fixed active cells in the py:percent format (#477)

1.4.1 (2020-03-19)
------------------

**Added**
- Script of script (SoS) notebooks are now supported. Thanks to Thomas Pernet-coudrier for contributing the sample notebook (#453).
- New MyST Markdown format (`md:myst`), developed by the [ExecutableBookProject](https://github.com/ExecutableBookProject) team. Read more about the MyST Markdown format in the [documentation](https://jupytext.readthedocs.io/en/latest/formats.html#myst-markdown). And many thanks to Chris Sewell for contributing the actual implementation! (#447 #456 #458)

**Fixed**
- When using `jupytext --pipe cmd`, the output of `cmd` should not appear in the terminal (#432)


1.4.0 (2020-03-09)
------------------

**Changed**
- The new jupyterlab extension (in version 1.2.0) is compatible with JupyterLab 2.0. Many thanks to Jean Helie! (#449)
- It is not compatible with JupyterLab 1.x anymore. If you wish, you can install manually the previous version of the extension with `jupyter labextension install jupyterlab-jupytext@1.1.1`.

**Fixed**
- Display the output/errors of command executed with `jupytext --pipe` or `jupytext --check` (#432)

1.3.5 (2020-03-08)
------------------

**Fixed**
- Removed leading slash in notebook paths (#444)
- Fixed `jupytext --set-formats` when using formats with prefix and/or suffix (#450)


1.3.4 (2020-02-18)
------------------

**Added**
- C# and F# Jupyter notebooks are now supported (#427, #429)

**Fixed**
- `jupytext --to script *.ipynb` now computes the script extension for each notebook (#428)
- Fix shebang handling for languages with non-# comments, by Jonas Bushart (#434)
- Indented bash commands are now commented out (#437)
- The main formats are documented in `jupytext --help` (#426, #433)


1.3.3 (2020-01-27)
------------------

**Added**
- Jupytext has a logo! Many thanks to Kyle Kelley for contributing the actual logo (#423), and to Chris Holdgraf for suggesting this (#260).
- Nested metadata filtering is now supported! You can use this to rid of `jupytext_version` if you wish (#416).

**Fixed**
- Code cells in the Markdown format can contain triple backticks inside multiline strings (#419).
- Changes in the YAML header when running `jupytext --test` on text files are ignored (#414).

1.3.2 (2020-01-08)
------------------

**Fixed**
- The `--pre-commit` mode now ignores non-notebook files in the index (#338).
- `nbformat_minor` is taken from the notebook with outputs When inputs and outputs are merged.

1.3.1 (2019-12-26)
------------------

**Added**
- New `nomarker` format in the Jupyter Notebook and JupyterLab extensions (#397)

**Changed**
- The `normarker` format replaces the one previously named `bare`.

**Fixed**
- Multiline strings are now accepted in the YAML header (#404). Fix contributed by ZHUO Qiang (#405).
- Fixed the instructions on how to use multiline comments for all Markdown cells in the py:percent format, by ZHUO Qiang  (#403).
- Added `cd` to the list of magic commands.
- Do not read paired files when `--set-formats` is being used (fixes #399).

1.3.0 (2019-11-23)
------------------

See also [What's new in Jupytext 1.3?](https://gist.github.com/mwouts/724efe5e00654fc2145a4c916796e071)

**Added**

- Pairing a notebook to both `.md` and `.py` is now supported. Input cells are loaded from the most recent text representation (#290)
- Both the Jupyter Notebook and the Jupyter Lab extension for Jupytext were updated (#290)
- Raw cells are now encoded using HTML comments (`<!-- #raw -->` and `<!-- #endraw -->`) in Markdown files (#321)
- Markdown cells can be delimited with any of `<!-- #region -->`,  `<!-- #markdown -->` or `<!-- #md -->` (#344)
- Code blocks from Markdown files, when they don't have an explicit language, appear in Markdown cells in Jupyter (#321)
- Code blocks with an explicit language and a `.noeval` attribute are inactive in Jupyter (#347)
- Markdown and raw cells can be quoted with triple quotes in the `py:percent` format. And Markdown cells can start with just `# %% [md]` (#305)
- The light format uses `# + [markdown]` rather than the previous `cell_type` metadata to identify markdown cells with metadata (#356)
- Explicit Markdown cells in the light format `# + [markdown]` can use triple quotes (#356)
- IPython magic help commands like `float?` are classified as magics, and thus commented in Python scripts (#297)
- Cell metadata can be encoded as either `key=value` (the new default) or in JSON. An automatic option `cell_metadata_json` should help minimize the impact on existing files (#344)
- R Markdown hidden inputs, outputs, or cells are now mapped to the corresponding Jupyter Book tags by default (#337)
- The notebook metadata filter is automatically updated when extra keys are added to the YAML header (#376)
- The Jupyter Notebook extension for Jupytext is compatible with Jupyter Notebook 6.0 (#346)
- `jupytext notebook.py --to ipynb` updates the timestamp of `notebook.py` so that the paired notebook still works in Jupyter (#335, #254)
- `jupytext --check pytest notebook.ipynb` can be used to run test functions in a notebook (#286)
- `jupytext --check` and `jupytext --pipe` can run commands that only operate on files: when `{}` is found in the text of the command, `jupytext` saves the text representation of the notebook in a temp file, and replaces `{}` with the name of that file before executing the command. (#286)
- Documented how to sync notebooks in a pre-commit hook (#338)
- Added support for Rust/Evxcr, by Jonas Bushart (#351)
- Added support for [Robot Framework](https://robots-from-jupyter.github.io/), by Asko Soukka (#378)
- Added support for PowerShell (#349)

**Changed**

- Use `CHANGELOG.md` rather than `HISTORY.rst`

**Fixed**

- Commands like `cat = x` are not magic commands, so they are not commented any more (#339)
- Fixed an inconsistent round trip (code cell with `"cat"` being converted to a markdown cell) in the `py:light` format (#339)
- `jupytext --test textfile.ext` now really compares the text file to its round trip (rather than the corresponding notebook) (#339)
- Markdown cells that contain code are now preserved in a round trip through the Markdown and R Markdown formats (#361)
- Code cells with a `%%python3` cell magic are now preserved in a round trip through the Markdown format (#365)
- `jupytext --execute` runs the notebook in its folder (#382)
- Strings in the metadata of code cells are quoted in the Rmd representation. And we escape R code in chunk options with `#R_CODE#` (#383)

1.2.4 (2019-09-19)
------------------

**Added**

- The documentation includes a mention on how to set metadata filters at the command line (#330)
- Jupytext will not catch any error when the flag `--warn-only` is not set (#327)

**Fixed**

- Now the flag `--warn-only` catches every possible error (#263)
- `.md` and `.markdown` files are treated identically (#325)
- Fixed `--set-kernel` when using pipes (#326)
- Fixed utf-8 encoding on stdout on Python 2 (#331)


1.2.3 (2019-09-02)
------------------

**Fixed**

- Dependency on `setuptools` in `pandoc.py` made optional to fix the build of the conda package (#310, #323)


1.2.2 (2019-09-01)
------------------

**Added**

- Documentation includes a section on how to use Jupytext as a Python library (#317)
- Mention of the server extension in the documentation (#304)
- Text notebooks can be tested with `jupytext --execute notebook.md` (#303)
- The default value of `as_version` in `jupytext.read` is `nbformat.NO_CONVERT`, as for `nbformat.read`
- Jupytext tests are now included in sdist (#310)

**Fixed**

- Fixed the usability of the `fmt` argument in `jupytext.read` (#312)
- Fixed the download notebook error when `c.notebook_extensions` has a custom value (#318)
- String delimiters in commented text are now ignored (#307)


1.2.1 (2019-07-20)
------------------

**Added**

- Added documentation on how to use Jupytext with JupyterLab 0.35 (#299)
- and on using Jupytext with the pre-commit package manager (#292)
- The `read` and `write` functions are easier to use (#292)

**Fixed**

- Jupytext now ships the `jupyterlab-jupytext` extension in version 1.0.2. The version 1.0.1 erroneously introduces a `target_formats` metadata in the jupytext section, instead of `formats`, and works only after two clicks.


1.2.0 (2019-07-18)
------------------

**Added**

- New `--execute` option in Jupytext CLI (#231)
- The `--set-formats` option in Jupytext CLI also triggers `--sync`, allowing shorter commands.
- `jupytext`'s `read` and `write` functions can be used as drop-in replacements for `nbformat`'s ones (#262).
- `jupytext --sync` will now skip unpaired notebooks (#281).
- The JupyterLab extension was updated. It now works on on text files (#213) and has a new option to include
(or not) the metadata in the text representation of the notebook.
- Jupytext's contents manager class is derived dynamically from the default CM class for compatibility with
`jupyter_server` (#270)
- Removed dependency on `mock` and `testfixtures`, thanks to Jean-Sebastien Dieu (#279)
- Added support for `.markdown` extension (#288)

**Fixed**

- The `jupyterlab-jupytext` extension shipped with the python package is in version 1.0.1, and is compatible only
with JupyterLab >= 1.0. If you use an earlier version of JupyterLab, please install the version 0.19 of the extension
with `jupyter labextension install jupyterlab-jupytext@0.19` (#276, #278)
- Text files can be unpaired (#289)


1.1.7 (2019-06-23)
------------------

**Added**

- Added support for Scala notebook, by Tobias Frischholz (#253)
- Added a getting started notebook for jupytext (and Binder), by Chris Holdgraf (#257)
- The Markdown and R Markdown representations are now tested for all the languages
- The Jupytext notebook extension also works when the notebook is a text file (#213)


**Fixed**

- The Jupytext Menu in Jupyter Notebook is now compatible with `jupyter_nbextensions_configurator` (#178)
- Entries in the Jupytext menu are updated when the menu is hovered on (#248)
- Fixed link to `.md` files in the documentation (#255)


1.1.6 (2019-06-11)
------------------

**Added**

- Jupytext now supports Javascript and Typescript, thanks to Hatem Hosny (#250)
- Jupytext works with Python 3.8 as well

**Fixed**

- Fix global `auto` pairing (#249)


1.1.5 (2019-06-06)
------------------

**Fixed**

- Fixed implicit dependency on `jupyter_client` (#245)


1.1.4 (2019-06-05)
------------------

**Added**

- New argument `--set-kernel` in Jupytext command line (#230)
- Jupytext now accepts `--to script` or `--to auto` (#240)
- Jupytext now has a real Sphinx documentation on [readthedocs](https://jupytext.readthedocs.io/en/latest), thanks to Chris Holdgraf (#237)

**Fixed**

- Invalid notebooks may cause a warning, but not a fatal error (#234)
- Jupyter server extension leaves the contents manager unchanged if it is a sub-class of Jupytext's CM (#236)
- Fixed format inference when metadata is present but not format information (#239)
- Preserve executable and encoding information in scripts with metadata (#241)

1.1.3 (2019-05-22)
------------------

**Added**

- Support for IDL notebooks and .pro scripts (#232)


1.1.2 (2019-05-16)
------------------

**Added**

- Jupytext's content manager has a new `notebook_extensions` option (#224, #183)
- Cells can be made inactive in scripts with the `active-ipynb` cell tag (#226)

**Fixed**

- Directories ending in .jl (or .ipynb) are not notebooks (#228)
- Empty notebooks have no language (#227)


1.1.1 (2019-04-16)
------------------

**Added**

- Jupytext server extension leaves the contents manager unchanged when it is already a subclass of TextFileContentsManager (#218)
- The base class for TextFileContentsManager defaults to FileContentsManager when LargeFileManager is not available (#217)


1.1.0 (2019-04-14)
------------------

**Added**

- Markdown and R Markdown formats now support metadata (#66, #111, #188)
- The `light` format for Scripts can use custom cell markers, e.g. Vim or VScode/PyCharm folding markers (#199)
- Pandoc's Markdown format for Jupyter notebooks is available in Jupytext as `md:pandoc` (#208)

**Fixed**

- Jupytext's contents manager is now based on `LargeFileManager` to allow large file uploads (#210)
- YAML header parsed with yaml.safe_load rather than yaml.load (#215)
- IPython line magic can be split across lines (#209)
- `jupytext --to py` rather than `--to python` in the README (#216)


1.0.5 (2019-03-26)
------------------

**Fixed**

- Fix the error 'notebook file has changed on disk' when saving large notebooks (#207)


1.0.4 (2019-03-20)
------------------

**Added**

- Wildcard are now supported on Windows (#202)
- Trusted notebooks remain trusted when inputs cells are modified (#203)

**Fixed**

- Pre-commit mode adds the result of conversion to the commit (#200)


1.0.3 (2019-03-13)
------------------

**Added**

- Matlab and Octave notebooks and scripts are now supported (#197)

**Fixed**

- `notebook_metadata_filter = "all"` now works (#196)
- Default pairing in subfolders fixed in Jupyter Lab (#180)


1.0.2 (2019-02-27)
------------------

**Added**

- Rename notebooks in pairs in the tree view (#190)
- Associate `.scm` file extension with Scheme scripts (#192)
- Added support for Clojure, by bzinberg (#193)

**Fixed**

- Allow spaces between `?` or `!` and python or bash command (#189)


1.0.1 (2019-02-23)
------------------

**Fixed**

- Exclude tests in package deployment (#184)
- Jupytext's serverextension only runs selected init steps (#185)
- Added an additional test for magic arguments (#111)

1.0.0 (2019-02-19)
------------------

**Added**

- Jupytext now includes a Jupyter Notebook extension and a JupyterLab extension (#86).
- Jupytext command line has more arguments: `--paired-paths` to list the paths for the paired representations of the notebook, and `--sync` to synchronise the content of all paired paths based on the most recent file (#146). In addition, the `--from` argument is optional even when the notebook is read from stdin (#148).
- The pairing information, and more generally the notebook metadata can be edited with the CLL, see the `--set-formats` and the `--update-metadata` arguments (#141).
- Jupytext can `--pipe` the text representation of a notebook to external programs like `black` or `flake8` (#154, #142)
- The Python representation of notebooks containing PEP8 cells is now expected to be PEP8 compliant (#154).
- Format specification allow prefix and suffix for path and file name (#138, #142). Use `ipynb,prefix/suffix.py:percent` to pair the current notebook named `notebook.ipynb` to a script named `prefixnotebooksuffix.py`. Suffix and prefix can also be configured on the `ipynb` file, with the same syntax.
- Introducing a new `hydrogen` format for scripts, which derives from `percent`. In that format Jupyter magic commands are not commented (#59, #126, #132).
- Introducing a new `bare` format for scripts, which derives from `light`. That format has no cell marker. Use a notebook metadata filter `{"jupytext": {"notebook_metadata_filter":"-all"}}` if you want no YAML header (#152).
- The default format for R script is now `light`, as for the other languages.
- Added support for q/kdb+ notebooks (#161).
- Python scripts or Markdown documents that have no Jupyter metadata receive a metadata filter that ensures that metadata is not exported back to the text representation (#124).
- Metadata filters are represented as strings rather than dictionaries to make YAML headers shorter. Previous syntax from #105 is still supported. They were also renamed to `notebook_metadata_filter` and `cell_metadata_filter`.
- Markdown and RMarkdown formats have a new option `split_at_heading` to split Markdown cells at heading (#130)

**Fixed**

- Main language of scripts is inferred from script extension. Fixes a round trip conversion issue for Python notebooks with a Javascript cell.
- Non-Python scripts opened as notebooks in Jupyter are now correctly saved even when no matching kernel is found.
- Jupyter magic commands like `ls` are commented in the light and R markdown format (#149).
- Cell starting with `%%html`, `%%latex` are now commented out in the `light`, `percent` and `Rmd` formats (#179).

0.8.6 (2018-11-29)
------------------

**Added**

- The `language_info` section is not part of the default header any more. Language information is now taken from metadata `kernelspec.language`. (#105).
- When opening a paired notebook, the active file is now the file that was originally opened (#118). When saving a notebook, timestamps of all the alternative representations are tested to ensure that Jupyter's autosave does not override manual modifications.
- Jupyter magic commands are now commented per default in the `percent` format (#126, #132). Version for the `percent` format increases from '1.1' to '1.2'. Set an option `comment_magics` to `false` either per notebook, or globally on Jupytext's contents manager, or on `jupytext`'s command line, if you prefer not to comment Jupyter magics.
- Jupytext command line has a pre-commit mode (#121).


0.8.5 (2018-11-13)
------------------

**Added**

- `bash` scripts as notebooks (#127)
- R scripts with `.r` extension are supported (#122)
- Jupytext selects the first kernel that matches the language (#120)

0.8.4 (2018-10-29)
------------------

**Added**

- Notebook metadata is filtered - only the most common metadata are stored in the text representation (#105)
- New config option `freeze_metadata` on the content manager and on the command line interface (defaults to `False`). Use this option to avoid creating a YAML header or cell metadata if there was none initially. (#110)
- Language magic arguments are preserved in R Markdown, and also supported in `light` and `percent` scripts (#111, #114, #115)
- First markdown cell exported as a docstring when using the Sphinx format (#107)

0.8.3 (2018-10-19)
------------------

**Added**

- Frozen cells are supported in R Markdown, light and percent scripts (#101)
- Inactive cells extended to percent scripts (#108)
- `jupytext` gains a `--version` argument (#103)
- "ExecuteTime" cell metadata is not included in the text representation anymore (#106)


0.8.2 (2018-10-15)
------------------

**Added**

- Round trip conversion testing with `jupytext --test` was improved (#99)
- Round trip conversion tested on Jake Vanderplas' Python for Data Science Handbook.

**Fixed**

- Nested lists and dictionaries are now supported in notebook metadata
- Final empty code cell supported in Sphinx representation

0.8.1 (2018-10-11)
------------------

**Fixed**

- Sphinx format tested on `World population` notebook (#97)
- Mirror test made stronger on this occasion!
- Markdown representation recognize Julia, Scheme and C++ code cells as such
- Light representation of Scheme and C++ notebooks fixed (#61)

0.8.0 (2018-10-10)
------------------

**Added**

- All `jupytext` related metadata goes to a `jupytext` section (#91). Please make sure your collaborators use the same version of Jupytext, as the new version can read previous metadata, but not the opposite.
- Notebooks extensions can be prefixed with any prefix of at most three chars (#87).
- Export of the same notebook to multiple formats is now supported. To export to all python formats, plus `.ipynb` and `.md`, use `"jupytext": {"formats": "ipynb,pct.py:percent,lgt.py:light,spx.py:sphinx,md"},`.
- README includes a short section on how to extend `light` and `percent` formats to more languages (#61).
- Jupytext's contents manager accepts the `auto` extension in `default_jupytext_formats` (#93).
- All Jupyter magics are escaped in `light` scripts and R markdown documents. Escape magics in other formats with a `comment_magics` metadata (true or false), or with the contents manager `comment_magics` global flag (#94).

**Fixed**

- Trusting notebooks made functional again.
- Command line `jupytext` returns a meaningful error when no argument is given.
- Fixed global pairing configuration (#95).

0.7.2 (2018-10-01)
------------------

**Added**

- `light` and `percent` formats made available for scheme and cpp notebooks. Adding more formats is straightforward - just add a new entry to _SCRIPT_EXTENSIONS in languages.py, a sample notebook and a mirror test (#61)
- Format name is automatically appended to extension in `jupytext_formats` when notebook is loaded/saved.

**Fixed**

- Notebooks extensions can only be prefixed with `.nb` (#87)


0.7.1 (2018-09-24)
------------------

**Fixed**

- Markdown cells header in sphinx gallery format may have a space between first # and following.

0.7.0 (2018-09-23)
------------------

**Added**

- Header for cells in `percent` format is more robust: use `[markdown]` and `[raw]` to identify cell types. Cell type comes after the cell title. (#59)
- Jupytext can read and write notebooks as Hydrogen/VScode/Spyder/PyCharm compatible scripts (cells starting with `# %%`) (#59)
- Jupytext can read and write notebooks as Sphinx-gallery compatible scripts (#80)
- Metadata are supported for all cell types in light python and percent formats (#66). Due to this, light python format version is now 1.3. Light python notebooks in versions 1.1 and 1.2 are still readable.
- Command line `jupytext` has a `from` argument, and now accepts notebook from the standard input.

**Fixed**

- Fix merging of input and output notebooks (#83)
- Removed extra new line on stdout in command line `jupytext` (#84)

0.6.5 (2018-09-13)
------------------

**Added**

- Code lines that start with a quotation mark in Jupyter are commented in the corresponding Python and Julia scripts (#73)
- Update pypy, add flake8 tests on Travis CI (#74)

**Fixed**

- Import notebook.transutils before notebook.services.contents.filemanager (#75)

0.6.4 (2018-09-12)
------------------

**Added**

- Jupytext will not load paired notebook when text representation is out of date (#63)
- Package tested against Python 3.7 (#68)

**Fixed**

- Allow unicode characters in notebook path (#70)
- Read README.md as unicode in `setup.py` (#71)

0.6.3 (2018-09-07)
------------------

**Added**

- Lighter cell markers for Python and Julia scripts (#57). Corresponding file format version at 1.2. Scripts in previous version 1.1 can still be opened.
- New screenshots for the README.

**Fixed**

- Command line conversion tool `jupytext` fixed on Python 2.7 (#46)

0.6.2 (2018-09-05)
------------------

**Added**

- Initial support for Jupyter notebooks as Julia scripts (#56)
- Command line conversion tool `jupytext` has explicit `to` and `output` options (#46)
- Round trip test with `jupytext --test` improved (#54)
- Improved README (#51)


**Fixed**

- testfixtures now in requirements (#55)
- Empty code cells are now preserved (#53)

0.6.1 (2018-08-31)
------------------

**Added**

- Package and conversion script renamed from `nbrmd` to `jupytext`.

0.6.0 (2018-08-31)
------------------

**Added**

- Cell parsing and exporting done in two specialized classes. This is way easier to read. Pylint score at 9.9 !
- Python file format updated to 1.1: default end of cell for python scripts is one blank space. Two blank spaces are allowed as well. Now you can reformat code in Python IDE without breaking notebook cells (#38).
- Added support for plain markdown files (#40, #44).
- Demonstration notebooks more user friendly (#45).
- Command line tool simpler to use (#46).
- Start code patterns present in Jupyter cells are escaped.
- Default `nbrmd_format` is empty (mwouts/nbsrc/#5): no Jupyter notebook is created on disk when the user opens a Python or R file and saves it from Jupyter, unless the users asks for it by setting `nbrmd_format`.

**Fixed**

- Fixed message in the `nbsrc` script (#43)
- Technical metadata don't appear any more in scripts unless required (#42)
- Code cells that are fully commented remain code cells after round trip (#41)

0.5.4 (2018-08-24)
------------------

**Added**

- R to Rmd conversion compares well to knitr::spin (#26)
- Increased coverage to 98%


0.5.3 (2018-08-22)
------------------

**Fixed**

- Read and write version to the same metadata (#36)


0.5.2 (2018-08-22)
------------------

**Added**

- Classical jupyter extensions (autoreload, rmagics) are also escaped (#35)
- Explicit file format version, set at 1.0, to avoid overriding ipynb files by accident (#36)


0.5.1 (2018-08-21)
------------------

**Fixed**

- Source only notebooks can be trusted.

0.5.0 (2018-08-21)
------------------

**Added**

- Jupyter magic commands escaped when exported (#29)
- 'endofcell' option for explicit (optional) end-of-cell marker (#31)
- 'active' cell option now supported for .py and .R export (#30)
- Raw cells now preserved when exported to .py or .R (#32)
- Extensions can be prefixed, like `.nb.py`, (mwouts/nbsrc#5)
- When a file with an extension not associated to 'ipynb' is opened and saved, no 'ipynb' file is created (mwouts/nbsrc#5)
- Extensions can now be a sequence of groups. For instance, `nbrmd_formats="ipynb,nb.py;script.ipynb,py"` will create an `ipynb` file when a `nb.py` is opened (and conversely), and a `script.ipynb` file when a `py` file is opened (mwouts/nbsrc#5)
- `nbsrc` script was moved to the `nbrmd` package. The `nbsrc` package now only contains the documentation (mwouts/nbsrc#3)


0.4.6 (2018-07-26)
------------------

- Ping pypi - previous version still not available


0.4.5 (2018-07-26)
------------------

**Fixed**

- Removed dependency of `setup.py` on `yaml`

0.4.4 (2018-07-26)
-------------------

**Fixed**

- Package republished with `python setup.py sdist bdist_wheel` to fix missing dependencies

0.4.3 (2018-07-26)
------------------

**Added**

- Multiline comments now supported #25
- Readme refactored, notebook demos available on binder #23

**Fixed**

- ContentsManager can be imported even if `notebook.transutils` is not available, for compatibility with older python distributions.
- Fixed missing cell metadata #27
- Documentation tells how to avoid creating `.ipynb` files #16

0.4.2 (2018-07-23)
------------------

**Added**

- Added test for R notebooks
- Added pylint badge, imports now in correct order
- New `active` cell metadata that allows cell activation only for desired extensions (currently available for Rmd and ipynb extensions only)

0.4.1 (2018-07-20)
------------------

**Fixed**

- Indented python code will not start a new cell #20
- Fixed parsing of Rmd cell metadata #21

0.4.0 (2018-07-18)
------------------

**Added**

- `.py` format for notebooks is lighter and pep8 compliant

**Fixed**

- Default nbrmd config not added to notebooks (#17)
- `nbrmd_formats` becomes a configurable traits (#16)
- Removed `nbrmd_sourceonly_format` metadata. Source notebook is current notebook when not `.ipynb`, otherwise the first notebook format in `nbrmd_formats` (not `.ipynb`) that is found on disk

0.3.0 (2018-07-17)
------------------

**Added**

- Introducing support for notebooks as python `.py` or R scripts `.R`

0.2.6 (2018-07-13)
------------------

**Added**

- Introduced `nbrmd_sourceonly_format` metadata
- Inputs are loaded from `.Rmd` file when a matching `.ipynb` file is opened.

**Fixed**

- Trusted notebooks remain trusted (#12)

0.2.5 (2018-07-11)
------------------

**Added**

- Outputs of existing `.ipynb` versions are combined with matching inputs of R markdown version, as suggested by @grst (#12)

**Fixed**

- Support for unicode text in python 2.7 (#11)


0.2.4 (2018-07-05)
------------------

**Added**

- nbrmd will always open notebooks, even if header of code cells are not terminated. Merge conflicts can thus be solved in Jupyter directly.
- New metadata 'main language' that preserves the notebook language.

**Fixed**

- dependencies included in `setup.py`
- pre_save_hook work with non-empty `notebook_dir` (#9)

0.2.3 (2018-06-28)
------------------

**Added**

- Screenshots in README

**Fixed**

- RMarkdown exporter for nbconvert fixed on non-recent python
- Tests compatible with other revisions of nbformat >= 4.0
- Tests compatible with older pytest versions


0.2.2 (2018-06-28)
-------------------

**Added**

- RMarkdown exporter for nbconvert
- Parsing of R options robust to parenthesis
- Jupyter cell tags are preserved

**Fixed**

- requirements.txt now included in pypi packages

0.2.1 (2018-06-24)
------------------

**Added**

- Support for editing markdown files in Jupyter
- New pre-save hook `update_selected_formats` that saves to formats in metadata 'nbrmd_formats'
- Rmd cell options directly mapped to cell metadata

**Fixed**

- ContentManager compatible with Python 2.7

0.2.0 (2018-06-21)
------------------

**Added**

- The package provides a `RmdFileContentsManager` for direct edit of R markdown files in Jupyter
- Notebook metadata and cell options are preserved


0.1.1 (2018-06-19)
------------------

**Added**

- `nbrmd` prints the result of conversion to stdout, unless flag `-i` is provided
- Notebooks with R code chunks are supported

0.1 (2018-06-18)
----------------

- Initial version with the `nbrmd` converter and Jupyter `pre_save_hook`
