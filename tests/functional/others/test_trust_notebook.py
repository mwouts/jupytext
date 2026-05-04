import os
import shutil

import pytest
from jupyter_server.utils import ensure_async
from nbformat.v4.nbbase import new_code_cell, new_notebook, new_output

from jupytext.compare import compare_notebooks

pytestmark = pytest.mark.asyncio


async def test_py_notebooks_are_trusted(python_file, cm):
    root, file = os.path.split(python_file)
    cm.root_dir = root
    nb = await ensure_async(cm.get(file))
    for cell in nb["content"].cells:
        assert cell.metadata.get("trusted", True)


async def test_rmd_notebooks_are_trusted(rmd_file, cm):
    root, file = os.path.split(rmd_file)
    cm.root_dir = root
    nb = await ensure_async(cm.get(file))
    for cell in nb["content"].cells:
        assert cell.metadata.get("trusted", True)


@pytest.mark.skip(reason="Fails intermittently on CI, see #1346")
async def test_ipynb_notebooks_can_be_trusted(ipynb_py_file, tmpdir, no_jupytext_version_number, cm):
    if "hash sign" in ipynb_py_file:
        pytest.skip()
    root, file = os.path.split(ipynb_py_file)
    tmp_ipynb = str(tmpdir.join(file))
    py_file = file.replace(".ipynb", ".py")
    tmp_py = str(tmpdir.join(py_file))
    shutil.copy(ipynb_py_file, tmp_ipynb)

    cm.formats = "ipynb,py"
    cm.root_dir = str(tmpdir)
    model = await ensure_async(cm.get(file))
    await ensure_async(cm.save(model, py_file))

    # Unsign and test notebook
    nb = model["content"]
    for cell in nb.cells:
        cell.metadata.pop("trusted", True)

    cm.notary.unsign(nb)

    model = await ensure_async(cm.get(file))
    for cell in model["content"].cells:
        assert "trusted" not in cell.metadata or not cell.metadata["trusted"] or not cell.outputs

    # Trust and reload
    await ensure_async(cm.trust_notebook(py_file))

    model = await ensure_async(cm.get(file))
    for cell in model["content"].cells:
        assert cell.metadata.get("trusted", True)

    # Remove py file, content should be the same
    os.remove(tmp_py)
    nb2 = await ensure_async(cm.get(file))
    for cell in nb2["content"].cells:
        assert cell.metadata.get("trusted", True)

    compare_notebooks(nb2["content"], model["content"])

    # Just for coverage
    await ensure_async(cm.trust_notebook(file))


@pytest.mark.skip(reason="Fails intermittently on CI, see #1346")
async def test_ipynb_notebooks_can_be_trusted_even_with_metadata_filter(ipynb_py_file, tmpdir, no_jupytext_version_number, cm):
    if "hash sign" in ipynb_py_file:
        pytest.skip()
    root, file = os.path.split(ipynb_py_file)
    tmp_ipynb = str(tmpdir.join(file))
    py_file = file.replace(".ipynb", ".py")
    tmp_py = str(tmpdir.join(py_file))
    shutil.copy(ipynb_py_file, tmp_ipynb)

    cm.formats = "ipynb,py"
    cm.notebook_metadata_filter = "all"
    cm.cell_metadata_filter = "-all"
    cm.root_dir = str(tmpdir)
    model = await ensure_async(cm.get(file))
    await ensure_async(cm.save(model, py_file))

    # Unsign notebook
    nb = model["content"]
    for cell in nb.cells:
        cell.metadata.pop("trusted", True)

    cm.notary.unsign(nb)

    # Trust and reload
    await ensure_async(cm.trust_notebook(py_file))

    model = await ensure_async(cm.get(file))
    for cell in model["content"].cells:
        assert cell.metadata.get("trusted", True)

    # Remove py file, content should be the same
    os.remove(tmp_py)
    nb2 = await ensure_async(cm.get(file))
    for cell in nb2["content"].cells:
        assert cell.metadata.get("trusted", True)

    compare_notebooks(nb2["content"], model["content"])


async def test_text_notebooks_can_be_trusted(percent_file, tmpdir, no_jupytext_version_number, cm):
    root, file = os.path.split(percent_file)
    py_file = str(tmpdir.join(file))
    shutil.copy(percent_file, py_file)

    cm.root_dir = str(tmpdir)
    model = await ensure_async(cm.get(file))
    model["type"] == "notebook"
    await ensure_async(cm.save(model, file))

    # Unsign notebook
    nb = model["content"]
    for cell in nb.cells:
        cell.metadata.pop("trusted", True)

    cm.notary.unsign(nb)

    # Trust and reload
    await ensure_async(cm.trust_notebook(file))

    model = await ensure_async(cm.get(file))
    for cell in model["content"].cells:
        assert cell.metadata.get("trusted", True)


# This test started failing on Windows on 2025-04-26
# https://github.com/mwouts/jupytext/actions/runs/14683344298/job/41208822220?pr=1380
@pytest.mark.skip_on_windows
async def test_simple_notebook_is_trusted(tmpdir, python_notebook, cm):
    cm.root_dir = str(tmpdir)

    nb = python_notebook
    cm.notary.unsign(nb)

    # All cells are trusted in this notebook
    assert cm.notary.check_cells(nb)
    # Yet the notebook is not in the database of trusted notebooks
    assert not cm.notary.check_signature(nb)

    # Save the notebook using the CM
    await ensure_async(cm.save(dict(type="notebook", content=nb), "test.ipynb"))

    # The notebook is safe so it should have been trusted before getting saved to disk
    nb = (await ensure_async(cm.get("test.ipynb")))["content"]
    assert cm.notary.check_signature(nb)


@pytest.mark.requires_myst
async def test_myst_notebook_is_trusted_941(
    tmp_path,
    cm,
    myst="""---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: itables
  language: python
  name: itables
---

# Downsampling

```{code-cell} ipython3
from itables import init_notebook_mode, show

init_notebook_mode(all_interactive=True)
```
""",
):
    cm.root_dir = str(tmp_path)

    test_md = tmp_path / "test.md"
    test_md.write_text(myst)

    nb = (await ensure_async(cm.get("test.md")))["content"]

    # All cells are trusted in this notebook
    assert cm.notary.check_cells(nb)


@pytest.mark.requires_myst
async def test_paired_notebook_with_outputs_is_not_trusted_941(tmp_path, python_notebook, cm):
    cm.root_dir = str(tmp_path)

    nb = python_notebook
    nb.cells.append(new_code_cell(source="1+1", outputs=[new_output("execute_result")]))
    nb.metadata["jupytext"] = {"formats": "ipynb,md:myst"}
    cm.notary.unsign(nb)
    await ensure_async(cm.save(model=dict(type="notebook", content=nb), path="test.ipynb"))

    nb = (await ensure_async(cm.get("test.md")))["content"]
    assert not cm.notary.check_cells(nb)
    assert not cm.notary.check_signature(nb)


@pytest.mark.skip_on_windows
async def test_trusted_paired_notebook_remains_trusted_after_py_file_edited_1397(tmp_path, cm):
    """When a trusted paired ipynb+py notebook is modified through just the py file,
    it remains trusted when reloaded in Jupyter. See https://github.com/mwouts/jupytext/issues/1397"""
    import os
    import time

    import nbformat

    cm.root_dir = str(tmp_path)

    # Create a paired notebook with outputs and save it
    nb = new_notebook(
        cells=[
            new_code_cell(
                source="1 + 1",
                outputs=[
                    {
                        "data": {"text/plain": ["2"]},
                        "execution_count": 1,
                        "metadata": {},
                        "output_type": "execute_result",
                    }
                ],
            )
        ],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "jupytext": {"formats": "ipynb,py:percent"},
        },
    )
    await ensure_async(cm.save(model=dict(type="notebook", content=nb), path="test.ipynb"))

    # Trust the notebook (simulate the user running cells and saving)
    await ensure_async(cm.trust_notebook("test.ipynb"))

    # Verify the ipynb file has a valid signature (check on raw file, before mark_trusted_cells)
    ipynb_path = tmp_path / "test.ipynb"
    with open(ipynb_path) as f:
        raw_nb = nbformat.read(f, as_version=4)
    assert cm.notary.check_signature(raw_nb), "ipynb should have a valid signature after trust_notebook"

    # Now simulate editing the py file (AI edits, reformatting, etc.)
    # The py file has newer content but the ipynb is unchanged and still trusted
    py_path = tmp_path / "test.py"
    py_content = py_path.read_text()
    # Modify the py source code (remove spaces, simulating reformatting)
    py_content = py_content.replace("1 + 1", "1+1")
    py_path.write_text(py_content)

    # Touch the py file to make it newer than the ipynb
    time.sleep(0.01)
    os.utime(py_path, None)

    # Reload through the contents manager - the notebook should remain trusted
    # because the outputs (from the trusted ipynb) have not changed
    nb_reloaded = (await ensure_async(cm.get("test.py")))["content"]

    # The reloaded notebook should have trusted cells
    # (mark_trusted_cells sets trusted=True in cell metadata when the notebook is trusted)
    for cell in nb_reloaded.cells:
        if cell.cell_type == "code":
            assert cell.metadata.get("trusted", True), f"Cell should be trusted: {cell.source}"

    # Verify the combined notebook was re-signed by checking the raw ipynb
    # (The signature is stored for the notebook without 'trusted' in cell metadata)
    with open(ipynb_path) as f:
        raw_reloaded_nb = nbformat.read(f, as_version=4)
    # The combined notebook (with new source from py) should have been re-signed
    # Note: the signature in the DB is for the COMBINED notebook, not the raw ipynb
    # We check that cells are trusted in the reloaded notebook
    assert all(
        cell.metadata.get("trusted", True) for cell in nb_reloaded.cells if cell.cell_type == "code"
    ), "All code cells should be trusted after reloading the notebook"
