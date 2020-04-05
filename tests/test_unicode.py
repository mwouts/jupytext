# coding: utf-8
import pytest
import jupytext
from .utils import list_notebooks

try:
    unicode  # Python 2
except NameError:
    unicode = str  # Python 3


@pytest.mark.parametrize("nb_file", list_notebooks() + list_notebooks("Rmd"))
def test_notebook_contents_is_unicode(nb_file):
    nb = jupytext.read(nb_file)

    for cell in nb.cells:
        assert cell.source == "" or isinstance(cell.source, unicode)


def test_write_non_ascii(tmpdir):
    nb = jupytext.reads(u"Non-ascii contênt", "Rmd")
    jupytext.write(nb, str(tmpdir.join("notebook.Rmd")))
    jupytext.write(nb, str(tmpdir.join("notebook.ipynb")))
