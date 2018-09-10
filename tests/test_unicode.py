# coding: utf-8
import sys
import pytest
import jupytext
from .utils import list_all_notebooks

try:
  unicode        # Python 2
except NameError:
  unicode = str  # Python 3


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb') +
                         list_all_notebooks('.Rmd'))
def test_notebook_contents_is_unicode(nb_file):
    nb = jupytext.readf(nb_file)

    for cell in nb.cells:
        if sys.version_info < (3, 0):
            assert cell.source == '' or isinstance(cell.source, unicode)
        else:
            assert isinstance(cell.source, str)


def test_write_non_ascii(tmpdir):
    nb = jupytext.reads(u'Non-ascii contênt', ext='.Rmd')
    jupytext.writef(nb, str(tmpdir.join('notebook.Rmd')))
    jupytext.writef(nb, str(tmpdir.join('notebook.ipynb')))
