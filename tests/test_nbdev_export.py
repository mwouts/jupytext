from copy import copy

import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

from jupytext import reads, writes
from jupytext.compare import compare_notebooks


@pytest.fixture
def nbdev_notebook(python_notebook):
    return new_notebook(
        metadata=copy(python_notebook.metadata),
        cells=[
            new_markdown_cell("A markdown cell"),
            new_code_cell("# A non-exported code cell\n1 + 1"),
            new_code_cell("#export\n# An exported code cell\n2 + 2"),
        ],
    )


@pytest.mark.parametrize("comment_out_non_nbdev_exported_cells", [True, False])
def test_use_nbdev_export(nbdev_notebook, comment_out_non_nbdev_exported_cells):
    nbdev_notebook.metadata["jupytext"] = {
        "comment_out_non_nbdev_exported_cells": comment_out_non_nbdev_exported_cells
    }

    py = writes(nbdev_notebook, fmt="py:percent")

    # the cell marked with "export" is always exported
    assert "\n2 + 2" in py

    # the cell not marked with "export" is not exported when comment_out_non_nbdev_exported_cells is True
    assert ("\n1 + 1" in py) != comment_out_non_nbdev_exported_cells

    # test the round trip
    nb = reads(py, fmt="py:percent")
    compare_notebooks(nb, nbdev_notebook)
