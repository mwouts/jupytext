"""Export notebook cells as text"""

import re
from copy import copy
from .languages import cell_language
from .cell_reader import CellReader
from .cell_metadata import filter_metadata, is_active, \
    metadata_to_rmd_options, metadata_to_json_options
from .magics import escape_magic, escape_code_start


def cell_source(cell):
    """
    Return the source of the current cell, as an array of lines
    :param cell:
    :return:
    """
    source = cell.source
    if source == '':
        return ['']
    if source.endswith('\n'):
        return source.splitlines() + ['']
    return source.splitlines()


def code_to_rmd(source, metadata, language):
    """
    Represent a code cell with given source and metadata as a rmd cell
    :param source:
    :param metadata:
    :param language:
    :return:
    """
    lines = []
    if not is_active('Rmd', metadata):
        metadata['eval'] = False
    options = metadata_to_rmd_options(language, metadata)
    lines.append('```{{{}}}'.format(options))
    lines.extend(source)
    lines.append('```')
    return lines


def code_to_md(source, metadata, language):
    """
    Represent a code cell with given source and metadata as a md cell
    :param source:
    :param metadata:
    :param language:
    :return:
    """
    options = []
    if language:
        options.append(language)
    if 'name' in metadata:
        options.append(metadata['name'])

    return ['```{}'.format(' '.join(options))] + source + ['```']


def code_to_r(source, metadata):
    """
    Represent a code cell with given source and metadata as a R cell
    :param source:
    :param metadata:
    :return:
    """
    lines = []
    if not is_active('R', metadata):
        metadata['eval'] = False
    options = metadata_to_rmd_options(None, metadata)
    if options:
        lines.append('#+ {}'.format(options))
    lines.extend(source)
    return lines


def code_to_py(source, metadata):
    """
    Represent a code cell with given source and metadata as a python cell
    """
    lines = []
    if not metadata:
        return source

    endofcell = metadata['endofcell']
    if endofcell == '-':
        del metadata['endofcell']
    options = metadata_to_json_options(metadata)
    lines.append('# + {}'.format(options))
    lines.extend(source)
    lines.append('# {}'.format(endofcell))
    return lines


def py_endofcell_marker(source):
    """Issues #31 #38:  does the cell contain a blank line? In that case
    we add an end-of-cell marker"""
    endofcell = '-'
    while True:
        endofcell_re = re.compile(r'^#( )' + endofcell + r'\s*$')
        if list(filter(endofcell_re.match, source)):
            endofcell = endofcell + '-'
        else:
            return endofcell


class CellExporter():
    """A class that represent a notebook cell as text"""

    def __init__(self, cell, default_language, ext):
        self.ext = ext
        self.prefix = '' if ext in ['.Rmd', '.md'] \
            else "#'" if ext == '.R' else '#'
        self.cell_type = cell.cell_type
        self.source = cell_source(cell)
        self.metadata = filter_metadata(cell.metadata)
        self.language = cell_language(self.source) or default_language

        # how many blank lines before next cell
        self.lines_to_next_cell = cell.metadata.get('lines_to_next_cell', 1)
        self.lines_to_end_of_cell_marker = \
            cell.metadata.get('lines_to_end_of_cell_marker', 0)

        # for compatibility with v0.5.4 and lower (to be removed)
        if 'skipline' in cell.metadata:
            self.lines_to_next_cell += 1
        if 'noskipline' in cell.metadata:
            self.lines_to_next_cell -= 1

        if cell.cell_type == 'raw' and 'active' not in self.metadata:
            self.metadata['active'] = ''

    def is_code(self):
        """Is this cell a code cell?"""
        if self.cell_type == 'code':
            return True
        if self.cell_type == 'raw' and 'active' in self.metadata:
            return True
        return False

    def cell_to_text(self):
        """Return the text representation for the cell"""
        if self.is_code():
            return self.code_to_text()

        source = copy(self.source)
        if self.ext in ['.Rmd', '.md']:
            escape_code_start(source, self.ext, None)
        return self.markdown_escape(source)

    def markdown_escape(self, source):
        """Escape the given source, for a markdown cell"""
        if self.ext in ['.Rmd', '.md']:
            return source
        return [self.prefix + ' ' + line if line else self.prefix
                for line in source]

    def explicit_start_marker(self, source):
        """Does the python representation of this cell requires an explicit
        start of cell marker?"""
        if self.metadata:
            return True
        if all([line.startswith('#') for line in self.source]):
            return True
        if CellReader(self.ext).read(source)[1] < len(source):
            return True

        return False

    def code_to_text(self):
        """Return the text representation of a code cell"""
        active = is_active(self.ext, self.metadata)
        if self.ext in ['.R', '.py', '.jl']:
            if active and self.language != (
                    'R' if self.ext == '.R' else
                    'python' if self.ext == '.py' else 'julia'):
                active = False
                self.metadata['active'] = 'ipynb'
                self.metadata['language'] = self.language

        source = copy(self.source)
        escape_code_start(source, self.ext, self.language)

        if active and self.ext != '.md':
            escape_magic(source, self.language)

        if self.ext == '.Rmd':
            return code_to_rmd(source, self.metadata, self.language)

        if self.ext == '.md':
            return code_to_md(
                source, self.metadata,
                self.language if self.cell_type == 'code' else None)

        if not active:
            source = ['# ' + line if line else '#' for line in source]

        if self.ext == '.R':
            return code_to_r(source, self.metadata)

        # py, jl
        if self.explicit_start_marker(source):
            self.metadata['endofcell'] = py_endofcell_marker(source)

        return code_to_py(source, self.metadata)
