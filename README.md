![](https://raw.githubusercontent.com/mwouts/jupytext/main/docs/logo_large.png)

![CI](https://github.com/mwouts/jupytext/workflows/CI/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/jupytext/badge/?version=latest)](https://jupytext.readthedocs.io/en/latest/?badge=latest)
[![codecov.io](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=main)](https://codecov.io/gh/mwouts/jupytext/branch/main)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/mwouts/jupytext.svg)](https://lgtm.com/projects/g/mwouts/jupytext/context:python)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub language count](https://img.shields.io/github/languages/count/mwouts/jupytext)](docs/languages.md)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/jupytext.svg)](https://anaconda.org/conda-forge/jupytext)
[![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![pyversions](https://img.shields.io/pypi/pyversions/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Binder:notebook](https://img.shields.io/badge/binder-notebook-0172B2.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?filepath=demo)
[![Binder:lab](https://img.shields.io/badge/binder-jupyterlab-0172B2.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb)
[![](https://img.shields.io/badge/YouTube-JupyterCon%202020-red.svg)](https://www.youtube.com/watch?v=SDYdeVfMh48)

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext is a plugin for Jupyter that can save Jupyter notebooks as either
- Markdown files (or [MyST Markdown](docs/formats.md#MyST-Markdown) files, or [R Markdown](docs/formats.md#R-Markdown) or [Quarto](docs/formats.md#Quarto) text notebooks)
- Scripts in [many languages](docs/languages.md).

## Use cases

Common [use cases](docs/examples.md) for Jupytext are:
- Doing version control on Jupyter Notebooks
- Editing, merging or refactoring notebooks in your favorite text editor
- Applying Q&A checks on notebooks.

## Install

You can install Jupytext with
- `pip install jupytext`
- or `conda install jupytext -c conda-forge`.

Please note that Jupytext includes an extension for Jupyter Lab. In the latest version of Jupytext, this extension is compatible with Jupyter Lab >= 3.0 only. If you use Jupyter Lab 2.x, please either stay with Jupytext 1.8.2, or install, on top of the latest pip or conda version of Jupytext, a version of the extension that is compatible with Jupyter Lab 2.x:
```
jupyter labextension install jupyterlab-jupytext@1.2.2  # For Jupyter Lab 2.x
```

Then, restart your Jupyter server (for more installation details, see the [install section](docs/install.md) in the documentation).

When Jupytext is installed, `.py` and `.md` files have a notebook icon. And you can really open and run these files as notebooks
<ul>
<details>
  <summary>With a click on the text file in Jupyter Notebook</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext-screenshots/main/JupytextDocumentation/TextNotebooks.png)](https://mybinder.org/v2/gh/mwouts/jupytext/main?filepath=demo)
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

Note: to open links to `.md` files in notebooks with the Notebook editor, use `jupyterlab>=4.0.0a16`.
</details><details>
  <summary>With a right click and <i>open with notebook</i> in Jupyter Lab</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext-screenshots/main/JupytextDocumentation/ContextMenuLab.png)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb)
(click on the image above to try this on [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb))
</details>
</ul>

## Paired notebooks

The most convenient way to use Jupytext is probably through [paired notebooks](docs/paired-notebooks.md).

To pair a given `.ipynb` or text notebook to an additional notebook format, use either
<ul>
<details>
  <summary>the <i>"pair notebook with..."</i> commands in Jupyter Lab</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext/main/packages/labextension/jupytext_commands.png)](docs/install.md#jupytext-commands-in-jupyterlab)
</details>

<details>
  <summary>the <i>"pair notebook with..."</i> menu entries in Jupyter Notebook</summary>

[![](https://raw.githubusercontent.com/mwouts/jupytext/main/jupytext/nbextension/jupytext_menu.png)](docs/install.md#Jupytext-menu-in-Jupyter-Notebook)
</details>

<details>
  <summary><code>jupytext</code> at the command line</summary>

with e.g.
```
jupytext --set-formats ipynb,py:percent notebook.ipynb
```
see the [documentation](docs/config.md#Per-notebook-configuration).
</details>

<details>
  <summary>or a local or global <code>jupytext.toml</code> configuration file.</summary>

with e.g. the following content:
```
formats = "ipynb,py:percent"
```
see the [documentation](docs/config.md#Configuring-paired-notebooks-globally).
</details>
</ul>

When you save a paired notebook in Jupyter, both the `.ipynb` file and the text version are updated on disk.

When a paired notebook is opened or _reloaded_ in Jupyter, the input cells are loaded from the text file, and combined with the output cells from the `.ipynb` file.

You can edit the text representation of the notebook in your favorite editor, and get the changes back in Jupyter by simply _reloading_ the notebook (Ctrl+R in Jupyter Notebook, <i>"reload notebook"</i> in Jupyter Lab). And the changes are propagated to the `.ipynb` file when you _save_ the notebook.

Alternatively, you can synchronise the two representations by running `jupytext --sync notebook.ipynb` at the command line.

## Which text format?

Jupytext implements many text [formats](docs/formats.md) for Jupyter Notebooks. If your notebook is mostly made of code, you will probably prefer to save it as a script:
-  Use the [percent format](docs/formats.md#The-percent-format), a format with explicit cell delimiters (`# %%`), supported by many IDE (Spyder, Hydrogen, VS Code, PyCharm and PTVS)
-  Or use the [light format](docs/formats.md#The-light-format), if you prefer to see fewer cell markers.

If your notebook contains more text than code, if you are writing a documentation or a book, you probably want to save your notebook as a Markdown document
- Use the [Jupytext Markdown format](docs/formats.md#Jupytext-Markdown) if you wish to render your notebook as a `.md` file (without its outputs) on GitHub
- Use the [MyST Markdown format](docs/formats.md#MyST-Markdown), a markdown flavor that “implements the best parts of reStructuredText”, if you wish to render your notebooks using Sphinx or [Jupyter Book](https://jupyterbook.org).
- Use the [R Markdown format](docs/formats.md#R-Markdown) or the [Quarto format](docs/formats.md#Quarto) if you want to open your Jupyter Notebooks in RStudio.

## More resources?

If you're new to Jupytext, you may want to start with the [FAQ](docs/faq.md) or with the [Tutorials](docs/tutorials.md), or with this short introduction to Jupytext: [![](https://img.shields.io/badge/YouTube-JupyterCon%202020-red.svg)](https://www.youtube.com/watch?v=SDYdeVfMh48).
