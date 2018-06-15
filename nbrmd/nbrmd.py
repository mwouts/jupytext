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
    new_code_cell, new_markdown_cell, new_notebook, nbformat, nbformat_minor,
)

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------

_header_re = re.compile(r"^---\s*")
_start_code_re = re.compile(r"^```\{")
_end_code_re = re.compile(r"^```\s*")


class State(Enum):
    HEADER = 1
    MARKDOWN = 2
    CODE = 3


class RmdReaderError(Exception):
    pass


class RmdReader(NotebookReader):

    def reads(self, s, **kwargs):
        return self.to_notebook(s, **kwargs)

    def markdown_cell(self, lines):
        if len(lines) >= 1:
            if lines[-1] == u'':
                lines = lines[:-1]
        return new_markdown_cell(source=u'\n'.join(lines))

    def to_notebook(self, s, **kwargs):
        lines = s.splitlines()

        header = None
        cells = []
        cell_lines = []
        state = State.MARKDOWN

        for line in lines:
            if state is State.HEADER:
                if _header_re.match(line):
                    state = State.MARKDOWN
                else:
                    header.append(line)
            elif state is State.MARKDOWN:
                if header is None and _header_re.match(line):
                    state = State.HEADER
                    header = []
                elif _start_code_re.match(line):
                    if len(cell_lines):
                        cells.append(self.markdown_cell(cell_lines))
                    # TODO: parse cell options
                    cell_lines = []
                    state = State.CODE
                else:
                    if line != u'' or len(cell_lines):
                        cell_lines.append(line)
            elif state is State.CODE:
                if _end_code_re.match(line):
                    cells.append(new_code_cell(source=u'\n'.join(cell_lines)))
                    cell_lines = []
                    state = State.MARKDOWN
                else:
                    cell_lines.append(line)

        # Append last cell if not empty
        if state is State.MARKDOWN:
            if len(cell_lines):
                cells.append(new_markdown_cell(source=u'\n'.join(cell_lines)))
        elif state is State.CODE:
            raise RmdReaderError('Unterminated code cell')
        elif state is State.HEADER:
            raise RmdReaderError('Unterminated YAML header')

        # TODO: Parse YAML header
        nb = new_notebook(cells=cells)
        return nb


class RmdWriter(NotebookWriter):

    def writes(self, nb, **kwargs):
        # TODO: write YAML header
        lines = []
        for cell in nb.cells:
            if cell.cell_type == u'code':
                input = cell.get(u'source')
                if input is not None:
                    lines.append(u'```{python}')
                    lines.extend(input.splitlines())
                    lines.append(u'```')
                    lines.append(u'')
            elif cell.cell_type == u'markdown' or cell.cell_type == u'raw':
                input = cell.get(u'source')
                if input is not None:
                    lines.extend(input.splitlines())
                    lines.append(u'')
        return u'\n'.join(lines)


_reader = RmdReader()
_writer = RmdWriter()

reads = _reader.reads
read = _reader.read
to_notebook = _reader.to_notebook
write = _writer.write
writes = _writer.writes
