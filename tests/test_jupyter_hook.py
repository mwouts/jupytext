import pytest
import os
import nbrmd
from .utils import list_all_notebooks, remove_outputs, \
    remove_outputs_and_header


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_rmd_is_ok(nb_file, tmpdir):
    nb = nbrmd.readf(nb_file)
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_rmd(model=dict(type='notebook', content=nb), path=tmp_ipynb)

    nb2 = nbrmd.readf(tmp_rmd)

    assert remove_outputs(nb) == remove_outputs(nb2)


@pytest.mark.parametrize('nb_file', list_all_notebooks('.Rmd'))
def test_ipynb_is_ok(nb_file, tmpdir):
    nb = nbrmd.readf(nb_file)
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_ipynb(model=dict(type='notebook', content=nb), path=tmp_rmd)

    nb2 = nbrmd.readf(tmp_ipynb)

    assert remove_outputs(nb) == remove_outputs(nb2)


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_all_files_created(nb_file, tmpdir):
    nb = nbrmd.readf(nb_file)
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_md = str(tmpdir.join('notebook.md'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))
    nb.metadata['nbrmd_formats'] = ['.Rmd', '.ipynb', '.md']

    nbrmd.update_selected_formats(
        model=dict(type='notebook', content=nb), path=tmp_ipynb)

    nb2 = nbrmd.readf(tmp_md)
    assert remove_outputs_and_header(nb) == remove_outputs_and_header(nb2)

    nb3 = nbrmd.readf(tmp_rmd)
    assert remove_outputs(nb) == remove_outputs(nb3)


def test_no_files_created_on_no_format(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_md = str(tmpdir.join('notebook.md'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_selected_formats(
        model=dict(type='notebook',
                   content=dict(nbformat=4, metadata=dict())),
        path=tmp_ipynb)

    assert not os.path.isfile(tmp_md)
    assert not os.path.isfile(tmp_rmd)


def test_raise_on_wrong_format(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    with pytest.raises(TypeError):
        nbrmd.update_selected_formats(
            model=dict(type='notebook',
                       content=dict(nbformat=4,
                                    metadata=dict(nbrmd_formats=['.doc']))),
            path=tmp_ipynb)


def test_no_rmd_on_not_notebook(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_rmd(model=dict(type='not notebook'), path=tmp_ipynb)
    assert not os.path.isfile(tmp_rmd)


def test_no_rmd_on_not_v4(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    nbrmd.update_rmd(
        model=dict(type='notebook', content=dict(nbformat=3)), path=tmp_ipynb)

    assert not os.path.isfile(tmp_rmd)
