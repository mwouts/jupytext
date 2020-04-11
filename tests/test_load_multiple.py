import pytest
from tornado.web import HTTPError
from nbformat.v4.nbbase import new_notebook
import jupytext


def test_combine_same_version_ok(tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_nbpy = "notebook.py"

    with open(str(tmpdir.join(tmp_nbpy)), "w") as fp:
        fp.write(
            """# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '1.2'
# ---

# New cell
"""
        )

    nb = new_notebook(metadata={"jupytext_formats": "ipynb,py"})
    jupytext.write(nb, str(tmpdir.join(tmp_ipynb)))

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    nb = cm.get(tmp_ipynb)
    cells = nb["content"]["cells"]
    assert len(cells) == 1
    assert cells[0].cell_type == "markdown"
    assert cells[0].source == "New cell"


def test_combine_lower_version_raises(tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_nbpy = "notebook.py"

    with open(str(tmpdir.join(tmp_nbpy)), "w") as fp:
        fp.write(
            """# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '0.0'
# ---

# New cell
"""
        )

    nb = new_notebook(metadata={"jupytext_formats": "ipynb,py"})
    jupytext.write(nb, str(tmpdir.join(tmp_ipynb)))

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    with pytest.raises(HTTPError):
        cm.get(tmp_ipynb)
