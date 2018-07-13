# From Jupyter notebooks to R markdown, and back

[![Pypi](https://img.shields.io/pypi/v/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Pypi](https://img.shields.io/pypi/l/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Build Status](https://travis-ci.com/mwouts/nbrmd.svg?branch=master)](https://travis-ci.com/mwouts/nbrmd)
[![codecov.io](https://codecov.io/github/mwouts/nbrmd/coverage.svg?branch=master)](https://codecov.io/github/mwouts/nbrmd?branch=master)
[![pyversions](https://img.shields.io/pypi/pyversions/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)


This is a utility that allows to open and run R markdown notebooks in Jupyter, and save Jupyter notebooks as R markdown.

You will be interested in this if
- you want to version your notebooks and occasionally have to merge versions
- you want to use RStudio's advanced rendering of notebooks to PDF, HTML or [HTML slides](https://rmarkdown.rstudio.com/ioslides_presentation_format.html)
- or, you have a collection of markdown or R markdown notebooks and you want to open them in Jupyter

## What is R markdown?

R markdown (extension `.Rmd`) is a *source only* format for notebooks.
As the name states, R markdown was designed in the R community, and is
the reference [notebook format](https://rmarkdown.rstudio.com/) there.
The format actually supports [many languages](https://yihui
.name/knitr/demo/engines/).

R markdown is almost like plain markdown. There are only two differences:
- R markdown has a specific syntax for active code cells, that start with

	```{python}

These active cells may optionally contain cell options.
- a YAML header, that describes the notebook title, author, and desired
output (HTML, slides, PDF...).

Look at [nbrmd/tests/ioslides.Rmd](https://github.com/mwouts/nbrmd/blob/master/tests/ioslides.Rmd) for a sample R markdown file (that, actually, only includes python cells).

## Why R markdown and not filtered `.ipynb` under version control?

The common practice for having Jupyter notebooks under version control is
to remove outputs with a pre-commit hook. That works well and this will
indeed get you a clean commit history.

However, you may run into trouble when you try to *merge* two `.ipynb`
notebooks in a simple text editor. Merging text notebooks, like the `.Rmd`
ones that this package provides, is much simpler.

## How do I open R markdown notebooks in Jupyter?

The `nbrmd` package offers a `ContentsManager` for Jupyter that recognizes `
.Rmd` files as notebooks. To use it,
- generate a jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`
- edit the config and include this:
```python
c.NotebookApp.contents_manager_class = 'nbrmd.RmdFileContentsManager'
```

Then, make sure you have the `nbrmd` package installed, and re-start jupyter, i.e. run
```bash
pip install nbrmd
jupyter notebook
```

Now you can open your `.Rmd` files as notebooks in Jupyter,
and save your jupyter notebooks in R markdown format (see below).

Rmd notebook in jupyter     | Rmd notebook as text
:--------------------------:|:-----------------------:
![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/rmd_notebook.png)   | ![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/rmd_in_text_editor.png)


## Can I save my Jupyter notebook as both R markdown and ipynb?

Yes. That's even the recommended setting for the notebooks you want to
set under *version control*.

You need to choose whever to configure this per notebook, or globally.

### Per-notebook configuration

The R markdown content manager includes a pre-save hook that will keep up-to date versions of your notebook
under the file extensions specified in the `nbrmd_formats` metadata. Edit the notebook metadata in Jupyter and
append a list for the desired formats, like this:
```
{
  "kernelspec": {
    "name": "python3",
    (...)
  },
  "language_info": {
    (...)
  },
  "nbrmd_formats": [".ipynb", ".Rmd"],
  "nbrmd_sourceonly_format": ".Rmd"
}
```

### Global configuration

If you want every notebook to be saved as both `.Rmd` and `.ipynb` files, then change your jupyter config to
```python
c.NotebookApp.contents_manager_class = 'nbrmd.RmdFileContentsManager'
c.ContentsManager.default_nbrmd_formats = ['.ipynb', '.Rmd']
```

If you prefer to update just `.Rmd`, change the above accordingly (you will
still be able to open regular `.ipynb` notebooks).

## Recommendations for version control

I recommend that you set `nbrmd_formats` to `[".ipynb", ".Rmd"]`, either
in the default configuration, or in the notebook metadata (see above).

When you save your notebook, two files are generated,
with `.Rmd` and `.ipynb` extensions. Then, when you reopen
either one or the other,
- cell input are taken from the _source only_ format, here `.Rmd` file
- cell outputs are taken from `.ipynb` file.

This way, you can set the `.Rmd` file under version control, and still have
the commodity of having cell output stored in the ` .ipynb` file. When
the `.Rmd` file is updated outside of Jupyter, then you simply reload the
notebook, and benefit of the updates.

:warning: Be careful not to open twice a notebook with two distinct
extensions! You should _shutdown_ the notebooks with the extension you are not
currently editing (list your open notebooks with the _running_ tab in Jupyter).

## How do I use the converter?

The package also provides a `nbrmd` script that converts Jupyter notebooks to R markdown notebooks, and vice-versa.

Use it as:
```bash
nbrmd jupyter.ipynb         # this prints the Rmarkdown alternative
nbrmd jupyter.ipynb -i      # this creates a jupyter.Rmd file
nbrmd jupyter.Rmd   -i      # and this, a jupyter.ipynb file
nbrmd jupyter.Rmd   -i -p   # update the jupyter.ipynb file and preserve outputs that correspond to unchanged inputs
```

Alternatively, the `nbrmd` package provides a `nbconvert` rmarkdown exporter that you can use with
```bash
nbconvert jupyter.ipynb --to rmarkdown
```

## And if I convert twice?

Round trip conversion of R markdown is identity.  
Round trip conversion of Jupyter notebooks preserves the source, not outputs.

