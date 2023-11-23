import pytest
from nbformat import writes as nbformat_writes
from nbformat.v3.nbbase import new_code_cell, new_notebook, new_text_cell, new_worksheet
from nbformat.v4.nbbase import new_markdown_cell
from nbformat.v4.nbbase import new_notebook as new_notebook_v4

from jupytext import reads, writes
from jupytext.jupytext import NotSupportedNBFormatVersion


@pytest.fixture()
def sample_notebook_v3():
    return new_notebook(
        worksheets=[
            new_worksheet(
                cells=[new_code_cell("1 + 1"), new_text_cell("markdown", "Hi")]
            )
        ]
    )


@pytest.fixture()
def sample_notebook_v3_json(sample_notebook_v3):
    return nbformat_writes(sample_notebook_v3)


@pytest.fixture()
def sample_notebook_v4_99():
    nb = new_notebook_v4(cells=[new_markdown_cell("Hi")])
    nb["nbformat_minor"] = 99
    return nb


def test_jupytext_can_read_nbformat_3(
    sample_notebook_v3_json,
):
    with pytest.warns(Warning, match="jupyter nbconvert --to notebook --inplace"):
        nb = reads(sample_notebook_v3_json, fmt="ipynb")
        assert nb["nbformat"] == 3

    nb = reads(sample_notebook_v3_json, as_version=4, fmt="ipynb")
    assert nb["nbformat"] == 4


@pytest.mark.parametrize("fmt", ["py:light", "py:percent", "md"])
def test_jupytext_gives_a_meaningful_error_when_writing_nbformat_3(
    sample_notebook_v3, fmt
):
    with pytest.raises(
        NotSupportedNBFormatVersion,
        match="Notebooks in nbformat version 3.0 are not supported by Jupytext",
    ):
        writes(sample_notebook_v3, fmt=fmt)

    writes(sample_notebook_v3, version=4, fmt=fmt)


@pytest.mark.parametrize("fmt", ["py:light", "py:percent", "md"])
def test_jupytext_gives_a_meaningful_error_when_writing_nbformat_4_99(
    sample_notebook_v4_99, fmt
):
    with pytest.warns(
        Warning,
        match="Notebooks in nbformat version 4.99 have not been tested",
    ):
        writes(sample_notebook_v4_99, fmt=fmt)
