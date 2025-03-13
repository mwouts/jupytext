"""Here we generate mirror representation of py, Rmd and ipynb files
as py or ipynb, and make sure that these representations minimally
change on new releases.
"""

import os
import re

import pytest
from nbformat.v4.nbbase import new_notebook

import jupytext
from jupytext.compare import (
    assert_conversion_same_as_mirror,
    compare_notebooks,
    create_mirror_file_if_missing,
)
from jupytext.formats import auto_ext_from_metadata
from jupytext.languages import _SCRIPT_EXTENSIONS


def test_create_mirror_file_if_missing(tmpdir, no_jupytext_version_number):
    py_file = str(tmpdir.join("notebook.py"))
    assert not os.path.isfile(py_file)
    create_mirror_file_if_missing(py_file, new_notebook(), "py")
    assert os.path.isfile(py_file)


"""---------------------------------------------------------------------------------

Part I: ipynb -> fmt -> ipynb

---------------------------------------------------------------------------------"""


def test_ipynb_to_percent(ipynb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_file, "auto:percent", "ipynb_to_percent")


def test_ipynb_to_hydrogen(ipynb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_file, "auto:hydrogen", "ipynb_to_hydrogen")


def test_ipynb_to_light(ipynb_to_light, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_to_light, "auto:light", "ipynb_to_script")


def test_ipynb_to_md(ipynb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_file, "md", "ipynb_to_md")


def test_ipynb_to_Rmd(ipynb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_file, "Rmd", "ipynb_to_Rmd")


@pytest.mark.requires_myst
def test_ipynb_to_myst(ipynb_file, no_jupytext_version_number):
    if re.match(
        r".*(html-demo|julia_functional_geometry|xcpp_by_quantstack).*", ipynb_file
    ):
        pytest.skip()
    assert_conversion_same_as_mirror(ipynb_file, "md:myst", "ipynb_to_myst")


"""---------------------------------------------------------------------------------

Part II: text -> ipynb -> text

---------------------------------------------------------------------------------"""


def test_script_to_ipynb(script_to_ipynb, no_jupytext_version_number):
    assert_conversion_same_as_mirror(script_to_ipynb, "ipynb:light", "script_to_ipynb")


def test_percent_to_ipynb(percent_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(percent_file, "ipynb:percent", "script_to_ipynb")


def test_hydrogen_to_ipynb(hydrogen_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(hydrogen_file, "ipynb:hydrogen", "script_to_ipynb")


def test_spin_to_ipynb(r_spin_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(r_spin_file, "ipynb:spin", "script_to_ipynb")


def test_md_to_ipynb(md_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(md_file, "ipynb", "md_to_ipynb")


@pytest.mark.requires_myst
def test_myst_file_has_myst_format(myst_file):
    with open(myst_file) as f:
        text = f.read()
    fmt = jupytext.guess_format(text, ".md")
    assert fmt == ("myst", {})


@pytest.mark.requires_myst
def test_myst_to_ipynb(myst_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(myst_file, "ipynb:myst", "myst_to_ipynb")


"""---------------------------------------------------------------------------------

Part III: More specific round trip tests

---------------------------------------------------------------------------------"""


def test_ipynb_to_percent_to_light(ipynb_file):
    nb = jupytext.read(ipynb_file)
    pct = jupytext.writes(nb, "auto:percent")
    auto_ext = auto_ext_from_metadata(nb.metadata)
    comment = _SCRIPT_EXTENSIONS[auto_ext]["comment"]
    lgt = (
        pct.replace(comment + " %%\n", comment + " +\n")
        .replace(comment + " %% ", comment + " + ")
        .replace(
            comment + "       format_name: percent",
            comment + "       format_name: light",
        )
    )
    nb2 = jupytext.reads(lgt, auto_ext)
    compare_notebooks(nb2, nb)


def test_ipynb_to_python_vim(ipynb_py_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(
        ipynb_py_file,
        {"extension": ".py", "cell_markers": "{{{,}}}"},
        "ipynb_to_script_vim_folding_markers",
    )


def test_ipynb_to_python_vscode(ipynb_py_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(
        ipynb_py_file,
        {"extension": ".py", "cell_markers": "region,endregion"},
        "ipynb_to_script_vscode_folding_markers",
    )


def test_ipynb_to_r_light(ipynb_R_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_R_file, ".low.r:light", "ipynb_to_script")


def test_ipynb_to_r_percent(ipynb_R_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_R_file, ".low.r:percent", "ipynb_to_percent")


def test_ipynb_to_R_spin(ipynb_R_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_R_file, "R:spin", "ipynb_to_spin")


def test_ipynb_to_r_spin(ipynb_R_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(ipynb_R_file, ".low.r:spin", "ipynb_to_spin")


@pytest.mark.parametrize("extension", ("ss", "scm"))
def test_ipynb_to_scheme_light(
    ipynb_scheme_file, extension, no_jupytext_version_number
):
    assert_conversion_same_as_mirror(
        ipynb_scheme_file, f"{extension}:light", "ipynb_to_script"
    )


@pytest.mark.parametrize("extension", ("ss", "scm"))
def test_ipynb_to_scheme_percent(
    ipynb_scheme_file, extension, no_jupytext_version_number
):
    assert_conversion_same_as_mirror(
        ipynb_scheme_file, f"{extension}:percent", "ipynb_to_percent"
    )
