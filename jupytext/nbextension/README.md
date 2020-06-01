# A Jupyter notebook extension for Jupytext

This extension adds a [Jupytext](https://github.com/mwouts/jupytext/blob/master/README.md) menu to Jupyter notebook. Use the menu to select the desired ipynb/text pairing for your notebook.

![Jupytext menu screenshot](jupytext_menu.png)

## Installation

The extension requires [Jupytext](https://github.com/mwouts/jupytext/blob/master/README.md). Please make sure that Jupytext is installed on you system, and that its contents manager is active, i.e. that Markdown files and scripts are displayed with a notebook icon.

Installing Jupytext activates the Jupytext Menu by default. If you want to install and activate it manually, use the following commands:

```bash
jupyter nbextension install --py jupytext
jupyter nbextension enable --py jupytext
```

Add `--user` to these commands if you want to activate the extension only for the current user.

## How to develop this extension

If you wish to develop this extension, install the javascript file locally with:

```bash
cd jupytext/nbextension
jupyter nbextension install index.js --symlink --user
jupyter nbextension enable index --user
```

Then, make the desired changes to `index.js` and reload the extension by simply refreshing the notebook (Ctrl+R). In case your OS does not allow symlinks, edit the copy of `index.js` that is actually used by Jupyter (refer to the output of `jupyter nbextension install --user index.js`).
