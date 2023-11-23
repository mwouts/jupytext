from copy import deepcopy

import pytest

from jupytext import read, write, writes
from jupytext.compare import compare
from jupytext.formats import long_form_one_format


@pytest.mark.parametrize(
    "fmt",
    ["auto:light", "auto:percent", "md", ".Rmd", ".ipynb"],
)
def test_write_notebook_does_not_change_it(ipynb_py_R_jl_file, fmt, tmpdir):
    nb_org = read(ipynb_py_R_jl_file)
    nb_org_copied = deepcopy(nb_org)
    ext = long_form_one_format(fmt, nb_org.metadata)["extension"]

    writes(nb_org, fmt)
    compare(nb_org, nb_org_copied)

    tmp_dest = str(tmpdir.join("notebook" + ext))
    write(nb_org, tmp_dest, fmt=fmt)
    compare(nb_org, nb_org_copied)
