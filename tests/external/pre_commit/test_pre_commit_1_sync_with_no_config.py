from copy import deepcopy

import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_markdown_cell
from pre_commit.main import main as pre_commit

import jupytext
from jupytext import TextFileContentsManager
from jupytext.compare import compare_notebooks


def test_pre_commit_hook_sync_with_no_config(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    jupytext_repo_root,
    jupytext_repo_rev,
    notebook_with_outputs,
):
    """In this test we reproduce the setting from https://github.com/mwouts/jupytext/issues/967"""
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [
      '--sync',
      '--set-formats',
      'ipynb,py:percent',
      '--show-changes',
      '--'
    ]
"""
    # Save a sample notebook with outputs in Jupyter
    nb = deepcopy(notebook_with_outputs)
    (tmpdir / "notebooks").mkdir()
    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.save(dict(type="notebook", content=nb), "nb.ipynb")

    # Add it to git
    tmp_repo.git.add("nb.ipynb")
    tmp_repo.index.commit("Notebook with outputs")

    # Configure the pre-commit hook
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)
    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    # Modify and save the notebook
    nb.cells.append(new_markdown_cell("New markdown cell"))
    cm.save(dict(type="notebook", content=nb), "nb.ipynb")

    # No .py file at the moment
    assert not (tmpdir / "nb.py").exists()

    # try to commit it, should fail as the py version hasn't been added
    tmp_repo.git.add("nb.ipynb")
    with pytest.raises(
        HookExecutionError,
        match="git add nb.py",
    ):
        tmp_repo.index.commit("failing")

    # Now the .py file is present
    assert "New markdown cell" in tmpdir.join("nb.py").read()

    # add the ipynb and the py file, now the commit will succeed
    tmp_repo.git.add("nb.ipynb")
    tmp_repo.git.add("nb.py")
    tmp_repo.index.commit("passing")
    assert "nb.ipynb" in tmp_repo.tree()
    assert "nb.py" in tmp_repo.tree()

    # The notebook on disk is the same as the original, except for the new cell added
    nb = jupytext.read(tmpdir / "nb.ipynb")
    extra_cell = nb.cells.pop()
    assert extra_cell.cell_type == "markdown"
    assert extra_cell.source == "New markdown cell"
    compare_notebooks(
        nb,
        notebook_with_outputs,
        compare_ids=True,
        compare_outputs=True,
    )
