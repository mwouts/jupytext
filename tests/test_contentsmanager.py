# coding: utf-8

import os
import time
import pytest
import itertools
from tornado.web import HTTPError
from testfixtures import compare
import jupytext
from jupytext.compare import compare_notebooks
from jupytext.header import header_to_metadata_and_cell
from jupytext.formats import read_format_from_metadata, auto_ext_from_metadata
from .utils import list_notebooks
from .utils import skip_if_dict_is_not_ordered


def test_create_contentsmanager():
    jupytext.TextFileContentsManager()


def test_rename(tmpdir):
    org_file = str(tmpdir.join('notebook.ipynb'))
    new_file = str(tmpdir.join('new.ipynb'))
    with open(org_file, 'w') as fp:
        fp.write('\n')

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.rename_file('notebook.ipynb', 'new.ipynb')

    assert os.path.isfile(new_file)
    assert not os.path.isfile(org_file)


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
    compare_notebooks(nb, nb_rmd['content'], 'Rmd')

    # save ipynb
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # rename ipynb
    cm.rename(tmp_ipynb, 'new.ipynb')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))

    assert os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.Rmd')))

    # delete one file, test that we can still read and rename it
    cm.delete('new.Rmd')
    assert not os.path.isfile(str(tmpdir.join('new.Rmd')))
    model = cm.get('new.ipynb', content=False)
    assert 'last_modified' in model
    cm.save(model=dict(type='notebook', content=nb), path='new.ipynb')
    assert os.path.isfile(str(tmpdir.join('new.Rmd')))

    cm.delete('new.Rmd')
    cm.rename('new.ipynb', tmp_ipynb)

    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))
    assert not os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert not os.path.isfile(str(tmpdir.join('new.Rmd')))


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb', skip='magic'))
def test_save_load_paired_md_notebook(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_md = 'notebook.md'

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open ipynb, save with cm, reopen
    nb = jupytext.readf(nb_file)
    nb.metadata['jupytext'] = {'formats': 'ipynb,md'}

    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)
    nb_md = cm.get(tmp_md)

    compare_notebooks(nb, nb_md['content'], 'md')
    assert nb_md['content'].metadata['jupytext']['formats'] == 'ipynb,md'


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('py_file', list_notebooks('percent'))
def test_pair_plain_script(py_file, tmpdir):
    tmp_py = 'notebook.py'
    tmp_ipynb = 'notebook.ipynb'

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open py file, pair, save with cm
    nb = jupytext.readf(py_file)
    nb.metadata['jupytext']['formats'] = 'ipynb,py:hydrogen'
    cm.save(model=dict(type='notebook', content=nb), path=tmp_py)

    assert os.path.isfile(str(tmpdir.join(tmp_py)))
    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))

    # Make sure we've not changed the script
    with open(py_file) as fp:
        script = fp.read()

    with open(str(tmpdir.join(tmp_py))) as fp:
        script2 = fp.read()

    compare(script, script2)

    # reopen py file with the cm
    nb2 = cm.get(tmp_py)['content']
    compare_notebooks(nb, nb2)
    assert nb2.metadata['jupytext']['formats'] == 'ipynb,py:hydrogen'

    # remove the pairing and save
    del nb.metadata['jupytext']['formats']
    cm.save(model=dict(type='notebook', content=nb), path=tmp_py)

    # reopen py file with the cm
    nb2 = cm.get(tmp_py)['content']
    compare_notebooks(nb, nb2)
    assert 'formats' not in nb2.metadata['jupytext']


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_load_save_rename_nbpy(nb_file, tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_nbpy = 'notebook.nb.py'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,.nb.py'
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

    # rename to a non-matching pattern
    with pytest.raises(HTTPError):
        cm.rename_file(tmp_nbpy, 'suffix_missing.py')


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('script', list_notebooks('python', skip='light'))
def test_load_save_py_freeze_metadata(script, tmpdir):
    tmp_nbpy = 'notebook.py'

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # read original file
    with open(script) as fp:
        text_py = fp.read()

    # write to tmp_nbpy
    with open(str(tmpdir.join(tmp_nbpy)), 'w') as fp:
        fp.write(text_py)

    # open and save notebook
    nb = cm.get(tmp_nbpy)['content']
    cm.save(model=dict(type='notebook', content=nb), path=tmp_nbpy)

    with open(str(tmpdir.join(tmp_nbpy))) as fp:
        text_py2 = fp.read()

    compare(text_py, text_py2)


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
    cm.default_jupytext_formats = 'ipynb,.nb.py'
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

    # rename notebook.nb.py to new.nb.py
    cm.rename(tmp_nbpy, 'new.nb.py')
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert os.path.isfile(str(tmpdir.join('new.nb.py')))

    # rename new.ipynb to notebook.ipynb
    cm.rename('new.ipynb', tmp_ipynb)
    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert not os.path.isfile(str(tmpdir.join('new.ipynb')))
    assert not os.path.isfile(str(tmpdir.join('new.nb.py')))


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_load_save_rename_non_ascii_path(nb_file, tmpdir):
    tmp_ipynb = u'notebôk.ipynb'
    tmp_nbpy = u'notebôk.nb.py'

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,.nb.py'
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

    # rename notebôk.nb.py to nêw.nb.py
    cm.rename(tmp_nbpy, u'nêw.nb.py')
    assert not os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert not os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert os.path.isfile(os.path.join(tmpdir, u'nêw.ipynb'))
    assert os.path.isfile(os.path.join(tmpdir, u'nêw.nb.py'))

    # rename nêw.ipynb to notebôk.ipynb
    cm.rename(u'nêw.ipynb', tmp_ipynb)
    assert os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert not os.path.isfile(os.path.join(tmpdir, u'nêw.ipynb'))
    assert not os.path.isfile(os.path.join(tmpdir, u'nêw.nb.py'))


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
    nb = cm.get(tmp_py)['content']
    del nb.metadata['jupytext']['notebook_metadata_filter']
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
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # read jl file
    with open(str(tmpdir.join(tmp_jl))) as stream:
        text_jl = stream.read()

    # Parse the YAML header
    metadata, _, _, _ = header_to_metadata_and_cell(text_jl.splitlines(), '#')
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
    nb['metadata']['jupytext'] = {'formats': 'ipynb,.pct.py:percent,.lgt.py:light,.spx.py:sphinx'}

    # save to ipynb and three python flavors
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # read files
    with open(str(tmpdir.join(tmp_pct_py))) as stream:
        assert read_format_from_metadata(stream.read(), '.py') == 'percent'

    with open(str(tmpdir.join(tmp_lgt_py))) as stream:
        assert read_format_from_metadata(stream.read(), '.py') == 'light'

    with open(str(tmpdir.join(tmp_spx_py))) as stream:
        assert read_format_from_metadata(stream.read(), '.py') == 'sphinx'

    model = cm.get(path=tmp_pct_py)
    compare_notebooks(nb, model['content'])

    model = cm.get(path=tmp_lgt_py)
    compare_notebooks(nb, model['content'])

    model = cm.get(path=tmp_spx_py)
    # (notebooks not equal as we insert %matplotlib inline in sphinx)

    model = cm.get(path=tmp_ipynb)
    compare_notebooks(nb, model['content'])


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_pair_notebook_with_dot(nb_file, tmpdir):
    # Reproduce issue #138
    tmp_py = 'file.5.1.py'
    tmp_ipynb = 'file.5.1.ipynb'

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    nb = jupytext.readf(nb_file)
    nb['metadata']['jupytext'] = {'formats': 'ipynb,py:percent'}

    # save to ipynb and three python flavors
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))

    # read files
    with open(str(tmpdir.join(tmp_py))) as stream:
        assert read_format_from_metadata(stream.read(), '.py') == 'percent'

    model = cm.get(path=tmp_py)
    assert model['name'] == 'file.5.1.py'
    compare_notebooks(nb, model['content'])

    model = cm.get(path=tmp_ipynb)
    assert model['name'] == 'file.5.1.ipynb'
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
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # Saving does not update the metadata, as 'save' makes a copy of the notebook
    # assert nb['metadata']['jupytext']['formats'] == 'ipynb,py:light'

    # Set preferred format for reading
    cm.preferred_jupytext_formats_read = 'py:percent'

    # Read notebook
    model = cm.get(tmp_nbpy)

    # Check that format is explicit
    assert model['content']['metadata']['jupytext']['formats'] == 'ipynb,py:light'

    # Check contents
    compare_notebooks(nb, model['content'])

    # Change save format and save
    model['content']['metadata']['jupytext']['formats'] == 'ipynb,py'
    cm.preferred_jupytext_formats_save = 'py:percent'
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # Read notebook
    model = cm.get(tmp_nbpy)
    compare_notebooks(nb, model['content'])

    # Check that format is explicit
    assert model['content']['metadata']['jupytext']['formats'] == 'ipynb,py:percent'


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
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == 'percent'

    # reload and compare with original notebook
    model = cm.get(path=tmp_script)

    # saving should not create a format entry #95
    assert 'formats' not in model['content'].metadata.get('jupytext', {})

    compare_notebooks(nb, model['content'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb'))
def test_save_in_auto_extension_global_with_format(nb_file, tmpdir):
    # load notebook
    nb = jupytext.readf(nb_file)
    if 'language_info' not in nb.metadata:
        return

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = 'notebook.ipynb'
    tmp_script = 'notebook' + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,auto:percent'
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == 'percent'

    # reload and compare with original notebook
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
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == 'percent'

    # reload and compare with original notebook
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
    cm.default_jupytext_formats = 'ipynb,.pct.auto,.lgt.auto'
    cm.preferred_jupytext_formats_save = '.pct.auto:percent,.lgt.auto:light'
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # check that text representation exists in percent format
    with open(str(tmpdir.join(tmp_pct_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == 'percent'

    # check that text representation exists in light format
    with open(str(tmpdir.join(tmp_lgt_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == 'light'


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb', skip='magic'))
def test_metadata_filter_is_effective(nb_file, tmpdir):
    nb = jupytext.readf(nb_file)
    tmp_ipynb = 'notebook.ipynb'
    tmp_script = 'notebook.py'

    # create contents manager
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # save notebook to tmpdir
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # set config
    cm.default_jupytext_formats = 'ipynb,py'
    cm.default_notebook_metadata_filter = 'jupytext,-all'
    cm.default_cell_metadata_filter = '-all'

    # load notebook
    nb = cm.get(tmp_ipynb)['content']

    assert nb.metadata['jupytext']['cell_metadata_filter'] == '-all'
    assert nb.metadata['jupytext']['notebook_metadata_filter'] == 'jupytext,-all'

    # save notebook again
    cm.save(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    # read text version
    nb2 = jupytext.readf(str(tmpdir.join(tmp_script)))

    # test no metadata
    assert set(nb2.metadata.keys()) <= {'jupytext'}
    for cell in nb2.cells:
        assert not cell.metadata

    # read paired notebook
    nb3 = cm.get(tmp_script)['content']

    compare_notebooks(nb, nb3)


@pytest.mark.parametrize('nb_file,ext', itertools.product(list_notebooks('ipynb_py'), ['.py', '.ipynb']))
def test_local_format_can_deactivate_pairing(nb_file, ext, tmpdir):
    """This is a test for #157: local format can be used to deactivate the """
    nb = jupytext.readf(nb_file)
    nb.metadata['jupytext_formats'] = ext[1:]  # py or ipynb

    # create contents manager with default pairing
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = 'ipynb,py'
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=dict(type='notebook', content=nb), path='notebook' + ext)

    # check that only the text representation exists
    assert os.path.isfile(str(tmpdir.join('notebook.py'))) == (ext == '.py')
    assert os.path.isfile(str(tmpdir.join('notebook.ipynb'))) == (ext == '.ipynb')
    nb2 = cm.get('notebook' + ext)['content']
    compare_notebooks(nb, nb2)

    # resave, check again
    cm.save(model=dict(type='notebook', content=nb2), path='notebook' + ext)

    assert os.path.isfile(str(tmpdir.join('notebook.py'))) == (ext == '.py')
    assert os.path.isfile(str(tmpdir.join('notebook.ipynb'))) == (ext == '.ipynb')
    nb3 = cm.get('notebook' + ext)['content']
    compare_notebooks(nb, nb3)
