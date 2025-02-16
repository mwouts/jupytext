from copy import deepcopy

import pytest
from nbformat.v4 import new_code_cell

from jupytext import writes
from jupytext.config import JupytextConfiguration


@pytest.mark.parametrize("config", [{"notebook_metadata_filter": "language_info"}, {}])
def test_md_myst_has_no_lexer_unless_language_info_is_set(
    config, python_notebook, no_jupytext_version_number
):
    nb = deepcopy(python_notebook)
    nb.cells.append(new_code_cell("1+ 1"))

    md = writes(nb, fmt="md:myst", config=JupytextConfiguration(**config))
    code_lines = [line for line in md.splitlines() if line.startswith("```{code-cell}")]
    assert code_lines == ["```{code-cell} ipython3"] if config else ["```{code-cell}"]
