import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_code_cell
from pre_commit.main import main as pre_commit

from jupytext import read, write


@pytest.mark.requires_user_kernel_python3
def test_pre_commit_hook_sync_execute(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    jupytext_repo_root,
    jupytext_repo_rev,
    notebook_with_outputs,
):
    """Here we sync the ipynb notebook with a py:percent file and execute it (this is probably not a very
    recommendable hook!)"""
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [--sync, --execute, --show-changes]
    additional_dependencies:
    - nbconvert
"""
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)

    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    # simple notebook with kernel 'user_kernel_python3'
    nb = notebook_with_outputs
    nb.cells = [new_code_cell("3+4")]

    # pair it to a py file and write it to disk
    nb.metadata["jupytext"] = {"formats": "ipynb,py:percent"}
    write(nb, "test.ipynb")

    # try to commit it, should fail because
    # 1. the py version hasn't been added
    # 2. the outputs are missing
    tmp_repo.git.add("test.ipynb")
    with pytest.raises(
        HookExecutionError,
        match="files were modified by this hook",
    ):
        tmp_repo.index.commit("failing")

    # Add the two files
    tmp_repo.git.add("test.ipynb")
    tmp_repo.git.add("test.py")

    # now the commit will succeed
    tmp_repo.index.commit("passing")
    assert "test.ipynb" in tmp_repo.tree()
    assert "test.py" in tmp_repo.tree()

    # the first cell has the expected output
    nb = read("test.ipynb")
    assert nb.cells[0].outputs[0]["data"]["text/plain"] == "7"
