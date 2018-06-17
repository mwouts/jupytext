import nbformat
import nbrmd
import pytest
from utils import list_all_notebooks, filter_output_and_compare_notebooks


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_identity_source_write_read(nb_file):
    """
    Test that writing the notebook with rmd, and read again, is the same as removing outputs
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        nb = nbformat.read(fp, as_version=4)

    rmd = nbrmd.nbrmd.writes(nb)
    nb2 = nbrmd.nbrmd.reads(rmd)

    filter_output_and_compare_notebooks(nb, nb2)
