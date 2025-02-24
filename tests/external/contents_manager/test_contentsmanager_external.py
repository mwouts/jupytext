import re

import pytest
from jupyter_server.utils import ensure_async

import jupytext
from jupytext.compare import compare_notebooks, notebook_model

pytestmark = pytest.mark.asyncio


@pytest.mark.requires_pandoc
async def test_save_load_paired_md_pandoc_notebook(ipynb_py_R_jl_file, tmpdir, cm):
    if re.match(
        r".*(functional|Notebook with|flavors|invalid|305).*", ipynb_py_R_jl_file
    ):
        pytest.skip()
    tmp_ipynb = "notebook.ipynb"
    tmp_md = "notebook.md"

    cm.root_dir = str(tmpdir)

    # open ipynb, save with cm, reopen
    nb = jupytext.read(ipynb_py_R_jl_file)
    nb.metadata["jupytext"] = {"formats": "ipynb,md:pandoc"}

    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))
    nb_md = await ensure_async(cm.get(tmp_md))

    compare_notebooks(nb_md["content"], nb, "md:pandoc")
    assert nb_md["content"].metadata["jupytext"]["formats"] == "ipynb,md:pandoc"


@pytest.mark.requires_quarto
async def test_save_load_paired_qmd_notebook(ipynb_py_R_jl_file, tmpdir, cm):
    if re.match(
        r".*(functional|Notebook with|plotly_graphs|flavors|complex_metadata|"
        "update83|raw_cell|_66|nteract|LaTeX|invalid|305|text_outputs|ir_notebook|jupyter|with_R_magic).*",
        ipynb_py_R_jl_file,
    ):
        pytest.skip()
    tmp_ipynb = "notebook.ipynb"
    tmp_qmd = "notebook.qmd"

    cm.root_dir = str(tmpdir)

    # open ipynb, save with cm, reopen
    nb = jupytext.read(ipynb_py_R_jl_file)
    nb.metadata["jupytext"] = {"formats": "ipynb,qmd"}

    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))
    nb_md = await ensure_async(cm.get(tmp_qmd))

    compare_notebooks(nb_md["content"], nb, "qmd")
    assert nb_md["content"].metadata["jupytext"]["formats"] == "ipynb,qmd"
