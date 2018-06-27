import nbrmd
import pytest


def test_parse_incomplete_code():
    s = """```{python}
1+1
"""
    with pytest.raises(nbrmd.nbrmd.RmdReaderError):
        nbrmd.reads(s)


def test_parse_incomplete_header():
    s = """---
title: Incomplete header
"""
    with pytest.raises(nbrmd.nbrmd.RmdReaderError):
        nbrmd.reads(s)


def test_read_wrong_ext(tmpdir, nb_file='notebook.ext'):
    nb_file = tmpdir.join('nb_file')
    nb_file.write('{}')
    with pytest.raises(TypeError):
        nbrmd.readf(str(nb_file))


def test_write_wrong_ext(tmpdir, nb_file='notebook.ext'):
    nb_file = str(tmpdir.join('nb_file'))
    with pytest.raises(TypeError):
        nbrmd.writef(dict(), nb_file)


def test_readme():
    nbrmd.nbrmd.readme()
