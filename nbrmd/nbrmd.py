"""Read and write notebooks as RStudio notebook files, with .Rmd extension.

Raw and markdown cells are converted to markdown, while code cells are converted
to code chunks. The transformation is reversible and all inputs are preserved (not
outputs, though).

Authors:

* Marc Wouts
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import re
from enum import Enum
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import (
    new_code_cell, new_markdown_cell, new_raw_cell, new_notebook
)
import yaml

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------

_header_re = re.compile(r"^---\s*")
_start_code_re = re.compile(r"^```\{(.*)\}\s*")
_end_code_re = re.compile(r"^```\s*")


class State(Enum):
    NONE = 0
    HEADER = 1
    MARKDOWN = 2
    CODE = 3


class RmdReaderError(Exception):
    pass


class RmdReader(NotebookReader):

    def reads(self, s, **kwargs):
        return self.to_notebook(s, **kwargs)

    def to_notebook(self, s, **kwargs):
        lines = s.splitlines()

        cells = []
        cell_lines = []
        chunk_options = None
        state = State.NONE

        for line in lines:
            if state is State.NONE:
                if _header_re.match(line):
                    state = State.HEADER
                    continue
                state = State.MARKDOWN

            if state is State.HEADER:
                if _header_re.match(line):
                    if len(cell_lines):
                        cells.append(new_raw_cell(source=u'\n'.join(['---'] + cell_lines + ['---'])))
                    cell_lines = []
                    state = State.MARKDOWN
                    continue

            if state is State.MARKDOWN:
                if _start_code_re.match(line):
                    if len(cell_lines):
                        cells.append(new_markdown_cell(source=u'\n'.join(cell_lines)))

                    chunk_options = _start_code_re.findall(line)[0]
                    cell_lines = []
                    state = State.CODE
                    continue

            if state is State.CODE:
                if _end_code_re.match(line):
                    cells.append(new_code_cell(source=u'\n'.join(cell_lines),
                                               metadata={'chunk_options': chunk_options}))
                    cell_lines = []
                    state = State.MARKDOWN
                    continue

            cell_lines.append(line)

        # Append last cell if not empty
        if state is State.MARKDOWN:
            if len(cell_lines):
                cells.append(new_markdown_cell(source=u'\n'.join(cell_lines)))
        elif state is State.CODE:
            raise RmdReaderError('Unterminated code cell')
        elif state is State.HEADER:
            raise RmdReaderError('Unterminated YAML header')

        nb = new_notebook(cells=cells)
        return nb


class RmdWriter(NotebookWriter):

    def writes(self, nb, **kwargs):
        lines = []
        for cell in nb.cells:
            if cell.cell_type == u'code':
                chunk_options = cell.get(u'metadata', {}).get(u'chunk_options', 'python')
                lines.append(u'```{' + chunk_options + '}')
                input = cell.get(u'source')
                if input is not None:
                    lines.extend(input.splitlines())
                lines.append(u'```')
            elif cell.cell_type == u'markdown' or cell.cell_type == u'raw':
                lines.append(cell.get(u'source', ''))

        # End file with a line return
        lines.append('')

        return u'\n'.join(lines)


_reader = RmdReader()
_writer = RmdWriter()

reads = _reader.reads
read = _reader.read
to_notebook = _reader.to_notebook
write = _writer.write
writes = _writer.writes
