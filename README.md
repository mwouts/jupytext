# A Jupyter notebook extension for Jupytext

This extension adds a [Jupytext](https://github.com/mwouts/jupytext) menu to Jupyter notebook, where you can select the desired ipynb/text pairing for your notebook.

![Jupytext menu screenshot](todo.png)

# Installation

Please [install Jupytext](https://github.com/mwouts/jupytext/blob/master/README.md#installation) first. Then, install this extension with:

```bash
jupyter nbextension install --user jupytext.js
jupyter nbextension enable jupytext
```

and restart your notebook server.

# How to develop this extension:

Clone this repository and install the extension as a symbolic link:

```bash
jupyter nbextension install --symlink --user jupytext.js
jupyter nbextension enable jupytext
```

Then, make the desired changes to `jupytext.js` and reload the extension by simply refreshing the notebook (Ctrl+R). In case your OS does not allow symlinks, edit the copy of `jupytext.js` that is actually used by Jupyter (refer to the output of the `jupyter nbextension install --user jupytext.js` command).