import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell

from jupytext import reads, writes
from jupytext.formats import formats_with_support_for_cell_metadata, is_myst_available


@pytest.fixture()
def notebook_with_tags(python_notebook):
    nb = python_notebook
    nb.cells = [
        new_code_cell("1 + 1", metadata={"tags": ["tag1"]}),
        new_markdown_cell("some text", metadata={"tags": ["tag2"]}),
    ]
    return nb


@pytest.mark.parametrize(
    "fmt", ["py:percent", "py:light", "md:markdown", "md:myst", "Rmd:rmarkdown"]
)
def test_main_formats_support_cell_metadata(fmt):
    if fmt == "md:myst" and not is_myst_available():
        pytest.skip("myst is not available")
    assert fmt in set(formats_with_support_for_cell_metadata())


def test_tags_are_preserved(notebook_with_tags, fmt_with_cell_metadata):
    text = writes(notebook_with_tags, fmt_with_cell_metadata)
    nb = reads(text, fmt_with_cell_metadata)
    assert nb.cells[0]["metadata"]["tags"] == ["tag1"]
    assert nb.cells[1]["metadata"]["tags"] == ["tag2"]
