import jupytext
from jupytext.compare import compare


def test_identity_write_read(rmd_file, no_jupytext_version_number):
    """Test that writing the notebook with ipynb, and read again, yields identity"""

    with open(rmd_file) as fp:
        rmd = fp.read()

    nb = jupytext.reads(rmd, "Rmd")
    rmd2 = jupytext.writes(nb, "Rmd")

    compare(rmd2, rmd)


def test_two_blank_lines_as_cell_separator():
    rmd = """Some markdown
text


And a new cell
"""

    nb = jupytext.reads(rmd, "Rmd")
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[0].source == "Some markdown\ntext"
    assert nb.cells[1].source == "And a new cell"
