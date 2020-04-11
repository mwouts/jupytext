import pytest
from jupytext.compare import compare
import jupytext
from .utils import list_notebooks
from .utils import skip_if_dict_is_not_ordered


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("Rmd"))
def test_identity_write_read(nb_file, no_jupytext_version_number):
    """Test that writing the notebook with ipynb, and read again, yields identity"""

    with open(nb_file) as fp:
        rmd = fp.read()

    nb = jupytext.reads(rmd, "Rmd")
    rmd2 = jupytext.writes(nb, "Rmd")

    compare(rmd2, rmd)


def test_two_blank_lines_as_cell_separator():
    rmd = """Some markdown
text


And a new cell
"""

    nb = jupytext.reads(rmd, "Rmd")
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[0].source == "Some markdown\ntext"
    assert nb.cells[1].source == "And a new cell"
