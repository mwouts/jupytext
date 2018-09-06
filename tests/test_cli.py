import os
from shutil import copyfile
import pytest
from testfixtures import compare
import mock
from nbformat.v4.nbbase import new_notebook
from jupytext import readf, writef, writes, file_format_version
from jupytext.cli import convert_notebook_files, cli_jupytext, jupytext
from jupytext.compare import compare_notebooks
from .utils import list_all_notebooks, list_py_notebooks

file_format_version.FILE_FORMAT_VERSION = {}
file_format_version.MIN_FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('nb_file',
                         list_all_notebooks('.ipynb') +
                         list_all_notebooks('.Rmd'))
def test_cli_single_file(nb_file):
    assert cli_jupytext([nb_file] + ['--to', 'py']).notebooks == [nb_file]


@pytest.mark.parametrize('nb_files', [list_all_notebooks('.ipynb') +
                                      list_all_notebooks('.Rmd')])
def test_cli_multiple_files(nb_files):
    assert cli_jupytext(nb_files + ['--to', 'py']).notebooks == nb_files


@pytest.mark.parametrize('nb_file',
                         list_py_notebooks('.ipynb'))
def test_convert_single_file_in_place(nb_file, tmpdir):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    base, ext = os.path.splitext(nb_org)
    nb_other = base + '.py'

    copyfile(nb_file, nb_org)
    convert_notebook_files([nb_org], ext='.py')

    nb1 = readf(nb_org)
    nb2 = readf(nb_other)

    compare_notebooks(nb1, nb2)


@pytest.mark.parametrize('nb_file',
                         list_all_notebooks('.ipynb') +
                         list_all_notebooks('.Rmd'))
def test_convert_single_file(nb_file, capsys):
    nb1 = readf(nb_file)
    pynb = writes(nb1, ext='.py')
    convert_notebook_files([nb_file], ext='.py', output='-')

    out, err = capsys.readouterr()
    assert err == ''
    compare(out[:-1], pynb)


@pytest.mark.parametrize('nb_files',
                         [list_py_notebooks('.ipynb')])
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

    convert_notebook_files(nb_orgs, ext='.py')

    for nb_org, nb_other in zip(nb_orgs, nb_others):
        nb1 = readf(nb_org)
        nb2 = readf(nb_other)
        compare_notebooks(nb1, nb2)


def test_error_not_notebook_ext_input(nb_file='notebook.ext'):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], ext='.py')


def test_error_not_notebook_ext_dest1(nb_file=list_all_notebooks('.ipynb')[0]):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], ext='.ext')


def test_error_not_notebook_ext_output(
        nb_file=list_all_notebooks('.ipynb')[0]):
    with pytest.raises(TypeError):
        cli_jupytext([nb_file, '-o', 'not.ext'])


def test_error_no_ext(nb_file=list_all_notebooks('.ipynb')[0]):
    with pytest.raises(TypeError):
        cli_jupytext([nb_file])


def test_error_not_same_ext(nb_file=list_all_notebooks('.ipynb')[0]):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], ext='.py', output='not.ext')


def test_error_update_not_ipynb(nb_file=list_all_notebooks('.ipynb')[0]):
    with pytest.raises(ValueError):
        cli_jupytext([nb_file, '--to', 'py', '--update'])


def test_error_multiple_input(nb_files=list_all_notebooks('.ipynb')):
    with pytest.raises(ValueError):
        convert_notebook_files(nb_files, ext='.py', output='notebook.py')


def test_combine_same_version_ok(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    with open(tmp_nbpy, 'w') as fp:
        fp.write("""# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '1.0'
# ---

# New cell
""")

    nb = new_notebook(metadata={'jupytext_formats': 'ipynb,py'})
    writef(nb, tmp_ipynb)

    with mock.patch('jupytext.file_format_version.FILE_FORMAT_VERSION',
                    {'.py': '1.0'}):
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
        with mock.patch('jupytext.file_format_version.FILE_FORMAT_VERSION',
                        {'.py': '1.0'}):
            jupytext(args=[tmp_nbpy, '--to', 'ipynb', '--update'])
