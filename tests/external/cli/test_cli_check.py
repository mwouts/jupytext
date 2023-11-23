import pytest
from nbformat.v4.nbbase import new_code_cell, new_notebook

from jupytext import write
from jupytext.cli import jupytext


@pytest.fixture
def non_black_notebook(python_notebook):
    return new_notebook(metadata=python_notebook.metadata, cells=[new_code_cell("1+1")])


@pytest.mark.requires_black
def test_check_notebooks_left_or_right_black(python_notebook, tmpdir, cwd_tmpdir):
    write(python_notebook, str(tmpdir / "nb1.ipynb"))
    write(python_notebook, str(tmpdir / "nb2.ipynb"))

    jupytext(["*.ipynb", "--check", "black --check {}"])
    jupytext(["--check", "black --check {}", "*.ipynb"])


@pytest.mark.requires_black
def test_check_notebooks_left_or_right_not_black(
    non_black_notebook, tmpdir, cwd_tmpdir
):
    write(non_black_notebook, str(tmpdir / "nb1.ipynb"))
    write(non_black_notebook, str(tmpdir / "nb2.ipynb"))

    with pytest.raises(SystemExit):
        jupytext(["*.ipynb", "--check", "black --check {}"])

    with pytest.raises(SystemExit):
        jupytext(["--check", "black --check {}", "*.ipynb"])
