import nbformat
import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

import jupytext
from jupytext.cli import jupytext as jupytext_cli
from jupytext.compare import compare_notebooks
from jupytext.languages import _JUPYTER_LANGUAGES_LOWER_AND_UPPER


def test_custom_language_magics_md_to_ipynb(tmpdir):
    """Code blocks in custom language magics should be converted to code cells"""
    assert "jsx" not in _JUPYTER_LANGUAGES_LOWER_AND_UPPER

    # Pass custom_language_magics directly via fmt options
    md = """```python
print("hello")
```

```jsx
const Hello = () => (Hello);
```
"""
    nb = jupytext.reads(md, fmt={"extension": ".md", "custom_language_magics": ["jsx"]})
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == 'print("hello")'
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "%%jsx\nconst Hello = () => (Hello);"


def test_custom_language_magics_ipynb_to_md(tmpdir):
    """Code cells with custom language magics are converted to code blocks in those languages"""
    assert "jsx" not in _JUPYTER_LANGUAGES_LOWER_AND_UPPER

    nb = new_notebook(
        cells=[
            new_code_cell('print("hello")'),
            new_code_cell("%%jsx\nconst Hello = () => (<b>Hello</b>);"),
        ]
    )

    md = jupytext.writes(nb, fmt={"extension": ".md", "custom_language_magics": ["jsx"]})
    assert "custom_language_magics:" in md
    assert "jsx" in md
    assert "```jsx" in md


def test_custom_language_magics_roundtrip(tmpdir):
    """Round-trip: md with custom language magic -> ipynb -> md should preserve the code cell"""
    assert "jsx" not in _JUPYTER_LANGUAGES_LOWER_AND_UPPER

    nb = new_notebook(
        cells=[
            new_code_cell('print("hello")'),
            new_code_cell("%%jsx\nconst Hello = () => (<b>Hello</b>);"),
        ]
    )

    # ipynb -> md
    md = jupytext.writes(nb, fmt={"extension": ".md", "custom_language_magics": ["jsx"]})
    assert "```jsx" in md

    # md -> ipynb
    nb2 = jupytext.reads(md, fmt={"extension": ".md", "custom_language_magics": ["jsx"]})
    assert len(nb2.cells) == 2
    assert nb2.cells[1].cell_type == "code"
    assert nb2.cells[1].source == "%%jsx\nconst Hello = () => (<b>Hello</b>);"


def test_custom_language_magics_config_file(tmpdir):
    """custom_language_magics from jupytext.toml should allow md -> ipynb conversion"""
    assert "jsx" not in _JUPYTER_LANGUAGES_LOWER_AND_UPPER

    cfg_file = tmpdir.join("jupytext.toml")
    cfg_file.write('custom_language_magics = ["jsx"]')

    md_file = tmpdir.join("notebook.md")
    nb_file = tmpdir.join("notebook.ipynb")

    md_file.write(
        """```python
print("hello")
```

```jsx
const Hello = () => (<b>Hello</b>);
```
"""
    )

    jupytext_cli([str(md_file), "--to", "notebook"])
    nb = nbformat.read(str(nb_file), as_version=4)

    assert len(nb.cells) == 2
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "%%jsx\nconst Hello = () => (<b>Hello</b>);"


def test_custom_language_magics_not_markdown_cell(tmpdir):
    """Without custom_language_magics, jsx code blocks should remain as markdown cells"""
    assert "jsx" not in _JUPYTER_LANGUAGES_LOWER_AND_UPPER

    md = """```jsx
const Hello = () => (<b>Hello</b>);
```
"""
    nb = jupytext.reads(md, fmt="md")
    # Without custom_language_magics, this should be a markdown cell
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "markdown"
