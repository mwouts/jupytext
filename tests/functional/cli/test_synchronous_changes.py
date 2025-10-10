"""
These tests ensure that Jupytext raises an error when a file loaded by Jupytext
changes while Jupytext is running.

To make the simultaneous change occur in the tests, we monkey-patch the function `create_prefix_dir`
which is called just before writing the file back to disk.
"""

from jupytext import cli
from jupytext import write

import pytest


def test_jupytext_sync_raises_on_synchronous_edits(tmp_path, python_notebook, monkeypatch):
    (tmp_path / "jupytext.toml").write_text("""formats = "ipynb,py" """)

    tmp_py = tmp_path / "notebook.py"
    tmp_ipynb = tmp_path / "notebook.ipynb"
    write(python_notebook, tmp_py, fmt="py:percent")

    def edit_py_file(path):
        text = tmp_py.read_text() + "\n# A new comment"
        tmp_py.write_text(text)

    # The print statements help to see which Jupytext actions correspond to which test
    print("Testing a synchronous edit on a .py file that does not have a .ipynb counterpart")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", edit_py_file)
    with pytest.raises(
        cli.SynchronousModificationError, match=r"The file .*notebook\.py.* was modified while Jupytext was running"
    ):
        cli.jupytext([str(tmp_py), "--sync"])

    assert not tmp_ipynb.exists()

    print("Testing the normal sync command that creates the .ipynb file")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", None)
    cli.jupytext([str(tmp_py), "--sync"])
    assert tmp_ipynb.exists()

    print("Testing a synchronous edit on a .py file that does have a .ipynb counterpart")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", edit_py_file)
    with pytest.raises(
        cli.SynchronousModificationError, match=r"The file .*notebook\.py.* was modified while Jupytext was running"
    ):
        cli.jupytext([str(tmp_py), "--sync"])

    print("Testing a synchronous deletion of the .ipynb file")

    def rm_ipynb_file(path):
        tmp_ipynb.unlink()

    monkeypatch.setattr(cli, "_callback_on_lazy_write", rm_ipynb_file)
    with pytest.raises(
        cli.SynchronousModificationError, match=r"The file .*notebook\.ipynb.* was deleted while Jupytext was running"
    ):
        cli.jupytext([str(tmp_py), "--sync"])

    assert not tmp_ipynb.exists()

    print("Testing a synchronous creation of the .ipynb file")

    def create_ipynb_file(path):
        tmp_ipynb.write_text("{}")

    monkeypatch.setattr(cli, "_callback_on_lazy_write", create_ipynb_file)
    with pytest.raises(
        cli.SynchronousModificationError, match=r"The file .*notebook\.ipynb.* was created while Jupytext was running"
    ):
        cli.jupytext([str(tmp_py), "--sync"])


def test_jupytext_to_raises_on_synchronous_edits(tmp_path, python_notebook, monkeypatch):
    tmp_py = tmp_path / "notebook.py"
    tmp_ipynb = tmp_path / "notebook.ipynb"
    write(python_notebook, tmp_py, fmt="py:percent")

    def edit_py_file(path):
        text = tmp_py.read_text() + "\n# A new comment"
        tmp_py.write_text(text)

    # The print statements help to see which Jupytext actions correspond to which test
    print("Testing a synchronous edit on a .py file")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", edit_py_file)
    with pytest.raises(
        cli.SynchronousModificationError, match=r"The file .*notebook\.py.* was modified while Jupytext was running"
    ):
        cli.jupytext([str(tmp_py), "--to", "ipynb"])

    assert not tmp_ipynb.exists()

    print("Testing the normal to command that creates the .ipynb file")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", None)
    cli.jupytext([str(tmp_py), "--to", "ipynb"])
    assert tmp_ipynb.exists()

    print("Testing a synchronous edit on a .py file that is not paired to a .ipynb file")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", edit_py_file)
    # This one works as the .py file is not paired, so it is not read
    cli.jupytext([str(tmp_ipynb), "--to", "py"])

    print("Turning the .py file into a paired notebook")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", None)
    cli.jupytext([str(tmp_ipynb), "--set-formats", "ipynb,py"])

    print("Testing a synchronous edit on a paired .py file")
    monkeypatch.setattr(cli, "_callback_on_lazy_write", edit_py_file)
    with pytest.raises(
        cli.SynchronousModificationError, match=r"The file .*notebook\.py.* was modified while Jupytext was running"
    ):
        cli.jupytext([str(tmp_py), "--to", "ipynb"])
