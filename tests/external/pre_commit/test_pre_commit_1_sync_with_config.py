import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_markdown_cell
from pre_commit.main import main as pre_commit

from jupytext import TextFileContentsManager, read


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

    tmpdir.join("jupytext.toml").write('formats = "ipynb,py:percent"\n')

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

    # modify the ipynb file in Jupyter
    # Reload the notebook
    nb = cm.get("test.ipynb")["content"]
    nb.cells.append(new_markdown_cell("A new cell"))
    cm.save(dict(type="notebook", content=nb), "test.ipynb")

    # The text representation metadata is in the py file
    assert "text_representation" in tmpdir.join("test.py").read()
    # But not in the ipynb notebook
    assert "text_representation" not in tmpdir.join("test.ipynb").read()

    # the text file has been updated (and the ipynb file as well)
    assert "A new cell" in tmpdir.join("test.py").read()
    nb = read("test.ipynb")
    assert len(nb.cells) == 2

    # add both files, the commit will succeed
    tmp_repo.git.add("test.ipynb")
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("passing")
