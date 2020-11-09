import pytest
from copy import deepcopy
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook
from jupytext.combine import combine_inputs_with_outputs
from jupytext.compare import compare_notebooks, compare
import jupytext
from .utils import list_notebooks


def test_combine():
    nb_source = new_notebook(
        cells=[
            new_markdown_cell("Markdown text"),
            new_code_cell("a=3"),
            new_code_cell("a+1"),
            new_code_cell("a+1"),
            new_markdown_cell("Markdown text"),
            new_code_cell("a+2"),
        ]
    )

    nb_outputs = new_notebook(
        cells=[
            new_markdown_cell("Markdown text"),
            new_code_cell("a=3"),
            new_code_cell("a+1"),
            new_code_cell("a+2"),
            new_markdown_cell("Markdown text"),
        ]
    )

    nb_outputs.cells[2].outputs = ["4"]
    nb_outputs.cells[3].outputs = ["5"]

    nb_source = combine_inputs_with_outputs(nb_source, nb_outputs)

    assert nb_source.cells[2].outputs == ["4"]
    assert nb_source.cells[3].outputs == []
    assert nb_source.cells[5].outputs == ["5"]


def test_read_text_and_combine_with_outputs(tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook.py"

    with (open(str(tmpdir.join(tmp_script)), "w")) as fp:
        fp.write(
            """# ---
# jupyter:
#   jupytext_formats: ipynb,py:light
# ---

1+1

2+2

3+3
"""
        )

    with (open(str(tmpdir.join(tmp_ipynb)), "w")) as fp:
        fp.write(
            """{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "2"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "1+1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "6"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "3+3"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 2
}
"""
        )

    # create contents manager
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # load notebook from script
    model = cm.get(tmp_script)
    nb = model["content"]

    assert nb.cells[0]["source"] == "1+1"
    assert nb.cells[1]["source"] == "2+2"
    assert nb.cells[2]["source"] == "3+3"

    # No output for the second cell, which is not in the ipynb
    assert nb.cells[0]["outputs"]
    assert not nb.cells[1]["outputs"]
    assert nb.cells[2]["outputs"]

    assert len(nb.cells) == 3


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all"))
def test_combine_stable(nb_file):
    nb_org = jupytext.read(nb_file)
    nb_source = deepcopy(nb_org)
    nb_outputs = deepcopy(nb_org)

    for cell in nb_source.cells:
        cell.outputs = []

    nb_source = combine_inputs_with_outputs(nb_source, nb_outputs)
    compare_notebooks(nb_source, nb_org)


def test_combine_reorder():
    nb_source = new_notebook(
        cells=[
            new_markdown_cell("Markdown text"),
            new_code_cell("1+1"),
            new_code_cell("2+2"),
            new_code_cell("3+3"),
            new_markdown_cell("Markdown text"),
            new_code_cell("4+4"),
        ]
    )

    nb_outputs = new_notebook(
        cells=[
            new_markdown_cell("Markdown text"),
            new_code_cell("2+2"),
            new_code_cell("4+4"),
            new_code_cell("1+1"),
            new_code_cell("3+3"),
            new_markdown_cell("Markdown text"),
        ]
    )

    nb_outputs.cells[1].outputs = ["4"]
    nb_outputs.cells[2].outputs = ["8"]
    nb_outputs.cells[3].outputs = ["2"]
    nb_outputs.cells[4].outputs = ["6"]

    nb_source = combine_inputs_with_outputs(nb_source, nb_outputs)

    assert nb_source.cells[1].outputs == ["2"]
    assert nb_source.cells[2].outputs == ["4"]
    assert nb_source.cells[3].outputs == ["6"]
    assert nb_source.cells[5].outputs == ["8"]


def test_combine_split():
    nb_source = new_notebook(cells=[new_code_cell("1+1"), new_code_cell("2+2")])

    nb_outputs = new_notebook(cells=[new_code_cell("1+1\n2+2")])

    nb_outputs.cells[0].outputs = ["4"]

    nb_source = combine_inputs_with_outputs(nb_source, nb_outputs)

    assert nb_source.cells[0].outputs == []
    assert nb_source.cells[1].outputs == ["4"]


def test_combine_refactor():
    nb_source = new_notebook(
        cells=[new_code_cell("a=1"), new_code_cell("a+1"), new_code_cell("a+2")]
    )

    nb_outputs = new_notebook(
        cells=[new_code_cell("b=1"), new_code_cell("b+1"), new_code_cell("b+2")]
    )

    nb_outputs.cells[1].outputs = ["2"]
    nb_outputs.cells[2].outputs = ["3"]

    nb_source = combine_inputs_with_outputs(nb_source, nb_outputs)

    assert nb_source.cells[0].outputs == []
    assert nb_source.cells[1].outputs == ["2"]
    assert nb_source.cells[2].outputs == ["3"]


def test_combine_attachments():
    nb_source = new_notebook(
        cells=[new_markdown_cell("![image.png](attachment:image.png)")]
    )

    nb_outputs = new_notebook(
        cells=[
            new_markdown_cell(
                "![image.png](attachment:image.png)",
                attachments={"image.png": {"image/png": "SOME_LONG_IMAGE_CODE...=="}},
            )
        ]
    )

    nb_source = combine_inputs_with_outputs(nb_source, nb_outputs)
    compare(nb_source, nb_outputs)
