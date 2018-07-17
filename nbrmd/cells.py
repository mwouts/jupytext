from .languages import cell_language
from .cell_metadata import metadata_to_rmd_options, rmd_options_to_metadata, \
    json_options_to_metadata, metadata_to_json_options
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell
import re


def code_to_rmd(source, metadata, default_language):
    lines = []
    language = cell_language(source) or default_language
    options = metadata_to_rmd_options(language, metadata)
    lines.append(u'```{{{}}}'.format(options))
    lines.extend(source)
    lines.append(u'```')
    return lines


def cell_to_text(self,
                 cell,
                 next_cell=None,
                 default_language='python'):
    source = cell.get('source').splitlines()
    metadata = cell.get('metadata', {})
    skipline = True
    if 'noskipline' in metadata:
        skipline = not metadata['noskipline']
        del metadata['noskipline']

    lines = []
    if cell.cell_type == 'code':
        if self.ext == '.Rmd':
            lines.extend(code_to_rmd(source, metadata, default_language))
        else:
            language = cell_language(source) or default_language
            if language == default_language:
                if self.ext == '.R':
                    options = metadata_to_rmd_options(language, metadata)[2:]
                    if options != '':
                        lines.append('#+ ' + options)
                else:
                    options = metadata_to_json_options(metadata)
                    if options != '{}':
                        lines.append('#+ ' + options)
                lines.extend(source)
            else:
                lines.extend(self.markdown_escape(
                    code_to_rmd(source, metadata, default_language)))

            # Two blank lines before next code cell
            if next_cell and next_cell.cell_type == 'code':
                lines.append('')
    else:
        if source == []:
            source = ['']
        lines.extend(self.markdown_escape(source))

        # Two blank lines between consecutive markdown cells
        if self.ext == '.Rmd' and next_cell \
                and next_cell.cell_type == 'markdown':
            lines.append('')

    if skipline:
        lines.append('')

    return lines


_start_code_rmd = re.compile(r"^```\{(.*)\}\s*$")
_start_code_md = re.compile(r"^```(.*)$")
_end_code_md = re.compile(r"^```\s*$")
_option_code_rpy = re.compile(r"^#\+(.*)$")
_blank = re.compile(r"^\s*$")


def start_code_rmd(line):
    return _start_code_rmd.match(line)


def start_code_rpy(line):
    return _option_code_rpy.match(line)


def text_to_cell(self, lines):
    if self.start_code(lines[0]):
        return self.code_to_cell(lines, parse_opt=True)
    elif self.prefix != '' and not lines[0].startswith(self.prefix):
        return self.code_to_cell(lines, parse_opt=False)
    else:
        return self.markdown_to_cell(lines)


def parse_code_options(line, ext):
    if ext == '.Rmd':
        return rmd_options_to_metadata(_start_code_rmd.findall(line)[0])
    else:
        language = 'R' if ext == '.R' else 'python'
        if _option_code_rpy.match(line):
            return language, rmd_options_to_metadata(
                _option_code_rpy.findall(line)[0])
        else:
            return language, {}


def code_to_cell(self, lines, parse_opt):
    # Parse options
    if parse_opt:
        language, metadata = parse_code_options(lines[0], self.ext)
        metadata['language'] = language
    else:
        metadata = {}

    # Find end of cell and return
    if self.ext == '.Rmd':
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

            if self.prefix != '' and line.startswith(self.prefix):
                if prev_blank:
                    return new_code_cell(
                        source='\n'.join(lines[parse_opt:(pos - 1)]),
                        metadata=metadata), pos
                else:
                    r = new_code_cell(
                        source='\n'.join(lines[parse_opt:pos]),
                        metadata=metadata)
                    r.metadata['noskipline'] = True
                    return r, pos

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


def markdown_to_cell(self, lines):
    md = []
    for pos, line in enumerate(lines):
        # Markdown stops with the end of comments
        if line.startswith(self.prefix):
            md.append(self.markdown_unescape(line))
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


def markdown_to_cell_rmd(lines):
    prev_blank = False
    for pos, line in enumerate(lines):
        if start_code_rmd(line):
            if prev_blank and pos > 1:
                return new_markdown_cell(
                    source='\n'.join(lines[:(pos - 1)])), pos
            else:

                r = new_markdown_cell(
                    source='\n'.join(lines[:pos]))
                r.metadata['noskipline'] = True
                return r, pos

        if _blank.match(line) and prev_blank:
            return new_markdown_cell(
                source='\n'.join(lines[:(pos - 1)])), pos + 1
        prev_blank = _blank.match(line)

    # Unterminated cell?
    if prev_blank:
        return new_markdown_cell(source='\n'.join(lines[:-1])), len(lines)
    else:
        r = new_markdown_cell(source='\n'.join(lines))
        r.metadata['noskipline'] = True
        return r, len(lines)
