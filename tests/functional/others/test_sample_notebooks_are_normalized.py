import nbformat
import pytest
from packaging import version

import jupytext


@pytest.mark.skipif(
    version.parse(nbformat.__version__) <= version.parse("5.7"),
    reason="normalize is not available",
)
def test_sample_notebooks_are_normalized(any_nb_file):
    if "myst/" in any_nb_file and not jupytext.myst.is_myst_available():
        pytest.skip("myst_parser not found")
    nb = jupytext.read(any_nb_file)

    changes, normalized_nb = nbformat.validator.normalize(nb)
    nbformat.validate(normalized_nb)

    if changes:  # pragma: no cover
        with open(any_nb_file, "w") as fp:
            jupytext.write(normalized_nb, fp)

        assert not changes

    nbformat.validate(nb)
