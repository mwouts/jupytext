import os
import pytest
from nbformat.v4.nbbase import new_notebook
from nbformat.validator import NotebookValidationError
from tornado.web import HTTPError
import jupytext
from jupytext.contentsmanager import TextFileContentsManager
from jupytext.compare import compare_notebooks
from .utils import list_all_notebooks, list_py_notebooks

jupytext.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_rmd_is_ok(nb_file, tmpdir):
    nb = jupytext.readf(nb_file)
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'

    nb.metadata['jupytext_formats'] = 'ipynb,Rmd'

    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    cm.save(
        model=dict(type='notebook', content=nb),
        path=tmp_ipynb)

    nb2 = jupytext.readf(str(tmpdir.join(tmp_rmd)))

    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('nb_file', list_all_notebooks('.Rmd'))
def test_ipynb_is_ok(nb_file, tmpdir):
    nb = jupytext.readf(nb_file)
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'

    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = 'ipynb,Rmd'

    cm.save(
        model=dict(type='notebook', content=nb),
        path=tmp_rmd)

    nb2 = jupytext.readf(str(tmpdir.join(tmp_ipynb)))

    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('nb_file', list_py_notebooks('.ipynb'))
def test_all_files_created(nb_file, tmpdir):
    nb = jupytext.readf(nb_file)
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'
    tmp_py = 'notebook.py'
    nb.metadata['jupytext_formats'] = 'ipynb,Rmd,py'

    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    cm.save(
        model=dict(type='notebook', content=nb),
        path=tmp_ipynb)

    nb2 = jupytext.readf(str(tmpdir.join(tmp_py)))
    compare_notebooks(nb, nb2)

    nb3 = jupytext.readf(str(tmpdir.join(tmp_rmd)))
    compare_notebooks(nb, nb3)


def test_no_files_created_on_no_format(tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'
    tmp_py = 'notebook.py'

    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = ''

    cm.save(
        model=dict(type='notebook',
                   content=new_notebook(nbformat=4,
                                        metadata=dict())),
        path=tmp_ipynb)

    assert not os.path.isfile(str(tmpdir.join(tmp_py)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))


def test_raise_on_wrong_format(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    with pytest.raises(HTTPError):
        cm.save(
            model=dict(type='notebook',
                       content=new_notebook(nbformat=4,
                                            metadata=dict(
                                                jupytext_formats=['.doc']))),
            path=tmp_ipynb)


def test_no_rmd_on_not_notebook(tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'

    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = 'ipynb,Rmd'

    with pytest.raises(HTTPError):
        cm.save(model=dict(type='not notebook',
                           content=new_notebook()),
                path=tmp_ipynb)
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))


def test_no_rmd_on_not_v4(tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_rmd = 'notebook.Rmd'

    cm = TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = 'ipynb,Rmd'

    with pytest.raises(NotebookValidationError):
        cm.save(model=dict(type='notebook',
                           content=new_notebook(nbformat=3)),
                path=tmp_rmd)

    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
