import nbformat
import pytest

import jupytext

from .utils import list_notebooks


@pytest.mark.skipif(nbformat.__version__ <= "5.7", reason="normalize is not available")
@pytest.mark.parametrize("nb_file", list_notebooks("all", skip="(invalid|pyc)"))
def test_sample_notebooks_are_normalized(nb_file):
    nb = jupytext.read(nb_file)

    changes, normalized_nb = nbformat.validator.normalize(nb)
    nbformat.validate(normalized_nb)

    if changes:  # pragma: no cover
        with open(nb_file, "w") as fp:
            jupytext.write(normalized_nb, fp)

        assert not changes

    nbformat.validate(nb)
