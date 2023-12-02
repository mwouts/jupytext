import re
from time import sleep

import nbformat
import pytest
from nbformat.v4.nbbase import (
    new_code_cell,
    new_markdown_cell,
    new_notebook,
    new_raw_cell,
)

import jupytext
from jupytext.cli import jupytext as jupytext_cli
from jupytext.compare import compare, compare_cells, compare_notebooks


def test_read_mostly_py_rmd_file(
    rmd="""---
title: Simple file
---

```{python, echo=TRUE}
import numpy as np
x = np.arange(0, 2*math.pi, eps)
```

```{python, echo=TRUE}
x = np.arange(0,1,eps)
y = np.abs(x)-.5
```

```{r}
ls()
```

```{r, results="asis", magic_args="-i x"}
cat(stringi::stri_rand_lipsum(3), sep='\n\n')
```
""",
):
    nb = jupytext.reads(rmd, "Rmd")
    compare_cells(
        nb.cells,
        [
            new_raw_cell("---\ntitle: Simple file\n---"),
            new_code_cell(
                "import numpy as np\n" "x = np.arange(0, 2*math.pi, eps)",
                metadata={"echo": True},
            ),
            new_code_cell(
                "x = np.arange(0,1,eps)\ny = np.abs(x)-.5", metadata={"echo": True}
            ),
            new_code_cell("%%R\nls()"),
            new_code_cell(
                "%%R -i x\ncat(stringi::" "stri_rand_lipsum(3), sep='\n\n')",
                metadata={"results": "asis"},
            ),
        ],
        compare_ids=False,
    )

    rmd2 = jupytext.writes(nb, "Rmd")
    rmd2 = re.sub(r"```{r ", "```{r, ", rmd2)
    rmd2 = re.sub(r"```{python ", "```{python, ", rmd2)
    compare(rmd2, rmd)


def test_markdown_cell_with_code_works(
    nb=new_notebook(
        cells=[
            new_markdown_cell(
                """```python
1 + 1
```"""
            )
        ]
    ),
):
    text = jupytext.writes(nb, "Rmd")
    nb2 = jupytext.reads(text, "Rmd")
    compare_notebooks(nb2, nb)


def test_two_markdown_cell_with_code_works(
    nb=new_notebook(
        cells=[
            new_markdown_cell(
                """```python
1 + 1
```"""
            ),
            new_markdown_cell(
                """```python
2 + 2
```"""
            ),
        ]
    )
):
    text = jupytext.writes(nb, "Rmd")
    nb2 = jupytext.reads(text, "Rmd")
    compare_notebooks(nb2, nb)


def test_tags_in_rmd(
    rmd="""---
jupyter:
  jupytext:
    text_representation:
      extension: .Rmd
      format_name: rmarkdown
      format_version: '1.1'
      jupytext_version: 1.2.3
---

```{python tags=c("parameters")}
p = 1
```
""",
    nb=new_notebook(cells=[new_code_cell("p = 1", metadata={"tags": ["parameters"]})]),
):
    nb2 = jupytext.reads(rmd, "Rmd")
    compare_notebooks(nb2, nb)


def round_trip_cell_metadata(cell_metadata):
    nb = new_notebook(
        metadata={"jupytext": {"main_language": "python"}},
        cells=[new_code_cell("1 + 1", metadata=cell_metadata)],
    )
    text = jupytext.writes(nb, "Rmd")
    nb2 = jupytext.reads(text, "Rmd")
    compare_notebooks(nb2, nb)


def test_comma_in_metadata(cell_metadata={"a": "b, c"}):
    round_trip_cell_metadata(cell_metadata)


def test_dict_in_metadata(cell_metadata={"a": {"b": "c"}}):
    round_trip_cell_metadata(cell_metadata)


def test_list_in_metadata(cell_metadata={"d": ["e"]}):
    round_trip_cell_metadata(cell_metadata)


@pytest.mark.parametrize("root_level_metadata_as_raw_cell", [True, False])
def test_root_level_metadata_as_raw_cell(
    tmpdir,
    root_level_metadata_as_raw_cell,
    rmd="""---
author: R Markdown document author
title: R Markdown notebook title
---

```{r}
1 + 1
```
""",
):
    nb_file = tmpdir.join("notebook.ipynb")
    rmd_file = tmpdir.join("notebook.Rmd")
    cfg_file = tmpdir.join("jupytext.toml")

    cfg_file.write(
        "root_level_metadata_as_raw_cell = {}".format(
            "true" if root_level_metadata_as_raw_cell else "false"
        )
    )
    rmd_file.write(rmd)

    jupytext_cli([str(rmd_file), "--to", "ipynb"])

    nb = nbformat.read(str(nb_file), as_version=4)

    if root_level_metadata_as_raw_cell:
        compare_cells(
            nb.cells,
            [
                new_raw_cell(
                    """---
author: R Markdown document author
title: R Markdown notebook title
---"""
                ),
                new_code_cell("1 + 1"),
            ],
            compare_ids=False,
        )
    else:
        compare_cells(nb.cells, [new_code_cell("1 + 1")], compare_ids=False)
        assert nb.metadata["jupytext"]["root_level_metadata"] == {
            "title": "R Markdown notebook title",
            "author": "R Markdown document author",
        }

    # Writing back to Rmd should preserve the original document
    jupytext_cli([str(nb_file), "--to", "Rmd"])
    compare(rmd_file.read(), rmd)


def test_pair_rmd_file_with_cell_tags_and_options(
    tmpdir, cwd_tmpdir, no_jupytext_version_number
):
    rmd = """```{r plot_1, dpi=72}
plot(3:30)
```
"""
    rmd_file = tmpdir.join("test.Rmd")
    rmd_file.write(rmd)

    # Pair Rmd with ipynb
    jupytext_cli(["--set-formats", "ipynb,Rmd", "test.Rmd"])

    # Wait so that ipynb will be more recent
    sleep(0.2)

    # Modify the ipynb file
    nb_file = tmpdir.join("test.ipynb")
    nb = nbformat.read(nb_file, as_version=4)
    nb.cells[0].source = "plot(4:40)"
    nb_file.write(nbformat.writes(nb))

    # Sync the two files
    jupytext_cli(["--sync", "test.Rmd"])

    # Remove the header
    rmd2 = rmd_file.read()
    rmd2 = rmd2.rsplit("---\n\n")[1]

    # The new code chunk has the new code, and options are still there
    compare(rmd2, rmd.replace("3", "4"))


def test_apostrophe_in_parameter_1079(
    rmd="""```{python some-name, param="Problem's"}
a = 1
```
""",
):
    nb = jupytext.reads(rmd, fmt="Rmd")
    rmd2 = jupytext.writes(nb, fmt="Rmd")
    compare(rmd2, rmd)
    nb2 = jupytext.reads(rmd, fmt="Rmd")
    compare_notebooks(nb2, nb)


@pytest.mark.parametrize("line", [" #'''", "a = 2  #'''"])
def test_commented_triple_quote_1060(line):
    rmd = f"""```{{python}}
{line}
```

```{{python}}
# Another cell
```
"""
    nb = jupytext.reads(rmd, fmt="Rmd")
    assert nb.cells[0].source == line

    rmd2 = jupytext.writes(nb, fmt="Rmd")
    compare(rmd2, rmd)
    nb2 = jupytext.reads(rmd, fmt="Rmd")
    compare_notebooks(nb2, nb)


def test_bibliography_in_rmd(
    rmd="""Issue #1161

The bibliography section below should not
become a code cell

```{bibliography}
```

```{r}
6
```
""",
):
    nb = jupytext.reads(rmd, fmt="Rmd")
    assert len(nb.cells) == 2, nb.cells
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "6"
    rmd2 = jupytext.writes(nb, fmt="Rmd")
    compare(rmd2, rmd)
