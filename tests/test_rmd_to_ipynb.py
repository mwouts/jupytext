import sys
import pytest
from testfixtures import compare
import nbrmd
from .utils import list_all_notebooks


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('nb_file', list_all_notebooks('.Rmd'))
def test_identity_write_read(nb_file):
    """
    Test that writing the notebook with ipynb, and read again, yields identity
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        rmd = fp.read()

    nb = nbrmd.reads(rmd)
    rmd2 = nbrmd.writes(nb)

    compare(rmd, rmd2)


def test_two_blank_lines_as_cell_separator():
    rmd = """Some markdown
text


And a new cell
"""

    nb = nbrmd.reads(rmd)
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[0].source == 'Some markdown\ntext'
    assert nb.cells[1].source == 'And a new cell'
