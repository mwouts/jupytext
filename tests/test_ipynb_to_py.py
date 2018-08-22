import nbformat
import pytest
from testfixtures import compare
import nbrmd
from .utils import list_all_notebooks, remove_outputs

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

    py = nbrmd.writes(nb1, ext='.py')
    nb2 = nbrmd.reads(py, ext='.py')

    compare(remove_outputs(nb1), remove_outputs(nb2))
