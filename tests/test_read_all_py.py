import pytest
from testfixtures import compare
import jupytext
from .utils import list_all_notebooks

jupytext.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('py_file', list_all_notebooks('.py', '../jupytext') +
                         list_all_notebooks('.py'))
def test_identity_source_write_read(py_file):
    with open(py_file) as fp:
        py = fp.read()

    nb = jupytext.reads(py, ext='.py')
    py2 = jupytext.writes(nb, ext='.py')

    compare(py, py2)
