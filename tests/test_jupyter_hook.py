import pytest
import os
import nbrmd
from tests.utils import list_all_notebooks, filter_output_and_compare_notebooks


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_rmd_is_ok(nb_file, tmpdir):
    nb = nbrmd.readf(nb_file)
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.jupyter_hook.pre_save_hook(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    nb2 = nbrmd.readf(tmp_rmd)

    filter_output_and_compare_notebooks(nb, nb2)


def test_no_rmd_on_not_notebook(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.jupyter_hook.pre_save_hook(model=dict(type='not notebook'), path=tmp_ipynb)
    assert not os.path.isfile(tmp_rmd)


def test_no_rmd_on_not_v4(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.jupyter_hook.pre_save_hook(model=dict(type='notebook', content=dict(nbformat=3)), path=tmp_ipynb)

    assert not os.path.isfile(tmp_rmd)
