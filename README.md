# Jupyter notebooks as Markdown documents, Python or R scripts

[![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Pypi](https://img.shields.io/pypi/l/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Build Status](https://travis-ci.com/mwouts/jupytext.svg?branch=master)](https://travis-ci.com/mwouts/jupytext)
[![codecov.io](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=master)](https://codecov.io/github/mwouts/jupytext?branch=master)
![pylint Score](https://mperlet.github.io/pybadge/badges/9.9.svg)
[![pyversions](https://img.shields.io/pypi/pyversions/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo)

You've always wanted to 
* edit Jupyter notebooks in your favorite editor? 
* have Jupyter notebooks under version control? 
* *collaborate* on Jupyter notebooks using standard (text-only) merge tools?

## Format comparison

| Format       | Extension          | text editor | git friendly | preserve output |
| ------------ | ------------------ | ----------- | ------------ | --------------- |
| jupyter notebook | `.ipynb`       |             |              | ✔               | 
| script/markdown  | `.py`/`.R`/`.md`/`.Rmd` | ✔  | ✔            |                 |
| [paired notebook](#paired-notebooks)  | (`.py`/`.R`/`.md`/`.Rmd`) + `.ipynb` | ✔ | ✔ | ✔ |

## Supported formats

The `jupytext` package allows you to open and edit, in Jupyter,
- Python and R scripts ( extensions `.py` and `.R`)
- Markdown documents (extension `.md`)
- R Markdown documents (extension `.Rmd`).

Obviously these documents can also be edited outside of Jupyter. You will find it useful to refactor your notebook as a mere python script in a real IDE. If you are working on a documentation and you prefer the Markdown format, you will be able to use both Jupyter and your specialized Markdown editor.

Reloading the updated document in Jupyter is just a matter of reloading the corresponding page in the browser. Refreshing preserves the python variables. Outputs are also preserved when you use the text notebooks *in pair* with classical notebooks.

## Try it!

- See how notebooks are represented as text in our [demo](https://github.com/mwouts/jupytext/tree/master/demo) folder.
- Open these text notebooks in Jupyter on [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo)! And run then like you would do for any classical notebook.
- You may also open arbitrary python scripts like `Matplotlib example.py` (run it).
- Feel free to explore the package files with Jupyter (open `README.md` at the project root).
- Check by yourself that outputs and variables are preserved, and inputs are updated, when a [paired notebook](#paired-notebooks) is modified outside of Jupyter (this is `Paired Jupyter notebook and python script.ipynb`).

## Installation

To open `.py`, `.R`, `.md` and `.Rmd` files as notebooks in Jupyter, use our `ContentsManager`. To do so:
- generate a Jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`
- edit the config and include the following:
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
```

Then, make sure you have the `jupytext` package up-to-date and restart jupyter, i.e. run
```bash
pip install jupytext --upgrade
jupyter notebook
```

## Screenshots

The animated GIF below demonstrates the same notebook with three different extensions
- Original `.ipynb` file, in JSON format (5.5MB). Not adapted to text editors, but great for use in Jupyter, and also a perfect support for sharing your work. GitHub has full support for displaying notebooks and their outputs.
- Paired python script (`.py`, 2.2KB). An excellent format for developing Jupyter notebooks with complex code: code is easily **refactored**. **Navigating** through **code** and **documentation** is easier than in Jupyter. Step by step execution and breakpoints are accessible. Notebooks as python scripts are, in our opinion, the best candidate for **versioning** and **collaborating** on Jupyter notebooks - for sure you already have lots of practice on collaborating on simple scripts with Git, right? And when you're done with developping, you just need to refresh the notebook in Jupyter, run it all, save and share!
- Paired markdown document (`.md`, 2.2KB). An excellent format for developing documentation with few code samples.

![](https://raw.githubusercontent.com/mwouts/jupytext/master/img/jupyter_python_markdown.gif)

## Round-trip conversion

Round-trip conversion is safe! A few hundred tests help guarantee this.
- Script to Jupyter notebook, to script again is identity. If you
associate a Jupyter kernel with your notebook, that information will go to
a yaml header at the top of your script.
- Markdown to Jupyter notebook, to Markdown again is identity. 
- Jupyter to script, then back to Jupyter again preserves source and metadata.
- Jupyter to Markdown, and Jupyter again preserves source and metadata (cell metadata available only for R Markdown). Note that Markdown cells with two consecutive blank lines will be split into multiple cells (as the two blank line pattern is used to separate cells).

## Paired notebooks

The idea of paired notebooks is to store a `.ipynb` file alongside the text-only version. This lets us get the best of both worlds: a text-only document to put under version control, and an easily sharable notebook which stores the outputs. 

To enable paired notebooks, add a `jupytext_formats` entry to the notebook metadata with *Edit/Edit Notebook Metadata* in Jupyter's menu:
```
{
  "kernelspec": {
    "name": "python3",
    (...)
  },
  "language_info": {
    (...)
  },
  "jupytext_formats": "ipynb,py"
}
```

When you save the notebook, both the Jupyter notebook and the python scripts are updated. You can edit the text version
and then get the updated version in Jupyter by refreshing your browser (you may want to deactivate Jupyter's autosave with `%autosave 0`).

Accepted formats are: `ipynb`, `md`, `Rmd`, `py` and `R`. In case you want multiple text extensions, please note that the
order matters: the first non-`ipynb` extension
is the one used as the reference source for notebook inputs when you open the `ipynb` file.

Finally, it is also possible to pair every notebook with a text representation. If you add
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
c.ContentsManager.default_jupytext_formats = "ipynb,py" # or "ipynb,nb.py" # or "ipynb,md" # or "ipynb,Rmd"
```
to your Jupyter configuration file, then *every* Jupyter notebook that you save will have a companion `.py` (`.nb.py`, `.md`, or `.Rmd`) notebook. And every `.py` (`.nb.py`, `.md`, or `.Rmd`) notebook will have a companion `.ipynb` notebook.

## Command line conversion

The package provides a `jupytext` script for command line conversion between the various notebook extensions:

```bash
jupytext notebook.ipynb md --test          # Test round trip conversion
jupytext notebook.ipynb md                 # display the markdown version on screen

jupytext notebook.ipynb .md                # create a notebook.md file
jupytext notebook.ipynb .py                # create a notebook.py file
jupytext notebook.ipynb notebook.py        # create a notebook.py file

jupytext notebook.md .ipynb                # overwrite notebook.ipynb (remove outputs)
jupytext notebook.md .ipynb --update       # update notebook.ipynb (preserve outputs)

jupytext notebook1.md notebook2.py .ipynb  # overwrite notebook1.ipynb notebook2.ipynb
```

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

### Python scripts

We wanted to represent Jupyter notebooks with the least explicit markers possible. The rationale for that is to allow **arbitrary** python files to open as Jupyter notebooks, even files which were never prepared to become a notebook. Precisely:
- Jupyter metadata go to an escaped YAML header
- Markdown cells are commented with `# `, and separated with a blank line
- Code cells are exported verbatim (except for Jupyter magics, which are escaped), and separated with blank lines. Code cells are reconstructed from consistent python paragraphs (no function, class or multiline comment will be broken). A start-of-cell delimiter `# + {}` is used for cells that have explicit metadata (inside the curly bracket, in JSON format), and for cells that include blank lines (outside of functions, classes, etc). The end of cell delimiter is `# -`, and is omitted when followed by another explicit start of cell marker.

## Will my notebook really run in an IDE?

Well, that's what we expect. There's however a big difference between the python environments between Jupyter and Python IDEs, or RStudio: in the IDE code is executed with `python` rather than `ipython`. For this reason, `jupytext` escapes Jupyter magics found in your notebook. Comment a magic with `#noescape` on the same line to avoid escaping. User defined magics can be escaped with `#escape` (magics are not escaped in the plain Markdown representation).

Also, you may want some cells to be active only in the Python, or R Markdown representation. For this, use the `active` cell metadata. Set `"active": "ipynb"` if you want that cell to be active only in the Jupyter notebook. And `"active": "py"` if you want it to be active only in the Python script. And `"active": "ipynb,py"` if you want it to be active in both, but not in the R Markdown representation...

## I like this, how can I contribute?

Your feedback is precious to us: please let us know how we can improve `jupytext`. With enough feedback we will be able to transition from the current beta phase to a stable phase. Thanks for staring the project on GitHub. Sharing it is also very helpful! By the way: stay tuned for announcements and demos on [medium](https://medium.com/@marc.wouts) and [twitter](https://twitter.com/marcwouts)!
