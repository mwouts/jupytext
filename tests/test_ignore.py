import pytest

from jupytext import TextFileContentsManager
from jupytext.cli import jupytext


def test_ignore_works_on_a_non_existing_file(tmp_path, cwd_tmp_path, capsys):
    jupytext(["test.py", "--to", "ipynb", "--ignore", "test*.py"])


def test_warning_when_all_files_ignored(tmp_path, cwd_tmp_path, capsys):
    (tmp_path / "test.py").write_text("# to be ignored\n")
    jupytext(["test.py", "--to", "ipynb", "--ignore", "test*.py"])
    _, err = capsys.readouterr()
    assert "Warning: all input files were ignored" in err

    jupytext(["test.py", "--set-formats", "ipynb,py:percent", "--ignore", "test*.py"])
    _, err = capsys.readouterr()
    assert "Warning: all input files were ignored" in err


@pytest.mark.parametrize(
    "command", [["--to", "ipynb"], ["--set-formats", "ipynb,py:percent"]]
)
def test_ignored_files_are_ignored_at_the_cli(tmp_path, cwd_tmp_path, command):
    (tmp_path / "nb.py").write_text("# %%\n1 + 1\n")
    (tmp_path / "test.py").write_text("# to be ignored\n")

    jupytext(["nb.py", "test.py", "--ignore", "test*.py"] + command)
    assert (tmp_path / "nb.ipynb").exists()
    assert not (tmp_path / "test.ipynb").exists()


@pytest.mark.parametrize(
    "command", [["--to", "ipynb"], ["--set-formats", "ipynb,py:percent"]]
)
def test_ignore_files_through_config(tmp_path, cwd_tmp_path, command):
    (tmp_path / "jupytext.toml").write_text('ignore = ["test*.py"]')
    (tmp_path / "nb.py").write_text("# %%\n1 + 1\n")
    (tmp_path / "test.py").write_text("# to be ignored\n")

    jupytext(["nb.py", "test.py"] + command)
    assert (tmp_path / "nb.ipynb").exists()
    assert not (tmp_path / "test.ipynb").exists()


def test_ignored_files_are_not_notebooks(tmp_path, cwd_tmp_path):
    (tmp_path / "jupytext.toml").write_text('ignore = ["test*.py"]')
    (tmp_path / "nb.py").write_text("# %%\n1 + 1\n")
    (tmp_path / "test.py").write_text("# to be ignored\n")

    cm = TextFileContentsManager()
    cm.root_dir = str(tmp_path)

    model = cm.get("nb.py")
    assert model["type"] == "notebook"

    model = cm.get("test.py")
    assert model["type"] == "text"
