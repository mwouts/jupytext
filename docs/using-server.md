# Using Jupytext in Jupyter

## Paired notebooks

Jupytext can write a given notebook to multiple files. In addition to the original notebook file, Jupytext can save the input cells to a text file &mdash; either a script or a Markdown document. Put the text file under version control for a clear commit history. Or refactor the paired script, and reimport the updated input cells by simply refreshing the notebook in Jupyter.

## Per-notebook configuration

Select the pairing for a given notebook using either the [Jupytext menu](install.html#jupytext-menu-in-jupyter-notebook) in Jupyter Notebook, or the [Jupytext commands](install.html#jupytext-commands-in-jupyterlab) in JupyterLab.

These command simply add a `"jupytext": {"formats": "ipynb,md"}`-like entry in the notebook metadata. You could also set that metadata yourself with _Edit/Edit Notebook Metadata_ in Jupyter Notebook. In JupyterLab, use [this extension](https://github.com/yuvipanda/jupyterlab-nbmetadata).

The pairing information for one or multiple notebooks can be set on the command line:
```
jupytext --set-formats ipynb,py [--sync] notebook.ipynb
```
You can pair a notebook to as many text representations as you want (see our _World population_ notebook in the demo folder). Format specifications are of the form
```
[[path/][prefix]/][suffix.]ext[:format_name]
```
where
- `ext` is one of `ipynb`, `md`, `Rmd`, `jl`, `py`, `R`, `sh`, `cpp`, `q`. Use the `auto` extension to have the script extension chosen according to the Jupyter kernel.
- `format_name` (optional) is either `light` (default for scripts), `bare`, `percent`, `hydrogen`, `sphinx` (Python only), `spin` (R only) &mdash; see the [format specifications](formats.md).
- `path`, `prefix` and `suffix` allow to save the text representation to files with different names, or in a different folder.

If you want to pair a notebook to a python script in a subfolder named `scripts`, set the formats metadata to `ipynb,scripts//py`. If the notebook is in a `notebooks` folder and you want the text representation to be in a `scripts` folder at the same level, set the Jupytext formats to `notebooks//ipynb,scripts//py`.

Jupytext accepts a few additional options. These options should be added to the `"jupytext"` section in the metadata &mdash; use either the metadata editor or the `--opt/--format-options` argument on the command line.
- `comment_magics`: By default, Jupyter magics are commented when notebooks are exported to any other format than markdown. If you prefer otherwise, use this boolean option, or is global counterpart (see below).
- `notebook_metadata_filter`: By default, Jupytext only exports the `kernelspec` and `jupytext` metadata to the text files. Set `"jupytext": {"notebook_metadata_filter": "-all"}` if you want that the script has no notebook metadata at all. The value for `notebook_metadata_filter` is a comma separated list of additional/excluded (negated) entries, with `all` a keyword that allows to exclude all entries.
- `cell_metadata_filter`: By default, cell metadata `autoscroll`, `collapsed`, `scrolled`, `trusted` and `ExecuteTime` are not included in the text representation. Add or exclude more cell metadata with this option.

## Global configuration

Jupytext's contents manager also accepts global options. These options have to be set on Jupytext's contents manager, so please first include the following line in your `.jupyter/jupyter_notebook_config.py` file:
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
```

We start with the default format pairing. Say you want to always associate every `.ipynb` notebook with a `.md` file  (and reciprocally). This is simply done by adding the following to your Jupyter configuration file:
```python
# Always pair ipynb notebooks to md files
c.ContentsManager.default_jupytext_formats = "ipynb,md"
```
(and similarly for the other formats).

In case the [`percent`](formats.html#the-percent-format) format is your favorite, add the following to your `.jupyter/jupyter_notebook_config.py` file:
```python
# Use the percent format when saving as py
c.ContentsManager.preferred_jupytext_formats_save = "py:percent"
```
and then, Jupytext will understand `"jupytext": {"formats": "ipynb,py"}` as an instruction to create the paired Python script in the `percent` format.

To disable global pairing for an individual notebook, set formats to a single format, e.g.:
`"jupytext": {"formats": "ipynb"}`

## Metadata filtering

You can specify which metadata to include or exclude in the text files created by Jupytext by setting `c.ContentsManager.default_notebook_metadata_filter` (notebook metadata) and `c.ContentsManager.default_cell_metadata_filter` (cell metadata). They accept a string of comma separated keywords. A minus sign `-` in front of a keyword means exclusion.

Suppose you want to keep all the notebook metadata but `widgets` and `varInspector` in the YAML header. For cell metadata, you want to allow `ExecuteTime` and `autoscroll`, but not `hide_output`. You can set
```python
c.ContentsManager.default_notebook_metadata_filter = "all,-widgets,-varInspector"
c.ContentsManager.default_cell_metadata_filter = "ExecuteTime,autoscroll,-hide_output"
```

If you want that the text files created by Jupytext have no metadata, you may use the global metadata filters below. Please note that with this setting, the metadata is only preserved in the `.ipynb` file.
```python
c.ContentsManager.default_notebook_metadata_filter = "-all"
c.ContentsManager.default_cell_metadata_filter = "-all"
```

NB: All these global options (and more) are documented [here](https://github.com/mwouts/jupytext/blob/master/jupytext/contentsmanager.py).

## Can I edit a notebook simultaneously in Jupyter and in a text editor?

When saving a paired notebook using Jupytext's contents manager, Jupyter updates both the `.ipynb` and its text representation. The text representation can be edited outside of Jupyter. When the notebook is refreshed in Jupyter, the input cells are read from the text file, and the output cells from the `.ipynb` file.

It is possible (and convenient) to leave the notebook open in Jupyter while you edit its text representation. However, you don't want that the two editors save the notebook simultaneously. To avoid this:
- deactivate Jupyter's autosave, by toggling the `"Autosave notebook"` menu entry (or run `%autosave 0` in a cell of the notebook)
- and refresh the notebook when you switch back from the editor to Jupyter.

In case you forgot to refresh, and saved the Jupyter notebook while the text representation had changed, no worries: Jupyter will ask you which version you want to keep:

![](https://github.com/mwouts/jupytext-screenshots/raw/master/JupytextDocumentation/NotebookChanged.png)

When that occurs, please choose the version in which you made the latest changes. And give a second look to our advice to deactivate the autosaving of notebooks in Jupyter.

## How to open scripts with either the text or notebook view in Jupyter?

With Jupytext's contents manager for Jupyter, scripts and Markdown documents gain a notebook icon. If you don't see the notebook icon, double check the [contents manager configuration](https://github.com/mwouts/jupytext/blob/master/README.md#jupytexts-contents-manager).

By default, Jupyter Notebook open scripts and Markdown documents as notebooks. If you want to open them with the text editor, select the document and click on _edit_:

![](https://github.com/mwouts/jupytext-screenshots/raw/master/JupytextDocumentation/OpenAsText.png)


In JupyterLab this is slightly different. Scripts and Markdown document also have a notebook icon. But they open as text by default. Open them as notebooks with the  _Open With -> Notebook_ context menu (available in JupyterLab 0.35 and above):

![](https://github.com/mwouts/jupytext-screenshots/raw/master/JupytextDocumentation/ContextMenuLab.png)

If do not want to classify scripts or Markdown documents as notebooks, please use the `notebook_extension` option. For instance, if you want to get the notebook icon only for `.ipynb` and `.Rmd` files, set

```python
c.ContentsManager.notebook_extensions = "ipynb,Rmd"
``` 

Please note that, with the above setting, Jupyter will not let you open scripts as notebooks. If you still want to do so, use Jupytext command line (see below) to first convert or pair the script to an `.ipynb` notebook.
