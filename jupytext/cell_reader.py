"""Read notebook cells from their text representation"""

import re
from nbformat.v4.nbbase import new_code_cell, new_raw_cell, new_markdown_cell
from .languages import _SCRIPT_EXTENSIONS

try:
    from sphinx_gallery.notebook import rst2md
except ImportError:
    rst2md = None

from .cell_metadata import is_active, json_options_to_metadata, md_options_to_metadata, rmd_options_to_metadata, \
    double_percent_options_to_metadata
from .stringparser import StringParser
from .magics import uncomment_magic, is_magic, unescape_code_start
from .pep8 import pep8_lines_between_cells

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


def paragraph_is_fully_commented(lines, comment, main_language):
    """Is the paragraph fully commented?"""
    for i, line in enumerate(lines):
        if line.startswith(comment):
            if line.startswith((comment + ' %', comment + ' ?')) and is_magic(line, main_language):
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


def count_lines_to_next_cell(cell_end_marker, next_cell_start, total, explicit_eoc):
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
    return not _BLANK_LINE.match(source[-3]) and _BLANK_LINE.match(source[-2]) and _BLANK_LINE.match(source[-1])


class BaseCellReader(object):
    """A class that can read notebook cells from their text representation"""
    default_comment_magics = None
    lines_to_next_cell = 1

    start_code_re = None
    simple_start_code_re = None
    end_code_re = None

    # How to make code inactive
    comment = ''

    # Any specific prefix for lines in markdown cells (like in R spin format?)
    markdown_prefix = None

    def __init__(self, fmt=None):
        """Create a cell reader with empty content"""
        if not fmt:
            fmt = {}
        self.ext = fmt.get('extension')
        self.default_language = _SCRIPT_EXTENSIONS.get(self.ext, {}).get('language', 'python')
        self.comment_magics = fmt['comment_magics'] if 'comment_magics' in fmt else self.default_comment_magics
        self.metadata = None
        self.content = []
        self.explicit_eoc = None
        self.cell_type = None
        self.language = None

    def read(self, lines):
        """Read one cell from the given lines, and return the cell,
        plus the position of the next cell
        """

        # Do we have an explicit code marker on the first line?
        self.metadata_and_language_from_option_line(lines[0])

        if self.metadata and 'language' in self.metadata:
            self.language = self.metadata.pop('language')

        # Parse cell till its end and set content, lines_to_next_cell
        pos_next_cell = self.find_cell_content(lines)

        if self.cell_type == 'code':
            new_cell = new_code_cell
        elif self.cell_type == 'markdown':
            new_cell = new_markdown_cell
        else:
            new_cell = new_raw_cell

        if not self.metadata:
            self.metadata = {}

        org_lines = self.content
        if self.ext == '.py' and self.cell_type != 'code' and self.content:
            org_lines = ['#']  # cell was originally commented
        if self.cell_type == 'code' and self.ext == '.py' and not self.explicit_eoc:
            expected_blank_lines = pep8_lines_between_cells(org_lines, lines[pos_next_cell:], self.ext)
        else:
            expected_blank_lines = 1

        if self.lines_to_next_cell != expected_blank_lines:
            self.metadata['lines_to_next_cell'] = self.lines_to_next_cell

        if self.language:
            self.metadata['language'] = self.language

        return new_cell(source='\n'.join(self.content), metadata=self.metadata), pos_next_cell

    def metadata_and_language_from_option_line(self, line):
        """Parse code options on the given line. When a start of a code cell
        is found, self.metadata is set to a dictionary."""
        if self.start_code_re.match(line):
            self.language, self.metadata = self.options_to_metadata(self.start_code_re.findall(line)[0])

    def options_to_metadata(self, options):
        """Return language (str) and metadata (dict) from the option line"""
        raise NotImplementedError("Option parsing must be implemented in a sub class")

    def find_code_cell_end(self, lines):
        """Given that this is a code cell, return position of
        end of cell marker, and position of next cell start"""
        if self.metadata and 'cell_type' in self.metadata:
            self.cell_type = self.metadata.pop('cell_type')
        else:
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

            if self.start_code_re.match(line) or (self.markdown_prefix and line.startswith(self.markdown_prefix)):
                if i > 1 and _BLANK_LINE.match(lines[i - 1]):
                    return i - 1, i, False
                return i, i, False

            # Simple code pattern in LightScripts must be preceded with a blank line
            if i > 0 and self.simple_start_code_re and _BLANK_LINE.match(lines[i - 1]) and \
                    self.simple_start_code_re.match(line):
                return i - 1, i, False

            if self.end_code_re:
                if self.end_code_re.match(line):
                    return i, i + 1, True
            elif _BLANK_LINE.match(line):
                if not next_code_is_indented(lines[i:]):
                    if i > 0:
                        return i, i + 1, False
                    if len(lines) > 1 and not _BLANK_LINE.match(lines[1]):
                        return 1, 1, False
                    return 1, 2, False

        return len(lines), len(lines), False

    def find_cell_end(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""
        raise NotImplementedError('This method must be implemented in a sub class')

    def find_cell_content(self, lines):
        """Parse cell till its end and set content, lines_to_next_cell.
        Return the position of next cell start"""
        cell_end_marker, next_cell_start, self.explicit_eoc = self.find_cell_end(lines)

        # Metadata to dict
        if self.metadata is None:
            cell_start = 0
            self.metadata = {}
        else:
            cell_start = 1

        # Cell content
        source = lines[cell_start:cell_end_marker]

        # Exactly two empty lines at the end of cell (caused by PEP8)?
        if self.ext == '.py' and self.explicit_eoc:
            if last_two_lines_blank(source):
                source = source[:-2]
                lines_to_end_of_cell_marker = 2
            else:
                lines_to_end_of_cell_marker = 0

            pep8_lines = pep8_lines_between_cells(source, lines[cell_end_marker:], self.ext)
            if lines_to_end_of_cell_marker != (0 if pep8_lines == 1 else 2):
                self.metadata['lines_to_end_of_cell_marker'] = lines_to_end_of_cell_marker

        if not is_active(self.ext, self.metadata) or \
                ('active' not in self.metadata and self.language and self.language != self.default_language):
            self.content = uncomment(source, self.comment if self.ext not in ['.r', '.R'] else '#')
        else:
            self.content = self.uncomment_code_and_magics(source)

        # Is this a raw cell?
        if ('active' in self.metadata and not is_active('ipynb', self.metadata)) or \
                (self.ext == '.md' and self.cell_type == 'code' and self.language is None):
            if self.metadata.get('active') == '':
                del self.metadata['active']
            self.cell_type = 'raw'

        # Explicit end of cell marker?
        if (next_cell_start + 1 < len(lines) and
                _BLANK_LINE.match(lines[next_cell_start]) and
                not _BLANK_LINE.match(lines[next_cell_start + 1])):
            next_cell_start += 1
        elif (self.explicit_eoc and next_cell_start + 2 < len(lines) and
              _BLANK_LINE.match(lines[next_cell_start]) and
              _BLANK_LINE.match(lines[next_cell_start + 1]) and
              not _BLANK_LINE.match(lines[next_cell_start + 2])):
            next_cell_start += 2

        self.lines_to_next_cell = count_lines_to_next_cell(
            cell_end_marker,
            next_cell_start,
            len(lines),
            self.explicit_eoc)

        return next_cell_start

    def uncomment_code_and_magics(self, lines):
        """Uncomment code and possibly commented magic commands"""
        raise NotImplementedError('This method must be implemented in a sub class')


class MarkdownCellReader(BaseCellReader):
    """Read notebook cells from Markdown documents"""
    comment = ''
    start_code_re = re.compile(r"^```(.*)")
    end_code_re = re.compile(r"^```\s*$")
    default_comment_magics = False

    def __init__(self, fmt=None):
        super(MarkdownCellReader, self).__init__(fmt)
        self.split_at_heading = (fmt or {}).get('split_at_heading', False)

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
                if self.split_at_heading and line.startswith('#') and prev_blank >= 1:
                    return i - 1, i, False
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
        if self.comment_magics:
            lines = uncomment_magic(lines, self.language)
        return unescape_code_start(lines, self.ext, self.language or self.default_language)


class RMarkdownCellReader(MarkdownCellReader):
    """Read notebook cells from R Markdown notebooks"""
    comment = ''
    start_code_re = re.compile(r"^```{(.*)}\s*$")
    default_language = 'R'
    default_comment_magics = True

    def options_to_metadata(self, options):
        return rmd_options_to_metadata(options)

    def uncomment_code_and_magics(self, lines):
        if self.cell_type == 'code':
            if is_active('.Rmd', self.metadata) and self.comment_magics:
                uncomment_magic(lines, self.language or self.default_language)

        unescape_code_start(lines, '.Rmd', self.language or self.default_language)

        return lines


class ScriptCellReader(BaseCellReader):
    """Read notebook cells from scripts
    (common base for R and Python scripts)"""

    def options_to_metadata(self, options):
        raise NotImplementedError()

    def uncomment_code_and_magics(self, lines):
        if self.cell_type == 'code' or self.comment != "#'":
            if self.comment_magics:
                if is_active(self.ext, self.metadata):
                    uncomment_magic(lines, self.language or self.default_language)
                else:
                    lines = uncomment(lines)

        if self.cell_type == 'code':
            unescape_code_start(lines, self.ext, self.language or self.default_language)

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
    default_comment_magics = True

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
    default_comment_magics = True

    def __init__(self, fmt=None):
        super(LightScriptCellReader, self).__init__(fmt)
        self.ext = self.ext or '.py'
        script = _SCRIPT_EXTENSIONS[self.ext]
        self.default_language = script['language']
        self.comment = script['comment']
        self.start_code_re = re.compile("^({0}|{0} )".format(self.comment) + r"\+(\s*){(.*)}\s*$")
        self.simple_start_code_re = re.compile(r"^({0}|{0} )\+(\s*)$".format(self.comment))

    def options_to_metadata(self, options):
        return json_options_to_metadata(options)

    def metadata_and_language_from_option_line(self, line):
        if self.start_code_re.match(line):
            self.metadata = self.options_to_metadata(self.start_code_re.match(line).group(3))
        elif self.simple_start_code_re.match(line):
            self.metadata = {}

        if self.metadata is not None:
            self.language = self.metadata.get('language', self.default_language)

    def find_cell_end(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""
        if self.metadata is None and paragraph_is_fully_commented(lines, self.comment, self.default_language):
            self.cell_type = 'markdown'
            for i, line in enumerate(lines):
                if _BLANK_LINE.match(line):
                    return i, i + 1, False
            return len(lines), len(lines), False

        if self.metadata is not None:
            end_of_cell = self.metadata.get('endofcell', '-')
            self.end_code_re = re.compile('^' + self.comment + ' ' + end_of_cell + r'\s*$')

        return self.find_code_cell_end(lines)


class DoublePercentScriptCellReader(ScriptCellReader):
    """Read notebook cells from Spyder/VScode scripts (#59)"""
    default_comment_magics = True

    def __init__(self, fmt):
        ScriptCellReader.__init__(self, fmt)
        script = _SCRIPT_EXTENSIONS[self.ext]
        self.default_language = script['language']
        self.comment = script['comment']
        self.start_code_re = re.compile(r"^{}\s*%%(%*)\s(.*)$".format(self.comment))
        self.alternative_start_code_re = re.compile(r"^{}\s*(%%|<codecell>|In\[[0-9 ]*\]:?)\s*$".format(self.comment))

    def metadata_and_language_from_option_line(self, line):
        """Parse code options on the given line. When a start of a code cell
        is found, self.metadata is set to a dictionary."""
        if self.start_code_re.match(line):
            self.language, self.metadata = self.options_to_metadata(line[line.find('%%') + 2:])
        elif self.alternative_start_code_re.match(line):
            self.metadata = {}

    def options_to_metadata(self, options):
        return None, double_percent_options_to_metadata(options)

    def find_cell_content(self, lines):
        """Parse cell till its end and set content, lines_to_next_cell.
        Return the position of next cell start"""
        cell_end_marker, next_cell_start, explicit_eoc = self.find_cell_end(lines)

        # Metadata to dict
        if self.start_code_re.match(lines[0]) or self.alternative_start_code_re.match(lines[0]):
            cell_start = 1
        else:
            cell_start = 0

        # Cell content
        source = lines[cell_start:cell_end_marker]

        if self.cell_type != 'code' or (self.metadata and not is_active('py', self.metadata)) \
                or (self.language is not None and self.language != self.default_language):
            source = uncomment(source, self.comment)
        elif self.metadata is not None and self.comment_magics:
            source = self.uncomment_code_and_magics(source)

        self.content = source

        self.lines_to_next_cell = count_lines_to_next_cell(
            cell_end_marker,
            next_cell_start,
            len(lines),
            explicit_eoc)

        return next_cell_start

    def find_cell_end(self, lines):
        """Return position of end of cell marker, and position
        of first line after cell"""

        if self.metadata and 'cell_type' in self.metadata:
            self.cell_type = self.metadata.pop('cell_type')
        else:
            self.cell_type = 'code'

        next_cell = len(lines)
        for i, line in enumerate(lines):
            if i > 0 and (self.start_code_re.match(line) or self.alternative_start_code_re.match(line)):
                next_cell = i
                break

        if last_two_lines_blank(lines[:next_cell]):
            return next_cell - 2, next_cell, False
        if next_cell > 0 and _BLANK_LINE.match(lines[next_cell - 1]):
            return next_cell - 1, next_cell, False
        return next_cell, next_cell, False


class HydrogenCellReader(DoublePercentScriptCellReader):
    """Read notebook cells from Hydrogen scripts (#59)"""
    default_comment_magics = False


class SphinxGalleryScriptCellReader(ScriptCellReader):
    """Read notebook cells from Sphinx Gallery scripts (#80)"""

    comment = '#'
    default_language = 'python'
    default_comment_magics = True
    twenty_hash = re.compile(r'^#( |)#{19,}\s*$')
    default_markdown_cell_marker = '#' * 79
    markdown_marker = None

    def __init__(self, fmt=None):
        super(SphinxGalleryScriptCellReader, self).__init__(fmt)
        self.ext = '.py'
        self.rst2md = (fmt or {}).get('rst2md', False)

    def start_of_new_markdown_cell(self, line):
        """Does this line starts a new markdown cell?
        Then, return the cell marker"""
        for empty_markdown_cell in ['""', "''"]:
            if line == empty_markdown_cell:
                return empty_markdown_cell

        for triple_quote in ['"""', "'''"]:
            if line.startswith(triple_quote):
                return triple_quote

        if self.twenty_hash.match(line):
            return line

        return None

    def metadata_and_language_from_option_line(self, line):
        self.markdown_marker = self.start_of_new_markdown_cell(line)
        if self.markdown_marker:
            self.cell_type = 'markdown'
            if self.markdown_marker != self.default_markdown_cell_marker:
                self.metadata = {'cell_marker': self.markdown_marker}
        else:
            self.cell_type = 'code'

    def options_to_metadata(self, options):
        pass

    def find_cell_end(self, lines):
        """Return position of end of cell, and position
        of first line after cell, and whether there was an
        explicit end of cell marker"""

        if self.cell_type == 'markdown':
            # Empty cell "" or ''
            if len(self.markdown_marker) <= 2:
                if len(lines) == 1 or _BLANK_LINE.match(lines[1]):
                    return 0, 2, True
                return 0, 1, True

            # Multi-line comment with triple quote
            if len(self.markdown_marker) == 3:
                for i, line in enumerate(lines):
                    if (i > 0 or line.strip() != self.markdown_marker) and line.rstrip().endswith(self.markdown_marker):
                        explicit_end_of_cell_marker = line.strip() == self.markdown_marker
                        if explicit_end_of_cell_marker:
                            end_of_cell = i
                        else:
                            end_of_cell = i + 1
                        if len(lines) <= i + 1 or _BLANK_LINE.match(
                                lines[i + 1]):
                            return end_of_cell, i + 2, explicit_end_of_cell_marker
                        return end_of_cell, i + 1, explicit_end_of_cell_marker
            else:
                # 20 # or more
                for i, line in enumerate(lines[1:], 1):
                    if not line.startswith(self.comment):
                        if _BLANK_LINE.match(line):
                            return i, i + 1, False
                        return i, i, False

        elif self.cell_type == 'code':
            parser = StringParser('python')
            for i, line in enumerate(lines):
                if parser.is_quoted():
                    parser.read_line(line)
                    continue

                if self.start_of_new_markdown_cell(line):
                    if i > 0 and _BLANK_LINE.match(lines[i - 1]):
                        return i - 1, i, False
                    return i, i, False
                parser.read_line(line)

        return len(lines), len(lines), False

    def find_cell_content(self, lines):
        """Parse cell till its end and set content, lines_to_next_cell.
        Return the position of next cell start"""
        cell_end_marker, next_cell_start, explicit_eoc = self.find_cell_end(lines)

        # Metadata to dict
        cell_start = 0
        if self.cell_type == 'markdown':
            if self.markdown_marker in ['"""', "'''"]:
                # Remove the triple quotes
                if lines[0].strip() == self.markdown_marker:
                    cell_start = 1
                else:
                    lines[0] = lines[0][3:]
                if not explicit_eoc:
                    last = lines[cell_end_marker - 1]
                    lines[cell_end_marker - 1] = last[:last.rfind(self.markdown_marker)]
            if self.twenty_hash.match(self.markdown_marker):
                cell_start = 1
        else:
            self.metadata = {}

        # Cell content
        source = lines[cell_start:cell_end_marker]

        if self.cell_type == 'code' and self.comment_magics:
            uncomment_magic(source, self.language or self.default_language)

        if self.cell_type == 'markdown' and source:
            if self.markdown_marker.startswith(self.comment):
                source = uncomment(source, self.comment)
                if self.rst2md:
                    if rst2md:
                        source = rst2md('\n'.join(source)).splitlines()
                    else:
                        raise ImportError('Could not import rst2md from sphinx_gallery.notebook')

        self.content = source

        self.lines_to_next_cell = count_lines_to_next_cell(
            cell_end_marker,
            next_cell_start,
            len(lines),
            explicit_eoc)

        return next_cell_start
