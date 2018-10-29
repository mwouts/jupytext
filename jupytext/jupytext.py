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
from nbformat.v4.nbbase import new_notebook, new_code_cell
import nbformat
from .formats import get_format, read_format_from_metadata, guess_format, \
    update_jupytext_formats_metadata, format_name_for_ext, transition_to_jupytext_section_in_metadata
from .header import header_to_metadata_and_cell, metadata_and_cell_to_header, \
    encoding_and_executable, insert_or_test_version_number
from .languages import default_language_from_metadata_and_ext, \
    set_main_and_cell_language


class TextNotebookReader(NotebookReader):
    """Text notebook reader"""

    def __init__(self, ext, format_name=None, freeze_metadata=False):
        self.ext = ext
        self.format = get_format(ext, format_name)
        self.freeze_metadata = freeze_metadata

    def reads(self, s, **_):
        """Read a notebook from text"""
        lines = s.splitlines()

        cells = []
        metadata, header_cell, pos = header_to_metadata_and_cell(lines, self.format.header_prefix)
        comment_magics = metadata.get('jupytext', {}).get('comment_magics')

        if header_cell:
            cells.append(header_cell)

        lines = lines[pos:]

        if self.format.format_name and self.format.format_name.startswith('sphinx'):
            cells.append(new_code_cell(source='%matplotlib inline'))

        cell_metadata = set()

        while lines:
            reader = self.format.cell_reader_class(self.format.extension, comment_magics)
            cell, pos = reader.read(lines)
            cells.append(cell)
            cell_metadata.update(cell.metadata.keys())
            if pos <= 0:
                raise Exception('Blocked at lines ' + '\n'.join(lines[:6]))
            lines = lines[pos:]

        if self.freeze_metadata:
            metadata['jupytext'] = {'metadata_filter': {
                'notebook': {'additional': list(metadata.keys()), 'excluded': 'all'}}}
            metadata['jupytext']['metadata_filter']['cells'] = {
                'additional': list(cell_metadata), 'excluded': 'all'}

        set_main_and_cell_language(metadata, cells, self.format.extension)

        if self.format.format_name and self.format.format_name.startswith('sphinx'):
            filtered_cells = []
            for i, cell in enumerate(cells):
                if cell.source == '' and i > 0 and i + 1 < len(cells) \
                        and cells[i - 1].cell_type != 'markdown' and cells[i + 1].cell_type != 'markdown':
                    continue
                filtered_cells.append(cell)
            cells = filtered_cells

        return new_notebook(cells=cells, metadata=metadata)


class TextNotebookWriter(NotebookWriter):
    """Write notebook to their text representations"""

    def __init__(self, ext, format_name=None):
        self.ext = ext
        self.format = get_format(ext, format_name)
        if not self.format.cell_exporter_class:
            raise ValueError("Saving notebooks in format '{}' is not possible."
                             " Please choose another format."
                             .format(self.format.format_name))

    def writes(self, nb, **kwargs):
        """Write the text representation of a notebook to a string"""
        nb = deepcopy(nb)
        default_language = default_language_from_metadata_and_ext(nb, self.format.extension)
        comment_magics = nb.metadata.get('jupytext', {}).get('comment_magics')
        cell_metadata_filter = nb.metadata.get('jupytext', {}).get('metadata_filter', {}).get('cells')
        if 'main_language' in nb.metadata.get('jupytext', {}):
            del nb.metadata['jupytext']['main_language']

        lines = encoding_and_executable(nb, self.ext)
        lines.extend(metadata_and_cell_to_header(nb, self.format, self.ext))

        cell_exporters = []
        looking_for_first_markdown_cell = self.format.format_name and self.format.format_name.startswith('sphinx')

        for cell in nb.cells:
            if looking_for_first_markdown_cell and cell.cell_type == 'markdown':
                cell.metadata.setdefault('cell_marker', '"""')
                looking_for_first_markdown_cell = False

            cell_exporters.append(self.format.cell_exporter_class(
                cell, default_language, self.format.extension, comment_magics, cell_metadata_filter))

        texts = [cell.cell_to_text() for cell in cell_exporters]

        for i, cell in enumerate(cell_exporters):
            text = cell.simplify_code_markers(
                texts[i], texts[i + 1] if i + 1 < len(texts) else None, lines)

            if i == 0 and self.format.format_name and \
                    self.format.format_name.startswith('sphinx') and \
                    (text in [['%matplotlib inline'], ['# %matplotlib inline']]):
                continue

            lines.extend(text)
            lines.extend([''] * cell.lines_to_next_cell)

            # two blank lines between markdown cells in Rmd
            if self.ext in ['.Rmd', '.md'] and not cell.is_code():
                if i + 1 < len(cell_exporters) and not cell_exporters[i + 1].is_code():
                    lines.append('')

            # "" between two consecutive code cells in sphinx
            if self.format.format_name.startswith('sphinx') and cell.is_code():
                if i + 1 < len(cell_exporters) and cell_exporters[i + 1].is_code():
                    lines.append('""')

        return '\n'.join(lines)


def reads(text, ext, format_name=None,
          rst2md=False, freeze_metadata=False, as_version=4, **kwargs):
    """Read a notebook from a string"""
    if ext.endswith('.ipynb'):
        return nbformat.reads(text, as_version, **kwargs)

    format_name = read_format_from_metadata(text, ext) or format_name

    if not format_name:
        format_name = guess_format(text, ext)
        if format_name == 'sphinx' and rst2md:
            format_name = 'sphinx-rst2md'

    reader = TextNotebookReader(ext, format_name, freeze_metadata)
    notebook = reader.reads(text, **kwargs)
    transition_to_jupytext_section_in_metadata(notebook.metadata, False)

    if format_name and insert_or_test_version_number():
        if format_name == 'sphinx-rst2md' and rst2md:
            format_name = 'sphinx'
        update_jupytext_formats_metadata(notebook, ext, format_name)
        notebook.metadata.setdefault('jupytext', {}).setdefault('text_representation', {}).update(
            {'extension': ext, 'format_name': format_name})

    return notebook


def read(file_or_stream, ext, format_name=None,
         freeze_metadata=False, as_version=4, **kwargs):
    """Read a notebook from a file"""
    if ext.endswith('.ipynb'):
        notebook = nbformat.read(file_or_stream, as_version, **kwargs)
        transition_to_jupytext_section_in_metadata(notebook.metadata, True)
        return notebook

    return reads(file_or_stream.read(), ext=ext, format_name=format_name,
                 freeze_metadata=freeze_metadata, **kwargs)


def readf(nb_file, format_name=None, freeze_metadata=False):
    """Read a notebook from the file with given name"""
    _, ext = os.path.splitext(nb_file)
    with io.open(nb_file, encoding='utf-8') as stream:
        return read(stream, as_version=4, ext=ext, format_name=format_name,
                    freeze_metadata=freeze_metadata)


def writes(notebook, ext, format_name=None,
           version=nbformat.NO_CONVERT, **kwargs):
    """Write a notebook to a string"""
    transition_to_jupytext_section_in_metadata(notebook.metadata, ext.endswith('.ipynb'))

    if ext.endswith('.ipynb'):
        return nbformat.writes(notebook, version, **kwargs)

    if not format_name:
        format_name = format_name_for_ext(notebook.metadata, ext)

    if format_name and insert_or_test_version_number():
        update_jupytext_formats_metadata(notebook, ext, format_name)

    writer = TextNotebookWriter(ext, format_name)
    return writer.writes(notebook)


def write(notebook, file_or_stream, ext, format_name=None,
          version=nbformat.NO_CONVERT, **kwargs):
    """Write a notebook to a file"""
    transition_to_jupytext_section_in_metadata(notebook.metadata, ext.endswith('.ipynb'))

    if ext.endswith('.ipynb'):
        return nbformat.write(notebook, file_or_stream, version, **kwargs)

    if not format_name:
        format_name = format_name_for_ext(notebook.metadata, ext)

    if format_name and insert_or_test_version_number():
        update_jupytext_formats_metadata(notebook, ext, format_name)

    writer = TextNotebookWriter(ext, format_name)
    return writer.write(notebook, file_or_stream)


def writef(notebook, nb_file, format_name=None):
    """Write a notebook to the file with given name"""
    _, ext = os.path.splitext(nb_file)
    with io.open(nb_file, 'w', encoding='utf-8') as stream:
        write(notebook, stream, version=nbformat.NO_CONVERT,
              ext=ext, format_name=format_name)
