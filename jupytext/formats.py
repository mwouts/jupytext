"""
In this file the various text notebooks formats are defined. Please contribute
new formats here!
"""

import os
import re
from .header import header_to_metadata_and_cell, insert_or_test_version_number
from .cell_reader import MarkdownCellReader, RMarkdownCellReader, \
    LightScriptCellReader, RScriptCellReader, DoublePercentScriptCellReader, \
    SphinxGalleryScriptCellReader, SphinxGalleryScriptRst2mdCellReader
from .cell_to_text import MarkdownCellExporter, RMarkdownCellExporter, \
    LightScriptCellExporter, RScriptCellExporter, DoublePercentCellExporter, \
    SphinxGalleryCellExporter
from .stringparser import StringParser
from .languages import _SCRIPT_EXTENSIONS


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
            format_name='spin',
            extension='.R',
            header_prefix="#'",
            cell_reader_class=RScriptCellReader,
            cell_exporter_class=RScriptCellExporter,
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            current_version_number='1.0'),

        NotebookFormatDescription(
            format_name='spin',
            extension='.r',
            header_prefix="#'",
            cell_reader_class=RScriptCellReader,
            cell_exporter_class=RScriptCellExporter,
            current_version_number='1.0')] + \
    [
        NotebookFormatDescription(
            format_name='light',
            extension=ext,
            header_prefix=_SCRIPT_EXTENSIONS[ext]['comment'],
            cell_reader_class=LightScriptCellReader,
            cell_exporter_class=LightScriptCellExporter,
            # Version 1.3 on 2018-09-22 - jupytext v0.7.0rc0 : Metadata are
            # allowed for all cell types (and then include 'cell_type')
            # Version 1.2 on 2018-09-05 - jupytext v0.6.3 : Metadata bracket
            # can be omitted when empty, if previous line is empty #57
            # Version 1.1 on 2018-08-25 - jupytext v0.6.0 : Cells separated
            # with one blank line #38
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            current_version_number='1.3',
            min_readable_version_number='1.1') for ext in _SCRIPT_EXTENSIONS] + \
    [
        NotebookFormatDescription(
            format_name='percent',
            extension=ext,
            header_prefix=_SCRIPT_EXTENSIONS[ext]['comment'],
            cell_reader_class=DoublePercentScriptCellReader,
            cell_exporter_class=DoublePercentCellExporter,
            # Version 1.1 on 2018-09-23 - jupytext v0.7.0rc1 : [markdown] and
            # [raw] for markdown and raw cells.
            # Version 1.0 on 2018-09-22 - jupytext v0.7.0rc0 : Initial version
            current_version_number='1.1') for ext in _SCRIPT_EXTENSIONS] + \
    [
        NotebookFormatDescription(
            format_name='sphinx',
            extension='.py',
            header_prefix='#',
            cell_reader_class=SphinxGalleryScriptCellReader,
            cell_exporter_class=SphinxGalleryCellExporter,
            # Version 1.0 on 2018-09-22 - jupytext v0.7.0rc0 : Initial version
            current_version_number='1.1'),
        NotebookFormatDescription(
            format_name='sphinx-rst2md',
            extension='.py',
            header_prefix='#',
            cell_reader_class=SphinxGalleryScriptRst2mdCellReader,
            cell_exporter_class=None,
            # Version 1.0 on 2018-09-22 - jupytext v0.7.0rc0 : Initial version
            current_version_number='1.0')
    ]

NOTEBOOK_EXTENSIONS = list(dict.fromkeys(
    ['.ipynb'] + [fmt.extension for fmt in JUPYTEXT_FORMATS]))


def get_format(ext, format_name=None):
    """Return the format description for the desired extension"""
    # remove pre-extension if any
    ext = '.' + ext.split('.')[-1]

    if ext.endswith('.ipynb'):
        return None

    formats_for_extension = []
    for fmt in JUPYTEXT_FORMATS:
        if fmt.extension == ext:
            if fmt.format_name == format_name or not format_name:
                return fmt
            formats_for_extension.append(fmt.format_name)

    if formats_for_extension:
        raise TypeError("Format '{}' is not associated to extension '{}'. "
                        "Please choose one of: {}."
                        .format(format_name, ext,
                                ', '.join(formats_for_extension)))
    raise TypeError("Not format associated to extension '{}'".format(ext))


def read_metadata(text, ext):
    """Return the header metadata"""
    ext = '.' + ext.split('.')[-1]
    lines = text.splitlines()

    if ext in ['.md', '.Rmd']:
        comment = ''
    else:
        comment = _SCRIPT_EXTENSIONS.get(ext, {}).get('comment', '#')

    metadata, _, _ = header_to_metadata_and_cell(lines, comment)
    if ext == '.R' and not metadata:
        metadata, _, _ = header_to_metadata_and_cell(lines, "#'")

    return metadata


def read_format_from_metadata(text, ext):
    """Return the format of the file, when that information is available from the metadata"""
    metadata = read_metadata(text, ext)
    transition_to_jupytext_section_in_metadata(metadata, ext.endswith('.ipynb'))
    return format_name_for_ext(metadata, ext, explicit_default=False)


def guess_format(text, ext):
    """Guess the format of the file, given its extension and content"""
    lines = text.splitlines()

    metadata = read_metadata(text, ext)

    if ('jupytext' in metadata and set(metadata['jupytext']).difference(['encoding', 'main_language'])) or \
            set(metadata).difference(['jupytext']):
        return format_name_for_ext(metadata, ext)

    # Is this a Hydrogen-like script?
    # Or a Sphinx-gallery script?
    if ext in _SCRIPT_EXTENSIONS:
        comment = _SCRIPT_EXTENSIONS[ext]['comment']
        twenty_hash = ''.join(['#'] * 20)
        double_percent_re = re.compile(r'^{}( %%|%%)$'.format(comment))
        double_percent_and_space_re = re.compile(r'^{}( %%|%%)\s'.format(comment))
        nbconvert_script_re = re.compile(r'^{}( <codecell>| In\[[0-9 ]*\]:?)'.format(comment))
        twenty_hash_count = 0
        double_percent_count = 0

        parser = StringParser(language='R' if ext == '.R' else 'python')
        for line in lines:
            parser.read_line(line)
            if parser.is_quoted():
                continue

            # Don't count escaped Jupyter magics (no space between
            # %% and command) as cells
            if double_percent_re.match(line) or double_percent_and_space_re.match(line) or nbconvert_script_re.match(line):
                double_percent_count += 1

            if line.startswith(twenty_hash) and ext == '.py':
                twenty_hash_count += 1

        if double_percent_count >= 1:
            return 'percent'

        if twenty_hash_count >= 2:
            return 'sphinx'

    # Default format
    return get_format(ext).format_name


def check_file_version(notebook, source_path, outputs_path):
    """Raise if file version in source file would override outputs"""
    if not insert_or_test_version_number():
        return

    _, ext = os.path.splitext(source_path)
    if ext.endswith('.ipynb'):
        return
    version = notebook.metadata.get('jupytext', {}).get('text_representation', {}).get('format_version')
    format_name = format_name_for_ext(notebook.metadata, ext)

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


def parse_one_format(ext_and_format_name):
    """Parse "py:percent" into (".py", "percent"), etc"""
    if ext_and_format_name.find(':') >= 0:
        ext, format_name = ext_and_format_name.split(':', 1)
    else:
        ext = ext_and_format_name
        format_name = None

    if not ext.startswith('.'):
        ext = '.' + ext

    return ext, format_name


def parse_formats(formats):
    """Parse "md,py:percent" into [(".md", None), (".py", "percent")], etc"""
    if not formats:
        return []
    return [parse_one_format(ext_and_format_name)
            for ext_and_format_name in formats.split(',')]


def update_formats(formats, ext, format_name):
    """Update the format list with the given format name"""
    updated_formats = []
    found_ext = False
    for org_ext, org_format_name in formats:
        if org_ext != ext:
            updated_formats.append((org_ext, org_format_name))
        elif not found_ext:
            updated_formats.append((ext, format_name))
            found_ext = True

    return updated_formats


def one_format_as_string(ext, format_name):
    """('.py', None) to 'py', etc"""
    if ext.startswith('.'):
        ext = ext[1:]
    if format_name:
        return ext + ':' + format_name
    return ext


def formats_as_string(formats):
    """Concatenate all formats into a string"""
    return ','.join([one_format_as_string(ext, format_name)
                     for ext, format_name in formats])


def auto_ext_from_metadata(metadata):
    """Script extension from kernel information"""
    auto_ext = metadata.get('language_info', {}).get('file_extension')
    if auto_ext == '.r':
        return '.R'
    return auto_ext


def format_name_for_ext(metadata, ext, cm_default_formats=None, explicit_default=True):
    """Return the format name for that extension"""

    # Current format: Don't change it unless an explicit instruction is given in the 'formats' field.
    text_repr = metadata.get('jupytext', {}).get('text_representation')
    if text_repr and text_repr.get('extension') == ext and text_repr.get('format_name'):
        current_format = text_repr.get('format_name')
    else:
        current_format = None

    auto_ext = auto_ext_from_metadata(metadata)

    formats = metadata.get('jupytext', {}).get('formats', '') or cm_default_formats
    formats = parse_formats(formats)
    for fmt_ext, ext_format_name in formats:
        if fmt_ext.endswith(ext) or (fmt_ext.endswith('.auto') and auto_ext and ext.endswith(auto_ext)):
            if (not explicit_default) or ext_format_name:
                return ext_format_name or current_format

    if current_format:
        return current_format

    if (not explicit_default) or ext in ['.Rmd', '.md']:
        return None

    return get_format(ext).format_name


def update_jupytext_formats_metadata(notebook, ext, format_name):
    """Update the jupytext_format metadata in the Jupyter notebook"""
    formats = parse_formats(notebook.metadata.get('jupytext', {}).get('formats', ''))
    formats = update_formats(formats, ext, format_name)
    if formats:
        notebook.metadata.setdefault('jupytext', {})['formats'] = formats_as_string(formats)


def transition_to_jupytext_section_in_metadata(metadata, is_ipynb):
    """Convert the jupytext_formats metadata entry to jupytext/formats, etc. See #91"""

    # Backward compatibility with nbrmd
    for key in ['nbrmd_formats', 'nbrmd_format_version']:
        if key in metadata:
            metadata[key.replace('nbrmd', 'jupytext')] = metadata.pop(key)

    if 'jupytext_formats' in metadata:
        metadata.setdefault('jupytext', {})['formats'] = metadata.pop('jupytext_formats')
    if 'jupytext_format_version' in metadata:
        metadata.setdefault('jupytext', {})['text_representation'] = {
            'format_version': metadata.pop('jupytext_format_version')}
    if 'main_language' in metadata:
        metadata.setdefault('jupytext', {})['main_language'] = metadata.pop('main_language')
    for entry in ['encoding', 'executable']:
        if is_ipynb and entry in metadata:
            metadata.setdefault('jupytext', {})[entry] = metadata.pop(entry)
