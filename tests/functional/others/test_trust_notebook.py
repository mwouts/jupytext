import os
import shutil

import pytest
from nbformat.v4.nbbase import new_code_cell, new_output

from jupytext.compare import compare_notebooks


async def test_py_notebooks_are_trusted(python_file, cm):
    root, file = os.path.split(python_file)
    cm.root_dir = root
    nb = await cm.get(file)
    for cell in nb["content"].cells:
        assert cell.metadata.get("trusted", True)


async def test_rmd_notebooks_are_trusted(rmd_file, cm):
    root, file = os.path.split(rmd_file)
    cm.root_dir = root
    nb = await cm.get(file)
    for cell in nb["content"].cells:
        assert cell.metadata.get("trusted", True)


async def test_ipynb_notebooks_can_be_trusted(
    ipynb_py_file, cm, tmpdir, no_jupytext_version_number
):
    if "hash sign" in ipynb_py_file:
        pytest.skip()
    root, file = os.path.split(ipynb_py_file)
    tmp_ipynb = str(tmpdir.join(file))
    py_file = file.replace(".ipynb", ".py")
    tmp_py = str(tmpdir.join(py_file))
    shutil.copy(ipynb_py_file, tmp_ipynb)

    cm.formats = "ipynb,py"
    cm.root_dir = str(tmpdir)
    model = await cm.get(file)
    await cm.save(model, py_file)

    # Unsign and test notebook
    nb = model["content"]
    for cell in nb.cells:
        cell.metadata.pop("trusted", True)

    cm.notary.unsign(nb)

    model = await cm.get(file)
    for cell in model["content"].cells:
        assert (
            "trusted" not in cell.metadata
            or not cell.metadata["trusted"]
            or not cell.outputs
        )

    # Trust and reload
    await cm.trust_notebook(py_file)

    model = await cm.get(file)
    for cell in model["content"].cells:
        assert cell.metadata.get("trusted", True)

    # Remove py file, content should be the same
    os.remove(tmp_py)
    nb2 = await cm.get(file)
    for cell in nb2["content"].cells:
        assert cell.metadata.get("trusted", True)

    compare_notebooks(nb2["content"], model["content"])

    # Just for coverage
    await cm.trust_notebook(file)


async def test_ipynb_notebooks_can_be_trusted_even_with_metadata_filter(
    ipynb_py_file, cm, tmpdir, no_jupytext_version_number
):
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
    model = await cm.get(file)
    await cm.save(model, py_file)

    # Unsign notebook
    nb = model["content"]
    for cell in nb.cells:
        cell.metadata.pop("trusted", True)

    cm.notary.unsign(nb)

    # Trust and reload
    await cm.trust_notebook(py_file)

    model = await cm.get(file)
    for cell in model["content"].cells:
        assert cell.metadata.get("trusted", True)

    # Remove py file, content should be the same
    os.remove(tmp_py)
    nb2 = await cm.get(file)
    for cell in nb2["content"].cells:
        assert cell.metadata.get("trusted", True)

    compare_notebooks(nb2["content"], model["content"])


async def test_text_notebooks_can_be_trusted(
    percent_file, cm, tmpdir, no_jupytext_version_number
):
    root, file = os.path.split(percent_file)
    py_file = str(tmpdir.join(file))
    shutil.copy(percent_file, py_file)

    cm.root_dir = str(tmpdir)
    model = await cm.get(file)
    model["type"] == "notebook"
    await cm.save(model, file)

    # Unsign notebook
    nb = model["content"]
    for cell in nb.cells:
        cell.metadata.pop("trusted", True)

    cm.notary.unsign(nb)

    # Trust and reload
    await cm.trust_notebook(file)

    model = await cm.get(file)
    for cell in model["content"].cells:
        assert cell.metadata.get("trusted", True)


async def test_simple_notebook_is_trusted(cm, tmpdir, python_notebook):
    cm.root_dir = str(tmpdir)

    nb = python_notebook
    cm.notary.unsign(nb)

    # All cells are trusted in this notebook
    assert cm.notary.check_cells(nb)
    # Yet the notebook is not in the database of trusted notebooks
    assert not cm.notary.check_signature(nb)

    # Save the notebook using the CM
    await cm.save(dict(type="notebook", content=nb), "test.ipynb")

    # The notebook is safe so it should have been trusted before getting saved to disk
    nb = (await cm.get("test.ipynb"))["content"]
    assert cm.notary.check_signature(nb)


@pytest.mark.requires_myst
async def test_myst_notebook_is_trusted_941(
    cm,
    tmp_path,
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

    nb = (await cm.get("test.md"))["content"]

    # All cells are trusted in this notebook
    assert cm.notary.check_cells(nb)


@pytest.mark.requires_myst
async def test_paired_notebook_with_outputs_is_not_trusted_941(
    cm, tmp_path, python_notebook
):
    cm.root_dir = str(tmp_path)

    nb = python_notebook
    nb.cells.append(new_code_cell(source="1+1", outputs=[new_output("execute_result")]))
    nb.metadata["jupytext"] = {"formats": "ipynb,md:myst"}
    cm.notary.unsign(nb)
    await cm.save(model=dict(type="notebook", content=nb), path="test.ipynb")

    nb = (await cm.get("test.md"))["content"]
    assert not cm.notary.check_cells(nb)
    assert not cm.notary.check_signature(nb)
