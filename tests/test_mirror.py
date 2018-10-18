"""Here we generate mirror representation of py, Rmd and ipynb files
as py or ipynb, and make sure that these representations minimally
change on new releases.
"""

import os
import pytest
from nbformat.v4.nbbase import new_notebook
from testfixtures import compare
import jupytext
from jupytext.compare import compare_notebooks, combine_inputs_with_outputs
from .utils import list_notebooks, skip_if_dict_is_not_ordered

jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER = False

pytestmark = skip_if_dict_is_not_ordered


def create_mirror_file_if_missing(mirror_file, notebook, format_name=None):
    if not os.path.isfile(mirror_file):
        jupytext.writef(notebook, mirror_file, format_name=format_name)


def test_create_mirror_file_if_missing(tmpdir):
    py_file = str(tmpdir.join('notebook.py'))
    assert not os.path.isfile(py_file)
    create_mirror_file_if_missing(py_file, new_notebook())
    assert os.path.isfile(py_file)


def assert_conversion_same_as_mirror(nb_file, ext, mirror_name, format_name=None, compare_notebook=False):
    dirname, basename = os.path.split(nb_file)
    file_name, org_ext = os.path.splitext(basename)
    mirror_file = os.path.join(dirname, '..', 'mirror', mirror_name, file_name + ext)

    notebook = jupytext.readf(nb_file, format_name=format_name)
    create_mirror_file_if_missing(mirror_file, notebook, format_name=format_name)

    # Compare the text representation of the two notebooks
    if compare_notebook:
        nb_mirror = jupytext.readf(mirror_file)
        compare(nb_mirror, notebook)
        return
    elif ext == '.ipynb':
        notebook = jupytext.readf(mirror_file)
        actual = jupytext.writes(notebook, ext=org_ext, format_name=format_name)
        with open(nb_file, encoding='utf-8') as fp:
            expected = fp.read()
    else:
        actual = jupytext.writes(notebook, ext=ext, format_name=format_name)
        with open(mirror_file, encoding='utf-8') as fp:
            expected = fp.read()

    if format_name and len(actual.splitlines()) > len(expected.splitlines()):
        actual = '\n'.join(actual.splitlines()[-len(expected.splitlines()):] + [''])

    compare(expected, actual)

    # Compare the two notebooks
    if ext != '.ipynb':
        notebook = jupytext.readf(nb_file)
        nb_mirror = jupytext.readf(mirror_file, format_name=format_name)

        if format_name == 'sphinx':
            nb_mirror.cells = nb_mirror.cells[1:]
            for cell in notebook.cells:
                cell.metadata = {}
            for cell in nb_mirror.cells:
                cell.metadata = {}

        if ext == '.md':
            for cell in notebook.cells:
                cell.metadata = {}

        compare_notebooks(notebook, nb_mirror, ext=ext)

        combine_inputs_with_outputs(nb_mirror, notebook)
        compare_notebooks(notebook, nb_mirror, ext=ext, compare_outputs=True)


@pytest.mark.parametrize('nb_file', list_notebooks('julia') + list_notebooks('python') + list_notebooks('R'))
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


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_scheme'))
def test_ipynb_to_scheme(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ss', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_cpp'))
def test_ipynb_to_cpp(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.cpp', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_julia'))
def test_ipynb_to_julia_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.jl', 'ipynb_to_percent', format_name='percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_ipynb_to_python_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.py', 'ipynb_to_percent', format_name='percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_R_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.R', 'ipynb_to_percent', format_name='percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_cpp'))
def test_ipynb_to_cpp_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.cpp', 'ipynb_to_percent', format_name='percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_scheme'))
def test_ipynb_to_scheme_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ss', 'ipynb_to_percent', format_name='percent')


@pytest.mark.parametrize('nb_file', list_notebooks('percent'))
def test_percent_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ipynb', 'script_to_ipynb', format_name='percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py', skip='(raw|hash|frozen)'))
def test_ipynb_to_python_sphinx(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.py', 'ipynb_to_sphinx', format_name='sphinx')


@pytest.mark.parametrize('nb_file', list_notebooks('sphinx'))
def test_sphinx_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ipynb', 'sphinx_to_ipynb', format_name='sphinx')


@pytest.mark.parametrize('nb_file', list_notebooks('sphinx'))
def test_sphinx_md_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ipynb', 'sphinx-rst2md_to_ipynb',
                                     format_name='sphinx-rst2md', compare_notebook=True)


@pytest.mark.parametrize('nb_file', list_notebooks('Rmd'))
def test_Rmd_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.ipynb', 'Rmd_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb', skip='66'))
def test_ipynb_to_Rmd(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.Rmd', 'ipynb_to_Rmd')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb', skip='66'))
def test_ipynb_to_md(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.md', 'ipynb_to_md')
