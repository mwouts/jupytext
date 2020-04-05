from nbformat.v4.nbbase import new_markdown_cell
from jupytext.cell_reader import RMarkdownCellReader, LightScriptCellReader, uncomment
from jupytext.cell_to_text import RMarkdownCellExporter


def test_uncomment():
    assert uncomment(["# line one", "#line two", "line three"], "#") == [
        "line one",
        "line two",
        "line three",
    ]
    assert uncomment(["# line one", "#line two", "line three"], "") == [
        "# line one",
        "#line two",
        "line three",
    ]


def test_text_to_code_cell():
    text = """```{python}
1+2+3
```
"""
    lines = text.splitlines()
    cell, pos = RMarkdownCellReader().read(lines)

    assert cell.cell_type == "code"
    assert cell.source == "1+2+3"
    assert cell.metadata == {"language": "python"}
    assert lines[pos:] == []


def test_text_to_code_cell_empty_code():
    text = """```{python}
```
"""
    lines = text.splitlines()
    cell, pos = RMarkdownCellReader().read(lines)

    assert cell.cell_type == "code"
    assert cell.source == ""
    assert cell.metadata == {"language": "python"}
    assert lines[pos:] == []


def test_text_to_code_cell_empty_code_no_blank_line():
    text = """```{python}
```
"""
    lines = text.splitlines()
    cell, pos = RMarkdownCellReader().read(lines)

    assert cell.cell_type == "code"
    assert cell.source == ""
    assert cell.metadata == {"language": "python"}
    assert lines[pos:] == []


def test_text_to_markdown_cell():
    text = """This is
a markdown cell

```{python}
1+2+3
```
"""
    lines = text.splitlines()
    cell, pos = RMarkdownCellReader().read(lines)

    assert cell.cell_type == "markdown"
    assert cell.source == "This is\na markdown cell"
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
    cell, pos = RMarkdownCellReader().read(lines)

    assert cell.cell_type == "markdown"
    assert cell.source == "This is\na markdown cell"
    assert cell.metadata == {"lines_to_next_cell": 0}
    assert pos == 2


def test_text_to_markdown_two_blank_line():
    text = """

```{python}
1+2+3
```
"""
    lines = text.splitlines()
    cell, pos = RMarkdownCellReader().read(lines)

    assert cell.cell_type == "markdown"
    assert cell.source == ""
    assert cell.metadata == {}
    assert pos == 2


def test_text_to_markdown_one_blank_line():
    text = """
```{python}
1+2+3
```
"""
    lines = text.splitlines()
    cell, pos = RMarkdownCellReader().read(lines)

    assert cell.cell_type == "markdown"
    assert cell.source == ""
    assert cell.metadata == {"lines_to_next_cell": 0}
    assert pos == 1


def test_empty_markdown_to_text():
    cell = new_markdown_cell(source="")
    text = RMarkdownCellExporter(cell, "python").cell_to_text()
    assert text == [""]


def test_text_to_cell_py():
    text = "1+1\n"
    lines = text.splitlines()
    cell, pos = LightScriptCellReader().read(lines)
    assert cell.cell_type == "code"
    assert cell.source == "1+1"
    assert cell.metadata == {}
    assert pos == 1


def test_text_to_cell_py2():
    text = """def f(x):
    return x+1"""
    lines = text.splitlines()
    cell, pos = LightScriptCellReader().read(lines)
    assert cell.cell_type == "code"
    assert cell.source == """def f(x):\n    return x+1"""
    assert cell.metadata == {}
    assert pos == 2


def test_code_to_cell():
    text = """def f(x):
    return x+1"""
    lines = text.splitlines()
    cell, pos = LightScriptCellReader().read(lines)
    assert cell.cell_type == "code"
    assert cell.source == """def f(x):\n    return x+1"""
    assert cell.metadata == {}
    assert pos == 2
