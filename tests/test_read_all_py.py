import pytest
from jupytext.compare import compare
import jupytext
from .utils import list_notebooks


@pytest.mark.parametrize(
    "py_file",
    [
        py_file
        for py_file in list_notebooks("../jupytext") + list_notebooks(".")
        if py_file.endswith(".py")
        if "folding_markers" not in py_file
    ],
)
def test_identity_source_write_read(py_file):
    with open(py_file) as fp:
        py = fp.read()

    nb = jupytext.reads(py, "py")
    py2 = jupytext.writes(nb, "py")

    compare(py2, py)
