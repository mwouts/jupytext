# Jupyter notebooks as markdown documents, Python or R scripts

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

| Format       | Extension          | text editor | git | preserve output |
| ------------ | ------------------ | ----------- | --- | --------------- |
| jupyter notebook | `.ipynb`       |             |     | ✔               | 
| script/markdown  | `.py`/`.R`/`.md`/`.Rmd` | ✔  | ✔   |       |
| [paired notebook](#paired-notebooks)  | (`.py`/`.R`/`.md`/`.Rmd`) + `.ipynb` | ✔  | ✔ | ✔       |

## Supported formats

The `jupytext` package allows to open and edit, in Jupyter,
- Python and R scripts ( extensions `.py` and `.R`)
- Markdown documents (extension `.md`)
- R Markdown documents (extension `.Rmd`).

Obviously these documents can also be edited outside of Jupyter. You will find useful to refactor your notebook as a mere python script in a real IDE. If you are working on a documentation and you prefer the markdown format, you will be able to use both Jupyter and your specialized markdown editor.

Reloading the updated document in Jupyter is just a matter of reloading the corresponding page in the browser. Refreshing preserves the python variables. Outputs are also preserved when you use the text notebooks *in pair* with classical notebooks.

## Try it!
Try our package on [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo)! Recommended experiments are
- Have a look at the sample text notebooks in the [demo](https://github.com/mwouts/jupytext/tree/master/demo) folder. See how notebook are represented as text
- Go to [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo) and open these notebooks
- You may also open arbitrary python scripts like `Matplotlib example.py` (run it)
- Feel free to explore the package files with Jupyter (open `README.md` at the project root)
- Check by yourself that outputs and variables are preserved, and inputs are updated, when the text notebook is modified outside of Jupyter (this is `Paired Jupyter notebook and python script.ipynb`).

## Installation

To open `.py`, `.R`, `.md` and `.Rmd` files as notebooks in Jupyter, use our `ContentsManager`. To do so:
- generate a jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`
- edit the config and include the below:
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
```

Then, make sure you have the `jupytext` package up-to-date, and re-start jupyter, i.e. run
```bash
pip install jupytext --upgrade
jupyter notebook
```

## Screenshots

![](https://raw.githubusercontent.com/mwouts/jupytext/master/img/jupyter_python_markdown.gif)

## Round-trip conversion

Round trip conversion is safe! A few hundred of tests help to guarantee this.
- Script to Jupyter notebook, to script again is identity. If you
associate a Jupyter kernel to your notebook, that information will go to
a yaml header at the top of your script.
- Markdown to Jupyter notebook, to markdown again is identity. 
- Jupyter to script, and Jupyter again preserves source and metadata.
- Jupyter to markdown, and Jupyter again preserves source and metadata (cell metadata available only for R markdown). Note that markdown cells with two consecutive blank lines will be splitted into multiple cells (as the two blank line pattern is used to separate cells).

## Paired notebooks

The idea of paired notebooks is to store a `.ipynb` file alongside the text-only version. Like this we get the best of two worlds: a text-only document to put under version control, and an easily sharable notebook which stores the outputs. 

To enable paired notebooks, add a `jupytext_formats` entry to the notebook metadata, in Jupyter, as follows:
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

Our implementation for Jupyter notebooks as Markdown or R markdown documents is unsurprizing:
- A YAML header contains the notebook metadata (Jupyter kernel, etc)
- Markdown cells are inserted verbatim, and separated with two blank lines
- Code and raw cells start with triple backticks collated with cell language, and end with triple backticks. Cell metadata are available in the [R markdown format](https://rmarkdown.rstudio.com/authoring_quick_tour.html).

### R scripts

Implement these [specifications](https://rmarkdown.rstudio.com/articles_report_from_r_script.html):
- Jupyter metadata in YAML format, in a `#' `-escaped header
- Markdown cells are commented with `#' `
- Code cells are exported verbatim. Cell metadata are signalled with `#+`. Cells end with a blank line, an explicit start of cell marker, or a markdown comment.

### Python scripts

We wanted to represent Jupyter notebooks with the least explicit markers possible. The rationale for that is to allow **arbitrary** python files to open as Jupyter notebooks, even files which were never prepared to become a notebook. Precisely:
- Jupyter metadata go to an escaped YAML header
- Markdown cells are commented with `# `, and separated with a blank line
- Code cells are exported verbatim (except for Jupyter magics, which are escaped), and separated with a blank lines. Code cells are reconstructed from consistent python paragraphs (no function, class or multiline comment will be broken). A start-of-cell delimiter `# + {}` is used for cells that have explicit metadata (inside the curly bracket, in JSON format), and for cells that include blank lines (outside of functions, classes, etc). The end of cell delimiter is `# -`, and is omitted when followed by another explicit start of cell marker.

## Usefull cell metadata

- Set `"active": "ipynb,py"` if you want that cell to be active only in the Jupyter notebook, and the Python script representation. Use `"active": "ipynb"` if you want that cell to be active only in Jupyter.
- Code cells that contain two consecutive blank lines use an explicit end-of-cell marker `"endofcell"` in the script representation.
- R markdown's cell options `echo` and `include` are mapped to the opposite of Jupyter cell metadata `hide_input` and `hide_output`.

## Jupyter magics

Jupyter magics are escaped in scripts and R markdown to allow code to be executed. Comment a magic with `#noescape` on the same line to avoid escaping. User defined magics can be escaped with `#escape`. Magics are not escaped in the plain markdown representation.
