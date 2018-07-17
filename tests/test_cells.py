import pytest
from nbrmd.nbrmd import TextNotebookReader, TextNotebookWriter
from nbformat.v4.nbbase import new_markdown_cell


@pytest.fixture
def reader():
    return TextNotebookReader(ext='.Rmd')


@pytest.fixture
def py_reader():
    return TextNotebookReader(ext='.py')


@pytest.fixture
def writer():
    return TextNotebookWriter(ext='.Rmd')


@pytest.fixture
def py_writer():
    return TextNotebookWriter(ext='.py')


def test_text_to_code_cell():
    text = """```{python}
1+2+3
```

"""
    lines = text.splitlines()
    cell, pos = reader().text_to_cell(lines)

    assert cell.cell_type == 'code'
    assert cell.source == '1+2+3'
    assert cell.metadata == {'language': 'python'}
    assert lines[pos:] == []


def test_text_to_code_cell_empty_code():
    text = """```{python}
```

"""
    lines = text.splitlines()
    cell, pos = reader().text_to_cell(lines)

    assert cell.cell_type == 'code'
    assert cell.source == ''
    assert cell.metadata == {'language': 'python'}
    assert lines[pos:] == []


def test_text_to_code_cell_empty_code_no_blank_line():
    text = """```{python}
```
"""
    lines = text.splitlines()
    cell, pos = reader().text_to_cell(lines)

    assert cell.cell_type == 'code'
    assert cell.source == ''
    assert cell.metadata == {'language': 'python'}
    assert lines[pos:] == []


def test_text_to_markdown_cell():
    text = """This is
a markdown cell

```{python}
1+2+3
```
"""
    lines = text.splitlines()
    cell, pos = reader().text_to_cell(lines)

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
    cell, pos = reader().text_to_cell(lines)

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
    cell, pos = reader().text_to_cell(lines)

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
    cell, pos = reader().text_to_cell(lines)

    assert cell.cell_type == 'markdown'
    assert cell.source == ''
    assert cell.metadata == {'noskipline': True}
    assert pos == 1


def test_empty_markdown_to_text():
    cell = new_markdown_cell(source='')
    text = writer().cell_to_text(cell, None, default_language='python')
    assert text == ['']


def test_text_to_cell_py():
    text = '1+1\n'
    lines = text.splitlines()
    cell, pos = py_reader().text_to_cell(lines)
    assert cell.cell_type == 'code'
    assert cell.source == '1+1'
    assert cell.metadata == {}
    assert pos == 1


def test_text_to_cell_py2():
    text = '''def f(x):
    return x+1'''
    lines = text.splitlines()
    cell, pos = py_reader().text_to_cell(lines)
    assert cell.cell_type == 'code'
    assert cell.source == '''def f(x):\n    return x+1'''
    assert cell.metadata == {}
    assert pos == 2


def test_code_to_cell():
    text = '''def f(x):
    return x+1'''
    lines = text.splitlines()
    cell, pos = py_reader().code_to_cell(lines, parse_opt=False)
    assert cell.cell_type == 'code'
    assert cell.source == '''def f(x):\n    return x+1'''
    assert cell.metadata == {}
    assert pos == 2
