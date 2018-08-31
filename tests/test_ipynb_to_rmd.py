import nbformat
import pytest
import nbrmd
from nbrmd.compare import compare_notebooks
from .utils import list_all_notebooks

nbrmd.file_format_version.FILE_FORMAT_VERSION = {}


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

    rmd = nbrmd.writes(nb1)
    nb2 = nbrmd.reads(rmd)

    compare_notebooks(nb1, nb2)
