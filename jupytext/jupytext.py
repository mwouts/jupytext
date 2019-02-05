"""Read and write Jupyter notebooks as text files"""

import os
import io
import sys
from copy import copy, deepcopy
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import new_notebook, new_code_cell
import nbformat
from .formats import _VALID_FORMAT_OPTIONS
from .formats import read_format_from_metadata, update_jupytext_formats_metadata, rearrange_jupytext_metadata
from .formats import format_name_for_ext, guess_format, divine_format, get_format_implementation, long_form_one_format
from .header import header_to_metadata_and_cell, metadata_and_cell_to_header
from .header import encoding_and_executable, insert_or_test_version_number
from .metadata_filter import update_metadata_filters
from .languages import default_language_from_metadata_and_ext, set_main_and_cell_language
from .pep8 import pep8_lines_between_cells


class TextNotebookConverter(NotebookReader, NotebookWriter):
    """A class that can read or write a Jupyter notebook as text"""

    def __init__(self, fmt):
        self.fmt = copy(long_form_one_format(fmt))
        self.ext = self.fmt['extension']
        self.implementation = get_format_implementation(self.ext, self.fmt.get('format_name'))

    def update_fmt_with_notebook_options(self, metadata):
        """Update format options with the values in the notebook metadata, and record those
        options in the notebook metadata"""
        # format options in notebook have precedence over that in fmt
        for opt in _VALID_FORMAT_OPTIONS:
            if opt in metadata.get('jupytext', {}):
                self.fmt.setdefault(opt, metadata['jupytext'][opt])
            if opt in self.fmt:
                metadata.setdefault('jupytext', {}).setdefault(opt, self.fmt[opt])

    def reads(self, s, **_):
        """Read a notebook represented as text"""
        lines = s.splitlines()

        cells = []
        metadata, jupyter_md, header_cell, pos = header_to_metadata_and_cell(lines,
                                                                             self.implementation.header_prefix,
                                                                             self.implementation.extension)
        default_language = default_language_from_metadata_and_ext(metadata, self.implementation.extension)
        self.update_fmt_with_notebook_options(metadata)

        if header_cell:
            cells.append(header_cell)

        lines = lines[pos:]

        if self.implementation.format_name and self.implementation.format_name.startswith('sphinx'):
            cells.append(new_code_cell(source='%matplotlib inline'))

        cell_metadata = set()

        while lines:
            reader = self.implementation.cell_reader_class(self.fmt, default_language)
            cell, pos = reader.read(lines)
            cells.append(cell)
            cell_metadata.update(cell.metadata.keys())
            if pos <= 0:
                raise Exception('Blocked at lines ' + '\n'.join(lines[:6]))  # pragma: no cover
            lines = lines[pos:]

        update_metadata_filters(metadata, jupyter_md, cell_metadata)
        set_main_and_cell_language(metadata, cells, self.implementation.extension)

        if self.implementation.format_name and self.implementation.format_name.startswith('sphinx'):
            filtered_cells = []
            for i, cell in enumerate(cells):
                if cell.source == '' and i > 0 and i + 1 < len(cells) \
                        and cells[i - 1].cell_type != 'markdown' and cells[i + 1].cell_type != 'markdown':
                    continue
                filtered_cells.append(cell)
            cells = filtered_cells

        # The rst2md option applies just once
        if self.fmt.get('rst2md'):
            metadata['jupytext']['rst2md'] = False

        return new_notebook(cells=cells, metadata=metadata)

    def writes(self, nb, metadata=None, **kwargs):
        """Return the text representation of the notebook"""
        # Copy the notebook, in order to be sure we do not modify the original notebook
        nb = new_notebook(cells=nb.cells, metadata=deepcopy(metadata or nb.metadata))
        default_language = default_language_from_metadata_and_ext(metadata, self.implementation.extension)
        self.update_fmt_with_notebook_options(metadata)

        if 'main_language' in metadata.get('jupytext', {}):
            del metadata['jupytext']['main_language']

        header = encoding_and_executable(nb, metadata, self.ext)
        header_content, header_lines_to_next_cell = metadata_and_cell_to_header(nb, metadata,
                                                                                self.implementation, self.ext)
        header.extend(header_content)

        cell_exporters = []
        looking_for_first_markdown_cell = (self.implementation.format_name and
                                           self.implementation.format_name.startswith('sphinx'))
        split_at_heading = self.fmt.get('split_at_heading', False)

        for cell in nb.cells:
            if looking_for_first_markdown_cell and cell.cell_type == 'markdown':
                cell.metadata.setdefault('cell_marker', '"""')
                looking_for_first_markdown_cell = False

            cell_exporters.append(self.implementation.cell_exporter_class(cell, default_language, self.fmt))

        texts = [cell.cell_to_text() for cell in cell_exporters]
        lines = []

        # concatenate cells in reverse order to determine how many blank lines (pep8)
        for i, cell in reversed(list(enumerate(cell_exporters))):
            text = cell.remove_eoc_marker(texts[i], lines)

            if i == 0 and self.implementation.format_name and \
                    self.implementation.format_name.startswith('sphinx') and \
                    (text in [['%matplotlib inline'], ['# %matplotlib inline']]):
                continue

            lines_to_next_cell = cell.lines_to_next_cell
            if lines_to_next_cell is None:
                lines_to_next_cell = pep8_lines_between_cells(text, lines, self.implementation.extension)

            text.extend([''] * lines_to_next_cell)

            # two blank lines between markdown cells in Rmd
            if self.ext in ['.Rmd', '.md'] and not cell.is_code():
                if i + 1 < len(cell_exporters) and not cell_exporters[i + 1].is_code() and (
                        not split_at_heading or not (texts[i + 1] and texts[i + 1][0].startswith('#'))):
                    text.append('')

            # "" between two consecutive code cells in sphinx
            if self.implementation.format_name.startswith('sphinx') and cell.is_code():
                if i + 1 < len(cell_exporters) and cell_exporters[i + 1].is_code():
                    text.append('""')

            if i + 1 < len(cell_exporters):
                lines = cell_exporters[i + 1].simplify_soc_marker(lines, text)
            lines = text + lines

        if header_lines_to_next_cell is None:
            header_lines_to_next_cell = pep8_lines_between_cells(header_content, lines, self.implementation.extension)

        header.extend([''] * header_lines_to_next_cell)

        if cell_exporters:
            lines = cell_exporters[0].simplify_soc_marker(lines, header)

        return '\n'.join(header + lines)


def reads(text, fmt, as_version=4, **kwargs):
    """Read a notebook from a string"""
    fmt = copy(fmt)
    fmt = long_form_one_format(fmt)
    ext = fmt['extension']

    if ext == '.ipynb':
        return nbformat.reads(text, as_version, **kwargs)

    format_name = read_format_from_metadata(text, ext) or fmt.get('format_name') or guess_format(text, ext)

    if format_name:
        fmt['format_name'] = format_name

    reader = TextNotebookConverter(fmt)
    notebook = reader.reads(text, **kwargs)
    rearrange_jupytext_metadata(notebook.metadata)

    if format_name and insert_or_test_version_number():
        notebook.metadata.setdefault('jupytext', {}).setdefault('text_representation', {}).update(
            {'extension': ext, 'format_name': format_name})

    return notebook


def read(file_or_stream, fmt, as_version=4, **kwargs):
    """Read a notebook from a file"""
    fmt = long_form_one_format(fmt)
    if fmt['extension'] == '.ipynb':
        notebook = nbformat.read(file_or_stream, as_version, **kwargs)
        rearrange_jupytext_metadata(notebook.metadata)
        return notebook

    return reads(file_or_stream.read(), fmt, **kwargs)


def readf(nb_file, fmt=None):
    """Read a notebook from the file with given name"""
    if nb_file == '-':
        text = sys.stdin.read()
        fmt = fmt or divine_format(text)
        return reads(text, fmt)

    _, ext = os.path.splitext(nb_file)
    fmt = copy(fmt or {})
    fmt.update({'extension': ext})
    with io.open(nb_file, encoding='utf-8') as stream:
        return read(stream, fmt, as_version=4)


def writes(notebook, fmt, version=nbformat.NO_CONVERT, **kwargs):
    """Write a notebook to a string"""
    metadata = deepcopy(notebook.metadata)
    rearrange_jupytext_metadata(metadata)
    fmt = copy(fmt)
    fmt = long_form_one_format(fmt, metadata)
    ext = fmt['extension']
    format_name = fmt.get('format_name')

    if ext == '.ipynb':
        # Remove jupytext section if empty
        metadata.get('jupytext', {}).pop('text_representation', {})
        if not metadata.get('jupytext', {}):
            metadata.pop('jupytext', {})
        return nbformat.writes(new_notebook(cells=notebook.cells, metadata=metadata), version, **kwargs)

    if not format_name:
        format_name = format_name_for_ext(metadata, ext, explicit_default=False)

    if format_name:
        fmt['format_name'] = format_name
        update_jupytext_formats_metadata(metadata, fmt)

    writer = TextNotebookConverter(fmt)
    return writer.writes(notebook, metadata)


def write(notebook, file_or_stream, fmt, version=nbformat.NO_CONVERT, **kwargs):
    """Write a notebook to a file"""
    # Python 2 compatibility
    text = u'' + writes(notebook, fmt, version, **kwargs)
    file_or_stream.write(text)
    # Add final newline #165
    if not text.endswith(u'\n'):
        file_or_stream.write(u'\n')


def writef(notebook, nb_file, fmt=None):
    """Write a notebook to the file with given name"""
    if nb_file == '-':
        write(notebook, sys.stdout, fmt)
        return

    _, ext = os.path.splitext(nb_file)
    fmt = copy(fmt or {})
    fmt = long_form_one_format(fmt)
    fmt.update({'extension': ext})
    with io.open(nb_file, 'w', encoding='utf-8') as stream:
        write(notebook, stream, fmt)
