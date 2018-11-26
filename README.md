# Jupyter notebooks as Markdown documents, Julia, Python or R scripts

[![Build Status](https://travis-ci.com/mwouts/jupytext.svg?branch=master)](https://travis-ci.com/mwouts/jupytext)
[![codecov.io](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=master)](https://codecov.io/github/mwouts/jupytext?branch=master)
[![Language grade: Python](https://img.shields.io/badge/lgtm-A+-brightgreen.svg)](https://lgtm.com/projects/g/mwouts/jupytext/context:python)

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningfull diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext can save Jupyter notebooks as
- Markdown and R Markdown documents,
- Julia, Python, R, Bash, Scheme and C++ scripts.

Jupytext is available as a command line tool and as a _contents manager_ for Jupyter. With the latter, Jupyter will save your notebook to your favorite format(s), from `.ipynb` to `.py`, `.R`, `.jl`, `.md`, `.Rmd`... The text representation can be edited outside of Jupyter. Simply refresh the notebook in Jupyter to get the latest input cells from the script or Markdown document. When refreshing, kernel variables are unaffected, and output cells are reloaded from the traditionnal `.ipynb` if present. You can also delete your `.ipynb` notebook entirely if you don't need to save output cells.

## Demo time

[![Introducing Jupytext](https://img.shields.io/badge/TDS-Introducing%20Jupytext-blue.svg)](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57)
[![PyParis](https://img.shields.io/badge/YouTube-PyParis-red.svg)](https://www.youtube.com/watch?v=y-VEZenk824)
[![Binder](https://img.shields.io/badge/Binder-Try%20it!-blue.svg)](https://mybinder.org/v2/gh/mwouts/jupytext_pyparis_2018/master?filepath=demo)

Looking for a demo?
- Read the original [announcement](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57) in Towards Data Science,
- Watch the [PyParis talk](https://github.com/mwouts/jupytext_pyparis_2018/blob/master/README.md),
- or, try Jupytext online with [binder](https://mybinder.org/v2/gh/mwouts/jupytext_pyparis_2018/master?filepath=demo)!

## Example usage

### Writing notebooks as plain text

You like to work with scripts? The good news is that plain scripts, which you can draft and test in your favorite IDE, open transparently as notebooks in Jupyter when using Jupytext. Run the notebook in Jupyter to generate the outputs, [associate](#paired-notebooks) an `.ipynb` representation, save and share your research as either a plain script or as a traditional Jupyter notebook with outputs.

### Collaborating on Jupyter Notebooks

With Jupytext, collaborating on Jupyter notebooks with Git becomes as easy as collaborating on text files.

The setup is straightforward:
- Open your favorite notebook in Jupyter notebook
- [Associate](#paired-notebooks) a `.py` representation (for instance) to that notebook
- Save the notebook, and put the Python script under Git control. Sharing the `.ipynb` file is possible, but not required.

Collaborating then works as follows:
- Your collaborator pulls your script. The script opens as a notebook in Jupyter, with no outputs.
- They run the notebook and save it. Outputs are regenerated, and a local `.ipynb` file is created.
- They change the notebook, and push their updated script. The diff is nothing else than a standard diff on a Python script.
- You pull the changed script, and refresh your browser. Input cells are updated. The outputs from cells that were changed are removed. Your variables are untouched, so you have the option to run only the modified cells to get the new outputs.

### Code refactoring

In the animation below we propose a quick demo of Jupytext. While the example remains simple, it shows how your favorite text editor or IDE can be used to edit your Jupyter notebooks. IDEs are more convenient than Jupyter for navigating through code, editing and executing cells or fractions of cells, and debugging.

- We start with a Jupyter notebook.
- The notebook includes a plot of the world population. The plot legend is not in order of decreasing population, we'll fix this.
- We want the notebook to be saved as both a `.ipynb` and a `.py` file: we add a `"jupytext": {"formats": "ipynb,py"},` entry to the notebook metadata.
- The Python script can be opened with PyCharm:
  - Navigating in the code and documentation is easier than in Jupyter.
  - The console is convenient for quick tests. We don't need to create cells for this.
  - We find out that the columns of the data frame were not in the correct order. We update the corresponding cell, and get the correct plot.
- The Jupyter notebook is refreshed in the browser. Modified inputs are loaded from the Python script. Outputs and variables are preserved. We finally rerun the code and get the correct plot.

![](https://gist.githubusercontent.com/mwouts/13de42d8bb514e4acf6481c580feffd0/raw/b8dd28f44678f8c91f262da2381276fc4d03b00a/JupyterPyCharm.gif)

## Installation

[![Conda Version](https://img.shields.io/conda/vn/conda-forge/jupytext.svg)](https://anaconda.org/conda-forge/jupytext)
[![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![pyversions](https://img.shields.io/pypi/pyversions/jupytext.svg)](https://pypi.python.org/pypi/jupytext)

Jupytext is available on pypi and on conda-forge. Run either of
```bash
pip install jupytext --upgrade
```
or
```bash
conda install -c conda-forge jupytext
```

Then, configure Jupyter to use Jupytext:
- generate a Jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`
- edit `.jupyter/jupyter_notebook_config.py` and append the following:
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
```
- and restart Jupyter, i.e. run
```bash
jupyter notebook
```

### <a name="paired-notebooks"></a> Per-notebook configuration

Configure the multiple export formats for your notebook by adding a `"jupytext": {"formats": "ipynb,py"},` entry to the notebook metadata with *Edit/Edit Notebook Metadata* in Jupyter's menu:
```
{
  "jupytext": {"formats": "ipynb,py"},
  "kernelspec": {
    (...)
  },
  "language_info": {
    (...)
  }
}
```
Accepted formats are composed of an extension, like `ipynb`, `md`, `Rmd`, `jl`, `py`, `R`, `sh`, `cpp`... and an optional format name among `light` (default for Julia, Python), `percent`, `sphinx`, `spin` (default for R) &mdash; see below for the [format specifications](#Format-specifications). Use `ipynb,py:percent` if you want to pair the `.ipynb` notebook with a `.py` script in the `percent` format. To have the script extension chosen according to the Jupyter kernel, use the `auto` extension.

Jupytext accepts a few additional options:
- `comment_magics`: By default, Jupyter magics are commented when notebooks are exported to any other format than markdown. If you prefer otherwise, use this boolean option, or is global counterpart (see below).
- `metadata_filter.notebook`: By default, Jupytext only exports the `kernelspec` and `jupytext` metadata to the text files. Set `"jupytext": {"metadata_filter": {"notebook": "-all"}}` if you want that the script has no notebook metadata at all. The value for `metadata_filter.notebook` is a comma separated list of additional/excluded (negated) entries, with `all` a keyword that allows to exclude all entries.
- `metadata_filter.cells`: By default, cell metadata `autoscroll`, `collapsed`, `scrolled`, `trusted` and `ExecuteTime` are not included in the text representation. Add or exclude more cell metadata with this option.

### Global configuration

Jupytext's contents manager also accepts global options. We start with the default format pairing. Say you want to always associate every `.ipynb` notebook with a `.md` file  (and reciprocally). This is simply done by adding the following to your Jupyter configuration file:
```python
# Always pair ipynb notebooks to md files
c.ContentsManager.default_jupytext_formats = "ipynb,md"
```
(and similarly for the other formats).

In case the [`percent`](#the-percent-format) format is your favorite, add the following to your `.jupyter/jupyter_notebook_config.py` file:
```python
# Use the percent format when saving as py
c.ContentsManager.preferred_jupytext_formats_save = "py:percent"
```
and then, Jupytext will understand `"jupytext": {"formats": "ipynb,py"},` as an instruction to create the paired Python script in the `percent` format.

If you want that the generated text files have no metadata, you may use the global metadata filters below. Please note that with this setting, the metadata is only preserved in the `.ipynb` file &mdash; be sure to open that file in Jupyter, and not the text file which will miss the pairing information.
```python
# Filter out all metadata in text representations
c.ContentsManager.default_notebook_metadata_filter = "-all"
c.ContentsManager.default_cell_metadata_filter = "-all"
```

Finally, if you use Jupytext as an interactive editor for scripts and markdown files, but you don't want Jupyter to add a YAML header to those, use:
```python
# Do not add metadata to existing scripts
c.ContentsManager.freeze_metadata = True
```


NB: All these global options (and more) are documented [here](https://github.com/mwouts/jupytext/blob/master/jupytext/contentsmanager.py).

## Command line conversion

The package provides a `jupytext` script for command line conversion between the various notebook extensions:

```bash
jupytext --to python notebook.ipynb             # create a notebook.py file
jupytext --to py:percent notebook.ipynb         # create a notebook.py file in the double percent format
jupytext --to py:percent --comment-magics false notebook.ipynb   # create a notebook.py file in the double percent format, and do not comment magic commands
jupytext --to markdown notebook.ipynb           # create a notebook.md file
jupytext --output script.py notebook.ipynb      # create a script.py file

jupytext --to notebook notebook.py              # overwrite notebook.ipynb (remove outputs)
jupytext --to notebook --update notebook.py     # update notebook.ipynb (preserve outputs)
jupytext --to ipynb notebook1.md notebook2.py   # overwrite notebook1.ipynb and notebook2.ipynb

jupytext --to md --test notebook.ipynb          # Test round trip conversion

jupytext --to md --output - notebook.ipynb      # display the markdown version on screen
jupytext --from ipynb --to py:percent           # read ipynb from stdin and write double percent script on stdout
```

## Reading notebooks in Python

Manipulate notebooks in a Python shell or script using `jupytext`'s main functions:

```python
# Read notebook from file, given format name (guess format when `format_name` is None)
readf(nb_file, format_name=None)

# Read notebook from text, given extension and format name
reads(text, ext, format_name=None, [...])

# Return the text representation for the notebook, given extension and format name
writes(notebook, ext, format_name=None, [...])

# Write notebook to file in desired format
writef(notebook, nb_file, format_name=None)
```

## Round-trip conversion

Representing Jupyter notebooks as scripts requires a solid round trip conversion. You don't want your notebooks (nor your scripts) to be modified because you are converting them to the other form. A few hundred tests ensure that round trip conversion is safe.

You can easily test that the round trip conversion preserves your Jupyter notebooks and scripts. Run for instance:
```bash
# Test the ipynb -> py:percent -> ipynb round trip conversion
jupytext --test notebook.ipynb --to py:percent

# Test the ipynb -> (py:percent + ipynb) -> ipynb (à la paired notebook) conversion
jupytext --test --update notebook.ipynb --to py:percent
```

Note that `jupytext --test` compares the resulting notebooks according to its expectations. If you wish to proceed to a strict comparison of the two notebooks, use `jupytext --test-strict`, and use the flag `-x` to report with more details on the first difference, if any.

Please note that
- When you associate a Jupyter kernel with your text notebook, that information goes to a YAML header at the top of your script or Markdown document. And Jupytext itself may create a `jupytext` entry in the notebook metadata. Have a look at the [`freeze_metadata` option](#cell-and-notebook-metadata-filtering) if you want to avoid this.
- Cell metadata are available in `light` and `percent` formats for all cell types. Sphinx Gallery scripts in `sphinx` format do not support cell metadata. R Markdown and R scripts in `spin` format support cell metadata for code cells only. Markdown documents do not support cell metadata.
- By default, a few cell metadata are not included in the text representation of the notebook. And only the most standard notebook metadata are exported. Learn more on this in this in the [metadata filtering](#Cell-and-notebook-metadata-filtering) section.
- Representing a Jupyter notebook as a Markdown or R Markdown document has the effect of splitting markdown cells with two consecutive blank lines into multiple cells (as the two blank line pattern is used to separate cells).

## Format specifications

### Markdown and R Markdown

Our implementation for Jupyter notebooks as [Markdown](https://daringfireball.net/projects/markdown/syntax) or [R Markdown](https://rmarkdown.rstudio.com/authoring_quick_tour.html) documents is straightforward:
- A YAML header contains the notebook metadata (Jupyter kernel, etc)
- Markdown cells are inserted verbatim, and separated with two blank lines
- Code and raw cells start with triple backticks collated with cell language, and end with triple backticks. Cell metadata are not available in the Markdown format. The [code cell options](https://yihui.name/knitr/options/) in the R Markdown format are mapped to the corresponding Jupyter cell metadata options, when available.

See how our `World population.ipynb` notebook in the [demo folder](https://github.com/mwouts/jupytext/tree/master/demo) is represented in [Markdown](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.md) or [R Markdown](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.Rmd).

### The `light` format for notebooks as scripts

The `light` format was created for this project. It is the default format for Python and Julia scripts. That format can read any script as a Jupyter notebook, even scripts which were never prepared to become a notebook. When a notebook is written as a script using this format, only a few cells markers are introduced—none if possible.

The `light` format has:
- A (commented) YAML header, that contains the notebook metadata.
- Markdown cells are commented, and separated with a blank line.
- Code cells are exported verbatim (except for Jupyter magics, which are commented), and separated with blank lines. Code cells are reconstructed from consistent Python paragraphs (no function, class or multiline comment will be broken).
- Cells that contain more than one Python paragraphs need an explicit start-of-cell delimiter `# +` (`// +` in C++, etc). Cells that have explicit metadata have a cell header `# + {JSON}` where the metadata is represented, in JSON format. The end of cell delimiter is `# -`, and is omitted when followed by another explicit start of cell marker.

The `light` format is currently available for Python, Julia, R, Bash, Scheme and C++. Open our sample notebook in the `light` format [here](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.lgt.py).

### The `percent` format

The `percent` format is a representation of Jupyter notebooks as scripts, in which cells are delimited with a commented double percent sign `# %%`. The format was introduced by Spyder five years ago, and is now supported by many editors, including
- [Spyder IDE](https://docs.spyder-ide.org/editor.html#defining-code-cells),
- [Hydrogen](https://atom.io/packages/hydrogen), a package for Atom,
- [VS Code](https://code.visualstudio.com/) with the [vscodeJupyter](https://marketplace.visualstudio.com/items?itemName=donjayamanne.jupyter) extension,
- [Python Tools for Visual Studio](https://github.com/Microsoft/PTVS),
- and [PyCharm Professional](https://www.jetbrains.com/pycharm/).

Our implementation of the `percent` format is compatible with the original specifications by Spyder. We extended the format to allow markdown cells and cell metadata. Cell headers have the following structure:
```python
# %% Optional text [cell type] {optional JSON metadata}
```
where cell type is either omitted (code cells), or `[markdown]` or  `[raw]`. The content of markdown and raw cells is commented out in the resulting script.

Percent scripts created by Jupytext have a header with an explicit format information. The format of scripts with no header is inferred automatically: scripts with at least one `# %%` cell are identified as `percent` scripts.

The `percent` format is currently available for Python, Julia, R, Bash, Scheme and C++. Open our sample notebook in the `percent` format [here](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.pct.py).

If the `percent` format is your favorite, add the following to your `.jupyter/jupyter_notebook_config.py` file:
```python
c.ContentsManager.preferred_jupytext_formats_save = "py:percent" # or "auto:percent"
```
Then, Jupytext's content manager will understand `"jupytext": {"formats": "ipynb,py"},` as an instruction to create the paired Python script in the `percent` format.

By default, Jupyter magics are commented in the `percent` representation. If you are using percent scripts in Hydrogen and you want to preserve Jupyter magics, then add a metadata `"jupytext": {"comment_magics": false},"` to your notebook, or add
```python
c.ContentsManager.comment_magics = False
```
to Jupyter's configuration file.

### Sphinx-gallery scripts

Another popular notebook-like format for Python script is the Sphinx-gallery [format](https://sphinx-gallery.readthedocs.io/en/latest/tutorials/plot_notebook.html). Scripts that contain at least two lines with more than twenty hash signs are classified as Sphinx-Gallery notebooks by Jupytext.

Comments in Sphinx-Gallery scripts are formatted using reStructuredText rather than markdown. They can be converted to markdown for a nicer display in Jupyter by adding a `c.ContentsManager.sphinx_convert_rst2md = True` line to your Jupyter configuration file. Please note that this is a non-reversible transformation—use this only with Binder. Revert to the default value `sphinx_convert_rst2md = False` when you edit Sphinx-Gallery files with Jupytext.

Turn a GitHub repository containing Sphinx-Gallery scripts into a live notebook repository with [Binder](https://mybinder.org/) and Jupytext by adding only two files to the repo:
- `binder/requirements.txt`, a list of the required packages (including `jupytext`)
- `.jupyter/jupyter_notebook_config.py` with the following contents:
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
c.ContentsManager.preferred_jupytext_formats_read = "py:sphinx"
c.ContentsManager.sphinx_convert_rst2md = True
```

Our sample notebook is also represented in `sphinx` format [here](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.spx.py).

### R knitr::spin scripts

The `spin` format implements these [specifications](https://rmarkdown.rstudio.com/articles_report_from_r_script.html):
- Jupyter metadata are in YAML format, in a `#' `-commented header.
- Markdown cells are commented with `#' `.
- Code cells are exported verbatim. Cell metadata are signalled with `#+`. Cells end with a blank line, an explicit start of cell marker, or a markdown cell.

## Jupyter Notebook or Jupyter Lab?

Jupytext works very well with the Jupyter Notebook editor, and we recommend that you get used to Jupytext within `jupyter notebook` first.

That being said, Jupytext also works well from Jupyter Lab. Please note that:
- Jupytext's installation is identical in both Jupyter Notebook and Jupyter Lab
- Jupyter Lab can open any [paired notebook](#paired-notebooks) with `.ipynb` extension. Paired notebooks work exactly as in Jupyter Notebook: input cells are taken from the text notebook, and outputs from the  `.ipynb` file. Both files are updated when the notebook is saved.
- Pairing notebooks is slightly less convenient in Jupyter Lab than in Jupyter Notebook as Jupyter Lab has no notebook metadata editor [yet](https://github.com/jupyterlab/jupyterlab/issues/1308). You will have to open the JSON representation of the notebook in an editor, find the notebook metadata and add the `"jupytext" : {"formats": "ipynb,py"},` entry manually.
- In Jupyter Lab, scripts or Markdown documents open as text by default. Open them as notebooks with the  _Open With -> Notebook_ context menu (available in Jupyter Lab 0.35 and above) as shown below:

![](https://gist.githubusercontent.com/mwouts/13de42d8bb514e4acf6481c580feffd0/raw/403b53ac5097446a15ea664579ba44cd1badcc57/ContextMenuLab.png)

## Will my notebook really run in an IDE?

Well, that's what we expect. There's however a big difference in the python environments between Python IDEs and Jupyter: in most IDEs the code is executed with  `python` and not in a Jupyter kernel. For this reason, `jupytext` comments Jupyter magics found in your notebook when exporting to all format but the plain Markdown one. Change this by adding a `#escape` or `#noescape` flag on the same line as the magic, or a `"comment_magics": true` or `false` entry in the notebook metadata, in the `"jupytext"` section. Or set your preference globally on the contents manager by adding this line to `.jupyter/jupyter_notebook_config.py`:
```python
c.ContentsManager.comment_magics = True # or False
```

Also, you may want some cells to be active only in the Python, or R Markdown representation. For this, use the `active` cell metadata. Set `"active": "ipynb"` if you want that cell to be active only in the Jupyter notebook. And `"active": "py"` if you want it to be active only in the Python script. And `"active": "ipynb,py"` if you want it to be active in both, but not in the R Markdown representation...

## Extending the `light` and `percent` formats to more languages

You want to extend the `light` and `percent` format to another language? Please let us know! In principle that is easy, and you will only have to:
- document the language extension and comment by adding one line to `_SCRIPT_EXTENSIONS` in `languages.py`.
- contribute a sample notebook in `tests\notebooks\ipynb_[language]`.
- add two tests in `test_mirror.py`: one for the `light` format, and another one for the `percent` format.
- Make sure that the tests pass, and that the text representations of your notebook, found in  `tests\notebooks\mirror\ipynb_to_script` and `tests\notebooks\mirror\ipynb_to_percent`, are valid scripts.

## Jupytext's releases and backward compatibility

Jupytext will continue to evolve as we collect more feedback, and discover more ways to represent notebooks as text files. When a new release of Jupytext comes out, we make our best to ensure that it will not break your notebooks. Format changes will not happen often, and we try hard not to introduce breaking changes.

Jupytext tests the version format for paired notebook only. If the format version of the text representation is not the current one, Jupytext will refuse to open the paired notebook. You may want to update Jupytext if the format version of the file is newer than the one available in the installed Jupytext. Otherwise, you will have to choose between deleting (or renaming) either the `.ipynb`, or its paired text representation. Keep the one that is up-to-date, re-open your notebook, and Jupytext will regenerate the other file.

We also recommend that people who use Jupytext to collaborate on notebooks use identical versions of Jupytext.

## I like this, how can I contribute?

Your feedback is precious to us: please let us know how we can improve `jupytext`. With enough feedback we will be able to transition from the current beta phase to a stable phase. Thanks for staring the project on GitHub. Sharing it is also very helpful! By the way: stay tuned for announcements and demos on [medium](https://medium.com/@marc.wouts) and [twitter](https://twitter.com/marcwouts)!
