"""Cell conversion methods.

Convert/read notebook cells to/from python, R and Rmd cells
"""

import re
from nbformat.v4.nbbase import new_code_cell, new_raw_cell, new_markdown_cell
from .cell_metadata import is_active, rmd_options_to_metadata, \
    json_options_to_metadata
from .magics import is_magic, unescape_magic
from .stringparser import StringParser

_START_CODE_RMD = re.compile(r"^```\{(.*)\}\s*$")
_END_CODE_MD = re.compile(r"^```\s*$")
_CODE_OPTION_R = re.compile(r"^#\+(.*)\s*$")
_CODE_OPTION_PY = re.compile(r"^(#|# )\+(\s*)\{(.*)\}\s*$")
_BLANK_LINE = re.compile(r"^\s*$")


def start_code_rmd(line):
    """
    Line indicates that a code cell starts, in a rmd file
    :param line:
    :return:
    """
    return _START_CODE_RMD.match(line)


def start_code_r(line):
    """
    A code cell starts here, in a R file
    :param line:
    :return:
    """
    return _CODE_OPTION_R.match(line)


def start_code_py(line):
    """
    A code cell starts here, in a R file
    :param line:
    :return:
    """
    return _CODE_OPTION_PY.match(line)


def start_code_rpy(line, ext):
    """
    A code cell starts here, in a py or R file
    :param line:
    :param ext:
    :return:
    """
    if ext == '.R':
        return start_code_r(line)
    if ext == '.py':
        return start_code_py(line)
    return False


def next_uncommented_is_code(lines):
    """
    Next non-commented line is code
    :param lines:
    :return:
    """
    for line in lines:
        if line.startswith('#'):
            continue
        return not _BLANK_LINE.match(line)

    return False


def text_to_cell(self, lines):
    """
    Parse text to a cell
    :param self:
    :param lines:
    :return: cell, cursor
    """
    if self.start_code(lines[0]):
        return self.code_to_cell(lines, parse_opt=True)
    if self.prefix != '' and not lines[0].startswith(self.prefix):
        return self.code_to_cell(lines, parse_opt=False)
    if self.ext == '.py' and (next_uncommented_is_code(lines)
                              or is_magic(lines[0])):
        return self.code_to_cell(lines, parse_opt=False)

    return self.markdown_to_cell(lines)


def parse_code_options(line, ext):
    """
    Parse code options on the given line
    :param line:
    :param ext:
    :return:
    """
    if ext == '.Rmd':
        return rmd_options_to_metadata(_START_CODE_RMD.findall(line)[0])
    if ext == '.R':
        language, metadata = \
            rmd_options_to_metadata(_CODE_OPTION_R.findall(line)[0])
        if 'language' in metadata:
            language = metadata['language']
            del metadata['language']
        return language, metadata

    return 'python', json_options_to_metadata(
        _CODE_OPTION_PY.match(line).group(3))


def next_code_is_indented(lines):
    """
    Is next code line indented?
    :param lines:
    :return:
    """
    for line in lines:
        if line.startswith('#'):
            continue
        if _BLANK_LINE.match(line):
            continue
        return line.startswith(' ')

    return False


def code_or_raw_cell(source, metadata):
    """Return a code, or raw cell from given source and metadata"""
    if not is_active('ipynb', metadata):
        if metadata.get('active') == '':
            del metadata['active']
        return new_raw_cell(source='\n'.join(source), metadata=metadata)
    return new_code_cell(source='\n'.join(source), metadata=metadata)


def code_to_cell(self, lines, parse_opt):
    """
    Parse code to a notebook cell
    :param self:
    :param lines:
    :param parse_opt:
    :return: cell, cursor
    """
    # Parse options
    if parse_opt:
        language, metadata = parse_code_options(lines[0], self.ext)
        if self.ext == '.Rmd' and metadata.get('active') != '':
            metadata['language'] = language
    else:
        language = 'python' if self.ext == '.py' else 'R'
        metadata = {}

    if self.ext == '.Rmd':
        end_cell_re = _END_CODE_MD
    elif self.ext == '.py' and 'endofcell' in metadata:
        end_cell_re = re.compile(r'^#( )' + metadata['endofcell'] + r'\s*$')
        del metadata['endofcell']
    elif not is_active(self.ext, metadata):
        end_cell_re = _BLANK_LINE
    else:
        end_cell_re = None

    # Find end of cell and return
    if end_cell_re:
        for pos, line in enumerate(lines):
            if not pos:
                continue
            if end_cell_re.match(line):
                next_line_blank = pos + 1 == len(lines) or \
                                  _BLANK_LINE.match(lines[pos + 1])
                source = lines[1:pos]
                if is_active(self.ext, metadata):
                    source = unescape_magic(source, language)
                elif self.ext in ['.py', '.R']:
                    source = [self.markdown_unescape(s) for s in source]
                if end_cell_re == _BLANK_LINE:
                    return code_or_raw_cell(
                        source=source, metadata=metadata), pos + 1
                if next_line_blank and pos + 2 != len(lines):
                    return code_or_raw_cell(
                        source=source, metadata=metadata), pos + 2
                cell = code_or_raw_cell(source=source, metadata=metadata)
                cell.metadata['noskipline'] = True
                return cell, pos + 1
            if start_code_rpy(line, self.ext):
                prev_blank = _BLANK_LINE.match(lines[pos - 1])
                source = lines[1:(pos - 1 if prev_blank else pos)]
                if is_active(self.ext, metadata):
                    source = unescape_magic(source, language)
                elif self.ext in ['.py', '.R']:
                    source = [self.markdown_unescape(s) for s in source]
                cell = code_or_raw_cell(source=source, metadata=metadata)
                if not prev_blank:
                    cell.metadata['noskipline'] = True
                return cell, pos
    else:
        # self.ext is .py or .R
        prev_blank = False
        parser = StringParser(language)
        for pos, line in enumerate(lines):
            if parse_opt and pos == 0:
                continue

            if parser.is_quoted():
                parser.read_line(line)
                continue

            parser.read_line(line)

            if start_code_rpy(line, self.ext) or (
                    self.ext == '.R' and line.startswith(self.prefix)):
                source = lines[parse_opt:pos]
                if is_active(self.ext, metadata):
                    source = unescape_magic(source, language)
                if prev_blank:
                    return code_or_raw_cell(
                        source=source[:-1], metadata=metadata), pos
                cell = code_or_raw_cell(
                    source=source, metadata=metadata)
                cell.metadata['noskipline'] = True
                return cell, pos

            if _BLANK_LINE.match(line):
                if pos == 0:
                    continue
                # This line blank and next one blank => two lines before and
                # after classes and functions. Three blank lines or more? May
                # be multiple cells
                if pos + 1 == len(lines) or _BLANK_LINE.match(lines[pos + 1]):
                    if (pos + 2 < len(lines) and
                            not _BLANK_LINE.match(lines[pos + 2])):
                        prev_blank = True
                        continue

                if next_code_is_indented(lines[pos:]):
                    continue

                source = lines[parse_opt:(pos - (1 if prev_blank else 0))]
                if is_active(self.ext, metadata):
                    source = unescape_magic(source, language)

                cell = code_or_raw_cell(source=source, metadata=metadata)
                if prev_blank or pos + 1 == len(lines):
                    cell['metadata']['skipline'] = True

                return cell, pos + 1

            prev_blank = _BLANK_LINE.match(line)

    # Unterminated cell?
    source = lines[parse_opt:]
    if is_active(self.ext, metadata):
        source = unescape_magic(source, language)
    elif self.ext in ['.py', '.R']:
        source = [self.markdown_unescape(s) for s in source]

    return code_or_raw_cell(source=source, metadata=metadata), len(lines)


def markdown_to_cell(self, lines):
    """
    Parse text and return a markdown cell
    :param self:
    :param lines:
    :return: cell, cursor
    """
    markdown = []
    for pos, line in enumerate(lines):
        # Markdown stops with the end of comments
        if line.startswith(self.prefix):
            markdown.append(self.markdown_unescape(line))
        elif _BLANK_LINE.match(line):
            return new_markdown_cell(source='\n'.join(markdown)), pos + 1
        else:
            cell = new_markdown_cell(source='\n'.join(markdown))
            cell.metadata['noskipline'] = True
            return cell, pos

    # still here => unterminated markdown
    return new_markdown_cell(source='\n'.join(markdown)), len(lines)


def markdown_to_cell_rmd(lines):
    """
    Parse text, in case of a rmd file, and return a markdown cell
    :param lines:
    :return: cell, cursor
    """
    prev_blank = False
    for pos, line in enumerate(lines):
        if start_code_rmd(line):
            if prev_blank and pos > 1:
                return new_markdown_cell(
                    source='\n'.join(lines[:(pos - 1)])), pos
            cell = new_markdown_cell(
                source='\n'.join(lines[:pos]))
            cell.metadata['noskipline'] = True
            return cell, pos

        if _BLANK_LINE.match(line) and prev_blank:
            return new_markdown_cell(
                source='\n'.join(lines[:(pos - 1)])), pos + 1
        prev_blank = _BLANK_LINE.match(line)

    # Unterminated cell?
    return new_markdown_cell(source='\n'.join(lines)), len(lines)
