import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

import jupytext
from jupytext.compare import compare, compare_notebooks


@pytest.mark.requires_quarto
def test_qmd_to_ipynb(
    qmd="""Some text

```{python}
1 + 1
```
""",
    nb=new_notebook(
        cells=[
            new_markdown_cell("Some text"),
            new_code_cell("1 + 1"),
        ],
        metadata={
            "kernelspec": {
                "display_name": "python_kernel",
                "language": "python",
                "name": "python_kernel",
            }
        },
    ),
):
    nb2 = jupytext.reads(qmd, "qmd")
    compare_notebooks(nb2, nb)

    # after a round trip we do get a yaml header.
    # here we remove it to make the comparison
    qmd2 = jupytext.writes(nb, "qmd")
    qmd2_without_header = qmd2.rsplit("---\n\n", 1)[1]
    compare(qmd2_without_header, qmd)
