import pytest

import jupytext
from jupytext.compare import compare, compare_notebooks


@pytest.mark.parametrize(
    "md,rmd",
    [
        ('tags=["remove_cell"]', "include=FALSE"),
        ('tags=["remove_output"]', "results='hide'"),
        ('tags=["remove_output"]', 'results="hide"'),
        ('tags=["remove_input"]', "echo=FALSE"),
    ],
)
def test_jupyter_book_options_to_rmarkdown(md, rmd):
    """By default, Jupyter Book tags are mapped to R Markdown options, and vice versa #337"""
    md = (
        "```python "
        + md
        + """
1 + 1
```
"""
    )

    rmd = (
        "```{python "
        + rmd
        + """}
1 + 1
```
"""
    )

    nb_md = jupytext.reads(md, "md")
    nb_rmd = jupytext.reads(rmd, "Rmd")
    compare_notebooks(nb_rmd, nb_md)

    md2 = jupytext.writes(nb_rmd, "md")
    compare(md2, md)

    rmd = rmd.replace('"hide"', "'hide'")
    rmd2 = jupytext.writes(nb_md, "Rmd")
    compare(rmd2, rmd)


@pytest.mark.parametrize(
    "md,rmd",
    [
        ("hide_input=true hide_output=true", "include=FALSE"),
        ("hide_output=true", "results='hide'"),
        ("hide_output=true", 'results="hide"'),
        ("hide_input=true", "echo=FALSE"),
    ],
)
def test_runtools_options_to_rmarkdown(md, rmd):
    """Options set by the runtools extension are mapped to the corresponding R Markdown options
    https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/runtools/readme.html
    """
    md = (
        "```python "
        + md
        + """
1 + 1
```
"""
    )

    rmd = (
        "```{python "
        + rmd
        + """}
1 + 1
```
"""
    )

    nb_md = jupytext.reads(md, "md")
    nb_rmd = jupytext.reads(rmd, fmt={"extension": ".Rmd", "use_runtools": True})
    compare_notebooks(nb_rmd, nb_md)

    md2 = jupytext.writes(nb_rmd, "md")
    compare(md2, md)

    rmd = rmd.replace('"hide"', "'hide'")
    rmd2 = jupytext.writes(nb_md, "Rmd")
    compare(rmd2, rmd)
