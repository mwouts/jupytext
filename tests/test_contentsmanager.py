from nbrmd.cm import RmdFileContentsManager
from utils import list_all_notebooks, remove_outputs
import os
import pytest
from nbrmd import readf


def test_create_contentsmanager():
    RmdFileContentsManager()


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_load_save_rename(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))
    tmp_md = str(tmpdir.join('notebook.md'))

    cm = RmdFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open ipynb, save md, reopen
    nb = readf(nb_file)
    cm.save(model=dict(type='notebook', content=nb), path=tmp_md)
    nb_md = cm.get(tmp_md)
    assert remove_outputs(nb) == nb_md['content']

    # save Rmd, reopen
    cm.save(model=dict(type='notebook', content=nb), path=tmp_rmd)
    nb_rmd = cm.get(tmp_rmd)
    assert remove_outputs(nb) == nb_rmd['content']

    # save ipynb
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # rename ipynb
    cm.rename(tmp_ipynb, str(tmpdir.join('new.ipynb')))
    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_md)
    assert not os.path.isfile(tmp_rmd)

    assert os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.md')))
    assert os.path.isfile(str(tmpdir.join('new.Rmd')))