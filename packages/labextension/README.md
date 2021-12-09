# A JupyterLab extension for Jupytext

This extension adds a few [Jupytext](https://github.com/mwouts/jupytext) commands to the command palette. Use these to select the desired ipynb/text pairing for your notebook.

The latest version for this extension is [![npm version](https://badge.fury.io/js/jupyterlab-jupytext.svg)](https://badge.fury.io/js/jupyterlab-jupytext).

Most users do not need to install this extension, since it is already included in the latest [jupytext](https://github.com/mwouts/jupytext/), both on [![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext) and
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/jupytext.svg)](https://anaconda.org/conda-forge/jupytext).

![](https://raw.githubusercontent.com/mwouts/jupytext/main/packages/labextension/jupytext_commands.png)

## Installation

Please install [Jupytext](https://github.com/mwouts/jupytext/blob/main/README.md#Install) first. As mentioned above, both the `pip` and `conda` packages do include the latest version of the JupyterLab extension, so in most cases you don't need to specifically install this `npm` package.

In case you're not using JupyterLab 3.x, you will have to install an older version of the extension that is compatible with your version. Please first install `jupytext` using `pip` or `conda`, and then downgrade the extension to a version compatible with your version of Jupyter Lab with:
```bash
jupyter labextension install jupyterlab-jupytext@1.2.2  # for JupyterLab 2.x
jupyter labextension install jupyterlab-jupytext@1.1.1  # for JupyterLab 1.x
```

# How to develop this extension

We assume that you have activated the conda environment described in [CONTRIBUTING.md](https://github.com/mwouts/jupytext/blob/main/CONTRIBUTING.md).

Then you can rebuild the Jupytext python package (with `BUILD_JUPYTERLAB_EXTENSION=1 python setup.py sdist bdist_wheel`) and reinstall it (`pip install dist/jupytext-x.x.x-py3-none-any.whl`).

Alternatively, if you prefer to develop iteratively, you could install a development version of the extension with

```bash
BUILD_JUPYTERLAB_EXTENSION=1 jupyter labextension develop . --overwrite
```

Read more on this on the [JupyterLab documentation](https://jupyterlab.readthedocs.io/en/latest/extension/extension_dev.html#developing-a-prebuilt-extension).

# How to publish a new version of the extension on npm

Please note that the main purpose of updating the extension on [npm](https://www.npmjs.com) is to keep the npm documentation up-to-date, since the extension is made available within the Python package itself.

Make sure you have `nodejs>=12` installed, bump the version in `package.json`, and then:
```bash
# Go to the extension folder
cd packages/labextension

# Cleanup
rm -rf lib node_modules yarn.lock

# Install JupyterLab's plugin manager
jlpm install

# Package the extension
npm pack

# Test the extension locally
jupyter labextension install jupyterlab-jupytext-xxx.tgz

# Publish the package on npm with
npm publish --access=public
```
