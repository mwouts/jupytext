import pytest
from jupyter_server.utils import ensure_async


@pytest.mark.asyncio
async def test_remove_encoding_907(tmp_path, python_notebook, cm):
    # Pair all notebooks to py:percent files
    (tmp_path / "jupytext.toml").write_text('formats="ipynb,py:percent"')

    # Create a contents manager
    cm.root_dir = str(tmp_path)

    # Save the notebook in Jupyter
    await ensure_async(
        cm.save(dict(type="notebook", content=python_notebook), path="nb.ipynb")
    )

    # No encoding is present in the py file
    py = (tmp_path / "nb.py").read_text()
    assert "coding" not in py

    # Add the encoding line
    py = "# -*- coding: utf-8 -*-\n" + py
    (tmp_path / "nb.py").write_text(py)

    # Reload the notebook
    nb = (await ensure_async(cm.get("nb.ipynb")))["content"]
    assert "encoding" in nb.metadata["jupytext"]

    # Save the notebook
    await ensure_async(cm.save(dict(type="notebook", content=nb), path="nb.ipynb"))

    # The encoding is still present in the py file
    py = (tmp_path / "nb.py").read_text()
    assert py.startswith("# -*- coding: utf-8 -*-")

    # Remove the encoding (mock ipyupgrade)
    py = "\n".join(py.splitlines()[1:])
    (tmp_path / "nb.py").write_text(py)

    # Reload the notebook - the encoding is not there anymore
    nb = (await ensure_async(cm.get("nb.ipynb")))["content"]
    assert "encoding" not in nb.metadata["jupytext"]

    # Save the notebook - the encoding is not there anymore
    py = (tmp_path / "nb.py").read_text()
    assert "coding" not in py
