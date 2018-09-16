"""Read and write notebooks as RStudio notebook files, with .Rmd extension.

Raw and markdown cells are converted to markdown, while code cells are
converted to code chunks. The transformation is reversible and all inputs
are preserved (not outputs, though).

Authors:

* Marc Wouts
"""

import os
import io
from copy import deepcopy
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import new_notebook
import nbformat

from .header import header_to_metadata_and_cell, metadata_and_cell_to_header, \
    encoding_and_executable
from .languages import default_language_from_metadata_and_ext, \
    set_main_and_cell_language
from .cell_to_text import CellExporter
from .cell_reader import CellReader

NOTEBOOK_EXTENSIONS = ['.ipynb', '.Rmd', '.md', '.jl', '.py', '.R']


def markdown_comment(ext):
    """Markdown escape for given notebook extension"""
    return '' if ext in ['.Rmd', '.md'] else "#'" if ext == '.R' else "#"


class TextNotebookReader(NotebookReader):
    """Text notebook reader"""

    def __init__(self, ext):
        self.ext = ext
        self.prefix = markdown_comment(ext)

    header_to_metadata_and_cell = header_to_metadata_and_cell

    def markdown_unescape(self, line):
        """Remove markdown escape, if any"""
        if self.prefix == '':
            return line
        line = line[len(self.prefix):]
        if line.startswith(' '):
            line = line[1:]
        return line

    def reads(self, s, **_):
        """Read a notebook from text"""
        lines = s.splitlines()

        cells = []
        metadata, header_cell, pos = \
            self.header_to_metadata_and_cell(lines)

        if header_cell:
            cells.append(header_cell)

        if pos > 0:
            lines = lines[pos:]

        while lines:
            reader = CellReader(self.ext)
            cell, pos = reader.read(lines)
            cells.append(cell)
            if pos <= 0:
                raise Exception('Blocked at lines ' + '\n'.join(lines[:6]))
            lines = lines[pos:]

        set_main_and_cell_language(metadata, cells, self.ext)

        return new_notebook(cells=cells, metadata=metadata)


class TextNotebookWriter(NotebookWriter):
    """Write notebook to their text representations"""

    def __init__(self, ext):
        self.ext = ext
        self.prefix = markdown_comment(ext)

    def markdown_escape(self, lines):
        """
        Escape markdown text
        :param lines:
        :return:
        """
        if self.prefix == '':
            return lines
        return [self.prefix if line == '' else self.prefix + ' ' + line
                for line in lines]

    encoding_and_executable = encoding_and_executable
    metadata_and_cell_to_header = metadata_and_cell_to_header

    def writes(self, nb, **kwargs):
        """Write the text representation of a notebook to a string"""
        nb = deepcopy(nb)
        default_language = default_language_from_metadata_and_ext(nb, self.ext)
        if 'main_language' in nb.metadata:
            del nb.metadata['main_language']

        lines = self.encoding_and_executable(nb)
        lines.extend(self.metadata_and_cell_to_header(nb))

        cells = [CellExporter(cell, default_language, self.ext)
                 for cell in nb.cells]

        texts = [cell.cell_to_text() for cell in cells]

        for i, cell in enumerate(cells):
            text = texts[i]

            if self.ext in ['.py', '.jl']:
                # Simplify cell marker when previous line is blank
                if text[0] == '# + {}' and (not lines or not lines[-1]):
                    text[0] = '# +'

                # remove end of cell marker when redundant
                # with next explicit marker
                if cell.is_code() and text[-1] == '# -':
                    if cell.lines_to_end_of_cell_marker:
                        text = text[:-1] + \
                               [''] * cell.lines_to_end_of_cell_marker + ['# -']
                    elif i + 1 >= len(texts) or \
                            (texts[i + 1][0].startswith('# + {')):
                        text = text[:-1]

            lines.extend(text)
            lines.extend([''] * cell.lines_to_next_cell)

            # two blank lines between markdown cells in Rmd
            if self.ext in ['.Rmd', '.md'] and not cell.is_code():
                if i + 1 < len(cells) and not cells[i + 1].is_code():
                    lines.append('')

        return '\n'.join(lines)


_NOTEBOOK_READERS = {ext: TextNotebookReader(ext)
                     for ext in NOTEBOOK_EXTENSIONS if ext != '.ipynb'}
_NOTEBOOK_WRITERS = {ext: TextNotebookWriter(ext)
                     for ext in NOTEBOOK_EXTENSIONS if ext != '.ipynb'}


def reads(text, ext, as_version=4, **kwargs):
    """Read a notebook from a string"""
    if ext == '.ipynb':
        return nbformat.reads(text, as_version, **kwargs)

    return _NOTEBOOK_READERS[ext].reads(text, **kwargs)


def read(file_or_stream, ext, as_version=4, **kwargs):
    """Read a notebook from a file"""
    if ext == '.ipynb':
        return nbformat.read(file_or_stream, as_version, **kwargs)

    return _NOTEBOOK_READERS[ext].read(file_or_stream, **kwargs)


def writes(notebook, ext, version=nbformat.NO_CONVERT, **kwargs):
    """Write a notebook to a string"""
    if ext == '.ipynb':
        return nbformat.writes(notebook, version, **kwargs)

    return _NOTEBOOK_WRITERS[ext].writes(notebook)


def write(notebook, file_or_stream, ext, version=nbformat.NO_CONVERT,
          **kwargs):
    """Write a notebook to a file"""
    if ext == '.ipynb':
        return nbformat.write(notebook, file_or_stream, version, **kwargs)

    return _NOTEBOOK_WRITERS[ext].write(notebook, file_or_stream)


def readf(nb_file):
    """Read a notebook from the file with given name"""
    _, ext = os.path.splitext(nb_file)
    if ext not in NOTEBOOK_EXTENSIONS:
        raise TypeError(
            'File {} is not a notebook. '
            'Expected extensions are {}'.format(nb_file,
                                                NOTEBOOK_EXTENSIONS))
    with io.open(nb_file, encoding='utf-8') as stream:
        return read(stream, as_version=4, ext=ext)


def writef(notebook, nb_file):
    """Write a notebook to the file with given name"""
    _, ext = os.path.splitext(nb_file)
    if ext not in NOTEBOOK_EXTENSIONS:
        raise TypeError(
            'File {} is not a notebook. '
            'Expected extensions are {}'.format(nb_file,
                                                NOTEBOOK_EXTENSIONS))
    with io.open(nb_file, 'w', encoding='utf-8') as stream:
        write(notebook, stream, version=nbformat.NO_CONVERT, ext=ext)
