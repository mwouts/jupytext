import pytest
from jupyter_server.utils import ensure_async
from nbformat.v4.nbbase import new_notebook
from tornado.web import HTTPError

import jupytext


@pytest.mark.asyncio
async def test_combine_same_version_ok(tmpdir, cm):
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

    cm.formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    nb = await ensure_async(cm.get(tmp_ipynb))
    cells = nb["content"]["cells"]
    assert len(cells) == 1
    assert cells[0].cell_type == "markdown"
    assert cells[0].source == "New cell"


@pytest.mark.asyncio
async def test_combine_lower_version_raises(tmpdir, cm):
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

    cm.formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    with pytest.raises(HTTPError):
        await ensure_async(cm.get(tmp_ipynb))
