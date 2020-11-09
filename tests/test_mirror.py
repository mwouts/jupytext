"""Here we generate mirror representation of py, Rmd and ipynb files
as py or ipynb, and make sure that these representations minimally
change on new releases.
"""

import os
import pytest
from nbformat.v4.nbbase import new_notebook
from jupytext.compare import compare

import jupytext
from jupytext.compare import compare_notebooks, combine_inputs_with_outputs
from jupytext.formats import (
    long_form_one_format,
    check_auto_ext,
    auto_ext_from_metadata,
)
from jupytext.languages import _SCRIPT_EXTENSIONS
from jupytext.paired_paths import full_path
from .utils import (
    list_notebooks,
    skip_if_dict_is_not_ordered,
    requires_pandoc,
    requires_sphinx_gallery,
    requires_myst,
)

pytestmark = skip_if_dict_is_not_ordered


def create_mirror_file_if_missing(mirror_file, notebook, fmt):
    if not os.path.isfile(mirror_file):
        jupytext.write(notebook, mirror_file, fmt=fmt)


def test_create_mirror_file_if_missing(tmpdir, no_jupytext_version_number):
    py_file = str(tmpdir.join("notebook.py"))
    assert not os.path.isfile(py_file)
    create_mirror_file_if_missing(py_file, new_notebook(), "py")
    assert os.path.isfile(py_file)


def assert_conversion_same_as_mirror(nb_file, fmt, mirror_name, compare_notebook=False):
    dirname, basename = os.path.split(nb_file)
    file_name, org_ext = os.path.splitext(basename)
    fmt = long_form_one_format(fmt)
    notebook = jupytext.read(nb_file, fmt=fmt)
    fmt = check_auto_ext(fmt, notebook.metadata, "")
    ext = fmt["extension"]
    mirror_file = os.path.join(
        dirname, "..", "mirror", mirror_name, full_path(file_name, fmt)
    )

    # it's better not to have Jupytext metadata in test notebooks:
    if fmt == "ipynb" and "jupytext" in notebook.metadata:  # pragma: no cover
        notebook.metadata.pop("jupytext")
        jupytext.write(nb_file, fmt=fmt)

    create_mirror_file_if_missing(mirror_file, notebook, fmt)

    # Compare the text representation of the two notebooks
    if compare_notebook:
        # Read and convert the mirror file to the latest nbformat version if necessary
        nb_mirror = jupytext.read(mirror_file, as_version=notebook.nbformat)
        nb_mirror.nbformat_minor = notebook.nbformat_minor
        compare(nb_mirror, notebook)
        return
    elif ext == ".ipynb":
        notebook = jupytext.read(mirror_file)
        fmt.update({"extension": org_ext})
        actual = jupytext.writes(notebook, fmt)
        with open(nb_file, encoding="utf-8") as fp:
            expected = fp.read()
    else:
        actual = jupytext.writes(notebook, fmt)
        with open(mirror_file, encoding="utf-8") as fp:
            expected = fp.read()

    if not actual.endswith("\n"):
        actual = actual + "\n"
    compare(actual, expected)

    # Compare the two notebooks
    if ext != ".ipynb":
        notebook = jupytext.read(nb_file)
        nb_mirror = jupytext.read(mirror_file, fmt=fmt)

        if fmt.get("format_name") == "sphinx":
            nb_mirror.cells = nb_mirror.cells[1:]
            for cell in notebook.cells:
                cell.metadata = {}
            for cell in nb_mirror.cells:
                cell.metadata = {}

        compare_notebooks(nb_mirror, notebook, fmt)

        nb_mirror = combine_inputs_with_outputs(nb_mirror, notebook)
        compare_notebooks(nb_mirror, notebook, fmt, compare_outputs=True)


"""---------------------------------------------------------------------------------

Part I: ipynb -> fmt -> ipynb

---------------------------------------------------------------------------------"""


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all", skip="many hash"))
def test_ipynb_to_light(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "auto", "ipynb_to_script")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all", skip=""))
def test_ipynb_to_percent(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "auto:percent", "ipynb_to_percent")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all", skip=""))
def test_ipynb_to_hydrogen(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "auto:hydrogen", "ipynb_to_hydrogen")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all", skip=""))
def test_ipynb_to_md(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "md", "ipynb_to_md")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all", skip=""))
def test_ipynb_to_Rmd(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "Rmd", "ipynb_to_Rmd")


@requires_pandoc
@pytest.mark.parametrize(
    "nb_file",
    list_notebooks("ipynb", skip="(functional|Notebook with|flavors|invalid|305)"),
)
def test_ipynb_to_pandoc(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "md:pandoc", "ipynb_to_pandoc")


@requires_myst
@pytest.mark.parametrize(
    "nb_file",
    list_notebooks(
        "ipynb_all", skip="html-demo|julia_functional_geometry|xcpp_by_quantstack"
    ),
)
def test_ipynb_to_myst(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "md:myst", "ipynb_to_myst")


@requires_sphinx_gallery
@pytest.mark.parametrize(
    "nb_file", list_notebooks("ipynb_py", skip="(raw|hash|frozen|magic|html|164|long)")
)
def test_ipynb_to_python_sphinx(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "py:sphinx", "ipynb_to_sphinx")


"""---------------------------------------------------------------------------------

Part II: text -> ipynb -> text

---------------------------------------------------------------------------------"""


@pytest.mark.parametrize(
    "nb_file",
    list_notebooks("julia")
    + list_notebooks("python")
    + list_notebooks("R")
    + list_notebooks("ps1"),
)
def test_script_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb", "script_to_ipynb")


@pytest.mark.parametrize("nb_file", list_notebooks("percent"))
def test_percent_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb:percent", "script_to_ipynb")


@pytest.mark.parametrize("nb_file", list_notebooks("hydrogen"))
def test_hydrogen_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb:hydrogen", "script_to_ipynb")


@pytest.mark.parametrize("nb_file", list_notebooks("R_spin"))
def test_spin_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb:spin", "script_to_ipynb")


@pytest.mark.parametrize("nb_file", list_notebooks("md"))
def test_md_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb", "md_to_ipynb")


@pytest.mark.parametrize("nb_file", list_notebooks("Rmd"))
def test_Rmd_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb", "Rmd_to_ipynb")


@requires_sphinx_gallery
@pytest.mark.parametrize("nb_file", list_notebooks("sphinx"))
def test_sphinx_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb:sphinx", "sphinx_to_ipynb")


@requires_sphinx_gallery
@pytest.mark.parametrize("nb_file", list_notebooks("sphinx"))
def test_sphinx_md_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(
        nb_file,
        {"extension": ".ipynb", "format_name": "sphinx", "rst2md": True},
        "sphinx-rst2md_to_ipynb",
        compare_notebook=True,
    )


"""---------------------------------------------------------------------------------

Part III: More specific round trip tests

---------------------------------------------------------------------------------"""


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_all", skip=""))
def test_ipynb_to_percent_to_light(nb_file):
    nb = jupytext.read(nb_file)
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


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py", skip=""))
def test_ipynb_to_python_vim(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(
        nb_file,
        {"extension": ".py", "cell_markers": "{{{,}}}"},
        "ipynb_to_script_vim_folding_markers",
    )


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py", skip=""))
def test_ipynb_to_python_vscode(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(
        nb_file,
        {"extension": ".py", "cell_markers": "region,endregion"},
        "ipynb_to_script_vscode_folding_markers",
    )


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_R"))
def test_ipynb_to_r(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, ".low.r", "ipynb_to_script")


@pytest.mark.parametrize(
    "nb_file,extension",
    [
        (nb_file, extension)
        for nb_file in list_notebooks("ipynb_scheme")
        for extension in ("ss", "scm")
    ],
)
def test_ipynb_to_scheme(nb_file, extension, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, extension, "ipynb_to_script")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_R"))
def test_ipynb_to_r_percent(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, ".low.r:percent", "ipynb_to_percent")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_R"))
def test_ipynb_to_R_spin(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "R", "ipynb_to_spin")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_R"))
def test_ipynb_to_r_spin(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, ".low.r", "ipynb_to_spin")


@pytest.mark.parametrize(
    "nb_file,extension",
    [
        (nb_file, extension)
        for nb_file in list_notebooks("ipynb_scheme")
        for extension in ("ss", "scm")
    ],
)
def test_ipynb_to_scheme_percent(nb_file, extension, no_jupytext_version_number):
    assert_conversion_same_as_mirror(
        nb_file, "{}:percent".format(extension), "ipynb_to_percent"
    )
