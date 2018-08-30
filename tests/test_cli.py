import os
from shutil import copyfile
import pytest
import mock
from nbformat.v4.nbbase import new_notebook
import nbrmd
from nbrmd.cli import convert as convert_, cli_nbrmd as cli, cli_nbsrc, nbsrc
from .utils import list_all_notebooks, remove_outputs

nbrmd.file_format_version.FILE_FORMAT_VERSION = {}


def convert(*args, **kwargs):
    return convert_(*args, markdown=True, **kwargs)


@pytest.mark.parametrize('nb_file',
                         list_all_notebooks('.ipynb') +
                         list_all_notebooks('.Rmd'))
def test_cli_single_file(nb_file):
    assert cli([nb_file]).notebooks == [nb_file]


@pytest.mark.parametrize('nb_files', [list_all_notebooks('.ipynb') +
                                      list_all_notebooks('.Rmd')])
def test_cli_multiple_files(nb_files):
    assert cli(nb_files).notebooks == nb_files


@pytest.mark.parametrize('nb_file',
                         list_all_notebooks('.ipynb') +
                         list_all_notebooks('.Rmd'))
def test_convert_single_file_in_place(nb_file, tmpdir):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    base, ext = os.path.splitext(nb_org)
    nb_other = base + '.ipynb' if ext == '.Rmd' else base + '.Rmd'

    copyfile(nb_file, nb_org)
    convert([nb_org])

    nb1 = nbrmd.readf(nb_org)
    nb2 = nbrmd.readf(nb_other)

    remove_outputs(nb1) == remove_outputs(nb2)


@pytest.mark.parametrize('nb_file',
                         list_all_notebooks('.ipynb') +
                         list_all_notebooks('.Rmd'))
def test_convert_single_file(nb_file, capsys):
    convert([nb_file], in_place=False)

    out, err = capsys.readouterr()
    assert out != ''
    assert err == ''


@pytest.mark.parametrize('nb_files',
                         [list_all_notebooks('.ipynb') +
                          list_all_notebooks('.Rmd')])
def test_convert_multiple_file(nb_files, tmpdir):
    nb_orgs = []
    nb_others = []

    for nb_file in nb_files:
        nb_org = str(tmpdir.join(os.path.basename(nb_file)))
        base, ext = os.path.splitext(nb_org)
        nb_other = base + '.ipynb' if ext == '.Rmd' else base + '.Rmd'
        copyfile(nb_file, nb_org)
        nb_orgs.append(nb_org)
        nb_others.append(nb_other)

    convert(nb_orgs)

    for nb_org, nb_other in zip(nb_orgs, nb_others):
        nb1 = nbrmd.readf(nb_org)
        nb2 = nbrmd.readf(nb_other)
        remove_outputs(nb1) == remove_outputs(nb2)


def test_error_not_notebook(nb_file='notebook.ext'):
    with pytest.raises(TypeError):
        convert([nb_file])


def test_combine_same_version_ok(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    with open(tmp_nbpy, 'w') as fp:
        fp.write("""# ---
# jupyter:
#   nbrmd_formats: ipynb,py
#   nbrmd_format_version: '1.0'
# ---

# New cell
""")

    nb = new_notebook(metadata={'nbrmd_formats': 'ipynb,py'})
    nbrmd.writef(nb, tmp_ipynb)

    with mock.patch('nbrmd.file_format_version.FILE_FORMAT_VERSION',
                    {'.py': '1.0'}):
        nbsrc(args=[tmp_nbpy, '-i', '-p'])

    nb = nbrmd.readf(tmp_ipynb)
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
#   nbrmd_formats: ipynb,py
#   nbrmd_format_version: '0.0'
# ---

# New cell
""")

    nb = new_notebook(metadata={'nbrmd_formats': 'ipynb,py'})
    nbrmd.writef(nb, tmp_ipynb)

    with pytest.raises(ValueError):
        with mock.patch('nbrmd.file_format_version.FILE_FORMAT_VERSION',
                        {'.py': '1.0'}):
            nbsrc(args=[tmp_nbpy, '-i', '-p'])
