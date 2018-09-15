import pytest
from testfixtures import compare
import jupytext
from .utils import list_notebooks

jupytext.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('py_file',
                         [py_file for py_file in
                          list_notebooks('../jupytext') +
                          list_notebooks('.') if py_file.endswith('.py')])
def test_identity_source_write_read(py_file):
    with open(py_file) as fp:
        py = fp.read()

    nb = jupytext.reads(py, ext='.py')
    py2 = jupytext.writes(nb, ext='.py')

    compare(py, py2)
