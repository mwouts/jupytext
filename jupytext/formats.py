"""
In this file the various text notebooks formats are defined. Please contribute
new formats here!
"""

import os
from .header import header_to_metadata_and_cell, insert_or_test_version_number
from .cell_reader import MarkdownCellReader, RMarkdownCellReader, \
    LightScriptCellReader, RScriptCellReader, DoublePercentScriptCellReader
from .cell_to_text import MarkdownCellExporter, RMarkdownCellExporter, \
    LightScriptCellExporter, RScriptCellExporter, DoublePercentCellExporter
from .stringparser import StringParser


class NotebookFormatDescription:
    """Description of a notebook format"""

    def __init__(self,
                 format_name,
                 extension,
                 header_prefix,
                 cell_reader_class,
                 cell_exporter_class,
                 current_version_number,
                 min_readable_version_number=None):
        self.format_name = format_name
        self.extension = extension
        self.header_prefix = header_prefix
        self.cell_reader_class = cell_reader_class
        self.cell_exporter_class = cell_exporter_class
        self.current_version_number = current_version_number
        self.min_readable_version_number = min_readable_version_number


JUPYTEXT_FORMATS = \
    [
        NotebookFormatDescription(
            format_name='markdown',
            extension='.md',
            header_prefix='',
            cell_reader_class=MarkdownCellReader,
            cell_exporter_class=MarkdownCellExporter,
            # Version 1.0 on 2018-08-31 - jupytext v0.6.0 : Initial version
            current_version_number='1.0'),

        NotebookFormatDescription(
            format_name='rmarkdown',
            extension='.Rmd',
            header_prefix='',
            cell_reader_class=RMarkdownCellReader,
            cell_exporter_class=RMarkdownCellExporter,
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            current_version_number='1.0'),

        NotebookFormatDescription(
            format_name='rscript',
            extension='.R',
            header_prefix="#'",
            cell_reader_class=RScriptCellReader,
            cell_exporter_class=RScriptCellExporter,
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            current_version_number='1.0')] + \
    [
        NotebookFormatDescription(
            format_name='light',
            extension=ext,
            header_prefix='#',
            cell_reader_class=LightScriptCellReader,
            cell_exporter_class=LightScriptCellExporter,
            # Version 1.3 on 2018-09-19 - jupytext v0.7.0 : Metadata are
            # allowed for all cell types (and then include 'cell_type')
            # Version 1.2 on 2018-09-05 - jupytext v0.6.3 : Metadata bracket
            # can be omitted when empty, if previous line is empty #57
            # Version 1.1 on 2018-08-25 - jupytext v0.6.0 : Cells separated
            # with one blank line #38
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            current_version_number='1.3',
            min_readable_version_number='1.1') for ext in ['.jl', '.py']] + \
    [
        NotebookFormatDescription(
            format_name='percent',
            extension=ext,
            header_prefix='#',
            cell_reader_class=DoublePercentScriptCellReader,
            cell_exporter_class=DoublePercentCellExporter,
            # Version 1.0 on 2018-09-18 - jupytext v0.7.0 : Initial version
            current_version_number='1.0')
        for ext in
        ['.jl', '.py', '.R']]

NOTEBOOK_EXTENSIONS = list(dict.fromkeys(
    ['.ipynb'] + [fmt.extension for fmt in JUPYTEXT_FORMATS]))


def get_format(ext, format_name=None):
    """Return the format description for the desired extension"""
    for fmt in JUPYTEXT_FORMATS:
        if fmt.extension == ext:
            if not format_name or fmt.format_name == format_name:
                return fmt

    if format_name:
        raise TypeError("Format '{}' is not associated to extension '{}'"
                        .format(format_name, ext))
    raise TypeError("Not format associated to extension '{}'".format(ext))


def guess_format(text, ext):
    """Guess the format of the file, given its extension and content"""
    lines = text.splitlines()

    metadata, _, _ = header_to_metadata_and_cell(
        lines, "#'" if ext == '.R' else '#')

    if metadata:
        return metadata.get('jupytext_format_name')

    # Is this a Hydrogen-like script?
    # Or a Sphinx-gallery script?
    if ext in ['.jl', '.py', '.R']:
        twenty_dash = ''.join(['#'] * 20)
        double_percent = '# %%'
        double_percent_and_space = double_percent + ' '
        twenty_dash_count = 0
        double_percent_count = 0

        parser = StringParser(language='R' if ext == '.R' else 'python')
        for line in lines:
            parser.read_line(line)
            if parser.is_quoted():
                continue

            # Don't count escaped Jupyter magics (no space between
            # %% and command) as cells
            if line == double_percent or \
                    line.startswith(double_percent_and_space):
                double_percent_count += 1

            if line.startswith(twenty_dash):
                twenty_dash_count += 1

        if double_percent_count >= 2 or twenty_dash_count >= 2:
            if double_percent_count >= twenty_dash_count:
                return 'percent'
            return 'sphinx'

    # Default format
    return None


def check_file_version(notebook, source_path, outputs_path):
    """Raise if file version in source file would override outputs"""
    if not insert_or_test_version_number():
        return

    _, ext = os.path.splitext(source_path)
    version = notebook.metadata.get('jupytext_format_version')
    format_name = notebook.metadata.get('jupytext_format_name')
    if version:
        del notebook.metadata['jupytext_format_version']

    fmt = get_format(ext, format_name)
    current = fmt.current_version_number

    # Missing version, still generated by jupytext?
    if notebook.metadata and not version:
        version = current

    # Same version? OK
    if version == fmt.current_version_number:
        return

    # Version larger than minimum readable version
    if (fmt.min_readable_version_number or current) <= version <= current:
        return

        # Not merging? OK
    if source_path == outputs_path:
        return

    raise ValueError("File {} has jupytext_format_version={}, but "
                     "current version for that extension is {}.\n"
                     "It would not be safe to override the source of {} "
                     "with that file.\n"
                     "Please remove one or the other file."
                     .format(os.path.basename(source_path),
                             version, current,
                             os.path.basename(outputs_path)))
