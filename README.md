# Jupyter notebooks as Markdown documents, Julia, Python or R scripts

[![Build Status](https://travis-ci.com/mwouts/jupytext.svg?branch=master)](https://travis-ci.com/mwouts/jupytext)
[![Documentation Status](https://readthedocs.org/projects/jupytext/badge/?version=latest)](https://jupytext.readthedocs.io/en/latest/?badge=latest)
[![codecov.io](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=master)](https://codecov.io/github/mwouts/jupytext?branch=master)
[![Language grade: Python](https://img.shields.io/badge/lgtm-A+-brightgreen.svg)](https://lgtm.com/projects/g/mwouts/jupytext/context:python)

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext can save Jupyter notebooks as
- Markdown and R Markdown documents,
- Scripts in many languages.

It can also convert these documents **into** Jupyter
Notebooks, allowing you to synchronize content in both
directions.

The languages that are currently supported by Jupytext are: Julia, Python, R, Bash, Scheme, Clojure, Matlab, Octave, C++, q/kdb+, IDL, TypeScript, Javascript and Scala. Extending Jupytext to more languages should be easy - read more at [CONTRIBUTING.md](https://github.com/mwouts/jupytext/blob/master/CONTRIBUTING.md). In addition, jupytext users can choose between two formats for notebooks as scripts:
- The `percent` format, compatible with several IDEs, including Spyder, Hydrogen, VScode and PyCharm. In that format, cells are delimited with a commented `%%`.
- The `light` format, designed for this project. Use that format to open standard scripts as notebooks, or to save notebooks as scripts with few cell markers - none when possible.

**For more complete information try [the jupytext documentation](https://jupytext.readthedocs.io), or have a look at our [FAQ](https://jupytext.readthedocs.io/en/latest/faq.html)**


## Try Jupytext

[![Introducing Jupytext](https://img.shields.io/badge/TDS-Introducing%20Jupytext-blue.svg)](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57)
[![PyParis](https://img.shields.io/badge/YouTube-PyParis-red.svg)](https://www.youtube.com/watch?v=y-VEZenk824)
[![Binder](https://img.shields.io/badge/Binder-Try%20it!-blue.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb)

Looking for a demo?
- Read the original [announcement](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57) in Towards Data Science,
- Watch the [PyParis talk](https://github.com/mwouts/jupytext_pyparis_2018/blob/master/README.md),
- or, try Jupytext online with [binder](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb)!

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

If you want to use Jupytext within Jupyter Notebook or JupyterLab, make sure you install Jupytext in the Python environment where the Jupyter server runs. If that environment is read-only, for instance if your server is started using JupyterHub, install Jupytext in user mode with:
```
/path_to_your_jupyter_environment/python -m pip install jupytext --upgrade --user
```

### Jupytext's contents manager

Jupytext includes a contents manager for Jupyter that allows Jupyter to open and save notebooks as text files. When Jupytext's content manager is active in Jupyter, scripts and Markdown documents have a notebook icon.

If you don't have the notebook icon on text documents after a fresh restart of your Jupyter server, install the contents manager manually. Append
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
```
to your `.jupyter/jupyter_notebook_config.py` file (generate a Jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`). Our contents manager accepts a few options: default formats, default metadata filter, etc. Then, restart Jupyter Notebook or JupyterLab, either from the JupyterHub interface or from the command line with
```bash
jupyter notebook # or lab
```

### Jupytext menu in Jupyter Notebook

Jupytext includes an extensions for Jupyter Notebook that adds a Jupytext section in the File menu.

![Jupyter notebook extension](https://raw.githubusercontent.com/mwouts/jupytext_nbextension/master/jupytext_menu.png)

If the extension was not automatically installed, install and activate it with
```
jupyter nbextension install --py jupytext [--user]
jupyter nbextension enable --py jupytext [--user]
```

### Jupytext commands in JupyterLab

In JupyterLab, Jupytext adds a set of commands to the command palette:

![JupyterLab extension](https://raw.githubusercontent.com/mwouts/jupyterlab-jupytext/master/jupytext_commands.png)

If you don't see these commands, install the extension manually with
```
jupyter labextension install jupyterlab-jupytext
```
(the above requires `npm`, run `conda install nodejs` first if you don't have `npm`).

## Using Jupytext

### Paired notebooks in the Jupyter Server

Jupytext can write a given notebook to multiple files. In addition to the original notebook file, Jupytext can save the input cells to a text file &mdash; either a script or a Markdown document. Put the text file under version control for a clear commit history. Or refactor the paired script, and reimport the updated input cells by simply refreshing the notebook in Jupyter.

### Configuring notebooks to use Jupytext

Select the pairing for a given notebook using either the [Jupytext menu](#jupytext-menu-in-jupyter-notebook) in Jupyter Notebook, or the [Jupytext commands](#jupytext-commands-in-jupyterlab) in JupyterLab.

Alternatively, the pairing information for one or multiple notebooks can be set on the command line:
```
jupytext --set-formats ipynb,py [--sync] notebook.ipynb
```

For more information see [the jupytext documentation](https://jupytext.readthedocs.io).

### Command line conversion

The package provides a `jupytext` script for command line conversion between the various notebook extensions:

```bash
jupytext --to py notebook.ipynb                 # convert notebook.ipynb to a .py file
jupytext --to notebook notebook.py              # convert notebook.py to an .ipynb file with no outputs
jupytext --to notebook --execute notebook.md    # convert notebook.md to an .ipynb file and run it 
jupytext --update --to notebook notebook.py     # update the input cells in the .ipynb file and preserve outputs and metadata
jupytext --set-formats --ipynb,py notebook.ipynb  # Turn notebook.ipynb into a paired ipynb/py notebook
jupytext --sync notebook.ipynb                  # Update all paired representations of notebook.ipynb
```

For more examples, see the [jupytext documentation](https://jupytext.readthedocs.io)

## Want to contribute?

Contributions are welcome. Please let us know how you use `jupytext` and how we could improve it. You think the documentation could be improved? Go ahead! Read our [`CONTRIBUTING.md`](CONTRIBUTING.md) to find out guidelines and instructions on how to setup a development environment. And stay tuned for more demos on [medium](https://medium.com/@marc.wouts) and [twitter](https://twitter.com/marcwouts)!
