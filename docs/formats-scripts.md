# Notebooks as code

## The `percent` format

The `percent` format is a representation of Jupyter notebooks as scripts, in which all cells are explicitly delimited with a commented double percent sign `# %%`. The `percent` format is currently available for these [languages](https://github.com/mwouts/jupytext/blob/main/src/jupytext/languages.py).

The format was introduced by Spyder in 2013, and is now supported by many editors, including
- [Spyder IDE](https://docs.spyder-ide.org/editor.html#defining-code-cells),
- [Hydrogen](https://nteract.gitbooks.io/hydrogen/docs/Usage/NotebookFiles.html#notebook-export), a package for Atom,
- [VS
  Code](https://code.visualstudio.com/docs/python/jupyter-support-py#_jupyter-code-cells),
- [Python Tools for Visual Studio](https://docs.microsoft.com/en-us/visualstudio/python/python-interactive-repl-in-visual-studio?view=vs-2019#work-with-code-cells),
- and [PyCharm Professional](https://www.jetbrains.com/help/pycharm/editing-jupyter-notebook-files.html#edit-content).

Our implementation of the `percent` format is as follows: cells can have
- a title
- a cell type (`markdown`, `md` or `raw`, omitted for code cells)
- and cell metadata
like in this example:

```python
# %% Optional title [cell type] key="value"
```

In the `percent` format, our previous example becomes:
```python
# %% [markdown]
# This is a multiline
# Markdown cell

# %% [markdown]
# Another Markdown cell


# %%
# This is a code cell
class A():
    def one():
        return 1

    def two():
        return 2
```

In the case of Python scripts, Markdown cells do accept multiline comments:
```python
# %% [markdown]
"""
This is a Markdown cell
that uses multiline comments
"""
```

By default Jupytext will use line comments when it converts your Jupyter notebooks for `percent` scripts. If you prefer to use multiline comments for all text cells, add a `{"jupytext": {"cell_markers": "\"\"\""}}` metadata to your notebook, either with the notebook metadata editor in Jupyter, or at the command line:
```bash
jupytext --update-metadata '{"jupytext": {"cell_markers": "\"\"\""}}' notebook.ipynb --to py:percent
```

If you want to use multiline comments for all your paired notebooks, you could also add
```python
cell_markers = '"""'
```
to your [`jupytext.toml` configuration file](config.md).

See how our `World population.ipynb` notebook is [represented](https://github.com/mwouts/jupytext/blob/main/demo/World%20population.pct.py) in the `percent` format.

## The `hydrogen` format

By default, [Jupyter magics](advanced-options.md#magic-commands) are commented in the `percent` representation. If you run the percent scripts in Hydrogen, use the `hydrogen` format, a variant of the `percent` format that does not comment Jupyter magic commands.

## The `light` format

The `light` format was introduced by Jupytext. That format can represent any script in one of these [languages](https://github.com/mwouts/jupytext/blob/main/src/jupytext/languages.py) as a Jupyter notebook.

When a script in the `light` format is converted to a notebook, Jupytext code paragraphs are turned into code cells, and comments that are not adjacent to code are converted to Markdown cells. Cell breaks occurs on blank lines outside of functions, classes or multiline comments.

For instance, in this example we have three cells:
```python
# This is a multiline
# Markdown cell

# Another Markdown cell


# This is a code cell
class A():
    def one():
        return 1

    def two():
        return 2
```

Code cells can contain multiple code paragraphs. In that case Jupytext uses an explicit start-of-cell delimiter that is, by default, `# +` (`// +` in C++, etc). The default end of cell delimiter is `# -`, and can be omitted when followed by another explicit start of cell marker, or the end of the file:

```python
# +
# A single code cell made of two paragraphs
a = 1


def f(x):
    return x+a
```

Metadata can be associated to a given cell using a key/value representation:
```python
# + key="value"
# A code cell with metadata

# + [markdown] key="value"
# A Markdown cell with metadata
```

The `light` format can use custom cell markers instead of `# +` or `# -`. If you prefer to mark cells with VS Code/PyCharm (resp. Vim) folding markers, set `"cell_markers": "region,endregion"` (resp. `"{{{,}}}"`) in the jupytext section of the notebook metadata. If you want to configure this as a global default, add either
```python
cell_markers = "region,endregion"  # Use VS Code/PyCharm region folding delimiters
```
or
```python
cell_markers = "{{{,}}}"           # Use Vim region folding delimiters
```
to your [`jupytext.toml` configuration file](config.md#).

See how our `World population.ipynb` notebook is [represented](https://github.com/mwouts/jupytext/blob/main/demo/World%20population.lgt.py) in that format.

## The `nomarker` format

The `nomarker` format is a variation of the `light` format with no cell marker at all. Please note that this format does not provide round-trip consistency - code cells are split on code paragraphs. By default, the `nomarker` format still includes a YAML header - if you prefer to also remove the header, set `"notebook_metadata_filter": "-all"` in the jupytext section of your notebook metadata.

## Sphinx-gallery scripts

Another popular notebook-like format for Python scripts is the Sphinx-gallery [format](https://sphinx-gallery.github.io/stable/syntax.html). Scripts that contain at least two lines with more than twenty hash signs are classified as Sphinx-Gallery notebooks by Jupytext.

Comments in Sphinx-Gallery scripts are formatted using reStructuredText rather than markdown. They can be converted to markdown for a nicer display in Jupyter by adding a `sphinx_convert_rst2md = True` line to your Jupytext configuration file. Please note that this is a non-reversible transformation—use this only with Binder. Revert to the default value `sphinx_convert_rst2md = False` when you edit Sphinx-Gallery files with Jupytext.

Turn a GitHub repository containing Sphinx-Gallery scripts into a live notebook repository with [Binder](https://mybinder.org/) and Jupytext by adding only two files to the repo:
- `binder/requirements.txt`, a list of the required packages (including `jupytext`)
- a [`jupytext.toml` configuration file](config.md#) with the following contents:
```
preferred_jupytext_formats_read = "py:sphinx"
sphinx_convert_rst2md = true
```

Our sample notebook is also represented in `sphinx` format [here](https://github.com/mwouts/jupytext/blob/main/demo/World%20population.spx.py).
