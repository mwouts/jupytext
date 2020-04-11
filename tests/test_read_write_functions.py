from io import StringIO
from pathlib import Path
import nbformat
from nbformat.v4.nbbase import new_notebook, new_markdown_cell
import jupytext
from jupytext.compare import compare


def test_simple_hook(tmpdir):
    nb_file = str(tmpdir.join("notebook.ipynb"))
    md_file = str(tmpdir.join("notebook.md"))
    nbformat.write(new_notebook(cells=[new_markdown_cell("Some text")]), nb_file)

    nb = jupytext.read(nb_file)
    jupytext.write(nb, md_file)

    with open(md_file) as fp:
        text = fp.read()

    assert "Some text" in text.splitlines()


def test_simple_hook_with_explicit_format(tmpdir):
    nb_file = str(tmpdir.join("notebook.ipynb"))
    py_file = str(tmpdir.join("notebook.py"))
    nbformat.write(new_notebook(cells=[new_markdown_cell("Some text")]), nb_file)

    nb = jupytext.read(nb_file)
    jupytext.write(nb, py_file, fmt="py:percent")

    with open(py_file) as fp:
        text = fp.read()

    assert "# %% [markdown]" in text.splitlines()
    assert "# Some text" in text.splitlines()


def test_no_error_on_path_object(tmpdir):
    nb_file = Path(str(tmpdir.join("notebook.ipynb")))
    md_file = nb_file.with_suffix(".md")
    nbformat.write(new_notebook(cells=[new_markdown_cell("Some text")]), str(nb_file))

    nb = jupytext.read(nb_file)
    jupytext.write(nb, md_file)


def test_read_ipynb_from_stream():
    def stream():
        return StringIO(
            u"""{
 "cells": [
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "1 + 1"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 4
}
"""
        )

    nb = jupytext.read(stream())
    nb2 = jupytext.read(stream(), fmt="ipynb")
    compare(nb2, nb)


def test_read_py_percent_from_stream():
    def stream():
        return StringIO(
            u"""# %%
1 + 1
"""
        )

    nb = jupytext.read(stream())
    nb2 = jupytext.read(stream(), fmt="py:percent")
    compare(nb2, nb)
