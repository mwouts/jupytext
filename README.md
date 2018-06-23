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

As the name states, R markdown (extension `.Rmd`) was designed in the R community. It is the format used by the RStudio IDE for notebooks. It actually support [many languages](https://yihui.name/knitr/demo/engines/). A few months back, the support for python significantly improved with the arrival of the [`reticulate`](https://github.com/rstudio/reticulate) package.

R markdown is almost identical to markdown export of Jupyter notebooks. For reference, Jupyter notebooks are exported to markdown using either
- _Download as Markdown (.md)_ in Jupyter's interface,
- or `nbconvert notebook.ipynb --to markdown`.

Major difference is that code chunks can be evaluated. While markdown's standard syntax start a python code paragraph with

    ```python
    
R markdown starts an active code chunks with

	```{python}

A smaller difference is the common presence of a YAML header, that describes the notebook title, author, and desired output (HTML, slides, PDF...).

Look at [nbrmd/tests/ioslides.Rmd](https://github.com/mwouts/nbrmd/blob/master/tests/ioslides.Rmd) for a sample R markdown file (that, actually, only includes python cells).


## How do I open R markdown notebooks in Jupyter?

The `nbrmd` package offers a `ContentsManager` for Jupyter that recognizes
 `.md` and `.Rmd` files as notebooks. To use it,
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

## Can I save my Jupyter notebook as both R markdown and ipynb ?

### Per-notebook configuration

The R markdown content manager includes a pre-save hook that will keep up-to date versions of your notebook
under the file extensions specified in the `nbrmd_formats` metadata. Edit the notebook metadata in Jupyter and
append a list for the desired format, like this:
```
{
  "kernelspec": {
    "name": "python3",
    (...)
  },
  "language_info": {
    (...)
  },
  "nbrmd_formats": [".ipynb", ".Rmd"]
}
```

Accepted formats are: `.ipynb`, `.Rmd` and `.md`.

### Global configuration

If you want every notebook to be saved as both `.Rmd` and `.ipynb` files, then change your jupyter config to
 ```python
c.NotebookApp.contents_manager_class = 'nbrmd.RmdFileContentsManager'
c.ContentsManager.pre_save_hook = 'nbrmd.update_rmd_and_ipynb'
```

If you prefer to update just one of `.Rmd` or `.ipynb` files, then change the above to
`nbrmd.update_rmd` or `nbrmd.update_ipynb` as the `pre_save_hook` (and yes, you're free to use the `pre_save_hook`
with the default `ContentsManager`).

:warning: Be careful not to open twice a notebook with two distinct extensions! You should _shutdown_ the notebooks
with the extension you are not currently editing (list your open notebooks with the _running_ tab in Jupyter).

## Recommendations for version control

I recommend that you only add the R markdown file to version control. When you integrate a change
on that file that was not done through your Jupyter editor, you should be careful to re-open the
`.Rmd` file, not the `.ipynb` one. 

## How do I use the converter?

The package also provides a `nbrmd` script that converts Jupyter notebooks to R markdown notebooks, and vice-versa.

Use it as:
```bash
nbrmd jupyter.ipynb      # this prints the Rmarkdown alternative
nbrmd jupyter.ipynb -i   # this creates a jupyter.Rmd file
nbrmd jupyter.Rmd   -i   # and this, a jupyter.ipynb file
```

## And if I convert twice?

Round trip conversion of R markdown is identity.  
Round trip conversion of Jupyter notebooks preserves the source.
Outputs are lost, however, like in any good [pre-commit hooks](https://gist.github.com/minrk/6176788).

