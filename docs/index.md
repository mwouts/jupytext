# Jupyter Notebooks as Markdown Documents, Julia, Python or R Scripts

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext can save Jupyter notebooks as Markdown files or as scripts in [many languages](languages.md).

With Jupytext, text files (`.md` and `.py`, and many others) become notebooks. You can open, edit and run them in Jupyter (right click, and _open with notebook_). You can also edit the text notebooks in any text editor, and reload them in Jupyter to get the latest changes there.

Jupytext also offers [paired notebooks](paired-notebooks.md), a mode in which notebooks are saved to both a classical `.ipynb` file and to an *editable* text file. In this mode you get all the convenience of the `.ipynb` file (e.g. outputs are persisted on disk), with all the advantages of the text notebooks (version control, easy editing, etc).

Jupytext implements many text [formats](formats.md) for Jupyter Notebooks. If your notebook is mostly made of code, you will probably prefer to save it as a script:
-  Use the [percent format](formats.md#the-percent-format), a format with explicit cell delimiters (`# %%`), supported by many IDE (Spyder, Hydrogen, VS Code, PyCharm and PTVS).
-  Or use the [light format](formats.md#the-light-format), if you prefer to see fewer cell markers.

If your notebook contains more text than code, if you are writing a documentation or a book, you probably want to save your notebook as a Markdown document.
- Use the [Jupytext Markdown format](formats.md#jupytext-markdown) if you wish to render your notebook as a `.md` file (without its outputs) on GitHub.
- Use the [Myst Markdown format](formats.md#myst-markdown), a markdown flavor that “implements the best parts of reStructuredText”, if you wish to render your notebooks using Sphinx or [Jupyter Book](https://jupyterbook.org).
- Finally, if you want to open your Jupyter Notebooks in RStudio, use the [R Markdown format](formats.md#r-markdown).

Jupytext is easy to [install](install.md). Run either of
```bash
pip install jupytext
```
or
```bash
conda install jupytext -c conda-forge
```
Restart your Jupyter server... and enjoy text notebooks (right-click, _open with notebook_) and paired notebooks (_pair notebook with..._ in the [Jupyter Commands](install.md#jupytext-commands-in-jupyterlab)!

If you're new to Jupytext, you may want to start with the [FAQ](faq.md) or the [Tutorials](tutorials.md).

## Contents

* [Installation](install.md)
* [Paired Notebooks](paired-notebooks.md)
* [Configuration](config.md)
* [Notebook Formats](formats.md)
* [Supported Languages](languages.md)
* [Using at the Command Line](using-cli.md)
* [Using as a pre-commit hook](using-pre-commit.md)
* [Using as a Python library](using-library.md)
* [Sample Use Cases](examples.md)
* [Frequently Asked Questions](faq.md)
* [Demos and Tutorials](tutorials.md)
