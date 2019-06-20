# Supported formats

Jupytext supports conversion between the `.ipynb` format and many different formats. This page describes
each format, as well as some considerations for each.

## Markdown and R Markdown

Save Jupyter notebooks as [Markdown](https://daringfireball.net/projects/markdown/syntax) documents and edit them in one of the many editors with good Markdown support.

[R Markdown](https://rmarkdown.rstudio.com/authoring_quick_tour.html) is [RStudio](https://www.rstudio.com/)'s format for notebooks, with support for R, Python, and many [other languages](https://bookdown.org/yihui/rmarkdown/language-engines.html).


Jupytext's implementation for Jupyter notebooks as [Markdown](https://daringfireball.net/projects/markdown/syntax) or [R Markdown](https://rmarkdown.rstudio.com/authoring_quick_tour.html) documents is as follows:
- The notebook metadata (Jupyter kernel, etc) goes to a YAML header
- Code and raw cells are encoded as Markdown code blocks with triple backticks. In a Python notebook, a code cell starts with ` ```python` and ends with ` ``` `. Cell metadata are found after the language information, with a `key=value` syntax, where `value` is encoded in JSON format (Markdown) or R format (R Markdown). R Markdown [code cell options](https://yihui.name/knitr/options/) are mapped to the corresponding Jupyter cell metadata options, when available.
- Markdown cells are inserted verbatim and separated with two blank lines. When required (cells with metadata, cells that contain two blank lines or code blocks), Jupytext protects the cell boundary with HTML comments: `<!-- #region -->` and `<!-- #endregion -->`. Cells with explicit boundaries are [foldable](https://code.visualstudio.com/docs/editor/codebasics#_folding) in vscode, and can accept both a title and/or metadata in JSON format: `<!-- #region This is the title for my protected cell {"key": "value"}-->`.

See how our `World population.ipynb` notebook in the [demo folder](https://github.com/mwouts/jupytext/tree/master/demo) is represented in [Markdown](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.md#) or [R Markdown](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.Rmd).

When you open a plain Markdown file in Jupytext, the Markdown text is rendered in Markdown cells. Cells breaks occur when the text contains two consecutive blank lines (or code cells). If you want to also split cells on Markdown headers, so that headers prefixed by one blank line appear at the top of a new cell, use the `split_at_heading` option. Set the option either on the command line, or by adding `"split_at_heading": true` to the jupytext section in the notebook metadata, or on Jupytext's content manager:

```python
c.ContentsManager.split_at_heading = True
```

## Pandoc's Markdown

Pandoc, the _Universal document converter_,  can now read and write Jupyter notebooks - see [Pandoc's documentation](https://pandoc.org/MANUAL.html#creating-jupyter-notebooks-with-pandoc).

Pandoc's Markdown format is available in Jupytext as `md:pandoc`. This requires `pandoc` in version 2.7.2 or above - please check Pandoc's version number with `pandoc -v` before running either `jupytext` command line, or before you start your Jupyter notebook or Lab server. Note that you can get the latest version of `pandoc` in a conda environment with
```
conda install pandoc -c conda-forge
```

Pandoc's format uses Pandoc divs (`:::`) as explicit cell markers. See how our `World population.ipynb` notebook is [represented](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.pandoc.md#) in that format. Please also note that `pandoc`, while preserving the HTML rendering, may reformat the text in some of the Markdown cells. If that is an issue for you, please wait until [jgm/pandoc#5408](https://github.com/jgm/pandoc/issues/5408) gets implemented.

Jupytext currently strips the output cells before calling `pandoc`. As for the other formats, outputs cells can be preserved in paired notebooks. In the case of the pandoc format, paired notebooks are available with the metadata `"jupytext": {"formats": "md:pandoc,ipynb"}`.

## The `light` format for notebooks as scripts

The `light` format was created for this project. It is the default format for scripts. That format can read any script as a Jupyter notebook, even scripts which were never prepared to become a notebook. When a notebook is written as a script using this format, only a few cells markers are introduced—none if possible.

The `light` format has:
- A (commented) YAML header, that contains the notebook metadata.
- Markdown cells are commented, and separated from other cells with a blank line.
- Code cells are exported verbatim (except for Jupyter magics, which are commented), and separated with blank lines. Code cells are reconstructed from consistent Python paragraphs (no function, class or multiline comment will be broken).
- Cells that contain more than one Python paragraphs need an explicit start-of-cell delimiter that is, by default, `# +` (`// +` in C++, etc). Cells that have explicit metadata have a cell header `# + {JSON}` where the metadata is represented, in JSON format. The default end of cell delimiter is `# -`, and is omitted when followed by another explicit start of cell marker.

The `light` format is available for these [languages](https://github.com/mwouts/jupytext/blob/master/jupytext/languages.py). Open our sample notebook in the `light` format [here](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.lgt.py).

A variation of the `light` format is the `bare` format, with no cell marker at all. Please note that this format will split your code cells on code paragraphs. By default, this format still includes a YAML header - if you prefer to also remove the header, set `"notebook_metadata_filter": "-all"` in the jupytext section of your notebook metadata.

The `light` format can use custom cell markers instead of `# +` or `# -`. If you prefer to mark cells with VScode/PyCharm (resp. Vim) folding markers, set `"cell_markers": "region,endregion"` (resp. `"{{{,}}}"`) in the jupytext section of the notebook metadata. If you want to configure this as a global default, add either
```python
c.ContentsManager.default_cell_markers = "region,endregion"  # Use VScode/PyCharm region folding delimiters
```
or
```python
c.ContentsManager.default_cell_markers = "{{{,}}}"           # Use Vim region folding delimiters
```
to your `.jupyter/jupyter_notebook_config.py` file.


## The `percent` format

The `percent` format is a representation of Jupyter notebooks as scripts, in which cells are delimited with a commented double percent sign `# %%`. The format was introduced by Spyder five years ago, and is now supported by many editors, including
- [Spyder IDE](https://docs.spyder-ide.org/editor.html#defining-code-cells),
- [Hydrogen](https://atom.io/packages/hydrogen), a package for Atom,
- [VS Code](https://code.visualstudio.com/) with the [vscodeJupyter](https://marketplace.visualstudio.com/items?itemName=donjayamanne.jupyter) extension,
- [Python Tools for Visual Studio](https://github.com/Microsoft/PTVS),
- and [PyCharm Professional](https://www.jetbrains.com/pycharm/).

Our implementation of the `percent` format is compatible with the original specifications by Spyder. We extended the format to allow markdown cells and cell metadata. Cell headers have the following structure:
```python
# %% Optional text [cell type] {optional JSON metadata}
```
where cell type is either omitted (code cells), or `[markdown]` or  `[raw]`. The content of markdown and raw cells is commented out in the resulting script.

Percent scripts created by Jupytext have a header with an explicit format information. The format of scripts with no header is inferred automatically: scripts with at least one `# %%` cell are identified as `percent` scripts. Scripts with at least one double percent cell, and an uncommented Jupyter magic command, are identified as `hydrogen` scripts.

The `percent` format is available for these [languages](https://github.com/mwouts/jupytext/blob/master/jupytext/languages.py). Open our sample notebook in the `percent` format [here](https://github.com/mwouts/jupytext/blob/master/demo/World%20population.pct.py).

If the `percent` format is your favorite one, add the following to your `.jupyter/jupyter_notebook_config.py` file:
```python
c.ContentsManager.preferred_jupytext_formats_save = "py:percent" # or "auto:percent"
```
Then, Jupytext's content manager will understand `"jupytext": {"formats": "ipynb,py"},` as an instruction to create the paired Python script in the `percent` format.

By default, Jupyter magics are commented in the `percent` representation. If you run the percent scripts in Hydrogen, use instead the `hydrogen` format, a variant of the `percent` format that does not comment Jupyter magic commands.

## Sphinx-gallery scripts

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

## R knitr::spin scripts

The `spin` format is specific to R scripts. These scripts can be compiled into reports using either `knitr::spin` or [RStudio](https://rmarkdown.rstudio.com/articles_report_from_r_script.html). The implementation of the format is as follows:
- Jupyter metadata are in YAML format, in a `#' `-commented header.
- Markdown cells are commented with `#' `.
- Code cells are exported verbatim. Cell metadata are signalled with `#+`. Cells end with a blank line, an explicit start of cell marker, or a markdown cell.