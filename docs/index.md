# Jupyter Notebooks as Markdown Documents, Julia, Python or R Scripts

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext is a plugin for Jupyter that can save Jupyter notebooks as either
- Markdown files (or [MyST Markdown](formats.md#MyST-Markdown) files, or [R Markdown](formats.md#R-Markdown) or [Quarto](formats.md#Quarto) text notebooks)
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

[![](https://raw.githubusercontent.com/mwouts/jupytext-screenshots/master/JupytextDocumentation/TextNotebooks.png)](https://mybinder.org/v2/gh/mwouts/jupytext/main?filepath=demo)
(click on the image above to try this on [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?filepath=demo))
</details>
<details>
<summary>With a click on the text file in JupyterLab (<b>⭐New⭐</b>)</summary>
To do that, you will need to change the default viewer for text notebooks by copy-pasting the following settings (or the subset that matches your use case) in the `Document Manager` section:

```json
{
  "defaultViewers": {
    "markdown": "Jupytext Notebook",
    "myst": "Jupytext Notebook",
    "r-markdown": "Jupytext Notebook",
    "quarto": "Jupytext Notebook",
    "julia": "Jupytext Notebook",
    "python": "Jupytext Notebook",
    "r": "Jupytext Notebook"
  }
}
```

Here is a screencast of the steps to follow:

[![](https://raw.githubusercontent.com/mwouts/jupytext/main/docs/jupyterlab_default_viewer.gif)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb)
(click on the image above to try this on [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb))

Another possibility is to activate this with a [default_setting_overrides.json](https://github.com/mwouts/jupytext/blob/main/binder/labconfig/default_setting_overrides.json) file in the `.jupyter/labconfig` folder with e.g.
```
wget https://raw.githubusercontent.com/mwouts/jupytext/main/binder/labconfig/default_setting_overrides.json -P  ~/.jupyter/labconfig/
```

Note: to open links to `.md` files in notebooks with the Notebook editor, use `jupyterlab>=3.6.0`.
</details>
<details>
  <summary>With a right click and <i>open with notebook</i> in Jupyter Lab</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext-screenshots/master/JupytextDocumentation/ContextMenuLab.png)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb)
(click on the image above to try this on [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb))
</details>
</ul>

## Paired notebooks

The most convenient way to use Jupytext is probably through [paired notebooks](paired-notebooks.md).

To pair a given `.ipynb` or text notebook to an additional notebook format, use either
<ul>
<details>
  <summary>the <i>"pair notebook with..."</i> commands in Jupyter Lab</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext/main/packages/labextension/jupytext_commands.png)](install.md#Jupytext-commands-in-JupyterLab)
</details>

<details>
  <summary>the <i>"pair notebook with..."</i> menu entries in Jupyter Notebook</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext/main/jupytext/nbextension/jupytext_menu.png)](install.md#Jupytext-menu-in-Jupyter-Notebook)
</details>

<details>
  <summary><code>jupytext</code> at the command line</summary>

with e.g.
```
jupytext --set-formats ipynb,py:percent notebook.ipynb
```
see the [documentation](config.md#Per-notebook-configuration).
</details>

<details>
  <summary>or a local or global <code>jupytext.toml</code> configuration file.</summary>

with e.g. the following content:
```
formats = "ipynb,py:percent"
```
see the [documentation](config.md#Configuring-paired-notebooks-globally).
</details>
</ul>

When you save a paired notebook in Jupyter, both the `.ipynb` file and the text version are updated on disk.

When a paired notebook is opened or _reloaded_ in Jupyter, the input cells are loaded from the text file, and combined with the output cells from the `.ipynb` file.

You can edit the text representation of the notebook in your favorite editor, and get the changes back in Jupyter by simply _reloading_ the notebook (Ctrl+R in Jupyter Notebook, <i>"reload notebook"</i> in Jupyter Lab). And the changes are propagated to the `.ipynb` file when you _save_ the notebook.

Alternatively, you can synchronise the two representations by running `jupytext --sync notebook.ipynb` at the command line.

## Which text format?

Jupytext implements many text [formats](formats.md) for Jupyter Notebooks. If your notebook is mostly made of code, you will probably prefer to save it as a script:
-  Use the [percent format](formats.md#The-percent-format), a format with explicit cell delimiters (`# %%`), supported by many IDE (Spyder, Hydrogen, VS Code, PyCharm and PTVS)
-  Or use the [light format](formats.md#The-light-format), if you prefer to see fewer cell markers.

If your notebook contains more text than code, if you are writing a documentation or a book, you probably want to save your notebook as a Markdown document
- Use the [Jupytext Markdown format](formats.md#Jupytext-Markdown) if you wish to render your notebook as a `.md` file (without its outputs) on GitHub
- Use the [MyST Markdown format](formats.md#MyST-Markdown), a markdown flavor that “implements the best parts of reStructuredText”, if you wish to render your notebooks using Sphinx or [Jupyter Book](https://jupyterbook.org).
- Use the [R Markdown format](formats.md#R-Markdown) or the [Quarto format](formats.md#Quarto) if you want to open your Jupyter Notebooks in RStudio.

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
