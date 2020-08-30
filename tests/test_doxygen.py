import pytest
import nbformat
import jupytext
from jupytext.cli import jupytext as jupytext_cli
from jupytext.doxygen import doxygen_to_markdown, markdown_to_doxygen
from jupytext.compare import compare, compare_notebooks

SAMPLE_MARKDOWN = """A latex formula $$1+1$$, another one $$2+2
$$

An inline formula $3+3$
"""

SAMPLE_DOXYGEN = """A latex formula \\f[1+1\\f], another one \\f[2+2
\\f]

An inline formula \\f$3+3\\f$
"""


def test_markdown_to_doxygen():
    compare(markdown_to_doxygen(SAMPLE_MARKDOWN), SAMPLE_DOXYGEN)


def test_doxygen_to_markdown():
    compare(doxygen_to_markdown(SAMPLE_DOXYGEN), SAMPLE_MARKDOWN)


@pytest.mark.parametrize(
    "latex,doxygen",
    [
        ("$$", "$$"),
        ("$1+1$", "\\f$1+1\\f$"),
        ("$1\\$ $", "\\f$1\\$ \\f$"),
        ("$$2+2$$", "\\f[2+2\\f]"),
        ("$$2+2$$ then $$3+3$$", "\\f[2+2\\f] then \\f[3+3\\f]"),
        ("$$2+2\n$$", "\\f[2+2\n\\f]"),
        ("$$1\\$+2\\$=3\\$$$", "\\f[1\\$+2\\$=3\\$\\f]"),
    ],
)
def test_simple_equations_to_doxygen_and_back(latex, doxygen):
    assert markdown_to_doxygen(latex) == doxygen
    assert doxygen_to_markdown(doxygen) == latex


def test_doxygen_equation_markers(tmpdir):
    cfg_file = tmpdir.join("jupytext.toml")
    nb_file = tmpdir.join("notebook.ipynb")
    md_file = tmpdir.join("notebook.md")

    cfg_file.write("hide_notebook_metadata = true\ndoxygen_equation_markers = true")
    nb = jupytext.reads(SAMPLE_MARKDOWN, "md")
    del nb.metadata["jupytext"]
    nbformat.write(nb, str(nb_file))

    jupytext_cli([str(nb_file), "--to", "md"])
    md = md_file.read()

    # Doxygen equation markers
    assert "$$" not in md
    assert "\\f[" in md
    assert "\\f]" in md
    assert "\\f$" in md
    assert "\\f$" in md

    # Metadata hidden
    assert md.startswith("<!--\n\n---\n")

    jupytext_cli([str(md_file), "--to", "notebook"])
    nb2 = nbformat.read(str(nb_file), as_version=4)

    compare_notebooks(nb2, nb)
