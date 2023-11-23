import jupytext
from jupytext.compare import compare


def test_identity_source_write_read(py_file):
    with open(py_file) as fp:
        py = fp.read()

    nb = jupytext.reads(py, "py")
    py2 = jupytext.writes(nb, "py")

    compare(py2, py)
