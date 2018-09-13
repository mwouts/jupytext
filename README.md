# Jupyter notebooks as Markdown documents, Julia, Python or R scripts

[![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Pypi](https://img.shields.io/pypi/l/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Build Status](https://travis-ci.com/mwouts/jupytext.svg?branch=master)](https://travis-ci.com/mwouts/jupytext)
[![codecov.io](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=master)](https://codecov.io/github/mwouts/jupytext?branch=master)
![pylint Score](https://mperlet.github.io/pybadge/badges/9.9.svg)
[![pyversions](https://img.shields.io/pypi/pyversions/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo)

You've always wanted to
* edit Jupyter notebooks as e.g. plain Python scripts in your favorite editor?
* do version control of Jupyter notebooks with clear and meaningful diffs?
* *collaborate* on Jupyter notebooks using standard (text oriented) merge tools?

Jupytext can convert notebooks to and from
- Julia, Python and R scripts (extensions `.jl`, `.py` and `.R`),
- Markdown documents (extension `.md`),
- R Markdown documents (extension `.Rmd`).

Jupytext is available from within Jupyter. You can work as usual on your notebook in Jupyter, and save and read it in the formats you choose. The text representations can be edited outside of Jupyter (see our [demo](#code-refactoring) below). When the notebook is refreshed in Jupyter, input cells are loaded from the script or Markdown document. Kernel variables are preserved. Outputs are not stored in such text documents, and are therefore lost when the notebook is refreshed. To avoid this, we recommend to [pair](#paired-notebooks) the text notebook with a traditional `.ipynb` notebook (both files are saved and loaded together).

| Format       | Extension          | Text editor friendly | Git friendly | Preserve outputs |
| ------------ | ------------------ | ----------- | ------------ | ---------------- |
| Jupyter notebook | `.ipynb`       |             |              | ✔                |
| Script or Markdown  | `.jl`/`.py`/`.R`/`.md`/`.Rmd` | ✔  | ✔            |                  |
| [Paired notebook](#paired-notebooks)  | (`.jl`/`.py`/`.R`/`.md`/`.Rmd`) + `.ipynb` | ✔ | ✔ | ✔ |


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
- We want the notebook to be saved as both a `.ipynb` and a `.py` file: we add a `"jupytext_formats": "ipynb,py",` entry to the notebook metadata.
- The Python script can be opened with PyCharm:
  - Navigating in the code and documentation is easier than in Jupyter.
  - The console is convenient for quick tests. We don't need to create cells for this.
  - We find out that the columns of the data frame were not in the correct order. We update the corresponding cell, and get the correct plot.
- The Jupyter notebook is refreshed in the browser. Modified inputs are loaded from the Python script. Outputs and variables are preserved. We finally rerun the code and get the correct plot.

![](https://gist.githubusercontent.com/mwouts/13de42d8bb514e4acf6481c580feffd0/raw/b8dd28f44678f8c91f262da2381276fc4d03b00a/JupyterPyCharm.gif)

## Installation

Install Jupytext with
```bash
pip install jupytext --upgrade
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

## Paired notebooks

The idea of paired notebooks is to store an `.ipynb` file alongside other formats. This lets us get the best of both worlds: an easily sharable notebook that stores the outputs, and one or more text-only files that can for instance be put under version control.

You can edit text-only files outside of Jupyter (first deactivate Jupyter's autosave by running `%autosave 0` in a cell), and then get the updated version in Jupyter by refreshing your browser.

When loading or refreshing an `.ipynb` file, the input cells of the notebook are read from the first non-`.ipynb` file among the associated formats.

When loading or refreshing a non-`.ipynb` file, the outputs are read from the `.ipynb` file (if `ipynb` is listed in the formats).

To enable paired notebooks, one option is to set the output formats by adding a `jupytext_formats` entry to the notebook metadata with *Edit/Edit Notebook Metadata* in Jupyter's menu:
```
{
  "jupytext_formats": "ipynb,py",
  "kernelspec": {
    (...)
  },
  "language_info": {
    (...)
  }
}
```
Accepted formats are: `ipynb`, `md`, `Rmd`, `py` and `R`.

Alternatively, it is also possible to set a default format pairing. Say you want to always associate `.ipynb` notebooks with an `.md` file  (and reciprocally). This is simply done by adding the following to your Jupyter configuration file:
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
c.ContentsManager.default_jupytext_formats = "ipynb,md"
```
(and similarly for the other formats).

## Command line conversion

The package provides a `jupytext` script for command line conversion between the various notebook extensions:

```bash
jupytext --to python notebook.ipynb             # create a notebook.py file
jupytext --to markdown notebook.ipynb           # create a notebook.md file
jupytext --output script.py notebook.ipynb      # create a script.py file

jupytext --to notebook notebook.py              # overwrite notebook.ipynb (remove outputs)
jupytext --to notebook --update notebook.py     # update notebook.ipynb (preserve outputs)
jupytext --to ipynb notebook1.md notebook2.py   # overwrite notebook1.ipynb and notebook2.ipynb

jupytext --to md --test notebook.ipynb          # Test round trip conversion

jupytext --to md --output - notebook.ipynb      # display the markdown version on screen
```

## Round-trip conversion

Round-trip conversion is safe! A few hundred tests help guarantee this.
- Script to Jupyter notebook, to script again is identity. If you
associate a Jupyter kernel with your notebook, that information will go to
a yaml header at the top of your script.
- Markdown to Jupyter notebook, to Markdown again is identity.
- Jupyter to script, then back to Jupyter again preserves source and metadata.
- Jupyter to Markdown, and Jupyter again preserves source and metadata (cell metadata available only for R Markdown). Note that Markdown cells with two consecutive blank lines will be split into multiple cells (as the two blank line pattern is used to separate cells).

## Format specifications

### Markdown and R markdown

Our implementation for Jupyter notebooks as Markdown or R Markdown documents is straightforward:
- A YAML header contains the notebook metadata (Jupyter kernel, etc)
- Markdown cells are inserted verbatim, and separated with two blank lines
- Code and raw cells start with triple backticks collated with cell language, and end with triple backticks. Cell metadata are available in the [R Markdown format](https://rmarkdown.rstudio.com/authoring_quick_tour.html).

### R scripts

Implement these [specifications](https://rmarkdown.rstudio.com/articles_report_from_r_script.html):
- Jupyter metadata in YAML format, in a `#' `-escaped header
- Markdown cells are commented with `#' `
- Code cells are exported verbatim. Cell metadata are signalled with `#+`. Cells end with a blank line, an explicit start of cell marker, or a Markdown comment.

### Python and Julia scripts

We wanted to represent Jupyter notebooks with the least explicit markers possible. The rationale for that is to allow **arbitrary** python files to open as Jupyter notebooks, even files which were never prepared to become a notebook. Precisely:
- Jupyter metadata go to an escaped YAML header
- Markdown cells are commented with `# `, and separated with a blank line
- Code cells are exported verbatim (except for Jupyter magics, which are escaped), and separated with blank lines. Code cells are reconstructed from consistent python paragraphs (no function, class or multiline comment will be broken). A start-of-cell delimiter `# +` is used for cells that contain blank lines (outside of functions, classes, etc). `# + {}` is used for cells that have explicit metadata (inside the curly bracket, in JSON format). The end of cell delimiter is `# -`, and is omitted when followed by another explicit start of cell marker.

## Will my notebook really run in an IDE?

Well, that's what we expect. There's however a big difference in the python environments between Python IDEs and Jupyter: in the IDE code is executed with  `python` and not in a Jupyter kernel. For this reason, `jupytext` escapes Jupyter magics found in your notebook. Comment a magic with `#noescape` on the same line to avoid escaping. User defined magics can be escaped with `#escape` (magics are not escaped in the plain Markdown representation).

Also, you may want some cells to be active only in the Python, or R Markdown representation. For this, use the `active` cell metadata. Set `"active": "ipynb"` if you want that cell to be active only in the Jupyter notebook. And `"active": "py"` if you want it to be active only in the Python script. And `"active": "ipynb,py"` if you want it to be active in both, but not in the R Markdown representation...

## I like this, how can I contribute?

Your feedback is precious to us: please let us know how we can improve `jupytext`. With enough feedback we will be able to transition from the current beta phase to a stable phase. Thanks for staring the project on GitHub. Sharing it is also very helpful! By the way: stay tuned for announcements and demos on [medium](https://medium.com/@marc.wouts) and [twitter](https://twitter.com/marcwouts)!


## Roadmap

Planned developments are:
- Refactor code to allow easier addition of new formats, and document the corresponding procedure [#61](https://github.com/mwouts/jupytext/issues/61).
- Implement a language agnostic format compatible with Atom/Hydrogen and VScode/Jupyter [#59](https://github.com/mwouts/jupytext/issues/59).
- Cell metadata for markdown cells (currently not covered) [#66](https://github.com/mwouts/jupytext/issues/66).
