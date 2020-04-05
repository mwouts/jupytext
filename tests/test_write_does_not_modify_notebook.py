import pytest
from copy import deepcopy
from jupytext.compare import compare
from itertools import product
from jupytext import read, write, writes
from jupytext.formats import long_form_one_format
from .utils import list_notebooks


@pytest.mark.parametrize(
    "nb_file,fmt",
    product(
        list_notebooks("ipynb_py") + list_notebooks("ipynb_R"),
        ["auto:light", "auto:percent", "md", ".Rmd", ".ipynb"],
    ),
)
def test_write_notebook_does_not_change_it(nb_file, fmt, tmpdir):
    nb_org = read(nb_file)
    nb_org_copied = deepcopy(nb_org)
    ext = long_form_one_format(fmt, nb_org.metadata)["extension"]

    writes(nb_org, fmt)
    compare(nb_org, nb_org_copied)

    tmp_dest = str(tmpdir.join("notebook" + ext))
    write(nb_org, tmp_dest, fmt=fmt)
    compare(nb_org, nb_org_copied)
