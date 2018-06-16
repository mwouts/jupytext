# From Jupyter notebooks to R markdown, and back

This is a converter that allows to create Jupyter notebooks from R markdown notebooks, and the opposite.

You will be interested in this if
- you prefer a simple markdown format over Jupyter's json notebook (especially you want to only version the input of your notebooks, and be able to merge easily different versions of the notebooks).
- you want to use RStudio's advanced rendering of notebooks (like: chunk options for activating/deactivating code or input, choosing figure size, etc), or even the well documented [slide format](https://rmarkdown.rstudio.com/ioslides_presentation_format.html)
- or, you have a collection of R notebooks and you want to open them in Jupyter

## What is R markdown?

This is markdown, extended with code chunks. Extension is `.Rmd`, and as the name states it contains most often only R code. But it can actually welcome [many languages](https://yihui.name/knitr/demo/engines/), including python, obviously. 

The R markdown files are made of
- a YAML header, that describes the notebook title, author, and desired output (HTML, slides, PDF...)
- markdown text
- and code chunks, that unlike classical markdown code, will be evaluated.

Look at [nbrmd/tests/ioslides.Rmd](https://github.com/mwouts/nbrmd/blob/master/tests/ioslides.Rmd) for a sample R markdown file (that, actually, only includes python cells).

## How do I use the converter

Install the package with
```python
pip install nbrmd
```
   
This provides a `nbrmd` script that converts Jupyter notebooks to R markdown notebooks, and vice-versa. Double conversion of R markdown is identity, however double conversion of Jupyter notebooks only preserves the source (i.e. metadata and outputs are lost).

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

