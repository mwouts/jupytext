import nbformat
import nbrmd
import pytest
from .utils import list_all_notebooks, remove_outputs, \
    remove_outputs_and_header


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_identity_source_write_read(nb_file):
    """
    Test that writing the notebook with rmd, and read again,
    is the same as removing outputs
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    rmd = nbrmd.writes(nb1)
    nb2 = nbrmd.reads(rmd)

    assert remove_outputs(nb1) == remove_outputs(nb2)


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_identity_source_write_read_md(nb_file):
    """
    Test that writing the notebook with rmd, and read again,
    is the same as removing outputs
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        nb1 = nbformat.read(fp, as_version=4)

    md = nbrmd.writes(nb1, ext='.md')
    nb2 = nbrmd.reads(md, ext='.md')

    assert remove_outputs_and_header(nb1) == remove_outputs_and_header(nb2)
