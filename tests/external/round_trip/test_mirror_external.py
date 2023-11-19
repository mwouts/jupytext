import pytest

from ...functional.round_trip.test_mirror import assert_conversion_same_as_mirror
from ...utils import list_notebooks

"""---------------------------------------------------------------------------------

Part I: ipynb -> fmt -> ipynb

---------------------------------------------------------------------------------"""


@pytest.mark.requires_pandoc
@pytest.mark.parametrize(
    "nb_file",
    list_notebooks("ipynb", skip="(functional|Notebook with|flavors|invalid|305)"),
)
def test_ipynb_to_pandoc(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "md:pandoc", "ipynb_to_pandoc")


@pytest.mark.requires_quarto
@pytest.mark.parametrize(
    "nb_file",
    list_notebooks(
        "ipynb",
        skip="(functional|Notebook with|plotly_graphs|flavors|complex_metadata|"
        "update83|raw_cell|_66|nteract|LaTeX|invalid|305|text_outputs|ir_notebook|jupyter|with_R_magic)",
    ),
)
def test_ipynb_to_quarto(
    nb_file,
    no_jupytext_version_number,
):
    assert_conversion_same_as_mirror(nb_file, "qmd", "ipynb_to_quarto")


@pytest.mark.requires_sphinx_gallery
@pytest.mark.parametrize(
    "nb_file", list_notebooks("ipynb_py", skip="(raw|hash|frozen|magic|html|164|long)")
)
def test_ipynb_to_python_sphinx(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "py:sphinx", "ipynb_to_sphinx")


"""---------------------------------------------------------------------------------

Part II: text -> ipynb -> text

---------------------------------------------------------------------------------"""


@pytest.mark.parametrize("nb_file", list_notebooks("Rmd"))
def test_Rmd_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb", "Rmd_to_ipynb")


@pytest.mark.requires_sphinx_gallery
@pytest.mark.parametrize("nb_file", list_notebooks("sphinx"))
def test_sphinx_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(nb_file, "ipynb:sphinx", "sphinx_to_ipynb")


@pytest.mark.requires_sphinx_gallery
@pytest.mark.parametrize("nb_file", list_notebooks("sphinx"))
def test_sphinx_md_to_ipynb(nb_file, no_jupytext_version_number):
    assert_conversion_same_as_mirror(
        nb_file,
        {"extension": ".ipynb", "format_name": "sphinx", "rst2md": True},
        "sphinx-rst2md_to_ipynb",
        compare_notebook=True,
    )
