import pytest
from nbformat.notebooknode import NotebookNode

import jupytext
from jupytext.formats import NOTEBOOK_EXTENSIONS
from jupytext.myst import is_myst_available, myst_extensions
from jupytext.quarto import is_quarto_available


@pytest.mark.parametrize("ext", sorted(set(NOTEBOOK_EXTENSIONS) - {".ipynb"}))
def test_read_empty_text_notebook(ext, tmp_path):
    if ext == ".qmd" and not is_quarto_available(min_version="0.2.0"):
        pytest.skip("quarto is not available")
    if ext in myst_extensions(no_md=True) and not is_myst_available():
        pytest.skip("MyST is not available")

    empty_nb = (tmp_path / "notebook").with_suffix(ext)
    empty_nb.touch()

    nb = jupytext.read(empty_nb)

    assert isinstance(nb, NotebookNode)
    assert not nb.cells
