import jupytext


def test_incomplete_header(
    rmd="""---
title: Incomplete header

```{python}
1+1
```
""",
):
    nb = jupytext.reads(rmd, "Rmd")
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "---\ntitle: Incomplete header"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "1+1"


def test_code_in_markdown_block(
    rmd="""```{python}
a = 1
b = 2
a + b
```

```python
'''Code here goes to a Markdown cell'''


'''even if we have two blank lines above'''
```

```{bash}
ls -l
```
""",
):
    nb = jupytext.reads(rmd, "Rmd")
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "a = 1\nb = 2\na + b"
    assert nb.cells[1].cell_type == "markdown"
    assert (
        nb.cells[1].source
        == """```python
'''Code here goes to a Markdown cell'''


'''even if we have two blank lines above'''
```"""
    )
    assert nb.cells[2].cell_type == "code"
    assert nb.cells[2].source == "%%bash\nls -l"


def test_unterminated_header(
    rmd="""---
title: Unterminated header

```{python}
1+3
```

some text

```{r}
1+4
```

```{python not_terminated}
1+5
""",
):
    nb = jupytext.reads(rmd, "Rmd")
    assert len(nb.cells) == 5
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "---\ntitle: Unterminated header"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "1+3"
    assert nb.cells[2].cell_type == "markdown"
    assert nb.cells[2].source == "some text"
    assert nb.cells[3].cell_type == "code"
    assert nb.cells[3].source == "%%R\n1+4"
    assert nb.cells[4].cell_type == "code"
    assert nb.cells[4].metadata == {"name": "not_terminated"}
    assert nb.cells[4].source == "1+5"
