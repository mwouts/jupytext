"""
Here we test the --check-source-is-newer option of the jupytext CLI
"""

import os
from jupytext import cli
from jupytext import write

import pytest


def test_check_source_is_newer_when_using_jupytext_to(tmp_path, python_notebook):
    tmp_ipynb = tmp_path / "notebook.ipynb"
    tmp_py = tmp_path / "notebook.py"
    write(python_notebook, tmp_ipynb, fmt="ipynb")

    # First, we convert the .ipynb to .py
    cli.jupytext([str(tmp_ipynb), "--to", "py", "--check-source-is-newer"])
    assert tmp_py.exists()

    # Now, we modify the .py file so that it is more recent than the .ipynb file
    text = tmp_py.read_text() + "\n# A new comment"
    tmp_py.write_text(text)

    # We can convert the .py to .ipynb because the .py is more recent than the .ipynb
    cli.jupytext([str(tmp_py), "--to", "ipynb", "--check-source-is-newer"])

    # We modify the .ipynb file so that it is more recent than the .py file
    text = tmp_ipynb.read_text().replace("A new comment", "Another new comment")
    tmp_ipynb.write_text(text)

    # Now, trying to convert the .py to .ipynb raises an error because the .py is older than the .ipynb
    with pytest.raises(ValueError, match=r"Source .*notebook\.py.* is older than destination .*notebook\.ipynb.*"):
        cli.jupytext([str(tmp_py), "--to", "ipynb", "--check-source-is-newer"])


def test_check_source_is_newer_when_using_jupytext_sync(tmp_path, python_notebook):
    tmp_ipynb = tmp_path / "notebook.ipynb"
    tmp_py = tmp_path / "notebook.py"
    write(python_notebook, tmp_ipynb, fmt="ipynb")

    # First, we turn the notebook into a paired notebook
    cli.jupytext([str(tmp_ipynb), "--set-formats", "ipynb,py", "--check-source-is-newer"])
    assert tmp_py.exists()

    # Running sync on the .py file works as .py is always more recent after a --sync operation
    cli.jupytext([str(tmp_py), "--sync", "--check-source-is-newer"])

    # Make .ipynb slightly older again to ensure .py is newer
    stat = os.stat(tmp_ipynb)
    os.utime(tmp_ipynb, (stat.st_atime, stat.st_mtime - 1))

    # Now, trying to sync the .ipynb to .py raises an error because .ipynb is older than .py
    with pytest.raises(ValueError, match=r"Source .*notebook\.ipynb.* is older than paired file .*notebook\.py.*"):
        cli.jupytext([str(tmp_ipynb), "--sync", "--check-source-is-newer"])

    # We modify the .ipynb file so that it is more recent than the .py file
    text = tmp_ipynb.read_text().replace("A short notebook", "A short notebook with a modification")
    tmp_ipynb.write_text(text)

    # Make .py slightly older to ensure .ipynb is newer
    stat = os.stat(tmp_py)
    os.utime(tmp_py, (stat.st_atime, stat.st_mtime - 1))

    # Now, trying to sync the .py to .ipynb raises an error because the .py is older than the .ipynb
    with pytest.raises(ValueError, match=r"Source .*notebook\.py.* is older than paired file .*notebook\.ipynb.*"):
        cli.jupytext([str(tmp_py), "--sync", "--check-source-is-newer"])

    # Running sync on the .ipynb file works as .ipynb is now more recent than .py
    cli.jupytext([str(tmp_ipynb), "--sync", "--check-source-is-newer"])
