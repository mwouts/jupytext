import pytest
import jupytext
from jupytext.header import header_to_metadata_and_cell
from .utils import list_notebooks, requires_nbconvert


@requires_nbconvert
@pytest.mark.parametrize("md_file", list_notebooks("md", skip="jupytext"))
def test_markdown_jupytext_nbconvert_is_identity(md_file):
    """Test that a Markdown file, converted to a notebook, then
    exported back to Markdown with nbconvert, yields the original file"""

    with open(md_file) as fp:
        md_org = fp.read()

    nb = jupytext.reads(md_org, "md")
    import nbconvert

    md_nbconvert, _ = nbconvert.export(nbconvert.MarkdownExporter, nb)

    # Our expectations
    md_expected = md_org.splitlines()
    # #region and #endregion comments are removed
    md_expected = [
        line
        for line in md_expected
        if line not in ["<!-- #region -->", "<!-- #endregion -->"]
    ]
    # language is not inserted by nbconvert
    md_expected = ["```" if line.startswith("```") else line for line in md_expected]
    # nbconvert inserts no empty line after the YAML header (which is in a Raw cell)
    md_expected = "\n".join(md_expected).replace("---\n\n", "---\n") + "\n"

    # an extra blank line is inserted before code cells
    md_nbconvert = md_nbconvert.replace("\n\n```", "\n```")

    jupytext.compare.compare(md_nbconvert, md_expected)


@requires_nbconvert
@pytest.mark.parametrize("nb_file", list_notebooks(skip="(html|magic)"))
def test_jupytext_markdown_similar_to_nbconvert(nb_file):
    """Test that the nbconvert export for a notebook matches Jupytext's one"""

    nb = jupytext.read(nb_file)

    # Remove cell outputs and metadata
    for cell in nb.cells:
        cell.outputs = []
        cell.execution_count = None
        cell.metadata = {}

    md_jupytext = jupytext.writes(nb, fmt="md")

    import nbconvert

    md_nbconvert, _ = nbconvert.export(nbconvert.MarkdownExporter, nb)

    # our expectations

    # nbconvert file has no YAML header
    md_jupytext_lines = md_jupytext.splitlines()
    _, _, raw_cell, pos = header_to_metadata_and_cell(md_jupytext_lines, "")
    md_jupytext = "\n".join(md_jupytext_lines[pos:]) + "\n"
    if raw_cell is not None:
        md_jupytext = raw_cell.source + "\n\n" + md_jupytext

    # region comments are not in nbconvert
    md_jupytext = md_jupytext.replace("<!-- #region -->\n", "").replace(
        "<!-- #endregion -->\n", ""
    )

    # Jupytext uses HTML comments to keep track of raw cells
    md_jupytext = (
        md_jupytext.replace("\n<!-- #raw -->\n", "")
        .replace("<!-- #raw -->\n", "")
        .replace("\n<!-- #endraw -->\n", "")
    )

    # nbconvert file may start with an empty line
    md_jupytext = md_jupytext.lstrip("\n")
    md_nbconvert = md_nbconvert.lstrip("\n")

    # Jupytext may not always have two blank lines between cells like Jupyter nbconvert
    md_jupytext = md_jupytext.replace("\n\n\n", "\n\n")
    md_nbconvert = md_nbconvert.replace("\n\n\n", "\n\n")

    jupytext.compare.compare(md_nbconvert, md_jupytext)
