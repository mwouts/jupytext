import pytest
from git.exc import HookExecutionError
from pre_commit.main import main as pre_commit

from jupytext import read, write


def test_pre_commit_hook_sync_black_nbstripout(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    jupytext_repo_root,
    jupytext_repo_rev,
    notebook_with_outputs,
):
    """Here we sync the ipynb notebook with a py:percent file and also apply black and nbstripout."""
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [--sync, --pipe, black]
    additional_dependencies:
    - black==22.3.0  # Matches hook

- repo: https://github.com/psf/black
  rev: 22.3.0
  hooks:
  - id: black

- repo: https://github.com/kynan/nbstripout
  rev: 0.5.0
  hooks:
  - id: nbstripout
"""
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)

    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    tmpdir.join("jupytext.toml").write('formats = "ipynb,py:percent"')
    tmp_repo.git.add("jupytext.toml")
    tmp_repo.index.commit("pair notebooks")

    # write a test notebook
    write(notebook_with_outputs, "test.ipynb")

    # try to commit it, should fail because
    # 1. the py version hasn't been added
    # 2. the first cell is '1+1' which is not black compliant
    # 3. the notebook has outputs
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

    # the first cell was reformatted
    nb = read("test.ipynb")
    assert nb.cells[0].source == "1 + 1"

    # the ipynb file has no outputs
    assert not nb.cells[0].outputs
