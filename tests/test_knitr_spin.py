import pytest
import jupytext
from .utils import list_notebooks, skip_if_dict_is_not_ordered


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("r_file", list_notebooks("R_spin"))
def test_jupytext_same_as_knitr_spin(r_file, tmpdir):
    nb = jupytext.read(r_file)
    rmd_jupytext = jupytext.writes(nb, "Rmd")

    # Rmd file generated with spin(hair='R/spin.R', knit=FALSE)
    rmd_file = r_file.replace("R_spin", "Rmd").replace(".R", ".Rmd")

    with open(rmd_file) as fp:
        rmd_spin = fp.read()

    assert rmd_spin == rmd_jupytext
