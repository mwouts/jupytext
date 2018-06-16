import nbrmd
import pytest
import notebooks

@pytest.mark.parametrize('nb_file', notebooks.list_all_notebooks('.Rmd'))
def test_identity_write_read(nb_file):
    """
    Test that writing the notebook with ipynb, and read again, yields identity
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        rmd = fp.read()

    nb = nbrmd.reads(rmd)
    rmd2 = nbrmd.writes(nb)

    assert rmd == rmd2
