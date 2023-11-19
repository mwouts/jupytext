import pytest
from git.exc import HookExecutionError
from pre_commit.main import main as pre_commit

from jupytext import read, write
from jupytext.cli import jupytext


def test_pre_commit_hook_sync_nbstripout(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    jupytext_repo_root,
    jupytext_repo_rev,
    notebook_with_outputs,
):
    """Here we sync the ipynb notebook with a Markdown file and also apply nbstripout."""
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [--sync]

- repo: https://github.com/kynan/nbstripout
  rev: 0.5.0
  hooks:
  - id: nbstripout
"""

    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)

    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    # write a test notebook
    write(notebook_with_outputs, "test.ipynb")

    # We pair the notebook to a md file
    jupytext(["--set-formats", "ipynb,md", "test.ipynb"])

    # try to commit it, should fail because
    # 1. the md version hasn't been added
    # 2. the notebook has outputs
    tmp_repo.git.add("test.ipynb")
    with pytest.raises(
        HookExecutionError,
        match="files were modified by this hook",
    ):
        tmp_repo.index.commit("failing")

    # Add the two files
    tmp_repo.git.add("test.ipynb")
    tmp_repo.git.add("test.md")

    # now the commit will succeed
    tmp_repo.index.commit("passing")
    assert "test.ipynb" in tmp_repo.tree()
    assert "test.md" in tmp_repo.tree()

    # the ipynb file has no outputs on disk
    nb = read("test.ipynb")
    assert not nb.cells[0].outputs
