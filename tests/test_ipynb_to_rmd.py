import nbformat
import nbrmd
import pytest

@pytest.mark.parametrize('nb_file', ['jupyter.ipynb'])
def test_identity_source_write_read(nb_file):
    """
    Test that writing the notebook with rmd, and read again, is the same as removing outputs
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        nb = nbformat.read(fp, as_version=4)

    rmd = nbrmd.nbrmd.writes(nb)
    nb2 = nbrmd.nbrmd.reads(rmd)

    cells_output_removed = nb.cells
    for cell in cells_output_removed:
        cell.execution_count = None
        cell.output = None

    assert nb.cells == cells_output_removed
