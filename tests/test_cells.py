from nbrmd.cells import text_to_cell


def test_text_to_code_cell():
    text = """```{python}
1+2+3
```

"""
    lines = text.splitlines()
    cell, pos = text_to_cell(lines)

    assert cell.cell_type == 'code'
    assert cell.source == '1+2+3'
    assert cell.metadata == {'language': 'python'}
    assert lines[pos:] == []


def test_text_to_code_cell_empty_code():
    text = """```{python}
```

"""
    lines = text.splitlines()
    cell, pos = text_to_cell(lines)

    assert cell.cell_type == 'code'
    assert cell.source == ''
    assert cell.metadata == {'language': 'python'}
    assert lines[pos:] == []


def test_text_to_code_cell_empty_code_no_blank_line():
    text = """```{python}
```
"""
    lines = text.splitlines()
    cell, pos = text_to_cell(lines)

    assert cell.cell_type == 'code'
    assert cell.source == ''
    assert cell.metadata == {'language': 'python', 'noskipline': True}
    assert lines[pos:] == []


def test_text_to_markdown_cell():
    text = """This is
a markdown cell

```{python}
1+2+3
```

"""
    lines = text.splitlines()
    cell, pos = text_to_cell(lines)

    assert cell.cell_type == 'markdown'
    assert cell.source == 'This is\na markdown cell'
    assert cell.metadata == {}
    assert pos == 3


def test_text_to_markdown_no_blank_line():
    text = """This is
a markdown cell
```{python}
1+2+3
```

"""
    lines = text.splitlines()
    cell, pos = text_to_cell(lines)

    assert cell.cell_type == 'markdown'
    assert cell.source == 'This is\na markdown cell'
    assert cell.metadata == {'noskipline': True}
    assert pos == 2


def test_text_to_markdown_two_blank_line():
    text = """

```{python}
1+2+3
```

"""
    lines = text.splitlines()
    cell, pos = text_to_cell(lines)

    assert cell.cell_type == 'markdown'
    assert cell.source == ''
    assert cell.metadata == {}
    assert pos == 2


def test_text_to_markdown_one_blank_line():
    text = """
```{python}
1+2+3
```

"""
    lines = text.splitlines()
    cell, pos = text_to_cell(lines)

    assert cell.cell_type == 'markdown'
    assert cell.source == ''
    assert cell.metadata == {'noskipline': True}
    assert pos == 1
