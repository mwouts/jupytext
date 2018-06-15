import nbrmd
import pytest

@pytest.mark.parametrize('nb_file', ['ioslides.Rmd', 'chunk_options.Rmd'])
def test_identity_write_read(nb_file):
    """
    Test that writing the notebook with ipynb, and read again, yields identify
    :param file:
    :return:
    """

    with open(nb_file) as fp:
        rmd = fp.read()

    nb = nbrmd.reads(rmd)
    rmd2 = nbrmd.writes(nb)

    assert rmd == rmd2
