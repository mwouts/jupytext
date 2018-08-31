import os
import sys
import pytest
import nbrmd
from nbrmd import RmdFileContentsManager, readf
from nbrmd.compare import compare_notebooks
from .utils import list_all_notebooks

nbrmd.file_format_version.FILE_FORMAT_VERSION = {}


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
    cm.default_nbrmd_formats = 'ipynb,Rmd'
    cm.root_dir = str(tmpdir)

    # open ipynb, save Rmd, reopen
    nb = readf(nb_file)
    cm.save(model=dict(type='notebook', content=nb), path=tmp_rmd)
    nb_rmd = cm.get(tmp_rmd)
    compare_notebooks(nb, nb_rmd['content'])

    # save ipynb
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # rename ipynb
    cm.rename(tmp_ipynb, 'new.ipynb')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))

    assert os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.Rmd')))


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(RmdFileContentsManager, str),
                    reason=RmdFileContentsManager)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_load_save_rename_nbpy(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_nbpy = 'notebook.nb.py'

    cm = RmdFileContentsManager()
    cm.default_nbrmd_formats = 'ipynb,nb.py'
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = readf(nb_file)
    cm.save(model=dict(type='notebook', content=nb), path=tmp_nbpy)
    nbpy = cm.get(tmp_nbpy)
    compare_notebooks(nb, nbpy['content'])

    # save ipynb
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # rename nbpy
    cm.rename(tmp_nbpy, 'new.nb.py')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.nb.py')))


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(RmdFileContentsManager, str),
                    reason=RmdFileContentsManager)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_load_save_rename_nbpy_default_config(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_nbpy = 'notebook.nb.py'

    cm = RmdFileContentsManager()
    cm.default_nbrmd_formats = 'ipynb'
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = readf(nb_file)
    cm.save(model=dict(type='notebook', content=nb), path=tmp_nbpy)
    nbpy = cm.get(tmp_nbpy)
    compare_notebooks(nb, nbpy['content'])

    # open ipynb
    nbipynb = cm.get(tmp_ipynb)
    compare_notebooks(nb, nbipynb['content'])

    # save ipynb
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # rename nbpy
    cm.rename(tmp_nbpy, 'new.nb.py')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.nb.py')))

    # rename ipynb
    cm.rename('new.ipynb', tmp_ipynb)
    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert not os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.nb.py')))
