# From Jupyter notebooks from/to R markdown

[![Pypi](https://img.shields.io/pypi/v/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Pypi](https://img.shields.io/pypi/l/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Build Status](https://travis-ci.com/mwouts/nbrmd.svg?branch=master)](https://travis-ci.com/mwouts/nbrmd)
[![codecov.io](https://codecov.io/github/mwouts/nbrmd/coverage.svg?branch=master)](https://codecov.io/github/mwouts/nbrmd?branch=master)
![pylint Score](https://mperlet.github.io/pybadge/badges/9.6.svg)
[![pyversions](https://img.shields.io/pypi/pyversions/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mwouts/nbrmd/master?filepath=demo)

This package is an implementation of the standard
[R markdown](https://rmarkdown.rstudio.com/) notebook format for Jupyter.
R markdown notebooks are source only notebooks, and they
are great companion files for the standard `.ipynb` notebooks.

Use the `nbrmd` package if
- you prefer to have simple text files under version control
- if you want to use RStudio's advanced rendering of notebooks to PDF, HTML or [HTML slides](https://rmarkdown.rstudio.com/ioslides_presentation_format.html)
- or, you have a collection of markdown or R markdown notebooks and you want to open them in Jupyter.

Only the source of your notebook is represented in R markdown.
When a pair of `.Rmd`, ``.ipynb` notebooks with identical names are opened
in Jupyter, inputs
are taken from the `.Rmd` file, and outputs, when they match the input,
are taken from the `.ipynb` file. This allows you to edit the R markdown
version in your favorite text editor, and reload the notebook in Jupyter with the
convenience of preserving outputs when possible.

## Can I have a demo?

Sure. Try our package on [binder](https://mybinder.org/v2/gh/mwouts/nbrmd/master?filepath=demo)
and open our python-oriented R markdown notebook!

As you will see there, the package also offers opening and saving
notebooks as python or R scripts. Go to
[nbsrc](https://github.com/mwouts/nbsrc) for a specific documentation on this.

## How does R markdown look like?

Rmd notebook in jupyter     | Rmd notebook as text
:--------------------------:|:-----------------------:
![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/rmd_notebook.png)   | ![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/rmd_in_text_editor.png)

## Have you tested round-trip conversion?

Round trip conversion is safe! And backed by hundreds of tests.
- R markdown to Jupyter notebook, to R markdown again is identity. If you
associate a Jupyter kernel to your notebook, that information will go to
the yaml header of your notebook.
- Jupyter to R markdown, and Jupyter again preserves source and metadata.
In some occasions (consecutive blank lines in
markdown cells), cells may be splitted into smaller ones.

## How do I activate R markdown notebooks in Jupyter?

The `nbrmd` package offers a `ContentsManager` for Jupyter that recognizes
`.Rmd` files as notebooks. To use it,
- generate a jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`
- edit the config and include the below:
```python
c.NotebookApp.contents_manager_class = 'nbrmd.RmdFileContentsManager'
c.ContentsManager.default_nbrmd_formats = 'ipynb,Rmd'
```

Then, make sure you have the `nbrmd` package up-to-date, and re-start jupyter, i.e. run
```bash
pip install nbrmd --upgrade
jupyter notebook
```

With the above configuration, every Jupyter notebook will have a companion `.Rmd` notebook.
And every `.Rmd` notebook will have a companion `.ipynb` notebook.

If you prefer the `.ipynb` notebook not to be created by Jupyter when a `.Rmd`
notebook is edited, set
```
c.ContentsManager.default_nbrmd_formats = ''
```
(as the default value is `ipynb`). Outputs for R markdown notebooks, however,
will not be saved any more.

## Per notebook configuration

If you prefer that the companion R markdown notebook be generated only for
 selected notebooks,
remove the `c.ContentsManager.default_nbrmd_formats` line from Jupyter's
configuration, and instead edit the notebook metadata as follows:
```
{
  "kernelspec": {
    "name": "python3",
    (...)
  },
  "language_info": {
    (...)
  },
  "nbrmd_formats": "ipynb,Rmd"
}
```

Accepted formats are: `ipynb`, `Rmd`, `py` and `R`.

In case you want both `py` and `Rmd`, please note that the
order matters: the first non-`ipynb` extension
is the one used as the reference source for notebook inputs.

## Command line conversion

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

