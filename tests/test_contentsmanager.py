# coding: utf-8

import os
import sys
import pytest
import jupytext
from jupytext import TextFileContentsManager, readf
from jupytext.compare import compare_notebooks
from .utils import list_all_notebooks, list_py_notebooks

jupytext.file_format_version.FILE_FORMAT_VERSION = {}
jupytext.file_format_version.MIN_FILE_FORMAT_VERSION = {}


@pytest.mark.skipif(isinstance(TextFileContentsManager, str),
                    reason=TextFileContentsManager)
def test_create_contentsmanager():
    TextFileContentsManager()


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(TextFileContentsManager, str),
                    reason=TextFileContentsManager)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_load_save_rename(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'

    cm = TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,Rmd'
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
@pytest.mark.skipif(isinstance(TextFileContentsManager, str),
                    reason=TextFileContentsManager)
@pytest.mark.parametrize('nb_file', list_py_notebooks('.ipynb'))
def test_load_save_rename_nbpy(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_nbpy = 'notebook.nb.py'

    cm = TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,nb.py'
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
@pytest.mark.skipif(isinstance(TextFileContentsManager, str),
                    reason=TextFileContentsManager)
@pytest.mark.parametrize('nb_file', list_py_notebooks('.ipynb'))
def test_load_save_rename_nbpy_default_config(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_nbpy = 'notebook.nb.py'

    cm = TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb'
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


@pytest.mark.skipif(isinstance(TextFileContentsManager, str),
                    reason=TextFileContentsManager)
@pytest.mark.parametrize('nb_file', list_py_notebooks('.ipynb'))
def test_load_save_rename_non_ascii_path(nb_file, tmpdir):
    tmp_ipynb = u'notebôk.ipynb'
    tmp_nbpy = u'notebôk.nb.py'

    cm = TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb'
    tmpdir = u'' + str(tmpdir)
    cm.root_dir = tmpdir

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
    cm.rename(tmp_nbpy, u'nêw.nb.py')
    assert not os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert not os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert os.path.isfile(os.path.join(tmpdir, u'nêw.ipynb'))
    assert os.path.isfile(os.path.join(tmpdir, u'nêw.nb.py'))

    # rename ipynb
    cm.rename(u'nêw.ipynb', tmp_ipynb)
    assert os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert not os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert not os.path.isfile(os.path.join(tmpdir, u'nêw.ipynb'))
    assert os.path.isfile(os.path.join(tmpdir, u'nêw.nb.py'))
