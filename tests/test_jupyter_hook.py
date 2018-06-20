import pytest
import os
import nbrmd
from utils import list_all_notebooks, remove_outputs


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_rmd_is_ok(nb_file, tmpdir):
    nb = nbrmd.readf(nb_file)
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_rmd(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    nb2 = nbrmd.readf(tmp_rmd)

    assert remove_outputs(nb) == remove_outputs(nb2)


def test_no_rmd_on_not_notebook(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_rmd(model=dict(type='not notebook'), path=tmp_ipynb)
    assert not os.path.isfile(tmp_rmd)


def test_no_rmd_on_not_v4(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_rmd(model=dict(type='notebook', content=dict(nbformat=3)), path=tmp_ipynb)

    assert not os.path.isfile(tmp_rmd)
