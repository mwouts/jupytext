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
import re
from copy import copy
from enum import Enum
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import (
    new_code_cell, new_markdown_cell, new_notebook
)
import nbformat

from .chunk_options import to_metadata, to_chunk_options
from .header import header_to_metadata_and_cell, metadata_and_cell_to_header
from .languages import get_default_language, find_main_language, cell_language


# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------


class State(Enum):
    MARKDOWN = 1
    CODE = 2


_header_re = re.compile(r"^---\s*")
_end_code_re = re.compile(r"^```\s*")

notebook_extensions = ['.ipynb', '.Rmd', '.md', '.py', '.R']


class RmdReader(NotebookReader):

    def __init__(self, markdown=False):
        self.start_code_re = re.compile(r"^```(.*)\s*") if markdown \
            else re.compile(r"^```\{(.*)\}\s*")

    def reads(self, s, **kwargs):
        return self.to_notebook(s, **kwargs)

    def to_notebook(self, s, **kwargs):
        lines = s.splitlines()

        cells = []
        metadata, header_cell, pos = header_to_metadata_and_cell(lines)

        if header_cell:
            cells.append(header_cell)

        if pos > 0:
            lines = lines[pos:]

        cell_lines = []

        def add_cell(new_cell=new_markdown_cell):
            if len(cell_lines) == 0:
                return

            if cell_lines[-1] == '':
                if len(cell_lines) > 1 or len(cells) == 0:
                    cells.append(new_cell(
                        source=u'\n'.join(cell_lines[:-1])))
                else:
                    cells[-1]['metadata']['noskipline'] = True
                    cells.append(new_cell(
                        source=u'\n'.join(cell_lines)))
            else:
                cells.append(new_cell(source=u'\n'.join(cell_lines),
                                      metadata={u'noskipline': True}))

        cell_metadata = {}
        state = State.MARKDOWN
        testblankline = False

        for line in lines:
            if testblankline:
                # Set 'noskipline' metadata if
                # no blank line is found after cell
                testblankline = False
                if line == '':
                    continue
                else:
                    if len(cells):
                        cells[-1]['metadata']['noskipline'] = True

            if state is State.MARKDOWN:
                if self.start_code_re.match(line):
                    add_cell()
                    cell_lines = []

                    chunk_options = self.start_code_re.findall(line)[0]
                    language, cell_metadata = to_metadata(chunk_options)
                    cell_metadata['language'] = language
                    state = State.CODE
                    continue

            if state is State.CODE:
                if _end_code_re.match(line):
                    cells.append(new_code_cell(source='\n'.join(cell_lines),
                                               metadata=cell_metadata))
                    cell_lines = []
                    cell_metadata = {}
                    state = State.MARKDOWN
                    testblankline = True
                    continue

            cell_lines.append(line)

        # Append last cell if not empty
        if state is State.MARKDOWN:
            add_cell()
        elif state is State.CODE:
            cells.append(new_code_cell(source='\n'.join(cell_lines),
                                       metadata=cell_metadata))

        find_main_language(metadata, cells)

        nb = new_notebook(cells=cells, metadata=metadata)
        return nb


class RmdWriter(NotebookWriter):

    def __init__(self, markdown=False):
        self.markdown = markdown

    def writes(self, nb):
        nb = copy(nb)
        default_language = get_default_language(nb)
        lines = metadata_and_cell_to_header(nb)

        for cell in nb.cells:
            if cell.cell_type in ['raw', 'markdown']:
                lines.append(cell.get('source', ''))
                if not cell.get('metadata', {}).get('noskipline', False):
                    lines.append('')
            elif cell.cell_type == 'code':
                input = cell.get('source').splitlines()
                cell_metadata = cell.get('metadata', {})
                if 'noskipline' in cell_metadata:
                    noskipline = cell_metadata['noskipline']
                    del cell_metadata['noskipline']
                else:
                    noskipline = False
                language = cell_language(input) or default_language
                if self.markdown:
                    lines.append(
                        u'```' + to_chunk_options(language, cell_metadata))
                else:
                    lines.append(
                        u'```{' +
                        to_chunk_options(language, cell_metadata) + '}')
                if input is not None:
                    lines.extend(input)
                lines.append(u'```')
                if not noskipline:
                    lines.append('')

        lines.append('')

        return '\n'.join(lines)


_readers = {'.Rmd': RmdReader(), '.md': RmdReader(markdown=True)}
_writers = {'.Rmd': RmdWriter(), '.md': RmdWriter(markdown=True)}


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
