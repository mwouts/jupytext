import nbformat

import jupytext
from jupytext.compare import compare_notebooks


def test_identity_source_write_read(ipynb_py_R_jl_file):
    """Test that writing the notebook with rmd, and read again,
    is the same as removing outputs"""

    with open(ipynb_py_R_jl_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    rmd = jupytext.writes(nb1, "Rmd")
    nb2 = jupytext.reads(rmd, "Rmd")

    compare_notebooks(nb2, nb1, "Rmd")
