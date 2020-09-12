# Installation

[![](https://img.shields.io/conda/vn/conda-forge/jupytext.svg)](https://anaconda.org/conda-forge/jupytext)
[![](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![](https://img.shields.io/pypi/pyversions/jupytext.svg)](https://pypi.python.org/pypi/jupytext)

Jupytext is available on pypi and on conda-forge. Run either of
```bash
pip install jupytext --upgrade
```
or
```bash
conda install jupytext -c conda-forge
```

If you want to use Jupytext within Jupyter Notebook or JupyterLab, make sure you install Jupytext in the Python environment where the Jupyter server runs. If that environment is read-only, for instance if your server is started using JupyterHub, install Jupytext in user mode with:
```
/path_to_your_jupyter_environment/python -m pip install jupytext --upgrade --user
```

## Jupytext's contents manager

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

## Jupytext menu in Jupyter Notebook

Jupytext includes an extensions for Jupyter Notebook that adds a Jupytext section in the File menu.

![](https://raw.githubusercontent.com/mwouts/jupytext/master/jupytext/nbextension/jupytext_menu.png)

If the extension was not automatically installed, install and activate it with
```
jupyter nbextension install --py jupytext [--user]
jupyter nbextension enable --py jupytext [--user]
```

## Jupytext commands in JupyterLab

In JupyterLab, Jupytext adds a set of commands to the command palette:

![](https://raw.githubusercontent.com/mwouts/jupytext/master/packages/labextension/jupytext_commands.png)

The Jupytext extension for JupyterLab is bundled with Jupytext. Installing Jupytext will trigger a build of JupyterLab the next time you open it. If you prefer, you can trigger the build manually with
```
jupyter lab build
```

The version of the extension that is shipped with Jupytext requires JupyterLab 2.0. If you prefer to continue using JupyterLab in version 1.x, you should install the version 1.1.1 of the extension:
```
jupyter labextension install jupyterlab-jupytext@1.1.1
```
