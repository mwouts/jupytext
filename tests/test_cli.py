import pytest
import os
from shutil import copyfile
import nbrmd
from nbrmd.cli import convert, cli
from utils import list_all_notebooks, filter_output_and_compare_notebooks


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb') + list_all_notebooks('.Rmd'))
def test_cli_single_file(nb_file):
    assert cli([nb_file]).notebooks == [nb_file]


@pytest.mark.parametrize('nb_files', [list_all_notebooks('.ipynb') + list_all_notebooks('.Rmd')])
def test_cli_multiple_files(nb_files):
    assert cli(nb_files).notebooks == nb_files


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb') + list_all_notebooks('.Rmd'))
def test_convert_single_file(nb_file, tmpdir):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    base, ext = os.path.splitext(nb_org)
    nb_other = base + '.ipynb' if ext == '.Rmd' else base + '.Rmd'

    copyfile(nb_file, nb_org)
    convert([nb_org])

    nb1 = nbrmd.readf(nb_org)
    nb2 = nbrmd.readf(nb_other)

    filter_output_and_compare_notebooks(nb1, nb2)


@pytest.mark.parametrize('nb_files', [list_all_notebooks('.ipynb') + list_all_notebooks('.Rmd')])
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
        filter_output_and_compare_notebooks(nb1, nb2)


def test_error_not_notebook(nb_file='notebook.ext'):
    with pytest.raises(TypeError):
        convert([nb_file])
