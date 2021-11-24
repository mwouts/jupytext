# Jupyter Notebooks as Markdown Documents, Julia, Python or R Scripts

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext is a plugin for Jupyter that can save Jupyter notebooks as either
- Markdown files (or [MyST Markdown](formats.md#myst-markdown) files, or [R Markdown](formats.md#r-markdown) or [Quarto](formats.md#quarto) text notebooks)
- Scripts in [many languages](languages.md).

## Use cases

Common [use cases](examples.md) for Jupytext are:
- Doing version control on Jupyter Notebooks
- Editing, merging or refactoring notebooks in your favorite text editor
- Applying Q&A checks on notebooks.

## Install

You can install Jupytext with
- `pip install jupytext`
- or `conda install jupytext -c conda-forge`.

Then, restart your Jupyter server (for more installation details, see the [install section](install.md) in the documentation).

When Jupytext is installed, `.py` and `.md` files have a notebook icon. And you can really open and run these files as notebooks
<ul>
<details>
  <summary>With a click on the text file in Jupyter Notebook</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext-screenshots/master/JupytextDocumentation/TextNotebooks.png)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo)
(click on the image above to try this on [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo))
</details>
<details>
<summary>With a click on the text file in JupyterLab</summary>
To do that, you will need to change the default viewer for text files supported by Jupytext as follow:

[![](https://raw.githubusercontent.com/mwouts/jupytext-screenshots/master/JupytextDocumentation/TextNotebooksLab.gif)](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb)
(click on the image above to try this on [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb))
</details>
<details>
  <summary>With a right click and <i>open with notebook</i> in Jupyter Lab</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext-screenshots/master/JupytextDocumentation/ContextMenuLab.png)](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb)
(click on the image above to try this on [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb))
</details>
</ul>

## Paired notebooks

The most convenient way to use Jupytext is probably through [paired notebooks](paired-notebooks.md).

To pair a given `.ipynb` or text notebook to an additional notebook format, use either
<ul>
<details>
  <summary>the <i>"pair notebook with..."</i> commands in Jupyter Lab</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext/master/packages/labextension/jupytext_commands.png)](install.md#jupytext-commands-in-jupyterlab)
</details>

<details>
  <summary>the <i>"pair notebook with..."</i> menu entries in Jupyter Notebook</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext/master/jupytext/nbextension/jupytext_menu.png)](install.md#jupytext-menu-in-jupyter-notebook)
</details>

<details>
  <summary><code>jupytext</code> at the command line</summary>

with e.g.
```
jupytext --set-formats ipynb,py:percent notebook.ipynb
```
see the [documentation](config.md#per-notebook-configuration).
</details>

<details>
  <summary>or a local or global <code>jupytext.toml</code> configuration file.</summary>

with e.g. the following content:
```
formats = "ipynb,py:percent"
```
see the [documentation](config.md#configuring-paired-notebooks-globally).
</details>
</ul>

When you save a paired notebook in Jupyter, both the `.ipynb` file and the text version are updated on disk.

When a paired notebook is opened or _reloaded_ in Jupyter, the input cells are loaded from the text file, and combined with the output cells from the `.ipynb` file.

You can edit the text representation of the notebook in your favorite editor, and get the changes back in Jupyter by simply _reloading_ the notebook (Ctrl+R in Jupyter Notebook, <i>"reload notebook"</i> in Jupyter Lab). And the changes are propagated to the `.ipynb` file when you _save_ the notebook.

Alternatively, you can synchronise the two representations by running `jupytext --sync notebook.ipynb` at the command line.

## Which text format?

Jupytext implements many text [formats](formats.md) for Jupyter Notebooks. If your notebook is mostly made of code, you will probably prefer to save it as a script:
-  Use the [percent format](formats.md#the-percent-format), a format with explicit cell delimiters (`# %%`), supported by many IDE (Spyder, Hydrogen, VS Code, PyCharm and PTVS)
-  Or use the [light format](formats.md#the-light-format), if you prefer to see fewer cell markers.

If your notebook contains more text than code, if you are writing a documentation or a book, you probably want to save your notebook as a Markdown document
- Use the [Jupytext Markdown format](formats.md#jupytext-markdown) if you wish to render your notebook as a `.md` file (without its outputs) on GitHub
- Use the [MyST Markdown format](formats.md#myst-markdown), a markdown flavor that “implements the best parts of reStructuredText”, if you wish to render your notebooks using Sphinx or [Jupyter Book](https://jupyterbook.org).
- Use the [R Markdown format](formats.md#r-markdown) or the [Quarto format](formats.md#quarto) if you want to open your Jupyter Notebooks in RStudio.

## More resources?

If you're new to Jupytext, you may want to start with the [FAQ](faq.md) or with the [Tutorials](tutorials.md).

## Table of Contents

```{toctree}
:maxdepth: 1
install.md
paired-notebooks.md
config.md
formats.md
languages.md
using-cli.md
using-pre-commit.md
using-library.md
examples.md
faq.md
tutorials.md
contributing.md
developing.md
CHANGELOG.md
```
