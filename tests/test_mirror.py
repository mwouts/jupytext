"""Here we generate mirror representation of py, Rmd and ipynb files
as py or ipynb, and make sure that these representations minimally
change on new releases.
"""

import os
import pytest
from nbformat.v4.nbbase import new_notebook
from testfixtures import compare
import jupytext
from jupytext import header
from .utils import list_notebooks, skip_if_dict_is_not_ordered

jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER = False

pytestmark = skip_if_dict_is_not_ordered


def create_mirror_file_if_missing(mirror_file, notebook):
    if not os.path.isfile(mirror_file):
        jupytext.writef(notebook, mirror_file)


def test_create_mirror_file_if_missing(tmpdir):
    py_file = str(tmpdir.join('notebook.py'))
    assert not os.path.isfile(py_file)
    create_mirror_file_if_missing(py_file, new_notebook())
    assert os.path.isfile(py_file)


def assert_conversion_same_as_mirror(nb_file, ext, mirror_name):
    dirname, basename = os.path.split(nb_file)
    file_name, org_ext = os.path.splitext(basename)
    mirror_file = os.path.join(dirname, '..', 'mirror',
                               mirror_name, file_name + ext)

    notebook = jupytext.readf(nb_file)
    create_mirror_file_if_missing(mirror_file, notebook)

    # Compare the text representation of the two notebooks
    if ext == '.ipynb':
        notebook = jupytext.readf(mirror_file)
        actual = jupytext.writes(notebook, ext=org_ext)
        with open(nb_file, encoding='utf-8') as fp:
            expected = fp.read()
    else:
        actual = jupytext.writes(notebook, ext=ext)
        with open(mirror_file, encoding='utf-8') as fp:
            expected = fp.read()

    compare(expected, actual)


@pytest.mark.parametrize('nb_file', list_notebooks('julia') +
                         list_notebooks('python') +
                         list_notebooks('R'))
def test_script_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ipynb', 'script_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_julia'))
def test_ipynb_to_julia(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.jl', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_ipynb_to_python(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.py', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_R(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.R', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('Rmd'))
def test_Rmd_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ipynb', 'Rmd_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb'))
def test_ipynb_to_Rmd(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.Rmd', 'ipynb_to_Rmd')
