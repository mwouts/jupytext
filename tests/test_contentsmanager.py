# coding: utf-8

import os
import time
import pytest
import mock
from tornado.web import HTTPError
from testfixtures import compare
import jupytext
from jupytext.compare import compare_notebooks
from jupytext.header import header_to_metadata_and_cell
from .utils import list_notebooks
from .utils import skip_if_dict_is_not_ordered

jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER = False


def test_create_contentsmanager():
    jupytext.TextFileContentsManager()


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb', skip='66'))
def test_load_save_rename(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,Rmd'
    cm.root_dir = str(tmpdir)

    # open ipynb, save Rmd, reopen
    nb = jupytext.readf(nb_file)
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


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_load_save_rename_nbpy(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_nbpy = 'notebook.nb.py'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,nb.py'
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.readf(nb_file)
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


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_load_save_rename_notebook_with_dot(nb_file, tmpdir):
    tmp_ipynb = '1.notebook.ipynb'
    tmp_nbpy = '1.notebook.py'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,py'
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.readf(nb_file)
    cm.save(model=dict(type='notebook', content=nb), path=tmp_nbpy)
    nbpy = cm.get(tmp_nbpy)
    compare_notebooks(nb, nbpy['content'])

    # save ipynb
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # rename py
    cm.rename(tmp_nbpy, '2.new.py')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join('2.new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('2.new.py')))


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_load_save_rename_nbpy_default_config(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_nbpy = 'notebook.nb.py'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb'
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.readf(nb_file)
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


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_load_save_rename_non_ascii_path(nb_file, tmpdir):
    tmp_ipynb = u'notebôk.ipynb'
    tmp_nbpy = u'notebôk.nb.py'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb'
    tmpdir = u'' + str(tmpdir)
    cm.root_dir = tmpdir

    # open ipynb, save nb.py, reopen
    nb = jupytext.readf(nb_file)
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


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py')[:1])
def test_outdated_text_notebook(nb_file, tmpdir):
    # 1. write py ipynb
    tmp_ipynb = u'notebook.ipynb'
    tmp_nbpy = u'notebook.py'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'py,ipynb'
    cm.outdated_text_notebook_margin = 0
    cm.root_dir = str(tmpdir)

    # open ipynb, save py, reopen
    nb = jupytext.readf(nb_file)
    cm.save(model=dict(type='notebook', content=nb), path=tmp_nbpy)
    model_py = cm.get(tmp_nbpy, load_alternative_format=False)
    model_ipynb = cm.get(tmp_ipynb, load_alternative_format=False)

    # 2. check that time of ipynb <= py
    assert model_ipynb['last_modified'] <= model_py['last_modified']

    # 3. wait some time
    time.sleep(0.5)

    # 4. touch ipynb
    with open(str(tmpdir.join(tmp_ipynb)), 'a'):
        os.utime(str(tmpdir.join(tmp_ipynb)), None)

    # 5. test error
    with pytest.raises(HTTPError):
        cm.get(tmp_nbpy)

    # 6. test OK with
    cm.outdated_text_notebook_margin = 1.0
    cm.get(tmp_nbpy)

    # 7. test OK with
    cm.outdated_text_notebook_margin = float("inf")
    cm.get(tmp_nbpy)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('percent'))
def test_load_save_percent_format(nb_file, tmpdir):
    tmp_py = 'notebook.py'
    with open(nb_file) as stream:
        text_py = stream.read()
    with open(str(tmpdir.join(tmp_py)), 'w') as stream:
        stream.write(text_py)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open python, save
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        nb = cm.get(tmp_py)['content']
        cm.save(model=dict(type='notebook', content=nb), path=tmp_py)

    # compare the new file with original one
    with open(str(tmpdir.join(tmp_py))) as stream:
        text_py2 = stream.read()

    # do we find 'percent' in the header?
    header = text_py2[:-len(text_py)]
    assert any(['percent' in line for line in header.splitlines()])

    # Remove the YAML header
    text_py2 = text_py2[-len(text_py):]

    compare(text_py, text_py2)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_julia'))
def test_save_to_percent_format(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_jl = 'notebook.jl'
    nb = jupytext.readf(nb_file)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = 'jl:percent'

    nb['metadata']['jupytext_formats'] = 'ipynb,jl'

    # open python, save
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # read jl file
    with open(str(tmpdir.join(tmp_jl))) as stream:
        text_jl = stream.read()

    # Parse the YAML header
    metadata, _, _ = header_to_metadata_and_cell(text_jl.splitlines(), '#')
    assert metadata['jupytext_formats'] == 'ipynb,jl:percent'
