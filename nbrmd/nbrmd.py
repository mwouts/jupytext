"""Read and write notebooks as RStudio notebook files, with .Rmd extension.

Raw and markdown cells are converted to markdown, while code cells are
converted to code chunks. The transformation is reversible and all inputs
are preserved (not outputs, though).

Authors:

* Marc Wouts
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import io
from copy import deepcopy
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import new_notebook
import nbformat

from .header import header_to_metadata_and_cell, metadata_and_cell_to_header, \
    encoding_and_executable
from .languages import get_default_language, find_main_language
from .cells import start_code_rmd, start_code_r, start_code_py
from .cells import cell_to_text, text_to_cell
from .cells import markdown_to_cell_rmd, markdown_to_cell, code_to_cell
from .magics import unescape_magic

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------


NOTEBOOK_EXTENSIONS = ['.ipynb', '.Rmd', '.py', '.R']


def markdown_comment(ext):
    """Markdown escape for given notebook extension"""
    return '' if ext == '.Rmd' else "#'" if ext == '.R' else "#"


class TextNotebookReader(NotebookReader):
    """Text notebook reader"""

    def __init__(self, ext):
        self.ext = ext
        self.prefix = markdown_comment(ext)
        self.start_code = start_code_rmd if ext == '.Rmd' else \
            start_code_py if ext == '.py' else start_code_r
        if ext == '.Rmd':
            self.markdown_to_cell = markdown_to_cell_rmd

    header_to_metadata_and_cell = header_to_metadata_and_cell
    text_to_cell = text_to_cell
    code_to_cell = code_to_cell
    markdown_to_cell = markdown_to_cell

    def markdown_unescape(self, line):
        """Remove markdown escape, if any"""
        if self.prefix == '':
            return line
        line = line[len(self.prefix):]
        if line.startswith(' '):
            line = line[1:]
        return line

    def reads(self, s, **kwargs):
        """
        Read a notebook from a given string
        :param s:
        :param kwargs:
        :return:
        """
        return self.to_notebook(s, **kwargs)

    def to_notebook(self, text, **kwargs):
        """
        Read a notebook from its text representation
        :param text:
        :param kwargs:
        :return:
        """
        lines = text.splitlines()

        cells = []
        metadata, header_cell, pos = \
            self.header_to_metadata_and_cell(lines)

        if header_cell:
            cells.append(header_cell)

        if pos > 0:
            lines = lines[pos:]

        lines = unescape_magic(lines)

        while lines:
            cell, pos = self.text_to_cell(lines)
            if cell is None:
                break
            cells.append(cell)
            if pos <= 0:
                raise Exception('Blocked at lines ' + '\n'.join(lines[:6]))
            lines = lines[pos:]

        if self.ext == '.Rmd':
            find_main_language(metadata, cells)

        nb = new_notebook(cells=cells, metadata=metadata)
        return nb


class TextNotebookWriter(NotebookWriter):
    """Write notebook to their text representations"""

    def __init__(self, ext='.Rmd'):
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
    cell_to_text = cell_to_text

    def writes(self, nb, **kwargs):
        """Write the text representation of a notebook to a string"""
        nb = deepcopy(nb)
        if self.ext == '.py':
            default_language = 'python'
        elif self.ext == '.R':
            default_language = 'R'
        else:
            default_language = get_default_language(nb)

        lines = self.encoding_and_executable(nb)
        lines.extend(self.metadata_and_cell_to_header(nb))

        for i in range(len(nb.cells)):
            cell = nb.cells[i]
            next_cell = nb.cells[i + 1] if i + 1 < len(nb.cells) else None
            if cell.cell_type == 'raw' and 'active' not in cell.metadata:
                cell.metadata['active'] = ''

            lines.extend(self.cell_to_text(cell, next_cell,
                                           default_language=default_language))

        return '\n'.join(lines + [''])


_NOTEBOOK_READERS = {ext: TextNotebookReader(ext)
                     for ext in NOTEBOOK_EXTENSIONS if ext != '.ipynb'}
_NOTEBOOK_WRITERS = {ext: TextNotebookWriter(ext)
                     for ext in NOTEBOOK_EXTENSIONS if ext != '.ipynb'}


def reads(text, as_version=4, ext='.Rmd', **kwargs):
    """Read a notebook from a string"""
    if ext == '.ipynb':
        return nbformat.reads(text, as_version, **kwargs)

    return _NOTEBOOK_READERS[ext].reads(text, **kwargs)


def read(fp, as_version=4, ext='.Rmd', **kwargs):
    """Read a notebook from a file"""
    if ext == '.ipynb':
        return nbformat.read(fp, as_version, **kwargs)

    return _NOTEBOOK_READERS[ext].read(fp, **kwargs)


def writes(nb, version=nbformat.NO_CONVERT, ext='.Rmd', **kwargs):
    """Write a notebook to a string"""
    if ext == '.ipynb':
        return nbformat.writes(nb, version, **kwargs)

    return _NOTEBOOK_WRITERS[ext].writes(nb)


def write(np, fp, version=nbformat.NO_CONVERT, ext='.Rmd', **kwargs):
    """Write a notebook to a file"""
    if ext == '.ipynb':
        return nbformat.write(np, fp, version, **kwargs)

    return _NOTEBOOK_WRITERS[ext].write(np, fp)


def readf(nb_file):
    """Read a notebook from the file with given name"""
    _, ext = os.path.splitext(nb_file)
    if ext not in NOTEBOOK_EXTENSIONS:
        raise TypeError(
            'File {} is not a notebook. '
            'Expected extensions are {}'.format(nb_file,
                                                NOTEBOOK_EXTENSIONS))
    with io.open(nb_file, encoding='utf-8') as fp:
        return read(fp, as_version=4, ext=ext)


def writef(nb, nb_file):
    """Write a notebook to the file with given name"""
    _, ext = os.path.splitext(nb_file)
    if ext not in NOTEBOOK_EXTENSIONS:
        raise TypeError(
            'File {} is not a notebook. '
            'Expected extensions are {}'.format(nb_file,
                                                NOTEBOOK_EXTENSIONS))
    with io.open(nb_file, 'w', encoding='utf-8') as fp:
        write(nb, fp, version=nbformat.NO_CONVERT, ext=ext)
