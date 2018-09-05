import nbformat
import pytest
import jupytext
from jupytext.compare import compare_notebooks
from .utils import list_py_notebooks

jupytext.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('nb_file', list_py_notebooks('.ipynb'))
def test_identity_source_write_read(nb_file):
    """
    Test that writing the notebook with jupytext, and read again,
    is the same as removing outputs
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    py = jupytext.writes(nb1, ext='.py')
    nb2 = jupytext.reads(py, ext='.py')

    compare_notebooks(nb1, nb2)
