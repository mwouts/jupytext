import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_markdown_cell, new_notebook
from pre_commit.main import main as pre_commit

from jupytext import read, write
from jupytext.cli import jupytext
from jupytext.compare import compare_cells


def test_pre_commit_hook_ipynb_to_py(
    tmpdir, cwd_tmpdir, tmp_repo, jupytext_repo_root, jupytext_repo_rev
):
    """Here we document and test the expected behavior of the pre-commit hook in the
    directional (--to) mode. Note that here, the ipynb file is always the source for
    updates - i.e. changes on the .py file will not trigger the hook.
    """
    # set up the tmpdir repo with pre-commit
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [--from, ipynb, --to, "py:percent"]
"""

    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)
    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks"])

    # write test notebook and output file
    nb = new_notebook(cells=[new_markdown_cell("A short notebook")])
    write(nb, "test.ipynb")
    jupytext(["--from", "ipynb", "--to", "py:percent", "test.ipynb"])

    tmp_repo.git.add(".")
    tmp_repo.index.commit("test")

    # make a change to the notebook
    nb = new_notebook(cells=[new_markdown_cell("Some other text")])
    write(nb, "test.ipynb")

    tmp_repo.git.add("test.ipynb")
    # now a commit will fail, and keep failing until we add the new
    # changes made to the existing output to the index ourselves
    with pytest.raises(HookExecutionError, match="files were modified by this hook"):
        tmp_repo.index.commit("fails")

    with pytest.raises(HookExecutionError, match="git add test.py"):
        tmp_repo.index.commit("fails again")

    # once we add the changes, it will pass
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("succeeds")

    assert "test.ipynb" in tmp_repo.tree()
    assert "test.py" in tmp_repo.tree()

    # Updating the .py file is possible
    nb = new_notebook(cells=[new_markdown_cell("Some updated text")])
    write(nb, "test.py", fmt="py:percent")
    tmp_repo.index.commit("update py version")

    # But it won't change the ipynb file (if you want that, use the --sync mode)
    nb = read("test.ipynb")
    compare_cells(nb.cells, [new_markdown_cell("Some other text")], compare_ids=False)
