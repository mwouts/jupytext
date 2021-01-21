# -*- coding: utf-8 -*-

from pathlib import Path
from textwrap import dedent

import pytest
from nbformat.v4.nbbase import new_markdown_cell, new_notebook

from jupytext import write
from jupytext.cli import is_untracked, jupytext, system

from .utils import requires_pre_commit

try:
    from pre_commit.main import main as pre_commit
except (ImportError, ModuleNotFoundError):
    pre_commit = None


def git_in_tmpdir(tmpdir):
    """Return a function that will execute git instruction in the desired directory"""

    def git(*args):
        out = system("git", *args, cwd=str(tmpdir))
        print(out)
        return out

    git("init")
    git("status")
    git("config", "user.name", "jupytext-test-cli")
    git("config", "user.email", "jupytext@tests.com")

    return git


def system_in_tmpdir(tmpdir):
    """Return a function that will execute system commands in the desired directory"""

    def system_(*args):
        return system(*args, cwd=str(tmpdir))

    return system_


def test_is_untracked(tmpdir):
    git = git_in_tmpdir(tmpdir)

    # make a test file
    file = tmpdir.join("test.txt")
    file.write("test file\n")
    file = str(file)

    with tmpdir.as_cwd():
        # untracked
        assert is_untracked(file)

        # added, not committed
        git("add", file)
        assert not is_untracked(file)

        # committed
        git("commit", "-m", "'test'")
        assert not is_untracked(file)


def test_ignore_unmatched_ignores(tmpdir):
    # Unmatched file
    file = tmpdir.join("test.txt")
    file.write("Hello\n")

    # Run jupytext
    status = jupytext(
        ["--from", "ipynb", "--to", "py:light", "--ignore-unmatched", str(file)]
    )

    assert status == 0
    assert not tmpdir.join("test.py").exists()


def test_alert_untracked_alerts(tmpdir):
    git_in_tmpdir(tmpdir)

    file = tmpdir.join("test.py")
    file.write("print('hello')\n")

    # Run jupytext
    with tmpdir.as_cwd():
        status = jupytext(
            ["--from", ".py", "--to", "ipynb", "--alert-untracked", str(file)]
        )

    assert status != 0
    assert tmpdir.join("test.ipynb").exists()


def test_alert_untracked_alerts_when_using_sync(tmpdir):
    git_in_tmpdir(tmpdir)

    file = tmpdir.join("test.py")
    file.write("print('hello')\n")

    tmpdir.join(".jupytext.toml").write('default_jupytext_formats = "ipynb,py"')

    # Run jupytext
    with tmpdir.as_cwd():
        status = jupytext(["--sync", "--alert-untracked", str(file)])

    assert status != 0
    assert tmpdir.join("test.ipynb").exists()


def test_alert_untracked_not_alerts_for_tracked(tmpdir):
    git = git_in_tmpdir(tmpdir)

    # write test notebook
    nb = new_notebook(cells=[new_markdown_cell("A short notebook")])
    nb_file = str(tmpdir.join("test.ipynb"))
    write(nb, nb_file)

    # write existing output
    tmpdir.join("test.py").write("# Hello")

    # track output file
    git("add", str("test.py"))

    # Run jupytext
    with tmpdir.as_cwd():
        status = jupytext(
            ["--from", "ipynb", "--to", "py:light", "--alert-untracked", str(nb_file)]
        )

    assert status == 0


@requires_pre_commit
def test_pre_commit_hook_for_new_file(tmpdir):
    # get the path and revision of this repo, to use with pre-commit
    repo_root = str(Path(__file__).parent.parent.resolve())
    repo_rev = system("git", "rev-parse", "HEAD", cwd=repo_root).strip()

    # set up the tmpdir repo with pre-commit
    git = git_in_tmpdir(tmpdir)

    pre_commit_config_yaml = dedent(
        f"""
        repos:
        - repo: {repo_root}
          rev: {repo_rev}
          hooks:
          - id: jupytext
            args: [--sync]
        """
    )
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)
    git("add", ".pre-commit-config.yaml")
    with tmpdir.as_cwd():
        pre_commit(["install", "--install-hooks", "-f"])

    # write test notebook and sync it to py:percent
    nb = new_notebook(cells=[new_markdown_cell("A short notebook")])
    nb_file = str(tmpdir.join("test.ipynb"))
    py_file = str(tmpdir.join("test.py"))
    write(nb, nb_file)

    with tmpdir.as_cwd():
        jupytext(["--set-formats", "ipynb,py:percent", nb_file])

    # try to commit it, should fail since the hook runs and makes changes
    git("add", nb_file)
    with pytest.raises(SystemExit):
        git("commit", "-m", "failing")

    # try again, it will still fail because the output hasn't been added
    with pytest.raises(SystemExit):
        git("commit", "-m", "still failing")

    # add the new file, now the commit will succeed
    git("add", py_file)
    git("commit", "-m", "passing")
    assert "test.ipynb" in git("ls-files")
    assert "test.py" in git("ls-files")


@requires_pre_commit
def test_pre_commit_hook_for_existing_changed_file(tmpdir):
    # get the path and revision of this repo, to use with pre-commit
    repo_root = str(Path(__file__).parent.parent.resolve())
    repo_rev = system("git", "rev-parse", "HEAD", cwd=repo_root).strip()

    git = git_in_tmpdir(tmpdir)

    # set up the tmpdir repo with pre-commit
    pre_commit_config_yaml = dedent(
        f"""
        repos:
        - repo: {repo_root}
          rev: {repo_rev}
          hooks:
          - id: jupytext
            args: [--from, ipynb, --to, "py:percent"]
        """
    )
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)
    git("add", ".pre-commit-config.yaml")
    with tmpdir.as_cwd():
        pre_commit(["install", "--install-hooks"])

    # write test notebook and output file
    nb = new_notebook(cells=[new_markdown_cell("A short notebook")])
    nb_file = str(tmpdir.join("test.ipynb"))
    write(nb, nb_file)
    py_file = str(tmpdir.join("test.py"))
    jupytext(["--from", "ipynb", "--to", "py:percent", str(nb_file)])

    git("add", ".")
    git("commit", "-m", "test")

    # make a change to the notebook
    nb = new_notebook(cells=[new_markdown_cell("Some other text")])
    write(nb, nb_file)

    git("add", nb_file)
    # now a commit will fail, and keep failing until we add the new
    # changes made to the existing output to the index ourselves
    with pytest.raises(SystemExit):
        git("commit", "-m", "fails")

    with pytest.raises(SystemExit):
        git("commit", "-m", "fails again")

    # once we add the changes, it will pass
    git("add", py_file)
    git("commit", "-m", "succeeds")

    assert "test.ipynb" in git("ls-files")
    assert "test.py" in git("ls-files")
