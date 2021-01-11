import pytest
from nbformat.v4.nbbase import new_notebook

import jupytext
from jupytext.formats import JupytextFormatError


def test_read_wrong_ext(tmpdir, nb_file="notebook.ext"):
    nb_file = tmpdir.join(nb_file)
    nb_file.write("{}")
    with pytest.raises(JupytextFormatError):
        jupytext.read(str(nb_file))


def test_write_wrong_ext(tmpdir, nb_file="notebook.ext"):
    nb_file = str(tmpdir.join(nb_file))
    with pytest.raises(JupytextFormatError):
        jupytext.write(new_notebook(), nb_file)
