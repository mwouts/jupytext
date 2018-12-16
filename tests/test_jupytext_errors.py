import pytest
import jupytext
from nbformat.v4.nbbase import new_notebook


def test_read_wrong_ext(tmpdir, nb_file='notebook.ext'):
    nb_file = tmpdir.join(nb_file)
    nb_file.write('{}')
    with pytest.raises(TypeError):
        jupytext.readf(str(nb_file))


def test_write_wrong_ext(tmpdir, nb_file='notebook.ext'):
    nb_file = str(tmpdir.join(nb_file))
    with pytest.raises(TypeError):
        jupytext.writef(new_notebook(), nb_file)
