import nbformat
import pytest
import nbrmd
from nbrmd.compare import compare_notebooks
from .utils import list_r_notebooks

nbrmd.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('nb_file', list_r_notebooks('.ipynb'))
def test_identity_source_write_read(nb_file):
    """
    Test that writing the notebook with R, and read again,
    is the same as removing outputs
    """

    with open(nb_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    R = nbrmd.writes(nb1, ext='.R')
    nb2 = nbrmd.reads(R, ext='.R')

    compare_notebooks(nb1, nb2)
