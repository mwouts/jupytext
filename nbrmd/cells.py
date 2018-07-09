from .languages import cell_language
from .chunk_options import to_chunk_options, to_metadata, _ignore_metadata
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell
import json
import re


def cell_to_text(cell,
                 next_cell=None,
                 default_language='python',
                 ext='.Rmd'):
    source = cell.get('source').splitlines()
    metadata = cell.get('metadata', {})

    skipline = True
    if 'noskipline' in metadata:
        skipline = not metadata['noskipline']
        del metadata['noskipline']

    lines = []
    if cell.cell_type == 'code':
        if ext == '.Rmd':
            metadata['language'] = cell_language(source) or default_language
            lines.append(u'```{' + to_chunk_options(metadata) + '}')
        elif ext == '.md':
            metadata['language'] = cell_language(source) or default_language
            lines.append(u'```' + to_chunk_options(metadata))
        elif ext == '.R':
            lines.append('#+ ' + to_chunk_options(metadata))
        else:  # ext == '.py':
            lines.append('#+ ' +
                         json.dumps({k: v for k, v in metadata.iteritems()
                                     if k not in _ignore_metadata}))

        if source is not None:
            lines.extend(source)
        lines.append(u'```')

        if skipline and ext == '.py' and next_cell \
                and next_cell.cell_type == 'code':
            lines.append('')
    else:
        lines.append(cell.get('source', ''))

    if skipline:
        lines.append('')

    return lines


_start_code_rmd = re.compile(r"^```\{(.*)\}\s*$")
_start_code_md = re.compile(r"^```(.*)$")
_end_code_md = re.compile(r"^```\s*$")
_option_code_rpy = re.compile(r"^#\+(.*)")
_markdown_rpy = re.compile(r"^#'")
_blank = re.compile(r"^\s*$")


def start_code(line, ext):
    if ext == '.Rmd':
        return _start_code_rmd.match(line)
    elif ext == '.md':
        return _start_code_md.match(line)
    else:  # .R or .py
        return not _markdown_rpy.match(line) or \
               _option_code_rpy.match(line)


def text_to_cell(lines, ext='.Rmd'):
    if start_code(lines[0], ext):
        return code_to_cell(lines, ext)
    else:
        return markdown_to_cell(lines, ext)


def parse_code_options(line, ext):
    if ext == '.Rmd':
        return to_metadata(_start_code_rmd.findall(line)[0])
    elif ext == '.md':
        return to_metadata(_start_code_md.findall(line)[0])
    elif ext == '.R':
        return to_metadata(_option_code_rpy.findall(line)[0])
    else:
        try:
            return json.loads(_option_code_rpy.findall(line)[0])
        except ValueError:
            return {}


def code_to_cell(lines, ext):
    # Parse options
    metadata = parse_code_options(lines[0], ext)

    # Find end of cell and return
    if ext in ['.Rmd', '.md']:
        for pos, line in enumerate(lines):
            if pos > 0 and _end_code_md.match(line):
                if pos + 1 < len(lines) and _blank.match(lines[pos + 1]):
                    return new_code_cell(
                        source='\n'.join(lines[1:pos]), metadata=metadata), \
                           pos + 2
                else:
                    r = new_code_cell(
                        source='\n'.join(lines[1:pos]),
                        metadata=metadata)
                    r.metadata['noskipline'] = True
                    return r, pos + 1
    else:
        prev_blank = False
        for pos, line in enumerate(lines):
            if pos == 0:
                continue

            if _markdown_rpy.match(line):
                pos -= 1
                if prev_blank:
                    return new_code_cell(
                        source='\n'.join(lines[1:(pos - 1)]),
                        metadata=metadata), pos + 1
                else:
                    r = new_code_cell(
                        source='\n'.join(lines[1:pos]),
                        metadata=metadata)
                    r.metadata['noskipline'] = True
                    return r, pos + 1

            if _blank.match(line):
                if prev_blank:
                    return new_code_cell(
                        source='\n'.join(lines[1:pos]),
                        metadata=metadata), pos + 1
                prev_blank = True
            else:
                prev_blank = False

    # Unterminated cell?
    r = new_code_cell(
        source='\n'.join(lines[1:]),
        metadata=metadata)
    return r, len(lines)


def markdown_to_cell(lines, ext):
    prev_blank = False

    for pos, line in enumerate(lines):
        if start_code(line, ext):
            if prev_blank and pos > 1:
                return new_markdown_cell(
                    source='\n'.join(lines[:(pos-1)])), pos
            else:
                r = new_markdown_cell(
                    source='\n'.join(lines[:pos]))
                r.metadata['noskipline'] = True
                return r, pos
        prev_blank = _blank.match(line)

    # Unterminated cell?
    if prev_blank:
        return new_markdown_cell(source='\n'.join(lines[:-1])), len(lines)
    else:
        r = new_markdown_cell(source='\n'.join(lines))
        r.metadata['noskipline'] = True
        return r, len(lines)
