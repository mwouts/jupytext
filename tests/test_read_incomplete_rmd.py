import nbrmd


def test_incomplete_header(rmd="""---
title: Incomplete header

```{python}
1+1
```
"""):
    nb = nbrmd.reads(rmd)
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Incomplete header'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == '1+1'


def test_incomplete_code_chunk(rmd="""```{python}
a = 1
b = 2
a + b
```

```

```{bash}
ls -l
```
"""):
    nb = nbrmd.reads(rmd)
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == 'code'
    assert nb.cells[0].source == 'a = 1\nb = 2\na + b'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == '```'
    assert nb.cells[2].cell_type == 'code'
    assert nb.cells[2].source == '%%bash\nls -l'


def test_unterminated_header_and_unstarted_chunk(rmd="""---
title: Unterminated header

```{python}
1+3
```

```

```{r}
1+4
```

```{python not_terminated}
1+5
"""):
    nb = nbrmd.reads(rmd)
    assert len(nb.cells) == 5
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Unterminated header'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == '1+3'
    assert nb.cells[2].cell_type == 'markdown'
    assert nb.cells[2].source == '```'
    assert nb.cells[3].cell_type == 'code'
    assert nb.cells[3].source == '%%R\n1+4'
    assert nb.cells[4].cell_type == 'code'
    assert nb.cells[4].metadata == {'name': 'not_terminated'}
    assert nb.cells[4].source == '1+5'
