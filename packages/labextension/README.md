# A JupyterLab extension for Jupytext

This extension adds a few [Jupytext](https://github.com/mwouts/jupytext) commands to the command palette. Use these to select the desired ipynb/text pairing for your notebook.

The latest version for this extension is [![npm version](https://badge.fury.io/js/jupyterlab-jupytext.svg)](https://badge.fury.io/js/jupyterlab-jupytext).
 
Most users do not need to install this extension, since it is already included in the latest [jupytext](https://github.com/mwouts/jupytext/), both on [![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext) and 
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/jupytext.svg)](https://anaconda.org/conda-forge/jupytext).

![](https://github.com/mwouts/jupytext/raw/master/packages/labextension/jupytext_commands.png)

## Installation

Please install [Jupytext](https://github.com/mwouts/jupytext/blob/master/README.md#installation) first. As mentioned above, both the `pip` and `conda` packages do include the latest version of the JupyterLab extension, so in most cases you don't need to specifically install this `npm` package. 

Installing Jupytext will trigger a build of JupyterLab the next time you open it. If you prefer, you can trigger the build manually with

```bash
jupyter lab build
```

In case you're not using JupyterLab 1.0, you may have to install another version of the extension that is compatible with your version. For instance, install the last version of the extension compatible with Jupyter 0.35 with

```bash
jupyter labextension install jupyterlab-jupytext@0.19
```

# How to develop this extension

We assume that you have activated the conda environment described in [CONTRIBUTING.md](https://github.com/mwouts/jupytext/blob/master/CONTRIBUTING.md). In addition to that environment, you will need `npm`. Install it with 

```bash
conda install nodejs
```

In that environment, install JupyterLab's plugin manager, and the extension with
```bash
# Go to the extension folder
cd packages/labextension

# Cleanup
rm -rf lib node_modules yarn.lock

# Install JupyterLab's plugin manager
jlpm install

# Package the extension
npm pack
```

Then you can rebuild the Jupytext python package (with `python setup.py sdist bdist_wheel`) and reinstall it (`pip install dist\jupytext-XXX.tar.gz`).

Alternatively, if you prefer to develop iteratively, you could install a development version of the extension with

```bash
jupyter labextension install . --no-build
```

Then start JupyterLab in watch mode in another shell on the same environment:
```bash
jupyter lab --watch
```

And finally, make changes to the extension and rebuild it (in the first shell) with:
```bash
jlpm run build
```

# How to publish a new version of the extension

Bump the version in `package.json`, rebuild the extension with `npm pack`. Include the new extension in Git and `setup.py`, and delete the previous version.

If you wish, you can also publish the package on [npm](https://www.npmjs.com) with

```bash
npm publish --access=public
```
