from nbrmd.header import header_to_metadata_and_cell, \
    metadata_and_cell_to_header
from nbformat.v4.nbbase import new_notebook, new_raw_cell, new_markdown_cell


def test_header_to_metadata_and_cell_blank_line():
    text = """---
title: Sample header
---

Header is followed by a blank line
"""
    lines = text.splitlines()
    metadata, cell, pos = header_to_metadata_and_cell(lines, '')

    assert metadata == {}
    assert cell.cell_type == 'raw'
    assert cell.source == """---
title: Sample header
---"""
    assert cell.metadata == {}
    assert lines[pos].startswith('Header is')


def test_header_to_metadata_and_cell_no_blank_line():
    text = """---
title: Sample header
---
Header is not followed by a blank line
"""
    lines = text.splitlines()
    metadata, cell, pos = header_to_metadata_and_cell(lines, '')

    assert metadata == {}
    assert cell.cell_type == 'raw'
    assert cell.source == """---
title: Sample header
---"""
    assert cell.metadata == {'noskipline': True}
    assert lines[pos].startswith('Header is')


def test_header_to_metadata_and_cell_metadata():
    text = """---
title: Sample header
jupyter:
  mainlanguage: python
---
"""
    lines = text.splitlines()
    metadata, cell, pos = header_to_metadata_and_cell(lines, '')

    assert metadata == {'mainlanguage': 'python'}
    assert cell.cell_type == 'raw'
    assert cell.source == """---
title: Sample header
---"""
    assert cell.metadata == {'noskipline': True}
    assert pos == len(lines)


def test_metadata_and_cell_to_header():
    nb = new_notebook(cells=[new_raw_cell(
        source="""---
title: Sample header
---""",
        metadata={'noskipline': True})],
        metadata=dict(mainlanguage='python'))
    header = metadata_and_cell_to_header(nb, '')
    assert '\n'.join(header) == """---
title: Sample header
jupyter:
  mainlanguage: python
---"""
    assert nb.cells == []


def test_metadata_and_cell_to_header():
    nb = new_notebook(cells=[new_markdown_cell(source="Some markdown\ntext")])
    header = metadata_and_cell_to_header(nb, '')
    assert header == []
    assert len(nb.cells) == 1
