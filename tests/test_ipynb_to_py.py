import nbformat
import nbrmd
import pytest
from testfixtures import compare
from .utils import list_all_notebooks, remove_outputs, \
    remove_outputs_and_header
import re


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_identity_source_write_read(nb_file):
    """
    Test that writing the notebook with rmd, and read again,
    is the same as removing outputs
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    py = nbrmd.writes(nb1, ext='.py')
    nb2 = nbrmd.reads(py, ext='.py')

    print(py)

    compare(remove_outputs(nb1), remove_outputs(nb2))
