# From Jupyter notebooks to R markdown, and back

This is a converter that creates Jupyter notebooks from R markdown notebooks, and the opposite.

You will be interested in this if
- you prefer a simple markdown format over Jupyter's json notebook (especially you want to only version the input of your notebooks, and be able to merge easily different versions of the notebooks).
- you want to use RStudio's advanced rendering of notebooks (like: chunk options for activating/deactivating code or input, choosing figure size, etc), or even the well documented [slide format](https://rmarkdown.rstudio.com/ioslides_presentation_format.html)
- or, you have a collection of R notebooks and you want to open them in Jupyter

## What is R markdown?

As the name states, R markdown (extension `.Rmd`) was designed in the R community. It is the format used by the RStudio IDE for notebooks. It actually support [many languages](https://yihui.name/knitr/demo/engines/). A few months back, the support for python significantly improved with the arrival of the [`reticulate`](https://github.com/rstudio/reticulate) package.

R markdown is almost identical to markdown export of Jupyter notebooks. For reference, Jupyter notebooks are exported to markdown using either
- _Download as Markdown (.md)_ in Jupyter's interface,
- or `nbconvert notebook.ipynb --to markdown`.

First difference is that code chunks can be evaluated. While markdown's standard syntax for a python code paragraph is

    ```python
    1+1
    ```
    
R markdown will also have code chunks like

    ```{python}
    1+1
    ```

with this syntax meaning that the code above should be _evaluated_.

Second difference is the common presence of a YAML header, that describes the notebook title, author, and desired output (HTML, slides, PDF...).

Look at [nbrmd/tests/ioslides.Rmd](https://github.com/mwouts/nbrmd/blob/master/tests/ioslides.Rmd) for a sample R markdown file (that, actually, only includes python cells).

## How do I use the converter?

Install the package with
```python
pip install nbrmd
```
  
This provides a `nbrmd` script that converts Jupyter notebooks to R markdown notebooks, and vice-versa.

Use it as:
```bash
nbrmd jupyter.ipynb    # this creates a jupyter.Rmd file
nbrmd jupyter.Rmd      # and this, a jupyter.ipynb file
```

## And if I convert twice?

Double conversion of R markdown is identity.  
Double conversion of Jupyter notebooks preserves the source, but metadata and outputs are lost, like in most [pre-commit hooks](https://gist.github.com/minrk/6176788).

## Can I save my Jupyter notebook under this format?

The `nbrmd` package offers a `pre_save_hook` for Jupyter notebook server, that will, in addition to your Jupyter notebook, maintain an up-to-date R markdown version. To use it,
- generate a jupyter config, if you don't have one yet, with `jupyter notebook --generate-config`
- edit the config and include this:
```python
from nbrmd import pre_save_hook
c.ContentsManager.pre_save_hook = pre_save_hook
```    

Please note that, however, if you edit the `.Rmd` file, the `.ipynb` will not be updated, unless you re-generate it with:
```bash
nbrmd notebook.Rmd
```

