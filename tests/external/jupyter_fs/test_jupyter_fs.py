import logging

import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

import jupytext
from jupytext.compare import compare_cells, notebook_model


def fs_meta_manager(tmpdir):
    try:
        from jupyterfs.metamanager import SyncMetaManager
    except ImportError:
        pytest.skip("jupyterfs is not available")

    cm_class = jupytext.build_sync_jupytext_contents_manager_class(SyncMetaManager)
    logger = logging.getLogger("jupyter-fs")
    cm = cm_class(parent=None, log=logger)
    cm.initResource(
        {
            "url": f"osfs://{tmpdir}",
        }
    )
    return cm


def test_jupytext_jupyter_fs_metamanager(tmpdir):
    """Test the basic get/save functions of Jupytext with a fs manager
    https://github.com/mwouts/jupytext/issues/618"""
    cm = fs_meta_manager(tmpdir)
    # the hash that corresponds to the osfs
    osfs = [h for h in cm._managers if h != ""][0]

    # save a few files
    text = "some text\n"
    cm.save(dict(type="file", content=text, format="text"), path=osfs + ":text.md")
    nb = new_notebook(
        cells=[new_markdown_cell("A markdown cell"), new_code_cell("1 + 1")]
    )
    cm.save(notebook_model(nb), osfs + ":notebook.ipynb")
    cm.save(notebook_model(nb), osfs + ":text_notebook.md")

    # list the directory
    directory = cm.get(osfs + ":/")
    assert {file["name"] for file in directory["content"]} == {
        "text.md",
        "text_notebook.md",
        "notebook.ipynb",
    }

    # get the files
    model = cm.get(osfs + ":/text.md", type="file")
    assert model["type"] == "file"
    assert model["content"] == text

    model = cm.get(osfs + ":text.md", type="notebook")
    assert model["type"] == "notebook"
    # We only compare the cells, as kernelspecs are added to the notebook metadata
    compare_cells(
        model["content"].cells, [new_markdown_cell(text.strip())], compare_ids=False
    )

    for nb_file in ["notebook.ipynb", "text_notebook.md"]:
        model = cm.get(osfs + ":" + nb_file)
        assert model["type"] == "notebook"
        actual_cells = model["content"].cells

        # saving adds 'trusted=True' to the code cell metadata
        for cell in actual_cells:
            cell.metadata = {}
        compare_cells(actual_cells, nb.cells, compare_ids=False)


def test_config_jupytext_jupyter_fs_meta_manager(tmpdir):
    """Test the configuration of Jupytext with a fs manager"""
    tmpdir.join("jupytext.toml").write('formats = "ipynb,py"')
    cm = fs_meta_manager(tmpdir)
    # the hash that corresponds to the osfs
    osfs = [h for h in cm._managers if h != ""][0]

    # save a few files
    nb = new_notebook()
    cm.save(dict(type="file", content="text", format="text"), path=osfs + ":text.md")
    cm.save(notebook_model(nb), osfs + ":script.py")
    cm.save(notebook_model(nb), osfs + ":text_notebook.md")
    cm.save(notebook_model(nb), osfs + ":notebook.ipynb")

    # list the directory
    directory = cm.get(osfs + ":/")
    assert {file["name"] for file in directory["content"]} == {
        "jupytext.toml",
        "text.md",
        "text_notebook.md",
        "notebook.ipynb",
        "notebook.py",
        "script.py",
        "script.ipynb",
    }
