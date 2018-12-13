from nbformat.v4.nbbase import new_notebook, new_raw_cell, new_markdown_cell
import mock
from testfixtures import compare
import jupytext
from jupytext.header import uncomment_line, header_to_metadata_and_cell, metadata_and_cell_to_header
from jupytext.formats import get_format

jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER = False


def test_uncomment():
    assert uncomment_line('# line one', '#') == 'line one'
    assert uncomment_line('#line two', '#') == 'line two'
    assert uncomment_line('#line two', '') == '#line two'


def test_header_to_metadata_and_cell_blank_line():
    text = """---
title: Sample header
---

Header is followed by a blank line
"""
    lines = text.splitlines()
    metadata, _, cell, pos = header_to_metadata_and_cell(lines, '')

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
    metadata, _, cell, pos = header_to_metadata_and_cell(lines, '')

    assert metadata == {}
    assert cell.cell_type == 'raw'
    assert cell.source == """---
title: Sample header
---"""
    assert cell.metadata == {'lines_to_next_cell': 0}
    assert lines[pos].startswith('Header is')


def test_header_to_metadata_and_cell_metadata():
    text = """---
title: Sample header
jupyter:
  mainlanguage: python
---
"""
    lines = text.splitlines()
    metadata, _, cell, pos = header_to_metadata_and_cell(lines, '')

    assert metadata == {'mainlanguage': 'python'}
    assert cell.cell_type == 'raw'
    assert cell.source == """---
title: Sample header
---"""
    assert cell.metadata == {'lines_to_next_cell': 0}
    assert pos == len(lines)


def test_metadata_and_cell_to_header():
    nb = new_notebook(
        metadata={'jupytext': {'mainlanguage': 'python'}},
        cells=[new_raw_cell(source="---\ntitle: Sample header\n---", metadata={'noskipline': True})])
    header = metadata_and_cell_to_header(nb, get_format('.md'), '.md')
    assert '\n'.join(header) == """---
title: Sample header
jupyter:
  jupytext:
    mainlanguage: python
---"""
    assert nb.cells == []


def test_metadata_and_cell_to_header2():
    nb = new_notebook(cells=[new_markdown_cell(source="Some markdown\ntext")])
    header = metadata_and_cell_to_header(nb, get_format('.md'), '.md')
    assert header == []
    assert len(nb.cells) == 1


def test_notebook_from_plain_script_has_metadata_filter(script="""print('Hello world")
"""):
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        nb = jupytext.reads(script, '.py')
    assert nb.metadata.get('jupytext', {}).get('metadata_filter', {}).get('notebook') == '-all'
    assert nb.metadata.get('jupytext', {}).get('metadata_filter', {}).get('cells') == '-all'
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', True):
        scripts2 = jupytext.writes(nb, '.py')

    compare(script, scripts2)
