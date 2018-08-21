# Jupyter notebooks from/to R markdown, Python and R scripts

[![Pypi](https://img.shields.io/pypi/v/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Pypi](https://img.shields.io/pypi/l/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Build Status](https://travis-ci.com/mwouts/nbrmd.svg?branch=master)](https://travis-ci.com/mwouts/nbrmd)
[![codecov.io](https://codecov.io/github/mwouts/nbrmd/coverage.svg?branch=master)](https://codecov.io/github/mwouts/nbrmd?branch=master)
![pylint Score](https://mperlet.github.io/pybadge/badges/9.6.svg)
[![pyversions](https://img.shields.io/pypi/pyversions/nbrmd.svg)](https://pypi.python.org/pypi/nbrmd)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mwouts/nbrmd/master?filepath=demo)

This package offers a representation of Jupyter notebooks as Python scripts, R scripts, or [R markdown](https://rmarkdown.rstudio.com/) notebooks. 

These alternative representations allow to
- edit notebooks as scripts in your favorite editor or IDE, and refactor them
- extract executable scripts from your notebooks
- get meaningfull diffs for notebooks under version control, and easily merge contributions
- edit the same notebook in both Jupyter and Rstudio, for instance if you want to use RStudio's advanced rendering of notebooks to PDF, HTML or [HTML slides](https://rmarkdown.rstudio.com/ioslides_presentation_format.html).

Scripts and R markdown notebooks only store the source and metadata of the notebook, and work in pair with the original `.ipynb` file. Jupyter saves notebooks to either form. When such a notebook is loaded in Jupyter, inputs are taken from the script of R markdown form, and outputs are taken from the `.ipynb` file, if present.

## Can I have a demo?

Sure. Try our package on [binder](https://mybinder.org/v2/gh/mwouts/nbrmd/master?filepath=demo). Notice that every `.py`, `.R` and `.Rmd` file now opens as a Jupyter notebook. I suggest you open the matplotlib demo there (`filled_steps.py`), run it and save it, close notebook and reopen, to observe persistence of outputs. 

The other examples demo how to *edit* the script and reload the notebook (preserving the kernel variables), and how to edit in Jupyter an interactive ioslide presentation.

## How does the Python script look like?

Python [notebook](https://mybinder.org/v2/gh/mwouts/nbrmd/master?filepath=tests/python_notebook_sample.py) in Jupyter  | Python [script](https://github.com/mwouts/nbrmd/blob/master/tests/python_notebook_sample.py)
:--------------------------:|:-----------------------:
![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/python_notebook.png)   | ![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/python_source.png)

## How does R markdown look like?

Rmd notebook in jupyter     | Rmd notebook as text
:--------------------------:|:-----------------------:
![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/rmd_notebook.png)   | ![](https://raw.githubusercontent.com/mwouts/nbrmd/master/img/rmd_in_text_editor.png)

## Have you tested round-trip conversion?

Round trip conversion is safe! A few hundreds of tests help to guarantee this.
- Script to Jupyter notebook, to script again is identity. If you
associate a Jupyter kernel to your notebook, that information will go to
a yaml header at the top of your script.
- R markdown to Jupyter notebook, to R markdown again is identity. 
- Jupyter to script, and Jupyter again preserves source and metadata.
- Jupyter to R markdown, and Jupyter again preserves source and metadata.
In some occasions (consecutive blank lines in markdown cells), markdown cells may
be splitted into smaller ones.

## How do I activate text notebooks in Jupyter?

The `nbrmd` package offers a `ContentsManager` for Jupyter that recognizes
`.py`, `.R` and `.Rmd` files as notebooks. To use it,
- generate a jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`
- edit the config and include the below:
```python
c.NotebookApp.contents_manager_class = "nbrmd.RmdFileContentsManager"
c.ContentsManager.default_nbrmd_formats = "ipynb,py" # "ipynb,nb.py" # or "ipynb,Rmd"
```

Then, make sure you have the `nbrmd` package up-to-date, and re-start jupyter, i.e. run
```bash
pip install nbrmd --upgrade
jupyter notebook
```

With the above configuration, every Jupyter notebook will have a companion `.py` (`.nb.py`, or `.Rmd`) notebook. And every `.py` (`.nb.py`, or `.Rmd`) notebook will have a companion `.ipynb` notebook.


## Per notebook configuration

If you prefer that the companion notebook be generated only for selected notebooks,
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
  "nbrmd_formats": "ipynb,py"
}
```

Accepted formats should have these extensions: `ipynb`, `Rmd`, `py` and `R`.

In case you want both `py` and `Rmd`, please note that the
order matters: the first non-`ipynb` extension
is the one used as the reference source for notebook inputs when you open the `ipynb` file.

Learn more on the possible values for `nbrmd_formats` [here](https://github.com/mwouts/nbsrc/issues/5#issuecomment-414093471).

## Command line conversion

The package provides two `nbrmd` and `nbsrc` scripts that convert Jupyter notebooks to R markdown notebooks and scripts, and vice-versa.

Use them as:
```bash
nbrmd jupyter.ipynb         # this prints the Rmarkdown alternative
nbrmd jupyter.ipynb -i      # this creates a jupyter.Rmd file
nbrmd jupyter.Rmd   -i      # and this, a jupyter.ipynb file
nbrmd jupyter.Rmd   -i -p   # update the jupyter.ipynb file and preserve outputs that correspond to unchanged inputs

nbsrc jupyter.ipynb         # this prints the `.py` or `.R` alternative
nbsrc jupyter.ipynb -i      # this creates a jupyter.py or jupyter.R file
nbsrc jupyter.py    -i      # and this, a jupyter.ipynb file
nbsrc jupyter.py    -i -p   # update the jupyter.ipynb file and preserve outputs that correspond to unchanged inputs
```

Alternatively, the `nbrmd` package provides a few `nbconvert` rmarkdown exporters that you can use with
```bash
nbconvert jupyter.ipynb --to rmarkdown
nbconvert jupyter.ipynb --to pynotebook
nbconvert jupyter.ipynb --to rnotebook
```

## Usefull cell metadata

- Set `"active": "ipynb,py"` if you want that cell to be active only in the Jupyter notebook, and the Python script representation. Use `"active": "ipynb"` if you want that cell to be active only in Jupyter.
- Code cells that contain two consecutive blank lines use an explicit end-of-cell marker that appear as `"endofcell": "-"` in the python file.
- R markdown's cell options `echo` and `include` are mapped to the opposite of Jupyter cell metadata `hide_input` and `hide_output`

## Jupyter magics

Jupyter magics are escaped in the text representations so that scripts can actually be executed. Comment a magic with `#noescape` on the same line to avoid escaping. Non-standard magics can be escaped with `#escape`.