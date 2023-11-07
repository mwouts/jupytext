import pytest
from nbformat.v4.nbbase import new_markdown_cell, new_notebook

import jupytext
from jupytext.compare import compare


def test_markdown_cell_with_backslash_is_encoded_with_raw_string(
    nb=new_notebook(cells=[new_markdown_cell(r"A $\LaTeX$ expression")]),
    py=r'''# %% [markdown]
r"""
A $\LaTeX$ expression
"""
''',
):
    nb.metadata["jupytext"] = {
        "cell_markers": '"""',
        "notebook_metadata_filter": "-all",
    }
    py2 = jupytext.writes(nb, "py:percent")
    compare(py2, py)


@pytest.mark.parametrize("r", ["r", "R"])
@pytest.mark.parametrize("triple_quote", ['"""', "'''"])
@pytest.mark.parametrize("expr", ["$\\LaTeX$", "common"])
def test_raw_string_is_stable_over_round_trip(r, triple_quote, expr):
    py = f"""# %% [markdown]
{r}{triple_quote}
A {expr} expression
{triple_quote}
"""

    nb = jupytext.reads(py, "py:percent")

    (cell,) = nb.cells
    assert cell.cell_type == "markdown"
    assert cell.source == f"A {expr} expression"
    assert cell.metadata["cell_marker"] == f"{r}{triple_quote}"

    py2 = jupytext.writes(nb, "py:percent")
    compare(py2, py)
