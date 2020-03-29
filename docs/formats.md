# Supported formats

Jupytext supports conversion between the `.ipynb` format and many different formats. This page describes each format, as well as some considerations for each.

## Markdown formats

### Jupytext Markdown

Jupytext can save notebooks as [Markdown](https://daringfireball.net/projects/markdown/syntax) documents. This format is well adapted to tutorials, books, or more generally notebooks that contain more text than code. Notebooks represented in this form are well rendered by most Markdown editors or renderers, including GitHub.

Like all the Jupytext formats, Jupytext Markdown notebooks start with an (optional) YAML header. This header is used to store selected notebook metadata like the kernel information, together with Jupytext's format and version information.
```
---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.1.0
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---
```

You can add custom notebook metadata like `author` or `title` under the `jupyter:` section, it will be synchronized with the notebook metadata. 
And if you wish to export more metadata from the notebook, have a look at the paragraph on [metadata filtering](#metadata-filtering).

In the Markdown format, markdown cells are inserted verbatim and separated with two blank lines.

If you'd like that cell breaks also occurs on Markdown headers, add a `split_at_heading: true` entry in the `jupytext` section in the YAML header, or if you want that option to be the default for all Markdown documents in Jupyter, activate the option on Jupytext's content manager:

```python
c.ContentsManager.split_at_heading = True
```

Code cells are encoded using the classical triple backticks, followed by the notebook language. Cell metadata are appended after the language information, with a `key=value` syntax, where `value` is encoded in JSON format. For instance, in a Python notebook, a simple code cell with a `parameters` tag is represented as:

    ```python tags=["parameters"]
    param = 5
    ```

Code snippets are turned into code cells in Jupyter as soon as they have an explicit language, when that language is supported in Jupyter. Thus, you have a code snippet that you don't want to execute in Jupyter, you can either
- remove the language information, 
- or, start the code snippet with a triple tilde, e.g. `~~~python`, instead of ` ```python`
- or, add an `active="md"` cell metadata, or a `.noeval` attribute after the language information, e.g. ` ```python .noeval `
- or, surround the code snippet with explicit Markdown cell markers (see below).

Raw cells are delimited with HTML comments, and accept cell metadata in the same key=value format:

    <!-- #raw -->
    raw text
    <!-- #endraw -->

    <!-- #raw key="value"-->
    raw cell with metadata
    <!-- #endraw -->

Markdown cells can also have explicit markers: use one of `<!-- #md -->` or `<!-- #markdown -->` or `<!-- #region -->` and the corresponding `<!-- #end... -->` counterpart. Note that the `<!-- #region -->` and `<!-- #endregion -->` cells markers are [foldable](https://code.visualstudio.com/docs/editor/codebasics#_folding) in VS Code, and that you can also insert a title there, e.g. `<!-- #region This is a title for my protected cell -->`. Cell metadata are accepted in the format `key="value"` (`"value"` being encoded in JSON) as for the other cell types.

For a concrete example, see how our `World population.ipynb` notebook in the [demo folder](https://github.com/mwouts/jupytext/tree/master/demo) is represented in [Markdown](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.md#).

### R Markdown

[R Markdown](https://rmarkdown.rstudio.com/authoring_quick_tour.html) is [RStudio](https://www.rstudio.com/)'s format for notebooks, with support for R, Python, and many [other languages](https://bookdown.org/yihui/rmarkdown/language-engines.html).

Jupytext's implementation of R Markdown is very similar to that of the Markdown format. The major difference is on code cells, which use R Markdown's convention, i.e. the language and options are surrounded by curly brackets, and the cell metadata are encoded as R objects. For instance our cell with the `parameters` tags would be represented as:

    ```{python tags=c("parameters")}
    param = 5
    ```

Python and R notebooks represented in the R Markdown format can run both in Jupyter and RStudio. Note that you can change the default Python environment in RStudio with `RETICULATE_PYTHON` in a `.Renviron` file, see [here](https://github.com/mwouts/jupytext/issues/267#issuecomment-506994930).

See how our `World population.ipynb` notebook in the [demo folder](https://github.com/mwouts/jupytext/tree/master/demo) is represented in [R Markdown](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.Rmd).

### Pandoc Markdown

Pandoc, the _Universal document converter_,  can read and write Jupyter notebooks - see [Pandoc's documentation](https://pandoc.org/MANUAL.html#creating-jupyter-notebooks-with-pandoc).

In Pandoc Markdown, all cells are marked with pandoc divs (`:::`). The format is therefore slightly more verbose than the Jupytext Markdown format.

See for instance how our `World population.ipynb` notebook is [represented](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.pandoc.md#) in the `md:pandoc` format.

If you wish to use that format, please install `pandoc` in version 2.7.2 or above, with e.g. `conda install pandoc -c conda-forge`.

### MyST Markdown

[MyST (Markedly Structured Text)][myst-parser] is a markdown flavor that "implements the best parts of reStructuredText". It provides a way to call Sphinx directives and roles from within Markdown,
using a *slight* extension of CommonMark markdown.
[MyST-NB][myst-nb] builds on this markdown flavor, to offer direct conversion of Jupyter Notebooks into Sphinx documents.

Similar to the jupytext Markdown format, MyST Markdown uses code blocks to contain code cells.
The difference though, is that the metadata is contained in a YAML block:

````md
```{code-cell} ipython3
---
other:
  more: true
tags: [hide-output, show-input]
---

print("Hallo!")
```
````

The `ipython3` here is purely optional, as an aide for syntax highlighting.
In the round-trip, it is copied from `notebook.metadata.language_info.pygments_lexer`.

Also, where possible the conversion will use the short-hand metadata format
(see the [MyST guide](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#parameterizing-directives)):

````md
```{code-cell} ipython3
:tags: [hide-output, show-input]

print("Hallo!")
```
````

Raw cells are also represented in a similare fashion:

````md
```{raw-cell}
:raw_mimetype: text/html

<b>Bold text<b>
```
````

Markdown cells are not wrapped. If a markdown cell has metadata, or
directly proceeds another markdown cell, then a [block break] will be inserted
above it, with an (optional) single line JSON representation of the metadata:

```md
+++ {"slide": true}

This is a markdown cell with metadata

+++

This is a new markdown cell with no metadata
```

See for instance how our `World population.ipynb` notebook is [represented](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.myst.md#) in the `myst` format.

If you wish to use that format, please install `conda install -c conda-forge myst-parser`,
or `pip install jupytext[myst]`.

**Tip**: You can use the [myst-highlight] VS Code extension to provide better syntax highlighting for this format.

[myst-parser]: https://myst-parser.readthedocs.io
[myst-nb]: https://myst-nb.readthedocs.io
[block break]: https://myst-parser.readthedocs.io/en/latest/using/syntax.html#block-breaks
[myst-highlight]: https://marketplace.visualstudio.com/items?itemName=ExecutableBookProject.myst-highlight

## Notebooks as scripts

### The `light` format

The `light` format was created for this project. That format can read any script in one of these [languages](https://github.com/mwouts/jupytext/blob/master/jupytext/languages.py) as a Jupyter notebook, even scripts which were never prepared to become a notebook.

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
c.ContentsManager.default_cell_markers = "region,endregion"  # Use VS Code/PyCharm region folding delimiters
```
or
```python
c.ContentsManager.default_cell_markers = "{{{,}}}"           # Use Vim region folding delimiters
```
to your `.jupyter/jupyter_notebook_config.py` file.

See how our `World population.ipynb` notebook is [represented](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.lgt.py) in that format.

### The `nomarker` format

The `nomarker` format is a variation of the `light` format with no cell marker at all. Please note that this format does not provide round-trip consistency - code cells are split on code paragraphs. By default, the `nomarker` format still includes a YAML header - if you prefer to also remove the header, set `"notebook_metadata_filter": "-all"` in the jupytext section of your notebook metadata.

### The `percent` format

The `percent` format is a representation of Jupyter notebooks as scripts, in which all cells are explicitely delimited with a commented double percent sign `# %%`. The `percent` format is currently available for these [languages](https://github.com/mwouts/jupytext/blob/master/jupytext/languages.py).

The format was introduced by Spyder in 2013, and is now supported by many editors, including
- [Spyder IDE](https://docs.spyder-ide.org/editor.html#defining-code-cells),
- [Hydrogen](https://nteract.gitbooks.io/hydrogen/docs/Usage/NotebookFiles.html#notebook-export), a package for Atom,
- [VS
  Code](https://code.visualstudio.com/docs/python/jupyter-support#_jupyter-code-cells),
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
c.ContentsManager.default_cell_markers = '"""'
```
to your `.jupyter/jupyter_notebook_config.py` file.

See how our `World population.ipynb` notebook is [represented](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.pct.py) in the `percent` format.

### The `hydrogen` format

By default, [Jupyter magics](#magic-commands) are commented in the `percent` representation. If you run the percent scripts in Hydrogen, use the `hydrogen` format, a variant of the `percent` format that does not comment Jupyter magic commands.

### Sphinx-gallery scripts

Another popular notebook-like format for Python scripts is the Sphinx-gallery [format](https://sphinx-gallery.readthedocs.io/en/latest/tutorials/plot_notebook.html). Scripts that contain at least two lines with more than twenty hash signs are classified as Sphinx-Gallery notebooks by Jupytext.

Comments in Sphinx-Gallery scripts are formatted using reStructuredText rather than markdown. They can be converted to markdown for a nicer display in Jupyter by adding a `c.ContentsManager.sphinx_convert_rst2md = True` line to your Jupyter configuration file. Please note that this is a non-reversible transformation—use this only with Binder. Revert to the default value `sphinx_convert_rst2md = False` when you edit Sphinx-Gallery files with Jupytext.

Turn a GitHub repository containing Sphinx-Gallery scripts into a live notebook repository with [Binder](https://mybinder.org/) and Jupytext by adding only two files to the repo:
- `binder/requirements.txt`, a list of the required packages (including `jupytext`)
- `.jupyter/jupyter_notebook_config.py` with the following contents:
```python
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
c.ContentsManager.preferred_jupytext_formats_read = "py:sphinx"
c.ContentsManager.sphinx_convert_rst2md = True
```

Our sample notebook is also represented in `sphinx` format [here](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.spx.py).

## Jupytext format options

### Metadata filtering

All the Jupytext formats (except Sphinx Gallery scripts) store a selection of the notebook metadata in a YAML header at the top of the text file. By default, Jupytext only includes the `kernelspec` and `jupytext` metadata (the remaining notebook metadata are preserved in the `.ipynb` document when you use paired notebook). 

If you want to include more (or less) jupyter metadata here, add a `notebook_metadata_filter` option to the `jupytext` metadata.
The additional metadata will be added to the `jupyter:` section in the YAML header (or, at the root of the YAML header for the `md:pandoc` and `md:myst` formats).
The value for `notebook_metadata_filter` is a comma separated list of additional/excluded (negated) entries, with `all` a keyword that allows to exclude all entries. For instance, if you don't want to store any notebook metadata in the text file, use `notebook_metadata_filter: -all`. If you want to store the whole, unfiltered notebook metadata then use `notebook_metadata_filter: all`. And if you want the default, plus a few specific section, use e.g. `notebook_metadata_filter: section_one,section_two`.

Similarly, cell metadata can be filtered with the `cell_metadata_filter` option. To minimize the differences when a notebook is edited, Jupytext's default cell metadata filter does not include the `autoscroll`, `collapsed`, `scrolled`, `trusted` and `ExecuteTime` cell metadata in the text representation.

### Magic commands

Jupyter notebooks often include _magic commands_ like `%load_ext` or `%matplotlib inline`. These commands are Jupyter specific and cannot be executed by the classical interpreter. 

By default, magic commands are commented out in all the Jupytext formats, with the exception of the Markdown format (not meant to be executed) and the Hydrogen format. You can change this by setting a `comment_magics` option (`true` or `false`) in the Jupytext section.

### Active and inactive cells

Sometimes you want a specific cell to be executable only in the `.ipynb` files, or only in the `.py` or `.Rmd` representation. To this end Jupytext introduces the notion of _active_ cells.

Mark a code cell with an `"active": "ipynb"` metadata or with an `active-ipynb` tag if you want it to be commented out in the paired script.

Mark a raw cell with an `"active": "py"` metadata or with an `active-py` tag if you want it to be inactive in the notebook but active in the script.
