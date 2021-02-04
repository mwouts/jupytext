from nbformat.v4.nbbase import new_markdown_cell, new_notebook

from jupytext import write
from jupytext.cli import is_untracked, jupytext


def test_is_untracked(tmpdir, cwd_tmpdir, tmp_repo):
    # make a test file
    file = "test.txt"
    tmpdir.join(file).write("test file\n")

    # untracked
    assert is_untracked(file)

    # added, not committed
    tmp_repo.git.add(file)
    assert not is_untracked(file)

    # committed
    tmp_repo.index.commit("test")
    assert not is_untracked(file)

    # changed
    tmpdir.join(file).write("modified file\n")
    assert is_untracked(file)

    # added, not committed
    tmp_repo.git.add(file)
    assert not is_untracked(file)


def test_ignore_unmatched_ignores(tmpdir, cwd_tmpdir):
    # Unmatched file
    file = "test.txt"
    tmpdir.join(file).write("Hello\n")

    # Run jupytext
    status = jupytext(
        ["--from", "ipynb", "--to", "py:light", "--pre-commit-mode", file]
    )

    assert status == 0
    assert not tmpdir.join("test.py").exists()


def test_alert_untracked_alerts(tmpdir, cwd_tmpdir, tmp_repo, capsys):
    file = "test.py"
    tmpdir.join(file).write("print('hello')\n")

    # Run jupytext
    status = jupytext(["--from", ".py", "--to", "ipynb", "--pre-commit-mode", file])

    assert status != 0
    assert tmpdir.join("test.ipynb").exists()

    out = capsys.readouterr()
    assert "git add test.ipynb" in out.out


def test_alert_untracked_alerts_when_using_sync(tmpdir, cwd_tmpdir, tmp_repo, capsys):
    tmpdir.join("test.py").write("print('hello')\n")
    tmp_repo.git.add("test.py")

    tmpdir.join(".jupytext.toml").write('default_jupytext_formats = "ipynb,py"')

    # Run jupytext
    status = jupytext(["--sync", "--pre-commit-mode", "test.py"])

    assert status != 0
    assert tmpdir.join("test.ipynb").exists()

    out = capsys.readouterr()
    assert "git add test.ipynb" in out.out


def test_alert_untracked_alerts_for_modified(tmpdir, cwd_tmpdir, tmp_repo, capsys):
    # write test notebook
    nb = new_notebook(cells=[new_markdown_cell("A short notebook")])
    write(nb, "test.ipynb")

    # write existing output
    tmpdir.join("test.py").write("# Hello")

    # track output file
    tmp_repo.git.add("test.py")

    # Run jupytext
    status = jupytext(
        ["--from", "ipynb", "--to", "py:light", "--pre-commit-mode", "test.ipynb"]
    )

    assert status == 1
    out = capsys.readouterr()
    assert "git add test.py" in out.out


def test_alert_inconsistent_versions(tmpdir, cwd_tmpdir, tmp_repo, capsys):
    """Jupytext refuses to sync two inconsistent notebooks"""
    write(new_notebook(cells=[new_markdown_cell("A short py notebook")]), "test.py")
    write(
        new_notebook(
            cells=[new_markdown_cell("Another ipynb notebook")],
            metadata={"jupytext": {"formats": "ipynb,py"}},
        ),
        "test.ipynb",
    )

    # Add them both
    tmp_repo.git.add("test.py")
    tmp_repo.git.add("test.ipynb")

    # Run jupytext
    status = jupytext(["--sync", "--pre-commit-mode", "test.ipynb"])

    # The diff should be visible
    assert status == 1
    out = capsys.readouterr()
    assert (
        """--- test.py
+++ test.ipynb"""
        in out.err
    )
    assert """-# A short py notebook
+# Another ipynb notebook
"""
    assert "Error: test.ipynb and test.py are inconsistent" in out.err
    assert "git reset test.py && git checkout -- test.py" in out.err
    assert "git reset test.ipynb && git checkout -- test.ipynb" in out.err
