"""Parse header of text notebooks
"""

import re
import yaml
from yaml.representer import SafeRepresenter
import nbformat
from nbformat.v4.nbbase import new_raw_cell
from .version import __version__
from .cell_to_text import comment_lines
from .languages import _SCRIPT_EXTENSIONS
from .metadata_filter import filter_metadata

SafeRepresenter.add_representer(nbformat.NotebookNode, SafeRepresenter.represent_dict)

_HEADER_RE = re.compile(r"^---\s*$")
_BLANK_RE = re.compile(r"^\s*$")
_JUPYTER_RE = re.compile(r"^jupyter\s*:\s*$")
_LEFTSPACE_RE = re.compile(r"^\s")
_UTF8_HEADER = ' -*- coding: utf-8 -*-'

_DEFAULT_METADATA = [
    # Preserve Jupytext section
    'jupytext',
    # Preserve kernel specs and language_info
    'kernelspec', 'language_info',
    # Kernel_info found in Nteract notebooks
    'kernel_info']

# Change this to False in tests
INSERT_AND_CHECK_VERSION_NUMBER = True


def insert_or_test_version_number():
    """Should the format name and version number be inserted in text
    representations (not in tests!)"""
    return INSERT_AND_CHECK_VERSION_NUMBER


def uncomment_line(line, prefix):
    """Remove prefix (and space) from line"""
    if not prefix:
        return line
    if line.startswith(prefix + ' '):
        return line[len(prefix) + 1:]
    if line.startswith(prefix):
        return line[len(prefix):]
    return line


def encoding_and_executable(notebook, ext):
    """
    Return encoding and executable lines for a notebook, if applicable
    :param self:
    :param notebook:
    :return:
    """
    lines = []
    metadata = notebook.get('metadata', {}).get('jupytext', {})
    comment = _SCRIPT_EXTENSIONS.get(ext, {}).get('comment')

    if ext not in ['.Rmd', '.md'] and 'executable' in metadata:
        lines.append(comment + '!' + metadata['executable'])
        del metadata['executable']

    if 'encoding' in metadata:
        lines.append(metadata['encoding'])
        del metadata['encoding']
    elif ext not in ['.Rmd', '.md']:
        for cell in notebook.cells:
            try:
                cell.source.encode('ascii')
            except (UnicodeEncodeError, UnicodeDecodeError):
                lines.append(comment + _UTF8_HEADER)
                break

    return lines


def metadata_and_cell_to_header(notebook, text_format, ext):
    """
    Return the text header corresponding to a notebook, and remove the
    first cell of the notebook if it contained the header
    """

    header = []
    skipline = True

    if notebook.cells:
        cell = notebook.cells[0]
        if cell.cell_type == 'raw':
            lines = cell.source.strip('\n\t ').splitlines()
            if len(lines) >= 2 \
                    and _HEADER_RE.match(lines[0]) \
                    and _HEADER_RE.match(lines[-1]):
                header = lines[1:-1]
                skipline = not cell.metadata.get('noskipline', False)
                notebook.cells = notebook.cells[1:]

    metadata = notebook.get('metadata', {})

    if insert_or_test_version_number():
        metadata.setdefault('jupytext', {})['text_representation'] = {
            'extension': ext,
            'format_name': text_format.format_name,
            'format_version': text_format.current_version_number,
            'jupytext_version': __version__}

    if 'jupytext' in metadata and not metadata['jupytext']:
        del metadata['jupytext']

    notebook_metadata_filter = metadata.get('jupytext', {}).get('metadata', {}).get('notebook')
    metadata = filter_metadata(metadata, notebook_metadata_filter, _DEFAULT_METADATA)

    if metadata:
        header.extend(yaml.safe_dump({'jupyter': metadata}, default_flow_style=False).splitlines())

    if header:
        header = ['---'] + header + ['---']

    header = comment_lines(header, text_format.header_prefix)

    if header and skipline:
        header += ['']

    return header


def header_to_metadata_and_cell(lines, header_prefix):
    """
    Return the metadata, first cell of notebook, and next loc in text
    """

    header = []
    jupyter = []
    injupyter = False
    ended = False
    metadata = {}
    start = 0
    i = -1

    comment = '#' if header_prefix == "#'" else header_prefix

    encoding_re = re.compile(r'^[ \t\f]*{}.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)'.format(comment))

    for i, line in enumerate(lines):
        if i == 0 and line.startswith(comment + '!'):
            metadata.setdefault('jupytext', {})['executable'] = line[2:]
            start = i + 1
            continue
        if i == 0 or (i == 1 and not encoding_re.match(lines[0])):
            encoding = encoding_re.match(line)
            if encoding:
                if encoding.group(1) != 'utf-8':
                    raise ValueError('Encodings other than utf-8 are not supported')
                metadata.setdefault('jupytext', {})['encoding'] = line
                start = i + 1
                continue

        if not line.startswith(header_prefix):
            break

        line = uncomment_line(line, header_prefix)

        if i == start:
            if _HEADER_RE.match(line):
                continue
            else:
                break

        if i > start and _HEADER_RE.match(line):
            ended = True
            break

        if _JUPYTER_RE.match(line):
            injupyter = True
        elif not _LEFTSPACE_RE.match(line):
            injupyter = False

        if injupyter:
            jupyter.append(line)
        else:
            header.append(line)

    if ended:
        if jupyter:
            metadata.update(yaml.load('\n'.join(jupyter))['jupyter'])

        skipline = True
        if len(lines) > i + 1:
            line = uncomment_line(lines[i + 1], header_prefix)
            if not _BLANK_RE.match(line):
                skipline = False
            else:
                i = i + 1
        else:
            skipline = False

        if header:
            cell = new_raw_cell(source='\n'.join(['---'] + header + ['---']),
                                metadata={} if skipline else
                                {'lines_to_next_cell': 0})
        else:
            cell = None

        return metadata, cell, i + 1

    return metadata, None, start
