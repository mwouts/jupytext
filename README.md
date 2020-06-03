![](https://raw.githubusercontent.com/mwouts/jupytext/master/docs/logo.png)

![CI (pip)](https://github.com/mwouts/jupytext/workflows/CI%20(pip)/badge.svg)
![CI (conda)](https://github.com/mwouts/jupytext/workflows/CI%20(conda)/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/jupytext/badge/?version=latest)](https://jupytext.readthedocs.io/en/latest/?badge=latest)
[![codecov.io](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=master)](https://codecov.io/github/mwouts/jupytext?branch=master)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/mwouts/jupytext.svg)](https://lgtm.com/projects/g/mwouts/jupytext/context:python)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub language count](https://img.shields.io/github/languages/count/mwouts/jupytext)

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext can save Jupyter notebooks as
- Markdown and R Markdown documents,
- Scripts in many languages.

It can also convert these documents **into** Jupyter
Notebooks, allowing you to synchronize content in both
directions.

The languages that are currently supported by Jupytext are: Julia, Python, R, Bash, Scheme, Clojure, Matlab, Octave, C++, q/kdb+, IDL, TypeScript, Javascript, Scala, Rust/Evxcr, PowerShell, C#, F#, Robot Framework, Script of Script, Java, Groovy, Coconut. Extending Jupytext to more languages should be easy - read more at [CONTRIBUTING.md](https://github.com/mwouts/jupytext/blob/master/CONTRIBUTING.md). In addition, jupytext users can choose between two formats for notebooks as scripts:
- The `percent` format, compatible with several IDEs, including Spyder, Hydrogen, VScode and PyCharm. In that format, cells are delimited with a commented `%%`.
- The `light` format, designed for this project. Use that format to open standard scripts as notebooks, or to save notebooks as scripts with few cell markers - none when possible.

**For more complete information see [the jupytext FAQ](https://jupytext.readthedocs.io/en/latest/faq.html) and [the jupytext documentation](https://jupytext.readthedocs.io)**


## Try Jupytext

[![Introducing Jupytext](https://img.shields.io/badge/TDS-Introducing%20Jupytext-blue.svg)](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57)
[![PyParis](https://img.shields.io/badge/YouTube-PyParis-red.svg)](https://www.youtube.com/watch?v=y-VEZenk824)
[![CFM insights](https://img.shields.io/badge/CFM%20insights-Jupytext%20&%20Papermill-00ab6c.svg)](https://medium.com/capital-fund-management/automated-reports-with-jupyter-notebooks-using-jupytext-and-papermill-619e60c37330)
[![Binder](https://img.shields.io/badge/Binder-Try%20it!-blue.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb)

Looking for a demo?
- Read the original [announcement](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57) in _Towards Data Science_ (Sept. 2018),
- Watch the [PyParis talk](https://github.com/mwouts/jupytext_pyparis_2018/blob/master/README.md) (Nov. 2018),
- Read our article on [Jupytext and Papermill](https://medium.com/capital-fund-management/automated-reports-with-jupyter-notebooks-using-jupytext-and-papermill-619e60c37330) in _CFM Insights_ (Sept. 2019)
- See how you can edit [Jupyter Notebooks in VS Code or PyCharm](https://towardsdatascience.com/jupyter-notebooks-in-the-ide-visual-studio-code-versus-pycharm-5e72218eb3e8) with (or without!) Jupytext (Jan. 2020)
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

Jupytext provides a contents manager for Jupyter that allows Jupyter to open and save notebooks as text files. When Jupytext's content manager is active in Jupyter, scripts and Markdown documents have a notebook icon.

In most cases, Jupytext's contents manager is activated automatically by Jupytext's server extension. When you restart either `jupyter lab` or `jupyter notebook`, you should see a line that looks like:
```bash
[I 10:28:31.646 LabApp] [Jupytext Server Extension] Changing NotebookApp.contents_manager_class from LargeFileManager to jupytext.TextFileContentsManager
```

If you don't have the notebook icon on text documents after a fresh restart of your Jupyter server, you can either enable our server extension explicitly (with `jupyter serverextension enable jupytext`), or install the contents manager manually. Append
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

The lab extension is included in the Python package. Unless you need to use an older version of the extension you don't have to either install or update the extension manually from [npm](https://www.npmjs.com/).

If you are wondering why the npm and the Python packages have different version, it's because the npm package is updated less often than the Python one. The latest versions are respectively [![npm version](https://badge.fury.io/js/jupyterlab-jupytext.svg)](https://badge.fury.io/js/jupyterlab-jupytext) and [![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext).

Installing Jupytext will trigger a build of JupyterLab the next time you open it. If you prefer, you can trigger the build manually with
```
jupyter lab build
```

The version of the extension that is shipped with Jupytext requires JupyterLab 1.0. If you prefer to continue using JupyterLab in version 0.35, you should install the version 0.19 of the extension:
```
jupyter labextension install jupyterlab-jupytext@0.19
```

## Using Jupytext

### Paired notebooks in the Jupyter Server

Jupytext can write a given notebook to multiple files. In addition to the original notebook file, Jupytext can save the input cells to a text file &mdash; either a script or a Markdown document. Put the text file under version control for a clear commit history. Or refactor the paired script, and reimport the updated input cells by simply refreshing the notebook in Jupyter.

### Configuring notebooks to use Jupytext

Select the pairing for a given notebook using either the [Jupytext menu](#jupytext-menu-in-jupyter-notebook) in Jupyter Notebook, or the [Jupytext commands](#jupytext-commands-in-jupyterlab) in JupyterLab.

Alternatively, the pairing information for one or multiple notebooks can be set on the command line:
```
jupytext --set-formats ipynb,py notebook.ipynb
```

For more information see [the jupytext documentation](https://jupytext.readthedocs.io).

### Command line conversion

The package provides a `jupytext` script for command line conversion between the various notebook extensions:

```bash
jupytext --to py notebook.ipynb                 # convert notebook.ipynb to a .py file
jupytext --to notebook notebook.py              # convert notebook.py to an .ipynb file with no outputs
jupytext --to notebook --execute notebook.md    # convert notebook.md to an .ipynb file and run it
jupytext --update --to notebook notebook.py     # update the input cells in the .ipynb file and preserve outputs and metadata
jupytext --set-formats ipynb,py notebook.ipynb  # Turn notebook.ipynb into a paired ipynb/py notebook
jupytext --sync notebook.ipynb                  # Update all paired representations of notebook.ipynb
```

For more examples, see the [jupytext documentation](https://jupytext.readthedocs.io)

## Want to contribute?

Contributions are welcome. Please let us know how you use `jupytext` and how we could improve it. You think the documentation could be improved? Go ahead and edit it on [GitHub](https://github.com/mwouts/jupytext/tree/master/docs)! Read our [`CONTRIBUTING.md`](CONTRIBUTING.md) to find out guidelines and instructions on how to setup a development environment. And stay tuned for more demos on [medium](https://medium.com/@marc.wouts) and [twitter](https://twitter.com/marcwouts)!
