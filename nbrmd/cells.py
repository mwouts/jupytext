from .languages import cell_language
from .cell_metadata import metadata_to_rmd_options, rmd_options_to_metadata, \
    json_options_to_metadata, metadata_to_json_options
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell
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
            language = cell_language(source) or default_language
            options = metadata_to_rmd_options(language, metadata)
            if ext == '.Rmd':
                lines.append(u'```{{{}}}'.format(options))
            else:
                lines.append(u'```{}'.format(options))

            lines.extend(source)
            lines.append(u'```')

        elif ext == '.R':
            language = cell_language(source) or default_language
            options = metadata_to_rmd_options(language, metadata)
            if language == 'R':
                if len(options) > 2:
                    lines.append('#+ ' + options[2:])
                lines.extend(source)
            else:
                lines.append(u"#' ```{{{}}}".format(options))
                lines.extend(["#' " + s for s in source])
                lines.append("#' ```")
        else:  # ext == '.py':
            language = cell_language(source) or default_language
            if language == 'python':
                options = metadata_to_json_options(metadata)
                if options != '{}':
                    lines.append('#+ ' + options)
                lines.extend(source)
            else:
                options = metadata_to_rmd_options(language, metadata)
                lines.append(u"## ```{{{}}}".format(options))
                lines.extend(["## " + s for s in source])
                lines.append("## ```")

            if next_cell and next_cell.cell_type == 'code':
                lines.append('')
    else:
        if ext == '.Rmd':
            lines.extend(source)
        elif ext == '.py':
            lines.extend(["## " + s for s in source])
        else:
            lines.extend(["#' " + s for s in source])

    if skipline:
        lines.append('')

    return lines


_start_code_rmd = re.compile(r"^```\{(.*)\}\s*$")
_start_code_md = re.compile(r"^```(.*)$")
_end_code_md = re.compile(r"^```\s*$")
_option_code_rpy = re.compile(r"^#\+(.*)$")
_blank = re.compile(r"^\s*$")


def start_code(line, ext):
    if ext == '.Rmd':
        return _start_code_rmd.match(line)
    else:  # .R or .py
        return _option_code_rpy.match(line)


def text_to_cell(lines, ext='.Rmd'):
    if start_code(lines[0], ext):
        return code_to_cell(lines, ext, True)
    elif ext == '.R' and not lines[0].startswith("#'"):
        return code_to_cell(lines, ext, False)
    elif ext == '.py' and not lines[0].startswith("##"):
        return code_to_cell(lines, ext, False)
    else:
        return markdown_to_cell(lines, ext)


def parse_code_options(line, ext):
    if ext == '.Rmd':
        return rmd_options_to_metadata(_start_code_rmd.findall(line)[0])
    else:
        if ext == '.R':
            if _option_code_rpy.match(line):
                return 'R', rmd_options_to_metadata(
                    _option_code_rpy.findall(line)[0])
            else:
                return 'R', {}
        else:  # ext=='.py'
            if _option_code_rpy.match(line):
                return 'python', json_options_to_metadata(
                    _option_code_rpy.findall(line)[0])
            else:
                return 'python', {}


def code_to_cell(lines, ext, parse_opt):
    # Parse options
    if parse_opt:
        language, metadata = parse_code_options(lines[0], ext)
        metadata['language'] = language
    else:
        metadata = {}

    # Find end of cell and return
    if ext == '.Rmd':
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
            prev_blank = _blank.match(line)
    else:
        prev_blank = False
        for pos, line in enumerate(lines):
            if parse_opt and pos == 0:
                continue

            if (ext == '.py' and line.startswith('##')) \
                    or (ext == '.R' and line.startswith("#'")):

                lines[pos] = line[3:]

                if prev_blank:
                    return new_code_cell(
                        source='\n'.join(lines[parse_opt:(pos - 1)]),
                        metadata=metadata), pos + 1
                else:
                    r = new_code_cell(
                        source='\n'.join(lines[parse_opt:pos]),
                        metadata=metadata)
                    r.metadata['noskipline'] = True
                    return r, pos + 1

            if _blank.match(line):
                if prev_blank:
                    return new_code_cell(
                        source='\n'.join(lines[parse_opt:(pos - 1)]),
                        metadata=metadata), pos + 1
                prev_blank = True
            else:
                prev_blank = False

    # Unterminated cell?
    if prev_blank:
        r = new_code_cell(
            source='\n'.join(lines[parse_opt:-1]),
            metadata=metadata)
    else:
        r = new_code_cell(
            source='\n'.join(lines[parse_opt:]),
            metadata=metadata)
    return r, len(lines)


def markdown_to_cell(lines, ext):
    prev_blank = False

    if ext in ['.py', '.R']:
        # Markdown stops with the end of comments
        md = []
        for pos, line in enumerate(lines):
            if (ext == '.py' and line.startswith("##")) \
                    or (ext == '.R' and line.startswith("#'")):
                md.append(line[3:])
            elif _blank.match(line):
                return new_markdown_cell(source='\n'.join(md)), pos + 1
            else:
                r = new_markdown_cell(source='\n'.join(md))
                r.metadata['noskipline'] = True
                return r, pos

        # still here=> unterminated markdown
        r = new_markdown_cell(source='\n'.join(md))
        r.metadata['noskipline'] = True
        return r, pos + 1

    for pos, line in enumerate(lines):
        if start_code(line, ext):
            if prev_blank and pos > 1:
                return new_markdown_cell(
                    source='\n'.join(lines[:(pos - 1)])), pos
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
