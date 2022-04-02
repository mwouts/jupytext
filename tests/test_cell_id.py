import pytest

from jupytext import reads
from jupytext.compare import compare_notebooks


@pytest.fixture()
def text_notebook():
    return """# %% [markdown]
# Some text

# %%
1 + 1
"""


def test_cell_ids_are_distinct(text_notebook):
    nb = reads(text_notebook, "py:percent")
    assert nb.cells[0].id != nb.cells[1].id


def test_cell_ids_are_deterministic(text_notebook):
    nb = reads(text_notebook, "py:percent")
    nb2 = reads(text_notebook, "py:percent")
    compare_notebooks(nb2, nb, compare_ids=True)
