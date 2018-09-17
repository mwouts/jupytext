"""Read notebook cells from their text representation"""

import re
from nbformat.v4.nbbase import new_code_cell, new_raw_cell, new_markdown_cell
from .cell_metadata import is_active, json_options_to_metadata, \
    md_options_to_metadata, rmd_options_to_metadata
from .stringparser import StringParser
from .magics import unescape_magic, is_magic, unescape_code_start

_CODE_OPTION_PY = re.compile(r"^(#|# )\+(\s*){(.*)}\s*$")
_SIMPLE_START_CODE_PY = re.compile(r"^(#|# )\+(\s*)$")
_BLANK_LINE = re.compile(r"^\s*$")
_PY_COMMENT = re.compile(r"^\s*#")
_PY_INDENTED = re.compile(r"^\s")


def uncomment(lines, prefix='#'):
    """Remove prefix and space, or only prefix, when possible"""
    if not prefix:
        return lines
    prefix_and_space = prefix + ' '
    length_prefix = len(prefix)
    length_prefix_and_space = len(prefix_and_space)
    return [line[length_prefix_and_space:] if line.startswith(prefix_and_space)
            else (line[length_prefix:] if line.startswith(prefix) else line)
            for line in lines]


def paragraph_is_fully_commented(lines, main_language):
    """Is the paragraph fully commented?"""
    for i, line in enumerate(lines):
        if line.startswith('#'):
            if (line.startswith(('# %', '# ?'))
                    and is_magic(line, main_language)):
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


class BaseCellReader:
    """A class that can read notebook cells from their text representation"""

    cell_type = None
    language = None
    default_language = 'python'
    metadata = None
    content = []
    lines_to_next_cell = 1

    start_code_re = None
    end_code_re = None

    # How to make code inactive
    comment = ''

    # Any specific prefix for lines in markdown cells (like in R spin format?)
    markdown_prefix = None

    def __init__(self, ext):
        """Create a cell reader with empty content"""
        self.ext = ext

    def read(self, lines):
        """Read one cell from the given lines, and return the cell,
        plus the position of the next cell
        """

        # Do we have an explicit code marker on the first line?
        self.metadata_and_language_from_option_line(lines[0])

        if self.metadata and 'language' in self.metadata:
            self.language = self.metadata['language']
            del self.metadata['language']

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
        if self.start_code_re.match(line):
            self.language, self.metadata = \
                self.options_to_metadata(self.start_code_re.findall(line)[0])

    def options_to_metadata(self, options):
        """Return language (str) and metadata (dict) from the option line"""
        raise NotImplementedError("Option parsing must be implemented in a "
                                  "sub class")

    def find_code_cell_end(self, lines):
        """Given that this is a code cell, return position of
        end of cell marker, and position of next cell start"""
        self.cell_type = 'code'
        parser = StringParser(self.language or self.default_language)
        for i, line in enumerate(lines):
            # skip cell header
            if self.metadata is not None and i == 0:
                continue

            if parser.is_quoted():
                parser.read_line(line)
                continue

            parser.read_line(line)

            if self.start_code_re.match(line) or \
                    (self.markdown_prefix and
                     line.startswith(self.markdown_prefix)):
                if i > 1 and _BLANK_LINE.match(lines[i - 1]):
                    return i - 1, i, False
                return i, i, False

            # Simple code pattern in LightScripts must be preceded with
            # a blank line
            if i > 0 and self.start_code_re == _CODE_OPTION_PY and \
                    _BLANK_LINE.match(lines[i - 1]) and \
                    _SIMPLE_START_CODE_PY.match(line):
                return i - 1, i, False

            if self.end_code_re:
                if self.end_code_re.match(line):
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
        raise NotImplementedError('This method must be implemented in a '
                                  'sub class')

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

        self.content = self.uncomment_code_and_magics(source)

        # Exactly two empty lines at the end of cell (caused by PEP8)?
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

    def uncomment_code_and_magics(self, lines):
        """Uncomment code and possibly commented magic commands"""
        raise NotImplementedError('This method must be implemented in a '
                                  'sub class')


class MarkdownCellReader(BaseCellReader):
    """Read notebook cells from Markdown documents"""
    comment = ''
    start_code_re = re.compile(r"^```(.*)")
    end_code_re = re.compile(r"^```\s*$")

    def options_to_metadata(self, options):
        return md_options_to_metadata(options)

    def find_cell_end(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""
        # markdown: (last) two consecutive blank lines
        if self.metadata is None:
            self.cell_type = 'markdown'
            prev_blank = 0
            for i, line in enumerate(lines):
                if self.start_code_re.match(line):
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
                if self.end_code_re.match(line):
                    return i, i + 1, True

        # End not found
        return len(lines), len(lines), False

    def uncomment_code_and_magics(self, lines):
        return unescape_code_start(lines, self.ext, self.language or
                                   self.default_language)


class RMarkdownCellReader(MarkdownCellReader):
    """Read notebook cells from R Markdown notebooks"""
    comment = ''
    start_code_re = re.compile(r"^```{(.*)}\s*$")
    default_language = 'R'

    def options_to_metadata(self, options):
        return rmd_options_to_metadata(options)

    def uncomment_code_and_magics(self, lines):
        if self.cell_type == 'code':
            if is_active(self.ext, self.metadata):
                unescape_magic(lines, self.language or self.default_language)

        unescape_code_start(lines, self.ext, self.language or
                            self.default_language)

        return lines


class ScriptCellReader(BaseCellReader):
    """Read notebook cells from scripts
    (common base for R and Python scripts)"""

    def options_to_metadata(self, options):
        raise NotImplementedError()

    def uncomment_code_and_magics(self, lines):
        if self.cell_type == 'code':
            if is_active(self.ext, self.metadata):
                unescape_magic(lines, self.language or self.default_language)
            else:
                lines = uncomment(lines)

        if self.cell_type == 'code':
            unescape_code_start(lines, self.ext, self.language or
                                self.default_language)

        if self.cell_type == 'markdown':
            lines = uncomment(lines, self.markdown_prefix or self.comment)

        return lines


class RScriptCellReader(ScriptCellReader):
    """Read notebook cells from R scripts written according
    to the knitr-spin syntax"""

    comment = "#'"
    markdown_prefix = "#'"
    default_language = 'R'
    start_code_re = re.compile(r"^#\+(.*)\s*$")

    def options_to_metadata(self, options):
        return rmd_options_to_metadata('r ' + options)

    def find_cell_end(self, lines):
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

        return self.find_code_cell_end(lines)


class LightScriptCellReader(ScriptCellReader):
    """Read notebook cells from plain Python or Julia files. Cells
    are identified by line breaks, unless they start with an
    explicit marker '# +' """
    comment = '#'
    start_code_re = _CODE_OPTION_PY

    def __init__(self, ext):
        super(LightScriptCellReader, self).__init__(ext)
        self.default_language = 'julia' if ext == '.jl' else 'python'

    def options_to_metadata(self, options):
        return json_options_to_metadata(options)

    def metadata_and_language_from_option_line(self, line):
        if _CODE_OPTION_PY.match(line):
            self.metadata = self.options_to_metadata(
                _CODE_OPTION_PY.match(line).group(3))
        elif _SIMPLE_START_CODE_PY.match(line):
            self.metadata = {}

        if self.metadata is not None:
            self.language = self.metadata.get(
                'language', self.default_language)

    def find_cell_end(self, lines):
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
            self.end_code_re = re.compile('^# ' + end_of_cell + r'\s*$')

        return self.find_code_cell_end(lines)
