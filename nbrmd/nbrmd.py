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
import re
from enum import Enum
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import (
    new_code_cell, new_markdown_cell, new_raw_cell, new_notebook
)
import nbformat
import yaml

from .chunk_options import to_metadata, to_chunk_options


# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------

def _language(metadata):
    try:
        return metadata.language_info.name.lower()
    except AttributeError:
        return u'python'


class State(Enum):
    NONE = 0
    HEADER = 1
    MARKDOWN = 2
    CODE = 3


_header_re = re.compile(r"^---\s*")
_end_code_re = re.compile(r"^```\s*")

_jupyter_languages = ['R', 'bash', 'sh', 'python', 'python2', 'python3',
                      'javascript', 'js', 'perl']
_jupyter_languages_re = [re.compile(r"^%%{}\s*".format(lang))
                         for lang in _jupyter_languages]


class RmdReaderError(Exception):
    pass


class RmdReader(NotebookReader):

    def __init__(self, markdown=False):
        self.start_code_re = re.compile(r"^```(.*)\s*") if markdown \
            else re.compile(r"^```\{(.*)\}\s*")

    def reads(self, s, **kwargs):
        return self.to_notebook(s, **kwargs)

    def to_notebook(self, s, **kwargs):
        lines = s.splitlines()

        metadata = {}
        cells = []
        cell_lines = []

        def add_markdown_cell():
            if len(cell_lines) == 0:
                return

            if cell_lines[-1] == '':
                if len(cell_lines) > 1 or len(cells) == 0:
                    cells.append(new_markdown_cell(
                        source=u'\n'.join(cell_lines[:-1])))
                else:
                    cells[-1]['metadata']['noskipline'] = True
                    cells.append(new_markdown_cell(
                        source=u'\n'.join(cell_lines)))
            else:
                cells.append(new_markdown_cell(source=u'\n'.join(cell_lines),
                                               metadata={u'noskipline': True}))

        cell_metadata = {}
        state = State.NONE
        testblankline = False

        for line in lines:
            if state is State.NONE:
                if _header_re.match(line):
                    state = State.HEADER
                    continue
                state = State.MARKDOWN

            if state is State.HEADER:
                if _header_re.match(line):
                    header = []
                    jupyter = []
                    in_header = True
                    for l in cell_lines:
                        if l.rstrip() == 'jupyter:':
                            in_header = False
                        if in_header:
                            header.append(l)
                        else:
                            jupyter.append(l)
                    if len(header):
                        cells.append(new_raw_cell(
                            source=u'\n'.join(['---'] + header + ['---'])))
                    if len(jupyter):
                        metadata = yaml.load(u'\n'.join(jupyter))['jupyter']
                    cell_lines = []
                    state = State.MARKDOWN
                    testblankline = True
                    continue

            if testblankline:
                # Set 'noskipline' metadata if
                # no blank line is found after cell
                testblankline = False
                if line == u'':
                    continue
                else:
                    if len(cells):
                        cells[-1][u'metadata'][u'noskipline'] = True

            if state is State.MARKDOWN:
                if self.start_code_re.match(line):
                    add_markdown_cell()
                    cell_lines = []

                    chunk_options = self.start_code_re.findall(line)[0]
                    language, cell_metadata = to_metadata(chunk_options)
                    cell_metadata['language'] = language
                    state = State.CODE
                    continue

            if state is State.CODE:
                if _end_code_re.match(line):
                    cells.append(new_code_cell(source=u'\n'.join(cell_lines),
                                               metadata=cell_metadata))
                    cell_lines = []
                    cell_metadata = {}
                    state = State.MARKDOWN
                    testblankline = True
                    continue

            cell_lines.append(line)

        # Append last cell if not empty
        if state is State.MARKDOWN:
            add_markdown_cell()
        elif state is State.CODE:
            raise RmdReaderError(u'Unterminated code cell')
        elif state is State.HEADER:
            raise RmdReaderError(u'Unterminated YAML header')

        # Determine main language
        main_language = metadata.get('language_info', {}).get('name')
        if main_language is None:
            languages = dict(python=0)
            for c in cells:
                if c['cell_type'] == 'code':
                    language = c['metadata']['language']
                    if language == 'r':
                        language = 'R'
                    languages[language] = languages.get(language, 0) + 1

            main_language = max(languages, key=languages.get)
            metadata['language_info'] = metadata.get('language_info', {})
            metadata['language_info']['name'] = main_language

        # Remove 'language' meta data and add a magic if not main language
        for c in cells:
            if c['cell_type'] == 'code':
                language = c['metadata']['language']
                del c['metadata']['language']
                if language != main_language and \
                        language in _jupyter_languages:
                    c['source'] = u'%%{}\n'.format(language) + c['source']

        nb = new_notebook(cells=cells, metadata=metadata)
        return nb


def _as_dict(metadata):
    if isinstance(metadata, nbformat.NotebookNode):
        return {k: _as_dict(metadata[k]) for k in metadata.keys()}
    return metadata


class RmdWriter(NotebookWriter):

    def __init__(self, markdown=False):
        self.markdown = markdown

    def writes(self, nb):
        default_language = _language(nb.metadata)
        metadata = _as_dict(nb.metadata)

        lines = []
        header_inserted = len(metadata) == 0

        for cell in nb.cells:
            if cell.cell_type == u'raw':
                # Is this the Rmd header?
                # Starts and ends with '---',
                # and can be parsed with yaml
                if len(lines) == 0 and not header_inserted:
                    header = cell.get(u'source', '').splitlines()
                    if len(header) >= 2 and _header_re.match(header[0]) \
                            and _header_re.match(header[-1]):
                        try:
                            header = header[1:-1]
                            yaml.load(u'\n'.join(header))
                            if not self.markdown:
                                header.extend(
                                    yaml.safe_dump(
                                        {u'jupyter': metadata},
                                        default_flow_style=False).splitlines())
                            lines = [u'---'] + header + [u'---']
                            header_inserted = True
                        except yaml.ScannerError:
                            pass
                    if not header_inserted:
                        lines.append(cell.get(u'source', ''))
                else:
                    lines.append(cell.get(u'source', ''))
                if not cell.get(u'metadata', {}).get('noskipline', False):
                    lines.append(u'')
            elif cell.cell_type == u'markdown':
                lines.append(cell.get(u'source', ''))
                if not cell.get(u'metadata', {}).get('noskipline', False):
                    lines.append(u'')
            elif cell.cell_type == u'code':
                input = cell.get(u'source').splitlines()
                cell_metadata = cell.get(u'metadata', {})
                if 'noskipline' in cell_metadata:
                    noskipline = cell_metadata['noskipline']
                    del cell_metadata['noskipline']
                else:
                    noskipline = False
                language = None
                if len(input):
                    for lang, pattern in zip(_jupyter_languages,
                                             _jupyter_languages_re):
                        if pattern.match(input[0]):
                            language = lang
                            input = input[1:]
                            break
                if language is None:
                    language = default_language
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
                    lines.append(u'')

        if not self.markdown and not header_inserted and len(metadata):
            header = yaml.safe_dump({u'jupyter': metadata},
                                    default_flow_style=False).splitlines()
            lines = [u'---'] + header + [u'---', u''] + lines

        lines.append(u'')

        return u'\n'.join(lines)


_reader = RmdReader()
_writer = RmdWriter()

reads = _reader.reads
read = _reader.read
to_notebook = _reader.to_notebook
write = _writer.write
writes = _writer.writes

_md_reader = RmdReader(markdown=True)
_md_writer = RmdWriter(markdown=True)

md_reads = _md_reader.reads
md_read = _md_reader.read
md_to_notebook = _md_reader.to_notebook
md_write = _md_writer.write
md_writes = _md_writer.writes


def readf(nb_file):
    """
    Load the notebook from the desired file
    :param nb_file: file with .ipynb or .Rmd extension
    :return: the notebook
    """
    file, ext = os.path.splitext(nb_file)
    with open(nb_file) as fp:
        if ext == '.Rmd':
            return read(fp)
        elif ext == '.md':
            return md_read(fp)
        elif ext == '.ipynb':
            return nbformat.read(fp, as_version=4)
        else:
            raise TypeError(
                'File {} has incorrect extension (.Rmd or .md or '
                '.ipynb expected)'.format(nb_file))


def writef(nb, nb_file):
    """
    Save the notebook in the desired file
    :param nb: notebook
    :param nb_file: file with .ipynb or .Rmd extension
    :return:
    """

    file, ext = os.path.splitext(nb_file)
    with open(nb_file, 'w') as fp:
        if ext == '.Rmd':
            write(nb, fp)
        elif ext == '.md':
            md_write(nb, fp)
        elif ext == '.ipynb':
            nbformat.write(nb, fp)
        else:
            raise TypeError(
                'File {} has incorrect extension (.Rmd or .md or '
                '.ipynb expected)'.format(nb_file))


def readme():
    """
    Contents of README.md
    :return:
    """
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'README.md')
    with open(readme_path) as fh:
        return fh.read()
