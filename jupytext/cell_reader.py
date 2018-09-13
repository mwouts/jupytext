"""Read notebook cells from their text representation"""

import re
from nbformat.v4.nbbase import new_code_cell, new_raw_cell, new_markdown_cell
from .cell_metadata import is_active, json_options_to_metadata, \
    md_options_to_metadata, rmd_options_to_metadata
from .stringparser import StringParser
from .magics import unescape_magic, is_magic, unescape_code_start

_START_CODE_RMD = re.compile(r"^```{(.*)}\s*$")
_START_CODE_MD = re.compile(r"^```(.*)")
_END_CODE_MD = re.compile(r"^```\s*$")
_CODE_OPTION_R = re.compile(r"^#\+(.*)\s*$")
_CODE_OPTION_PY = re.compile(r"^(#|# )\+(\s*){(.*)}\s*$")
_SIMPLE_START_CODE_PY = re.compile(r"^(#|# )\+(\s*)$")
_BLANK_LINE = re.compile(r"^\s*$")
_PY_COMMENT = re.compile(r"^\s*#")
_PY_INDENTED = re.compile(r"^\s")


def uncomment(lines):
    """Remove quote and space when possible"""
    return [line[2:] if line.startswith('# ')
            else (line[1:] if line.startswith('#') else line)
            for line in lines]


def paragraph_is_fully_commented(lines, main_language):
    """Is the paragraph fully commented?"""
    for i, line in enumerate(lines):
        if line.startswith('#'):
            if (line.startswith(('# %', '# ?'))
                    and is_magic(line, main_language):
                return False
            continue
        return i > 0 and _BLANK_LINE.match(line)
    return True


def next_code_is_indented(lines):
    """Is the next unescaped line indented?"""
    for line in lines:
        if _BLANK_LINE.match(line) or _PY_COMMENT.match(line):
            continue
        return _PY_INDENTED.match(line)
    return False


def count_lines_to_next_cell(cell_end_marker, next_cell_start,
                             total, explicit_eoc):
    """How many blank lines between end of cell marker and next cell?"""
    if cell_end_marker < total:
        lines_to_next_cell = next_cell_start - cell_end_marker
        if explicit_eoc:
            lines_to_next_cell -= 1
        if next_cell_start >= total:
            lines_to_next_cell += 1
        return lines_to_next_cell

    return 1


def last_two_lines_blank(source):
    """Are the two last lines blank, and not the third last one?"""
    if len(source) < 3:
        return False
    return (not _BLANK_LINE.match(source[-3]) and
            _BLANK_LINE.match(source[-2]) and
            _BLANK_LINE.match(source[-1]))


class CellReader():
    """A class that can read notebook cells from their text representation"""

    def __init__(self, ext):
        """Create a cell reader with empty content"""
        self.ext = ext
        self.markdown_prefix = ('' if ext in ['.Rmd', '.md'] else
                                "#'" if ext == '.R' else '#')
        self.cell_type = None
        self.language = None
        self.metadata = None
        self.content = []
        self.lines_to_next_cell = 1

    def read(self, lines):
        """Read one cell from the given lines, and return the cell,
        plus the position of the next cell
        """

        # Do we have an explicit code marker on the first line?
        self.metadata_and_language_from_option_line(lines[0])

        # Parse cell till its end and set content, lines_to_next_cell
        pos_next_cell = self.find_cell_content(lines)

        if self.cell_type == 'code':
            new_cell = new_code_cell
        elif self.cell_type == 'markdown':
            new_cell = new_markdown_cell
        else:
            new_cell = new_raw_cell

        if self.lines_to_next_cell != 1:
            self.metadata['lines_to_next_cell'] = self.lines_to_next_cell

        if self.language:
            self.metadata['language'] = self.language

        return new_cell(source='\n'.join(self.content),
                        metadata=self.metadata), pos_next_cell

    def metadata_and_language_from_option_line(self, line):
        """Parse code options on the given line. When a start of a code cell
        is found, self.metadata is set to a dictionary."""
        if self.ext == '.Rmd' and _START_CODE_RMD.match(line):
            self.language, self.metadata = \
                rmd_options_to_metadata(_START_CODE_RMD.findall(line)[0])

        if self.ext == '.md' and _START_CODE_MD.match(line):
            self.language, self.metadata = \
                md_options_to_metadata(_START_CODE_MD.findall(line)[0])

        if self.ext == '.R' and _CODE_OPTION_R.match(line):
            self.language, self.metadata = \
                rmd_options_to_metadata('r ' + _CODE_OPTION_R.findall(line)[0])

        if self.ext in ['.py', '.jl']:
            if _CODE_OPTION_PY.match(line):
                self.language = 'python' if self.ext == '.py' else 'julia'
                self.metadata = json_options_to_metadata(
                    _CODE_OPTION_PY.match(line).group(3))
            if _SIMPLE_START_CODE_PY.match(line):
                self.language = 'python' if self.ext == '.py' else 'julia'
                self.metadata = {}

        if self.metadata and 'language' in self.metadata:
            self.language = self.metadata['language']
            del self.metadata['language']

    def find_cell_end_rmd(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""
        # markdown: (last) two consecutive blank lines
        if self.metadata is None:
            self.cell_type = 'markdown'
            prev_blank = 0
            for i, line in enumerate(lines):
                if (self.ext == '.Rmd' and _START_CODE_RMD.match(line)) or \
                        (self.ext == '.md' and _START_CODE_MD.match(line)):
                    if i > 1 and prev_blank:
                        return i - 1, i, False
                    return i, i, False
                if _BLANK_LINE.match(lines[i]):
                    prev_blank += 1
                elif i > 2 and prev_blank >= 2:
                    return i - 2, i, True
                else:
                    prev_blank = 0
        else:
            self.cell_type = 'code'
            for i, line in enumerate(lines):
                # skip cell header
                if i == 0:
                    continue
                if _END_CODE_MD.match(line):
                    return i, i + 1, True

        # End not found
        return len(lines), len(lines), False

    def find_cell_end_r(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""
        if self.metadata is None and lines[0].startswith("#'"):
            self.cell_type = 'markdown'
            for i, line in enumerate(lines):
                if not line.startswith("#'"):
                    if _BLANK_LINE.match(line):
                        return i, i + 1, False
                    return i, i, False

            return len(lines), len(lines), False

        return self.find_cell_end_code(lines, None, _CODE_OPTION_R, "#'")

    def find_cell_end_py(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""
        if self.metadata is None and \
                paragraph_is_fully_commented(lines, 'python'):
            self.cell_type = 'markdown'
            for i, line in enumerate(lines):
                if _BLANK_LINE.match(line):
                    return i, i + 1, False
            return len(lines), len(lines), False

        if self.metadata is not None:
            end_of_cell = self.metadata.get('endofcell', '-')
            cell_end_re = re.compile('^# ' + end_of_cell + r'\s*$')
        else:
            cell_end_re = None

        return self.find_cell_end_code(lines, cell_end_re,
                                       _CODE_OPTION_PY, None)

    def find_cell_end_code(self, lines, cell_end_re,
                           cell_start_re, markdown_prefix):
        """Given that this is a code cell, return position of
        end of cell marker, and position of next cell start"""
        self.cell_type = 'code'
        parser = StringParser('python' if self.ext in ['.py', '.jl'] else 'R')
        for i, line in enumerate(lines):
            # skip cell header
            if self.metadata is not None and i == 0:
                continue

            if parser.is_quoted():
                parser.read_line(line)
                continue

            parser.read_line(line)

            if cell_start_re.match(line) or (
                    markdown_prefix and line.startswith(markdown_prefix)):
                if i > 1 and _BLANK_LINE.match(lines[i - 1]):
                    return i - 1, i, False
                return i, i, False

            if i > 0 and cell_start_re == _CODE_OPTION_PY and \
                    _BLANK_LINE.match(lines[i - 1]) and \
                    _SIMPLE_START_CODE_PY.match(line):
                return i - 1, i, False

            if cell_end_re:
                if cell_end_re.match(line):
                    return i, i + 1, True
            elif _BLANK_LINE.match(line):
                if not next_code_is_indented(lines[i:]):
                    if i > 0:
                        return i, i + 1, False
                    if len(lines) == 1 or _BLANK_LINE.match(lines[1]):
                        return 1, 2, False

        return len(lines), len(lines), False

    def find_cell_end(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""
        if self.ext in ['.py', '.jl']:
            return self.find_cell_end_py(lines)
        if self.ext in ['.Rmd', '.md']:
            return self.find_cell_end_rmd(lines)
        return self.find_cell_end_r(lines)

    def find_cell_content(self, lines):
        """Parse cell till its end and set content, lines_to_next_cell.
        Return the position of next cell start"""
        cell_end_marker, next_cell_start, explicit_eoc = \
            self.find_cell_end(lines)

        # Metadata to dict
        if self.metadata is None:
            cell_start = 0
            self.metadata = {}
        else:
            cell_start = 1

        # Cell content
        source = lines[cell_start:cell_end_marker]

        if self.cell_type == 'code':
            if self.ext != '.md' and is_active(self.ext, self.metadata):
                unescape_magic(source, self.language or 'python')
            elif self.ext in ['.py', '.jl', '.R']:
                source = uncomment(source)

        if self.cell_type == 'code' or self.ext in ['.Rmd', '.md']:
            unescape_code_start(source, self.ext, self.language or
                                ('python' if self.ext != '.Rmd' else None))

        if self.cell_type == 'markdown' and self.ext in ['.py', '.jl', '.R']:
            source = self.markdown_unescape(source)

        self.content = source

        # Exactly two empty lines at the end?
        if (self.ext == '.py' and explicit_eoc and
                last_two_lines_blank(source)):
            self.content = source[:-2]
            self.metadata['lines_to_end_of_cell_marker'] = 2

        # Is this a raw cell?
        if not is_active('ipynb', self.metadata) or (
                self.ext == '.md' and self.cell_type == 'code'
                and self.language is None):
            if self.metadata.get('active') == '':
                del self.metadata['active']
            self.cell_type = 'raw'

        # Explicit end of cell marker?
        if (next_cell_start + 1 < len(lines) and
                _BLANK_LINE.match(lines[next_cell_start]) and
                not _BLANK_LINE.match(lines[next_cell_start + 1])):
            next_cell_start += 1
        elif (explicit_eoc and next_cell_start + 2 < len(lines) and
              _BLANK_LINE.match(lines[next_cell_start]) and
              _BLANK_LINE.match(lines[next_cell_start + 1]) and
              not _BLANK_LINE.match(lines[next_cell_start + 2])):
            next_cell_start += 2

        self.lines_to_next_cell = count_lines_to_next_cell(
            cell_end_marker,
            next_cell_start,
            len(lines),
            explicit_eoc)

        return next_cell_start

    def markdown_unescape(self, lines):
        """Remove markdown prefix"""
        prefix = self.markdown_prefix
        prefix_and_space = self.markdown_prefix + ' '
        prefix_and_space_length = len(prefix_and_space)
        prefix_length = len(self.markdown_prefix)

        return [line[prefix_and_space_length:]
                if line.startswith(prefix_and_space)
                else (line[prefix_length:]
                      if line.startswith(prefix) else line)
                for line in lines]
