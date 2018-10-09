# coding: utf-8

import os
import shutil
import time
import pytest
import mock
from tornado.web import HTTPError
from testfixtures import compare
import jupytext
from jupytext.compare import compare_notebooks
from jupytext.header import header_to_metadata_and_cell
from jupytext.formats import read_format_from_metadata, auto_ext_from_metadata
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
    cm.rename(tmp_nbpy, '2.new_notebook.py')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join('2.new_notebook.ipynb')))
    assert os.path.isfile(str(tmpdir.join('2.new_notebook.py')))


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

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = 'jl:percent'

    nb = jupytext.readf(nb_file)
    nb['metadata']['jupytext'] = {'formats': 'ipynb,jl'}

    # save to ipynb and jl
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # read jl file
    with open(str(tmpdir.join(tmp_jl))) as stream:
        text_jl = stream.read()

    # Parse the YAML header
    metadata, _, _ = header_to_metadata_and_cell(text_jl.splitlines(), '#')
    assert metadata['jupytext']['formats'] == 'ipynb,jl:percent'


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_save_to_light_percent_sphinx_format(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_lgt_py = 'notebook.lgt.py'
    tmp_pct_py = 'notebook.pct.py'
    tmp_spx_py = 'notebook.spx.py'

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    nb = jupytext.readf(nb_file)
    nb['metadata']['jupytext'] = {'formats': 'ipynb,pct.py:percent,lgt.py:light,spx.py:sphinx'}

    # save to ipynb and three python flavors
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # read files
    with open(str(tmpdir.join(tmp_pct_py))) as stream:
        assert read_format_from_metadata(stream.read(), 'pct.py') == 'percent'

    with open(str(tmpdir.join(tmp_lgt_py))) as stream:
        assert read_format_from_metadata(stream.read(), 'lgt.py') == 'light'

    with open(str(tmpdir.join(tmp_spx_py))) as stream:
        assert read_format_from_metadata(stream.read(), 'spx.py') == 'sphinx'

    model = cm.get(path=tmp_pct_py)
    assert model['name'] == 'notebook.pct'
    compare_notebooks(nb, model['content'])

    model = cm.get(path=tmp_lgt_py)
    assert model['name'] == 'notebook.lgt'
    compare_notebooks(nb, model['content'])

    model = cm.get(path=tmp_spx_py)
    assert model['name'] == 'notebook.spx'
    # (notebooks not equal as we insert %matplotlib inline in sphinx)

    model = cm.get(path=tmp_ipynb)
    assert model['name'] == 'notebook.pct'
    compare_notebooks(nb, model['content'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py')[:1])
def test_preferred_format_allows_to_read_others_format(nb_file, tmpdir):
    # 1. write py ipynb
    tmp_ipynb = u'notebook.ipynb'
    tmp_nbpy = u'notebook.py'

    cm = jupytext.TextFileContentsManager()
    cm.preferred_jupytext_formats_save = 'py:light'
    cm.root_dir = str(tmpdir)

    # load notebook and save it using the cm
    nb = jupytext.readf(nb_file)
    nb['metadata']['jupytext'] = {'formats': 'ipynb,py'}
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # Saving does not update the metadata, as 'save' makes a copy of the notebook
    # assert nb['metadata']['jupytext']['formats'] == 'ipynb,py:light'

    # Set preferred format for reading
    cm.preferred_jupytext_formats_read = 'py:percent'

    # Read notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        model = cm.get(tmp_nbpy)

    # Check that format is explicit
    assert model['content']['metadata']['jupytext']['formats'] == 'ipynb,py:light'

    # Check contents
    compare_notebooks(nb, model['content'])

    # Change save format and save
    model['content']['metadata']['jupytext']['formats'] == 'ipynb,py'
    cm.preferred_jupytext_formats_save = 'py:percent'
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # Read notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        model = cm.get(tmp_nbpy)
    compare_notebooks(nb, model['content'])

    # Check that format is explicit
    assert model['content']['metadata']['jupytext']['formats'] == 'ipynb,py:percent'


@pytest.mark.parametrize('nb_file', list_notebooks('python'))
def test_preferred_format_allows_to_read_implicit_light_format(nb_file, tmpdir):
    # copy content to notebook.py
    tmp_nbpy = u'notebook.py'
    shutil.copy(nb_file, str(tmpdir.join(tmp_nbpy)))

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.preferred_jupytext_formats_read = 'py:percent'
    cm.root_dir = str(tmpdir)

    # load notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        model = cm.get(tmp_nbpy)

    # check that format (missing) is recognized as light
    if 'light' in nb_file:
        assert 'light' == model['content']['metadata']['jupytext']['text_representation']['format_name']
    else:
        assert 'percent' == model['content']['metadata']['jupytext']['text_representation']['format_name']


def test_preferred_formats_read_auto(tmpdir):
    tmp_py = u'notebook.py'
    with open(str(tmpdir.join(tmp_py)), 'w') as script:
        script.write("""# cell one
1 + 1
""")

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.preferred_jupytext_formats_read = 'auto:percent'
    cm.root_dir = str(tmpdir)

    # load notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        model = cm.get(tmp_py)

    # check that script is opened as percent
    assert 'percent' == model['content']['metadata']['jupytext']['text_representation']['format_name']


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb'))
def test_save_in_auto_extension_global(nb_file, tmpdir):
    # load notebook
    nb = jupytext.readf(nb_file)
    if 'language_info' not in nb.metadata:
        return

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = 'notebook.ipynb'
    tmp_script = 'notebook' + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,auto'
    cm.preferred_jupytext_formats_save = 'auto:percent'
    cm.root_dir = str(tmpdir)

    # save notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == 'percent'

    # reload and compare with original notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        model = cm.get(path=tmp_script)

    # saving should not create a format entry #95
    assert 'formats' not in model['content'].metadata.get('jupytext', {})

    compare_notebooks(nb, model['content'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb'))
def test_save_in_auto_extension_local(nb_file, tmpdir):
    # load notebook
    nb = jupytext.readf(nb_file)
    nb.metadata.setdefault('jupytext', {})['formats'] = 'ipynb,auto:percent'
    if 'language_info' not in nb.metadata:
        return

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = 'notebook.ipynb'
    tmp_script = 'notebook' + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # save notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == 'percent'

    # reload and compare with original notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        model = cm.get(path=tmp_script)

    compare_notebooks(nb, model['content'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb'))
def test_save_in_pct_and_lgt_auto_extensions(nb_file, tmpdir):
    # load notebook
    nb = jupytext.readf(nb_file)
    if 'language_info' not in nb.metadata:
        return

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = 'notebook.ipynb'
    tmp_pct_script = 'notebook.pct' + auto_ext
    tmp_lgt_script = 'notebook.lgt' + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,pct.auto,lgt.auto'
    cm.preferred_jupytext_formats_save = 'pct.auto:percent,lgt.auto:light'
    cm.root_dir = str(tmpdir)

    # save notebook
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # check that text representation exists in percent format
    with open(str(tmpdir.join(tmp_pct_script))) as stream:
        assert read_format_from_metadata(stream.read(), '.pct' + auto_ext) == 'percent'

    # check that text representation exists in light format
    with open(str(tmpdir.join(tmp_lgt_script))) as stream:
        assert read_format_from_metadata(stream.read(), '.lgt' + auto_ext) == 'light'
