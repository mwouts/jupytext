from nbrmd import RmdFileContentsManager, readf
from .utils import list_all_notebooks, remove_outputs,\
    remove_outputs_and_header
import os
import sys
import pytest


@pytest.mark.skipif(isinstance(RmdFileContentsManager, str),
                    reason=RmdFileContentsManager)
def test_create_contentsmanager():
    RmdFileContentsManager()


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(RmdFileContentsManager, str),
                    reason=RmdFileContentsManager)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_load_save_rename(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'

    cm = RmdFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open ipynb, save Rmd, reopen
    nb = readf(nb_file)
    cm.save(model=dict(type='notebook', content=nb), path=tmp_rmd)
    nb_rmd = cm.get(tmp_rmd)
    assert remove_outputs(nb) == remove_outputs(nb_rmd['content'])

    # save ipynb
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # rename ipynb
    cm.rename(tmp_ipynb, 'new.ipynb')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))

    assert os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.Rmd')))
