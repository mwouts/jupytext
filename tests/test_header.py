from nbformat.v4.nbbase import new_notebook, new_raw_cell, new_markdown_cell
from jupytext.compare import compare
import jupytext
from jupytext.header import (
    uncomment_line,
    header_to_metadata_and_cell,
    metadata_and_cell_to_header,
)
from jupytext.formats import get_format_implementation


def test_uncomment():
    assert uncomment_line("# line one", "#") == "line one"
    assert uncomment_line("#line two", "#") == "line two"
    assert uncomment_line("#line two", "") == "#line two"


def test_header_to_metadata_and_cell_blank_line():
    text = """---
title: Sample header
---

Header is followed by a blank line
"""
    lines = text.splitlines()
    metadata, _, cell, pos = header_to_metadata_and_cell(lines, "")

    assert metadata == {}
    assert cell.cell_type == "raw"
    assert (
        cell.source
        == """---
title: Sample header
---"""
    )
    assert cell.metadata == {}
    assert lines[pos].startswith("Header is")


def test_header_to_metadata_and_cell_no_blank_line():
    text = """---
title: Sample header
---
Header is not followed by a blank line
"""
    lines = text.splitlines()
    metadata, _, cell, pos = header_to_metadata_and_cell(lines, "")

    assert metadata == {}
    assert cell.cell_type == "raw"
    assert (
        cell.source
        == """---
title: Sample header
---"""
    )
    assert cell.metadata == {"lines_to_next_cell": 0}
    assert lines[pos].startswith("Header is")


def test_header_to_metadata_and_cell_metadata():
    text = """---
title: Sample header
jupyter:
  mainlanguage: python
---
"""
    lines = text.splitlines()
    metadata, _, cell, pos = header_to_metadata_and_cell(lines, "")

    assert metadata == {"mainlanguage": "python"}
    assert cell.cell_type == "raw"
    assert (
        cell.source
        == """---
title: Sample header
---"""
    )
    assert cell.metadata == {"lines_to_next_cell": 0}
    assert pos == len(lines)


def test_metadata_and_cell_to_header(no_jupytext_version_number):
    metadata = {"jupytext": {"mainlanguage": "python"}}
    nb = new_notebook(
        metadata=metadata, cells=[new_raw_cell(source="---\ntitle: Sample header\n---")]
    )
    header, lines_to_next_cell = metadata_and_cell_to_header(
        nb, metadata, get_format_implementation(".md"), ".md"
    )
    assert (
        "\n".join(header)
        == """---
title: Sample header
jupyter:
  jupytext:
    mainlanguage: python
---"""
    )
    assert nb.cells == []
    assert lines_to_next_cell is None


def test_metadata_and_cell_to_header2(no_jupytext_version_number):
    nb = new_notebook(cells=[new_markdown_cell(source="Some markdown\ntext")])
    header, lines_to_next_cell = metadata_and_cell_to_header(
        nb, {}, get_format_implementation(".md"), ".md"
    )
    assert header == []
    assert len(nb.cells) == 1
    assert lines_to_next_cell is None


def test_notebook_from_plain_script_has_metadata_filter(
    script="""print('Hello world")
""",
):
    nb = jupytext.reads(script, ".py")
    assert nb.metadata.get("jupytext", {}).get("notebook_metadata_filter") == "-all"
    assert nb.metadata.get("jupytext", {}).get("cell_metadata_filter") == "-all"
    script2 = jupytext.writes(nb, ".py")

    compare(script2, script)


def test_multiline_metadata(
    no_jupytext_version_number,
    notebook=new_notebook(
        metadata={
            "multiline": """A multiline string

with a blank line""",
            "jupytext": {"notebook_metadata_filter": "all"},
        }
    ),
    markdown="""---
jupyter:
  jupytext:
    notebook_metadata_filter: all
  multiline: 'A multiline string


    with a blank line'
---
""",
):
    actual = jupytext.writes(notebook, ".md")
    compare(actual, markdown)
    nb2 = jupytext.reads(markdown, ".md")
    compare(nb2, notebook)


def test_header_in_html_comment():
    text = """<!--

---
jupyter:
  title: Sample header
---

-->
"""
    lines = text.splitlines()
    metadata, _, cell, _ = header_to_metadata_and_cell(lines, "")

    assert metadata == {"title": "Sample header"}
    assert cell is None


def test_header_to_html_comment(no_jupytext_version_number):
    metadata = {"jupytext": {"mainlanguage": "python", "hide_notebook_metadata": True}}
    nb = new_notebook(metadata=metadata, cells=[])
    header, lines_to_next_cell = metadata_and_cell_to_header(
        nb, metadata, get_format_implementation(".md"), ".md"
    )
    compare(
        "\n".join(header),
        """<!--

---
jupyter:
  jupytext:
    hide_notebook_metadata: true
    mainlanguage: python
---

-->""",
    )
