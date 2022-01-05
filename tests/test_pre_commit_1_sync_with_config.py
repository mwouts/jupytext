import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_markdown_cell
from pre_commit.main import main as pre_commit

from jupytext import TextFileContentsManager, read, write

from .utils import (
    skip_pre_commit_tests_on_windows,
    skip_pre_commit_tests_when_jupytext_folder_is_not_a_git_repo,
)


@skip_pre_commit_tests_on_windows
@skip_pre_commit_tests_when_jupytext_folder_is_not_a_git_repo
def test_pre_commit_hook_sync_with_config(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    jupytext_repo_root,
    jupytext_repo_rev,
    python_notebook,
):
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [--sync]
"""
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)

    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    tmpdir.join(".jupytext.toml").write('formats = "ipynb,py:percent"\n')

    # create a test notebook and save it in Jupyter
    nb = python_notebook
    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.save(dict(type="notebook", content=nb), "test.ipynb")

    # Assert that "text_representation" is in the Jupytext metadata #900
    assert "text_representation" in tmpdir.join("test.py").read()
    # But not in the ipynb notebook
    assert "text_representation" not in tmpdir.join("test.ipynb").read()

    # try to commit it, should fail as the py version hasn't been added
    tmp_repo.git.add("test.ipynb")
    with pytest.raises(
        HookExecutionError,
        match="git add test.py",
    ):
        tmp_repo.index.commit("failing")

    # add the py file, now the commit will succeed
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("passing")
    assert "test.ipynb" in tmp_repo.tree()
    assert "test.py" in tmp_repo.tree()

    # The text representation metadata is still in the py file
    assert "text_representation" in tmpdir.join("test.py").read()
    # But not in the ipynb notebook
    assert "text_representation" not in tmpdir.join("test.ipynb").read()

    # modify the ipynb file in another editor
    nb = read("test.ipynb")
    nb.cells.append(new_markdown_cell("A new cell"))
    write(nb, "test.ipynb")

    tmp_repo.git.add("test.ipynb")

    # We try to commit one more time, this updates the py file
    with pytest.raises(
        HookExecutionError,
        match="files were modified by this hook",
    ):
        tmp_repo.index.commit("failing")

    # the text file has been updated
    assert "A new cell" in tmpdir.join("test.py").read()

    # trying to commit should fail again because we forgot to add the .py version
    with pytest.raises(HookExecutionError, match="git add test.py"):
        tmp_repo.index.commit("still failing")

    nb = read("test.ipynb")
    assert len(nb.cells) == 2

    # add the text file, now the commit will succeed
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("passing")

    # modify the .py file
    nb.cells.append(new_markdown_cell("A third cell"))
    write(nb, "test.py", fmt="py:percent")
    tmp_repo.git.add("test.py")

    # the pre-commit hook will update the .ipynb file
    with pytest.raises(HookExecutionError, match="git add test.ipynb"):
        tmp_repo.index.commit("failing")

    tmp_repo.git.add("test.ipynb")
    tmp_repo.index.commit("passing")

    nb = read("test.ipynb")
    assert len(nb.cells) == 3
