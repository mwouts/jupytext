import nbformat
import pytest

from .utils import list_notebooks


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all"))
def test_sample_notebooks_are_normalized(nb_file):
    nb = nbformat.read(nb_file, as_version=nbformat.current_nbformat)

    changes, normalized_nb = nbformat.validator.normalize(nb)
    nbformat.validate(normalized_nb)

    if changes:
        with open(nb_file, "w") as fp:
            nbformat.write(normalized_nb, fp)

        assert not changes

    nbformat.validate(nb)
