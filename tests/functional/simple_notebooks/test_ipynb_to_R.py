import nbformat
import pytest

import jupytext
from jupytext.compare import compare_notebooks


@pytest.mark.parametrize("ext", [".r", ".R"])
def test_identity_source_write_read(ipynb_R_file, ext):
    """
    Test that writing the notebook with R, and read again,
    is the same as removing outputs
    """

    with open(ipynb_R_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    R = jupytext.writes(nb1, ext)
    nb2 = jupytext.reads(R, ext)

    compare_notebooks(nb2, nb1)
