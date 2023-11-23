import nbformat

import jupytext
from jupytext.compare import compare_notebooks


def test_identity_source_write_read(ipynb_py_file):
    """Test that writing the notebook with jupytext, and read again,
    is the same as removing outputs"""

    with open(ipynb_py_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    py = jupytext.writes(nb1, "py")
    nb2 = jupytext.reads(py, "py")

    compare_notebooks(nb2, nb1)
