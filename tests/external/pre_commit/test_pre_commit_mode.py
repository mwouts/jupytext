import os
import time

import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

from jupytext import read, write
from jupytext.cli import get_timestamp, git_timestamp, is_untracked, jupytext


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
        ["--from", "ipynb", "--to", "py:percent", "--pre-commit-mode", file]
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

    tmpdir.join("jupytext.toml").write('formats = "ipynb,py"')

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
        ["--from", "ipynb", "--to", "py:percent", "--pre-commit-mode", "test.ipynb"]
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


def test_pre_commit_local_config(tmpdir, cwd_tmpdir, tmp_repo, python_notebook, capsys):
    tmpdir.join("jupytext.toml").write_text(
        """notebook_metadata_filter = "-all"
cell_metadata_filter = "-all"
formats = "ipynb,py:percent"
""",
        encoding="utf-8",
    )

    write(python_notebook, str(tmpdir.join("test.ipynb")))

    # create the paired file
    jupytext(["--sync", "test.ipynb"])

    print("--------- test.ipynb ---------")
    print(tmpdir.join("test.ipynb").read_text("utf-8"))
    print("--------- test.py ---------")
    print(tmpdir.join("test.py").read_text("utf-8"))

    tmp_repo.git.add(".")

    capsys.readouterr()
    exit_code = jupytext(
        ["--pre-commit-mode", "--sync", "test.ipynb", "--show-changes"]
    )

    out, err = capsys.readouterr()
    assert not err, err
    assert "updating test" not in out.lower(), out
    assert exit_code == 0, out


def test_git_timestamp(tmpdir, cwd_tmpdir, tmp_repo):
    # No commit yet => return the file timestamp
    tmpdir.join("file_1").write("")
    assert git_timestamp("file_1") == get_timestamp("file_1")

    # Staged files are always considered more recent than committed files, i.e timestamp==inf
    time.sleep(0.1)
    tmpdir.join("file_2").write("")
    tmp_repo.git.add(".")

    assert get_timestamp("file_1") < get_timestamp("file_2")
    assert git_timestamp("file_1") == git_timestamp("file_2") == float("inf")

    tmp_repo.index.commit("Add file_1 and file_2")
    assert get_timestamp("file_1") < get_timestamp("file_2")
    assert git_timestamp("file_1") == git_timestamp("file_2") < float("inf")
    assert (
        git_timestamp("file_1")
        < get_timestamp("file_1") + 1
        < git_timestamp("file_1") + 2
    )

    # Git timestamps have a resolution of 1 sec, so if we want to see
    # different git timestamps between file_1 and file_2 we need this:
    time.sleep(1.2)

    # Here we just touch the file (content unchanged). The git timestamp is not modified
    tmpdir.join("file_1").write("")
    assert get_timestamp("file_1") > get_timestamp("file_2")
    assert git_timestamp("file_1") == git_timestamp("file_2") < float("inf")

    # When we modify the file then its "git_timestamp" becomes inf again
    tmpdir.join("file_1").write("modified")
    assert get_timestamp("file_1") > get_timestamp("file_2")
    assert float("inf") == git_timestamp("file_1") > git_timestamp("file_2")

    tmp_repo.git.add(".")
    assert float("inf") == git_timestamp("file_1") > git_timestamp("file_2")

    # When the file is committed its timestamp is the commit timestamp
    tmp_repo.index.commit("Update file_1")
    assert float("inf") > git_timestamp("file_1") > git_timestamp("file_2")

    # If a file is not in the git repo then we return its timestamp
    tmpdir.join("file_3").write("")
    assert git_timestamp("file_3") == get_timestamp("file_3")


@pytest.mark.parametrize(
    "commit_order", [["test.py", "test.ipynb"], ["test.ipynb", "test.py"]]
)
@pytest.mark.parametrize("sync_file", ["test.py", "test.ipynb"])
def test_sync_pre_commit_mode_respects_commit_order_780(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    python_notebook,
    commit_order,
    sync_file,
):
    file_1, file_2 = commit_order

    nb = python_notebook
    nb.metadata["jupytext"] = {"formats": "ipynb,py:percent"}
    nb.cells = [new_code_cell("1 + 1")]
    write(nb, file_1)

    tmp_repo.git.add(file_1)
    tmp_repo.index.commit(file_1)

    # This needs to >1 sec because commit timestamps have a one-second resolution
    time.sleep(1.2)

    nb.cells = [new_code_cell("2 + 2")]
    write(nb, file_2)

    tmp_repo.git.add(file_2)
    tmp_repo.index.commit(file_2)

    # Invert file timestamps
    ts_1 = os.stat(file_1).st_mtime
    ts_2 = os.stat(file_2).st_mtime
    os.utime(file_1, (ts_2, ts_2))
    os.utime(file_2, (ts_1, ts_1))

    jupytext(["--sync", "--pre-commit-mode", sync_file])

    for file in commit_order:
        nb = read(file)
        assert nb.cells[0].source == "2 + 2", file


@pytest.mark.requires_user_kernel_python3
def test_skip_execution(tmpdir, cwd_tmpdir, tmp_repo, python_notebook, capsys):
    write(
        new_notebook(cells=[new_code_cell("1 + 1")], metadata=python_notebook.metadata),
        "test.ipynb",
    )
    tmp_repo.index.add("test.ipynb")

    jupytext(["--execute", "--pre-commit-mode", "test.ipynb"])
    captured = capsys.readouterr()
    assert "Executing notebook" in captured.out

    nb = read("test.ipynb")
    assert nb.cells[0].execution_count == 1

    jupytext(["--execute", "--pre-commit-mode", "test.ipynb"])
    captured = capsys.readouterr()
    assert "skipped" in captured.out
