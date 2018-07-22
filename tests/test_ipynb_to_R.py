import nbformat
import pytest
from testfixtures import compare
import nbrmd
from .utils import list_all_notebooks, remove_outputs


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_identity_source_write_read(nb_file):
    """
    Test that writing the notebook with R, and read again,
    is the same as removing outputs
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    R = nbrmd.writes(nb1, ext='.R')
    nb2 = nbrmd.reads(R, ext='.R')

    compare(remove_outputs(nb1), remove_outputs(nb2))
