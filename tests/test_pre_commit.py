from textwrap import dedent

import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_markdown_cell, new_notebook

from jupytext import write
from jupytext.cli import jupytext

try:
    from pre_commit.main import main as pre_commit
except (ImportError, ModuleNotFoundError) as err:
    pytestmark = pytest.mark.skip(str(err))


def test_pre_commit_hook_for_new_file(
    tmpdir, cwd_tmpdir, tmp_repo, capsys, jupytext_repo_root, jupytext_repo_rev
):
    pre_commit_config_yaml = dedent(
        f"""
        repos:
        - repo: {jupytext_repo_root}
          rev: {jupytext_repo_rev}
          hooks:
          - id: jupytext
            args: [--sync]
        """
    )
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)

    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    # write test notebook and sync it to py:percent
    nb = new_notebook(cells=[new_markdown_cell("A short notebook")])
    write(nb, "test.ipynb")

    jupytext(["--set-formats", "ipynb,py:percent", "test.ipynb"])

    # try to commit it, should fail since the hook runs and makes changes
    tmp_repo.git.add("test.ipynb")
    with pytest.raises(HookExecutionError, match="files were modified by this hook"):
        tmp_repo.index.commit("failing")

    # try again, it will still fail because the output hasn't been added
    with pytest.raises(
        HookExecutionError, match="Output file test.py is not tracked in the git index"
    ):
        tmp_repo.index.commit("still failing")

    # add the new file, now the commit will succeed
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("passing")
    assert "test.ipynb" in tmp_repo.tree()
    assert "test.py" in tmp_repo.tree()


def test_pre_commit_hook_for_existing_changed_file(
    tmpdir, cwd_tmpdir, tmp_repo, capsys, jupytext_repo_root, jupytext_repo_rev
):
    # set up the tmpdir repo with pre-commit
    pre_commit_config_yaml = dedent(
        f"""
        repos:
        - repo: {jupytext_repo_root}
          rev: {jupytext_repo_rev}
          hooks:
          - id: jupytext
            args: [--from, ipynb, --to, "py:percent"]
        """
    )
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

    # TODO: Not sure this is the expected message?
    with pytest.raises(HookExecutionError, match="files were modified by this hook"):
        tmp_repo.index.commit("fails again")

    # once we add the changes, it will pass
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("succeeds")

    assert "test.ipynb" in tmp_repo.tree()
    assert "test.py" in tmp_repo.tree()
