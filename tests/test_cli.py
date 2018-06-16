import pytest
import os
from shutil import copyfile
import nbrmd
from nbrmd.cli import convert
from tests.utils import list_all_notebooks, filter_output_and_compare_notebooks


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb') + list_all_notebooks('.Rmd'))
def test_convert_single_file(nb_file, tmpdir):
    nb_org = tmpdir.join(os.path.basename(nb_file))
    base, ext = os.path.splitext(str(nb_org))
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
        nb_org = tmpdir.join(os.path.basename(nb_file))
        base, ext = os.path.splitext(str(nb_org))
        nb_other = base + '.ipynb' if ext == '.Rmd' else base + '.Rmd'
        copyfile(nb_file, nb_org)
        nb_orgs.append(nb_org)
        nb_others.append(nb_other)

    convert(nb_orgs)

    for nb_org, nb_other in zip(nb_orgs, nb_others):
        nb1 = nbrmd.readf(nb_org)
        nb2 = nbrmd.readf(nb_other)
        filter_output_and_compare_notebooks(nb1, nb2)

