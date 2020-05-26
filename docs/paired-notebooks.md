# Paired notebooks

Jupytext can write a given notebook to multiple files. In addition to the original notebook file, Jupytext can save the input cells to a text file &mdash; either a script or a Markdown document. Put the text file under version control for a clear commit history. Or refactor the paired script, and reimport the updated input cells by simply refreshing the notebook in Jupyter.

## How to pair a notebook to multiple formats

In Jupyter Notebook, pair your notebook to one or more text formats with the [Jupytext menu](install.html#jupytext-menu-in-jupyter-notebook):

![](https://raw.githubusercontent.com/mwouts/jupytext_nbextension/master/jupytext_menu.png)

In JupyterLab, use the [Jupytext commands](install.html#jupytext-commands-in-jupyterlab):

![](https://raw.githubusercontent.com/mwouts/jupyterlab-jupytext/master/jupytext_commands.png)

These command simply add a `"jupytext": {"formats": "ipynb,md"}`-like entry in the notebook metadata.

You can also configure the notebook pairing on the command line, and set a default pairing for all the notebooks either globally or in a subfolder - see [here](config.md#).

## Can I edit a notebook simultaneously in Jupyter and in a text editor?

When saving a paired notebook using Jupytext's contents manager, Jupyter updates both the `.ipynb` and its text representation. The text representation can be edited outside of Jupyter. When the notebook is refreshed in Jupyter, the input cells are read from the text file, and the output cells from the `.ipynb` file.

It is possible (and convenient) to leave the notebook open in Jupyter while you edit its text representation. However, you don't want that the two editors save the notebook simultaneously. To avoid this:
- deactivate Jupyter's autosave, by either toggling the `"Autosave notebook"` menu entry or run `%autosave 0` in a cell of the notebook (see in the [faq](https://github.com/mwouts/jupytext/blob/master/docs/faq.md#jupyter-warns-me-that-the-file-has-changed-on-disk) how to deactivate autosave permanently)
- and refresh the notebook when you switch back from the editor to Jupyter.

In case you forgot to refresh, and saved the Jupyter notebook while the text representation had changed, no worries: Jupyter will ask you which version you want to keep:

![](https://github.com/mwouts/jupytext-screenshots/raw/master/JupytextDocumentation/NotebookChanged.png)

When that occurs, please choose the version in which you made the latest changes. And give a second look to our advice to deactivate the autosaving of notebooks in Jupyter.

## How to open scripts with either the text or notebook view in Jupyter?

With Jupytext's contents manager for Jupyter, scripts and Markdown documents gain a notebook icon. If you don't see the notebook icon, double check the [contents manager configuration](install.html#jupytexts-contents-manager).

By default, Jupyter Notebook open scripts and Markdown documents as notebooks. If you want to open them with the text editor, select the document and click on _edit_:

![](https://github.com/mwouts/jupytext-screenshots/raw/master/JupytextDocumentation/OpenAsText.png)


In JupyterLab this is slightly different. Scripts and Markdown document also have a notebook icon. But they open as text by default. Open them as notebooks with the  _Open With -> Notebook_ context menu (available in JupyterLab 0.35 and above):

![](https://github.com/mwouts/jupytext-screenshots/raw/master/JupytextDocumentation/ContextMenuLab.png)

If do not want to classify scripts or Markdown documents as notebooks, please use the `notebook_extension` option. For instance, if you want to get the notebook icon only for `.ipynb` and `.Rmd` files, set

```python
c.ContentsManager.notebook_extensions = "ipynb,Rmd"
```

Please note that, with the above setting, Jupyter will not let you open scripts as notebooks. If you still want to do so, use Jupytext command line (see below) to first convert or pair the script to an `.ipynb` notebook.
