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
from copy import copy
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import new_notebook
import nbformat

from .header import header_to_metadata_and_cell, metadata_and_cell_to_header
from .languages import get_default_language, find_main_language
from .cells import cell_to_text, text_to_cell

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------


notebook_extensions = ['.ipynb', '.Rmd', '.py', '.R']


class RmdReader(NotebookReader):

    def __init__(self, ext):
        self.ext = ext
        self.comment = '' if ext == '.Rmd' else "## " \
            if ext == '.py' else "#' "

    def reads(self, s, **kwargs):
        return self.to_notebook(s, **kwargs)

    def to_notebook(self, s, **kwargs):
        lines = s.splitlines()

        cells = []
        metadata, header_cell, pos = \
            header_to_metadata_and_cell(lines, self.comment)

        if header_cell:
            cells.append(header_cell)

        if pos > 0:
            lines = lines[pos:]

        while len(lines):
            cell, pos = text_to_cell(lines, self.ext)
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


class RmdWriter(NotebookWriter):

    def __init__(self, ext='.Rmd'):
        self.ext = ext
        self.prefix = '' if ext == '.Rmd' else\
            "#' " if ext == '.R' else "## "

    def writes(self, nb):
        nb = copy(nb)
        if self.ext == '.py':
            default_language = 'python'
        elif self.ext == '.R':
            default_language = 'R'
        else:
            default_language = get_default_language(nb)

        lines = metadata_and_cell_to_header(nb, self.prefix)

        for i in range(len(nb.cells)):
            cell = nb.cells[i]
            next_cell = nb.cells[i + 1] if i + 1 < len(nb.cells) else None
            lines.extend(
                cell_to_text(cell, next_cell,
                             default_language=default_language,
                             ext=self.ext))

        return '\n'.join(lines + [''])


_readers = {ext: RmdReader(ext) for ext in notebook_extensions if
            ext != '.ipynb'}
_writers = {ext: RmdWriter(ext) for ext in notebook_extensions if
            ext != '.ipynb'}


def reads(s, as_version=4, ext='.Rmd', **kwargs):
    if ext == '.ipynb':
        return nbformat.reads(s, as_version, **kwargs)
    else:
        return _readers[ext].reads(s, **kwargs)


def read(fp, as_version=4, ext='.Rmd', **kwargs):
    if ext == '.ipynb':
        return nbformat.read(fp, as_version, **kwargs)
    else:
        return _readers[ext].read(fp, **kwargs)


def writes(s, version=nbformat.NO_CONVERT, ext='.Rmd', **kwargs):
    if ext == '.ipynb':
        return nbformat.writes(s, version, **kwargs)
    else:
        return _writers[ext].writes(s)


def write(np, fp, version=nbformat.NO_CONVERT, ext='.Rmd', **kwargs):
    if ext == '.ipynb':
        return nbformat.write(np, fp, version, **kwargs)
    else:
        return _writers[ext].write(np, fp)


def readf(nb_file):
    """Load the notebook from the desired file"""
    file, ext = os.path.splitext(nb_file)
    if ext not in notebook_extensions:
        raise TypeError(
            'File {} is not a notebook. '
            'Expected extensions are {}'.format(nb_file,
                                                notebook_extensions))
    with io.open(nb_file, encoding='utf-8') as fp:
        return read(fp, as_version=4, ext=ext)


def writef(nb, nb_file):
    """Save the notebook in the desired file"""
    file, ext = os.path.splitext(nb_file)
    if ext not in notebook_extensions:
        raise TypeError(
            'File {} is not a notebook. '
            'Expected extensions are {}'.format(nb_file,
                                                notebook_extensions))
    with io.open(nb_file, 'w', encoding='utf-8') as fp:
        write(nb, fp, version=nbformat.NO_CONVERT, ext=ext)


def readme():
    """
    Contents of README.md
    :return:
    """
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'README.md')
    with open(readme_path) as fh:
        return fh.read()
