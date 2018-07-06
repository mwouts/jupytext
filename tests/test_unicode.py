# coding: utf-8
import nbrmd
import pytest
from .utils import list_all_notebooks
import sys


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb') +
                         list_all_notebooks('.Rmd'))
def test_notebook_contents_is_unicode(nb_file):
    nb = nbrmd.readf(nb_file)

    for cell in nb.cells:
        if sys.version_info < (3, 0):
            assert cell.source == '' or isinstance(cell.source, unicode)
        else:
            assert isinstance(cell.source, str)


def test_write_non_ascii(tmpdir):
    nb = nbrmd.reads(u'Non-ascii contênt')
    nbrmd.writef(nb, str(tmpdir.join('notebook.Rmd')))
    nbrmd.writef(nb, str(tmpdir.join('notebook.ipynb')))
