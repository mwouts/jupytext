import pytest
import os
import nbrmd
from tests.utils import list_all_notebooks, filter_output_and_compare_notebooks


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_pre_save_hook(nb_file, tmpdir):
    nb = nbrmd.readf(nb_file)
    tmp_ipynb = os.path.join(tmpdir, 'notebook.ipynb')
    tmp_rmd = os.path.join(tmpdir, 'notebook.Rmd')

    nbrmd.jupyter_hook.pre_save_hook(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    nb2 = nbrmd.readf(tmp_rmd)

    filter_output_and_compare_notebooks(nb, nb2)
