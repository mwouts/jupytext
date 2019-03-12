"""Here we generate mirror representation of py, Rmd and ipynb files
as py or ipynb, and make sure that these representations minimally
change on new releases.
"""

import os
import mock
import pytest
from nbformat.v4.nbbase import new_notebook
from testfixtures import compare
import jupytext
from jupytext.compare import compare_notebooks, combine_inputs_with_outputs
from jupytext.formats import long_form_one_format
from jupytext.paired_paths import full_path
from .utils import list_notebooks, skip_if_dict_is_not_ordered

pytestmark = skip_if_dict_is_not_ordered


def create_mirror_file_if_missing(mirror_file, notebook, fmt):
    if not os.path.isfile(mirror_file):
        with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', False):
            jupytext.writef(notebook, mirror_file, fmt)


def test_create_mirror_file_if_missing(tmpdir):
    py_file = str(tmpdir.join('notebook.py'))
    assert not os.path.isfile(py_file)
    create_mirror_file_if_missing(py_file, new_notebook(), 'py')
    assert os.path.isfile(py_file)


def assert_conversion_same_as_mirror(nb_file, fmt, mirror_name, compare_notebook=False):
    dirname, basename = os.path.split(nb_file)
    file_name, org_ext = os.path.splitext(basename)
    fmt = long_form_one_format(fmt)
    ext = fmt['extension']
    mirror_file = os.path.join(dirname, '..', 'mirror', mirror_name, full_path(file_name, fmt))

    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', False):
        notebook = jupytext.readf(nb_file, fmt)
    create_mirror_file_if_missing(mirror_file, notebook, fmt)

    # Compare the text representation of the two notebooks
    if compare_notebook:
        nb_mirror = jupytext.readf(mirror_file)
        compare(nb_mirror, notebook)
        return
    elif ext == '.ipynb':
        notebook = jupytext.readf(mirror_file)
        fmt.update({'extension': org_ext})
        with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', False):
            actual = jupytext.writes(notebook, fmt)
        with open(nb_file, encoding='utf-8') as fp:
            expected = fp.read()
    else:
        with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', False):
            actual = jupytext.writes(notebook, fmt)
        with open(mirror_file, encoding='utf-8') as fp:
            expected = fp.read()

    compare(expected, actual)

    # Compare the two notebooks
    if ext != '.ipynb':
        with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', False):
            notebook = jupytext.readf(nb_file)
            nb_mirror = jupytext.readf(mirror_file, fmt)

        if fmt.get('format_name') == 'sphinx':
            nb_mirror.cells = nb_mirror.cells[1:]
            for cell in notebook.cells:
                cell.metadata = {}
            for cell in nb_mirror.cells:
                cell.metadata = {}

        if ext == '.md':
            for cell in notebook.cells:
                cell.metadata = {}

        compare_notebooks(notebook, nb_mirror, ext)

        combine_inputs_with_outputs(nb_mirror, notebook)
        compare_notebooks(notebook, nb_mirror, ext, compare_outputs=True)


@pytest.mark.parametrize('nb_file', list_notebooks('julia') + list_notebooks('python') + list_notebooks('R'))
def test_script_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'ipynb', 'script_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_julia'))
def test_ipynb_to_julia(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'jl', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py', skip=''))
def test_ipynb_to_python(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'py', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_R(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'R', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_r(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.low.r', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_m'))
def test_ipynb_to_m(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.m', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file,extension',
                         [(nb_file, extension)
                          for nb_file in list_notebooks('ipynb_scheme')
                          for extension in ('ss', 'scm')])
def test_ipynb_to_scheme(nb_file, extension):
    assert_conversion_same_as_mirror(nb_file, extension, 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_clojure'))
def test_ipynb_to_clojure(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'clj', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_bash'))
def test_ipynb_to_bash(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'sh', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_cpp'))
def test_ipynb_to_cpp(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'cpp', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_q'))
def test_ipynb_to_q(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'q', 'ipynb_to_script')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_julia'))
def test_ipynb_to_julia_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'jl:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_m'))
def test_ipynb_to_julia_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'm:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py', skip=''))
def test_ipynb_to_python_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'py:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_ipynb_to_python_hydrogen(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'py:hydrogen', 'ipynb_to_hydrogen')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_R_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'R:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_r_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.low.r:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_R_spin(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'R', 'ipynb_to_spin')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R'))
def test_ipynb_to_r_spin(nb_file):
    assert_conversion_same_as_mirror(nb_file, '.low.r', 'ipynb_to_spin')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_cpp'))
def test_ipynb_to_cpp_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'cpp:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file,extension',
                         [(nb_file, extension)
                          for nb_file in list_notebooks('ipynb_scheme')
                          for extension in ('ss', 'scm')])
def test_ipynb_to_scheme_percent(nb_file, extension):
    assert_conversion_same_as_mirror(nb_file,
                                     '{}:percent'.format(extension),
                                     'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_clojure'))
def test_ipynb_to_clojure_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'clj:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_bash'))
def test_ipynb_to_bash_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'sh:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_q'))
def test_ipynb_to_q_percent(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'q:percent', 'ipynb_to_percent')


@pytest.mark.parametrize('nb_file', list_notebooks('percent'))
def test_percent_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'ipynb:percent', 'script_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('hydrogen'))
def test_hydrogen_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'ipynb:hydrogen', 'script_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('R_spin'))
def test_spin_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'ipynb:spin', 'script_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py', skip='(raw|hash|frozen|magic|html|164)'))
def test_ipynb_to_python_sphinx(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'py:sphinx', 'ipynb_to_sphinx')


@pytest.mark.parametrize('nb_file', list_notebooks('sphinx'))
def test_sphinx_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'ipynb:sphinx', 'sphinx_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('sphinx'))
def test_sphinx_md_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, {'extension': '.ipynb', 'format_name': 'sphinx', 'rst2md': True},
                                     'sphinx-rst2md_to_ipynb', compare_notebook=True)


@pytest.mark.parametrize('nb_file', list_notebooks('Rmd'))
def test_Rmd_to_ipynb(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'ipynb', 'Rmd_to_ipynb')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb', skip='66'))
def test_ipynb_to_Rmd(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'Rmd', 'ipynb_to_Rmd')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb', skip='(66|frozen|magic)'))
def test_ipynb_to_md(nb_file):
    assert_conversion_same_as_mirror(nb_file, 'md', 'ipynb_to_md')
