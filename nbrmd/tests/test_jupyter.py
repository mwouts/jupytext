import nbformat
import nbrmd

def test_jupyter_write_read(file='jupyter.ipynb'):
    """
    Test that writing the notebook with rmd, and read again, is the same as removing outputs
    :param file:
    :return:
    """

    with open(file) as fp:
        nb = nbformat.read(fp, as_version=4)

    rmd = nbrmd.nbrmd.writes(nb)
    nb2 = nbrmd.nbrmd.reads(rmd)

    cells_output_removed = nb.cells
    for cell in cells_output_removed:
        cell.execution_count = None
        cell.output = None

    assert nb.cells == cells_output_removed
