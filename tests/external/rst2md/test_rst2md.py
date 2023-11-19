import os

import pytest
from nbformat.v4.nbbase import new_markdown_cell, new_notebook

from jupytext import TextFileContentsManager, read, write
from jupytext.cli import jupytext


@pytest.mark.requires_sphinx_gallery
def test_rst2md(tmpdir, cwd_tmpdir):
    tmp_py = "notebook.py"
    tmp_ipynb = "notebook.ipynb"

    # Write notebook in sphinx format
    nb = new_notebook(
        cells=[
            new_markdown_cell("A short sphinx notebook"),
            new_markdown_cell(":math:`1+1`"),
        ]
    )
    write(nb, tmp_py, fmt="py:sphinx")

    jupytext(
        [
            tmp_py,
            "--from",
            "py:sphinx",
            "--to",
            "ipynb",
            "--opt",
            "rst2md=True",
            "--opt",
            "cell_metadata_filter=-all",
        ]
    )

    assert os.path.isfile(tmp_ipynb)
    nb = read(tmp_ipynb)

    assert nb.metadata["jupytext"]["cell_metadata_filter"] == "-all"
    assert nb.metadata["jupytext"]["rst2md"] is False

    # Was rst to md conversion effective?
    assert nb.cells[2].source == "$1+1$"


@pytest.mark.requires_sphinx_gallery
def test_rst2md_option(tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))

    # Write notebook in sphinx format
    nb = new_notebook(
        cells=[
            new_markdown_cell("A short sphinx notebook"),
            new_markdown_cell(":math:`1+1`"),
        ]
    )
    write(nb, tmp_py, fmt="py:sphinx")

    cm = TextFileContentsManager()
    cm.sphinx_convert_rst2md = True
    cm.root_dir = str(tmpdir)

    nb2 = cm.get("notebook.py")["content"]

    # Was rst to md conversion effective?
    assert nb2.cells[2].source == "$1+1$"
    assert nb2.metadata["jupytext"]["rst2md"] is False
