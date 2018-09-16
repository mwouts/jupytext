"""Export notebook cells as text"""

import re
from copy import copy
from .languages import cell_language
from .cell_reader import CellReader
from .cell_metadata import filter_metadata, is_active, \
    metadata_to_rmd_options, metadata_to_json_options
from .magics import escape_magic, escape_code_start


def cell_source(cell):
    """Return the source of the current cell, as an array of lines"""
    source = cell.source
    if source == '':
        return ['']
    if source.endswith('\n'):
        return source.splitlines() + ['']
    return source.splitlines()


class BaseCellExporter:
    """A class that represent a notebook cell as text"""

    def __init__(self, cell, default_language, ext):
        self.ext = ext
        self.cell_type = cell.cell_type
        self.source = cell_source(cell)
        self.metadata = filter_metadata(cell.metadata)
        self.language = cell_language(self.source) or default_language
        self.default_language = default_language

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
        if not self.prefix:
            escape_code_start(source, self.ext, None)
        return self.markdown_to_text(source)

    def markdown_to_text(self, source):
        """Escape the given source, for a markdown cell"""
        if not self.prefix:
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


class MarkdownCellExporter(BaseCellExporter):
    """A class that represent a notebook cell as Markdown"""
    prefix = ''

    def code_to_text(self):
        """Return the text representation of a code cell"""
        source = copy(self.source)
        escape_code_start(source, self.ext, self.language)

        options = []
        if self.cell_type == 'code' and self.language:
            options.append(self.language)
        if 'name' in self.metadata:
            options.append(self.metadata['name'])

        return ['```{}'.format(' '.join(options))] + source + ['```']


class RMarkdownCellExporter(BaseCellExporter):
    """A class that represent a notebook cell as Markdown"""
    prefix = ''

    def code_to_text(self):
        """Return the text representation of a code cell"""
        active = is_active(self.ext, self.metadata)
        source = copy(self.source)
        escape_code_start(source, self.ext, self.language)

        if active:
            escape_magic(source, self.language)

        lines = []
        if not is_active('Rmd', self.metadata):
            self.metadata['eval'] = False
        options = metadata_to_rmd_options(self.language, self.metadata)
        lines.append('```{{{}}}'.format(options))
        lines.extend(source)
        lines.append('```')
        return lines


class LightScriptCellExporter(BaseCellExporter):
    """A class that represent a notebook cell as a Python or Julia script"""
    prefix = '#'

    def endofcell_marker(self, source):
        """Issues #31 #38:  does the cell contain a blank line? In that case
        we add an end-of-cell marker"""
        endofcell = '-'
        while True:
            endofcell_re = re.compile(r'^#( )' + endofcell + r'\s*$')
            if list(filter(endofcell_re.match, source)):
                endofcell = endofcell + '-'
            else:
                return endofcell

    def code_to_text(self):
        """Return the text representation of a code cell"""
        active = is_active(self.ext, self.metadata)
        if active and self.language != (
                'python' if self.ext == '.py' else 'julia'):
            active = False
            self.metadata['active'] = 'ipynb'
            self.metadata['language'] = self.language

        source = copy(self.source)
        escape_code_start(source, self.ext, self.language)

        if active:
            escape_magic(source, self.language)
        else:
            source = ['# ' + line if line else '#' for line in source]

        if self.explicit_start_marker(source):
            self.metadata['endofcell'] = self.endofcell_marker(source)

        if not self.metadata:
            return source

        lines = []
        endofcell = self.metadata['endofcell']
        if endofcell == '-':
            del self.metadata['endofcell']
        options = metadata_to_json_options(self.metadata)
        lines.append('# + {}'.format(options))
        lines.extend(source)
        lines.append('# {}'.format(endofcell))
        return lines


class RScriptCellExporter(BaseCellExporter):
    """A class that represent a notebook cell as a R script"""
    prefix = "#'"

    def code_to_text(self):
        """Return the text representation of a code cell"""
        active = is_active(self.ext, self.metadata)
        if active and self.language != 'R':
            active = False
            self.metadata['active'] = 'ipynb'
            self.metadata['language'] = self.language

        source = copy(self.source)
        escape_code_start(source, self.ext, self.language)

        if active:
            escape_magic(source, self.language)

        if not active:
            source = ['# ' + line if line else '#' for line in source]

        lines = []
        if not is_active('R', self.metadata):
            self.metadata['eval'] = False
        options = metadata_to_rmd_options(None, self.metadata)
        if options:
            lines.append('#+ {}'.format(options))
        lines.extend(source)
        return lines


def CellExporter(cell, default_language, ext):
    if ext == '.md':
        return MarkdownCellExporter(cell, default_language, ext)
    if ext == '.Rmd':
        return RMarkdownCellExporter(cell, default_language, ext)
    if ext == '.R':
        return RScriptCellExporter(cell, default_language, ext)

    return LightScriptCellExporter(cell, default_language, ext)
