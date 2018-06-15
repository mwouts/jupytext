import nbrmd

def test_ioslides_write_read(file='ioslides.Rmd'):
    """
    Test that writing the notebook with ipynb, and read again, yields identify
    :param file:
    :return:
    """

    with open(file) as fp:
        rmd = fp.read()

    nb = nbrmd.reads(rmd)
    rmd2 = nbrmd.writes(nb)

    assert rmd == rmd2
