"""Parse header of text notebooks
"""

import re
import yaml
import nbformat
from nbformat.v4.nbbase import new_raw_cell
from .file_format_version import file_format_version

_HEADER_RE = re.compile(r"^---\s*$")
_BLANK_RE = re.compile(r"^\s*$")
_JUPYTER_RE = re.compile(r"^jupyter\s*:\s*$")
_LEFTSPACE_RE = re.compile(r"^\s")
_ENCODING_RE = re.compile('^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)')
_UTF8_HEADER = '# -*- coding: utf-8 -*-'


def _as_dict(metadata):
    if isinstance(metadata, nbformat.NotebookNode):
        return {k: _as_dict(metadata[k]) for k in metadata.keys()}
    return metadata


def encoding_and_executable(self, notebook):
    """
    Return encoding and executable lines for a notebook, if applicable
    :param self:
    :param notebook:
    :return:
    """
    lines = []
    metadata = notebook.get('metadata', {})

    if self.ext not in ['.Rmd', '.md'] and 'executable' in metadata:
        lines.append('#!' + metadata['executable'])
        del metadata['executable']

    if 'encoding' in metadata:
        lines.append(metadata['encoding'])
        del metadata['encoding']
    elif self.ext not in ['.Rmd', '.md']:
        for cell in notebook.cells:
            try:
                cell.source.encode('ascii')
            except (UnicodeEncodeError, UnicodeDecodeError):
                lines.append(_UTF8_HEADER)
                break

    return lines


def metadata_and_cell_to_header(self, notebook):
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

    metadata = _as_dict(notebook.get('metadata', {}))

    if file_format_version(self.ext):
        metadata['jupytext_format_version'] = file_format_version(self.ext)

    if metadata:
        header.extend(yaml.safe_dump({'jupyter': metadata},
                                     default_flow_style=False).splitlines())

    if header:
        header = ['---'] + header + ['---']

    header = self.markdown_escape(header)

    if header and skipline:
        header += ['']

    return header


def header_to_metadata_and_cell(self, lines):
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

    for i, line in enumerate(lines):
        if i == 0 and line.startswith('#!'):
            metadata['executable'] = line[2:]
            start = i + 1
            continue
        if i == 0 or (i == 1 and not _ENCODING_RE.match(lines[0])):
            encoding = _ENCODING_RE.match(line)
            if encoding:
                if encoding.group(1) != 'utf-8':
                    raise ValueError('Encodings other than utf-8 '
                                     'are not supported')
                if line != _UTF8_HEADER:
                    metadata['encoding'] = line
                start = i + 1
                continue

        if not line.startswith(self.prefix):
            break

        line = self.markdown_unescape(line)

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
            line = self.markdown_unescape(lines[i + 1])
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
