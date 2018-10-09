import os
from shutil import copyfile
import pytest
from testfixtures import compare
import mock
from nbformat.v4.nbbase import new_notebook
from jupytext import header
from jupytext import readf, writef, writes
from jupytext.cli import convert_notebook_files, cli_jupytext, jupytext
from jupytext.compare import compare_notebooks
from .utils import list_notebooks

header.INSERT_AND_CHECK_VERSION_NUMBER = False


def test_cli_no_argument():
    with pytest.raises(ValueError):
        cli_jupytext([])


@pytest.mark.parametrize('nb_file', list_notebooks())
def test_cli_single_file(nb_file):
    assert cli_jupytext([nb_file] + ['--to', 'py']).notebooks == [nb_file]


@pytest.mark.parametrize('nb_files', [list_notebooks()])
def test_cli_multiple_files(nb_files):
    assert cli_jupytext(nb_files + ['--to', 'py']).notebooks == nb_files


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_convert_single_file_in_place(nb_file, tmpdir):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    base, ext = os.path.splitext(nb_org)
    nb_other = base + '.py'

    copyfile(nb_file, nb_org)
    convert_notebook_files([nb_org], fmt='py')

    nb1 = readf(nb_org)
    nb2 = readf(nb_other)

    compare_notebooks(nb1, nb2)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb') +
                         list_notebooks('Rmd'))
def test_convert_single_file(nb_file, capsys):
    nb1 = readf(nb_file)
    pynb = writes(nb1, ext='.py')
    convert_notebook_files([nb_file], fmt='py', output='-')

    out, err = capsys.readouterr()
    assert err == ''
    compare(out, pynb)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_cpp'))
def test_to_cpluplus(nb_file, capsys):
    nb1 = readf(nb_file)
    text_cpp = writes(nb1, ext='.cpp')
    jupytext([nb_file, '--to', 'c++', '--output', '-'])

    out, err = capsys.readouterr()
    assert err == ''
    compare(out, text_cpp)


@pytest.mark.parametrize('nb_files', [list_notebooks('ipynb_py')])
def test_convert_multiple_file(nb_files, tmpdir):
    nb_orgs = []
    nb_others = []

    for nb_file in nb_files:
        nb_org = str(tmpdir.join(os.path.basename(nb_file)))
        base, ext = os.path.splitext(nb_org)
        nb_other = base + '.py'
        copyfile(nb_file, nb_org)
        nb_orgs.append(nb_org)
        nb_others.append(nb_other)

    convert_notebook_files(nb_orgs, fmt='py')

    for nb_org, nb_other in zip(nb_orgs, nb_others):
        nb1 = readf(nb_org)
        nb2 = readf(nb_other)
        compare_notebooks(nb1, nb2)


def test_error_not_notebook_ext_input(nb_file='notebook.ext'):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], fmt='py')


def test_error_not_notebook_ext_dest1(nb_file=list_notebooks()[0]):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], fmt='ext')


def test_error_not_notebook_ext_output(
        nb_file=list_notebooks()[0]):
    with pytest.raises(TypeError):
        cli_jupytext([nb_file, '-o', 'not.ext'])


def test_error_no_ext(nb_file=list_notebooks()[0]):
    with pytest.raises(ValueError):
        cli_jupytext([nb_file])


def test_error_not_same_ext(nb_file=list_notebooks()[0]):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], fmt='py', output='not.ext')


def test_error_update_not_ipynb(nb_file=list_notebooks()[0]):
    with pytest.raises(ValueError):
        cli_jupytext([nb_file, '--to', 'py', '--update'])


def test_error_multiple_input(nb_files=list_notebooks()):
    with pytest.raises(ValueError):
        convert_notebook_files(nb_files, fmt='py', output='notebook.py')


def test_combine_same_version_ok(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    with open(tmp_nbpy, 'w') as fp:
        fp.write("""# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '1.2'
# ---

# New cell
""")

    nb = new_notebook(metadata={'jupytext_formats': 'ipynb,py'})
    writef(nb, tmp_ipynb)

    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        # to jupyter notebook
        jupytext(args=[tmp_nbpy, '--to', 'ipynb', '--update'])
        # test round trip
        jupytext(args=[tmp_nbpy, '--to', 'notebook', '--test'])
        # test ipynb to rmd
        jupytext(args=[tmp_ipynb, '--to', 'rmarkdown'])

    nb = readf(tmp_ipynb)
    cells = nb['cells']
    assert len(cells) == 1
    assert cells[0].cell_type == 'markdown'
    assert cells[0].source == 'New cell'

    nb = readf(tmp_rmd)
    cells = nb['cells']
    assert len(cells) == 1
    assert cells[0].cell_type == 'markdown'
    assert cells[0].source == 'New cell'


def test_combine_lower_version_raises(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    with open(tmp_nbpy, 'w') as fp:
        fp.write("""# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '0.0'
# ---

# New cell
""")

    nb = new_notebook(metadata={'jupytext_formats': 'ipynb,py'})
    writef(nb, tmp_ipynb)

    with pytest.raises(SystemExit):
        with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER',
                        True):
            jupytext(args=[tmp_nbpy, '--to', 'ipynb', '--update'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_ipynb_to_py_then_update_test(nb_file, tmpdir):
    """Reproduce https://github.com/mwouts/jupytext/issues/83"""
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    copyfile(nb_file, tmp_ipynb)

    jupytext(['--to', 'py', tmp_ipynb])
    jupytext(['--test', '--update', '--to', 'ipynb', tmp_nbpy])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_convert_to_percent_format(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    copyfile(nb_file, tmp_ipynb)

    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        jupytext(['--to', 'py:percent', tmp_ipynb])

    with open(tmp_nbpy) as stream:
        py_script = stream.read()
        assert 'format_name: percent' in py_script

    nb1 = readf(tmp_ipynb)
    nb2 = readf(tmp_nbpy)

    compare_notebooks(nb1, nb2)
