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
import jupytext
from .formats import get_format, guess_format
from .header import header_to_metadata_and_cell, metadata_and_cell_to_header, \
    encoding_and_executable
from .languages import default_language_from_metadata_and_ext, \
    set_main_and_cell_language


class TextNotebookReader(NotebookReader):
    """Text notebook reader"""

    def __init__(self, ext, format_name=None):
        self.ext = ext
        self.format = get_format(ext, format_name)

    def reads(self, s, **_):
        """Read a notebook from text"""
        lines = s.splitlines()

        cells = []
        metadata, header_cell, pos = \
            header_to_metadata_and_cell(lines, self.format.header_prefix)

        if header_cell:
            cells.append(header_cell)

        lines = lines[pos:]

        while lines:
            reader = self.format.cell_reader_class(self.format.extension)
            cell, pos = reader.read(lines)
            cells.append(cell)
            if pos <= 0:
                raise Exception('Blocked at lines ' + '\n'.join(lines[:6]))
            lines = lines[pos:]

        set_main_and_cell_language(metadata, cells, self.format.extension)

        return new_notebook(cells=cells, metadata=metadata)


class TextNotebookWriter(NotebookWriter):
    """Write notebook to their text representations"""

    def __init__(self, ext, format_name=None):
        self.ext = ext
        self.format = get_format(ext, format_name)

    def writes(self, nb, **kwargs):
        """Write the text representation of a notebook to a string"""
        nb = deepcopy(nb)
        default_language = default_language_from_metadata_and_ext(
            nb, self.format.extension)
        if 'main_language' in nb.metadata:
            del nb.metadata['main_language']

        lines = encoding_and_executable(nb, self.ext)
        lines.extend(metadata_and_cell_to_header(nb, self.format))

        cells = [self.format.cell_exporter_class(
            cell, default_language,
            self.format.extension) for cell in nb.cells]

        texts = [cell.cell_to_text() for cell in cells]

        for i, cell in enumerate(cells):
            text = cell.simplify_code_markers(
                texts[i], texts[i + 1] if i + 1 < len(texts) else None, lines)

            lines.extend(text)
            lines.extend([''] * cell.lines_to_next_cell)

            # two blank lines between markdown cells in Rmd
            if self.ext in ['.Rmd', '.md'] and not cell.is_code():
                if i + 1 < len(cells) and not cells[i + 1].is_code():
                    lines.append('')

        return '\n'.join(lines)


def reads(text, ext, as_version=4, format_name=None, **kwargs):
    """Read a notebook from a string"""
    if ext == '.ipynb':
        return nbformat.reads(text, as_version, **kwargs)

    if not format_name:
        format_name = guess_format(text, ext)

    notebook = TextNotebookReader(ext, format_name).reads(text, **kwargs)
    if format_name and jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER:
        if 'jupytext_format_name' not in notebook.metadata:
            notebook.metadata['jupytext_format_name'] = {}
        notebook.metadata['jupytext_format_name'].update(
            {ext[1:]: format_name})

    return notebook


def read(file_or_stream, ext, as_version=4, format_name=None, **kwargs):
    """Read a notebook from a file"""
    if ext == '.ipynb':
        return nbformat.read(file_or_stream, as_version, **kwargs)

    return reads(file_or_stream.read(), ext=ext, format_name=format_name,
                 **kwargs)


def readf(nb_file):
    """Read a notebook from the file with given name"""
    _, ext = os.path.splitext(nb_file)
    with io.open(nb_file, encoding='utf-8') as stream:
        return read(stream, as_version=4, ext=ext)


def writes(notebook, ext, format_name=None,
           version=nbformat.NO_CONVERT, **kwargs):
    """Write a notebook to a string"""
    if ext == '.ipynb':
        return nbformat.writes(notebook, version, **kwargs)

    if not format_name:
        format_name = notebook.metadata.get('jupytext_format_name', {})
        if isinstance(format_name, dict):
            format_name = format_name.get(ext[1:])

    return TextNotebookWriter(ext, format_name).writes(notebook)


def write(notebook, file_or_stream, ext, format_name=None,
          version=nbformat.NO_CONVERT, **kwargs):
    """Write a notebook to a file"""
    if ext == '.ipynb':
        return nbformat.write(notebook, file_or_stream, version, **kwargs)

    return TextNotebookWriter(ext, format_name).write(notebook, file_or_stream)


def writef(notebook, nb_file, format_name=None):
    """Write a notebook to the file with given name"""
    _, ext = os.path.splitext(nb_file)
    with io.open(nb_file, 'w', encoding='utf-8') as stream:
        write(notebook, stream, version=nbformat.NO_CONVERT,
              ext=ext, format_name=format_name)
