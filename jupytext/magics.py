"""Escape Jupyter magics when converting to other formats"""

import re
from .stringparser import StringParser
from .languages import _SCRIPT_EXTENSIONS

# A magic expression is a line or cell or metakernel magic (#94, #61) escaped zero, or multiple times
_MAGIC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*(%|%%|%%%)[a-zA-Z]".format(_SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_MAGIC_FORCE_ESC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*(%|%%|%%%)[a-zA-Z](.*){0}\s*escape".format(
        _SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_MAGIC_NOT_ESC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*(%|%%|%%%)[a-zA-Z](.*){0}\s*noescape".format(
        _SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_COMMENT = {_SCRIPT_EXTENSIONS[ext]['language']: _SCRIPT_EXTENSIONS[ext]['comment'] for ext in _SCRIPT_EXTENSIONS}

# Commands starting with a question marks have to be escaped
_HELP_RE = re.compile(r"^(# |#)*\?")


def is_magic(line, language, global_escape_flag=True):
    """Is the current line a (possibly escaped) Jupyter magic, and should it be commented?"""
    if _MAGIC_FORCE_ESC_RE.get(language, _MAGIC_FORCE_ESC_RE['python']).match(line):
        return True
    if _MAGIC_NOT_ESC_RE.get(language, _MAGIC_NOT_ESC_RE['python']).match(line):
        return False
    if not global_escape_flag:
        return False
    if _MAGIC_RE.get(language, _MAGIC_RE['python']).match(line):
        return True
    if language == 'python':
        return _HELP_RE.match(line)
    return False


def comment_magic(source, language='python', global_escape_flag=True):
    """Escape Jupyter magics with '# '"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_magic(line, language, global_escape_flag):
            source[pos] = _COMMENT[language] + ' ' + line
        parser.read_line(line)
    return source


def unesc(line, language):
    """Uncomment once a commented line"""
    comment = _COMMENT[language]
    if line.startswith(comment + ' '):
        return line[len(comment) + 1:]
    if line.startswith(comment):
        return line[len(comment):]
    return line


def uncomment_magic(source, language='python', global_escape_flag=True):
    """Unescape Jupyter magics"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_magic(line, language, global_escape_flag):
            source[pos] = unesc(line, language)
        parser.read_line(line)
    return source


_ESCAPED_CODE_START = {'.Rmd': re.compile(r"^(# |#)*```{.*}"),
                       '.md': re.compile(r"^(# |#)*```")}
_ESCAPED_CODE_START.update({ext: re.compile(
    r"^({0} |{0})*({0}|{0} )\+".format(_SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS})


def is_escaped_code_start(line, ext):
    """Is the current line a possibly commented code start marker?"""
    return _ESCAPED_CODE_START[ext].match(line)


def escape_code_start(source, ext, language='python'):
    """Escape code start with '# '"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_escaped_code_start(line, ext):
            source[pos] = _SCRIPT_EXTENSIONS.get(ext, {}).get('comment', '#') + ' ' + line
        parser.read_line(line)
    return source


def unescape_code_start(source, ext, language='python'):
    """Unescape code start"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_escaped_code_start(line, ext):
            unescaped = unesc(line, language)
            # don't remove comment char if we break the code start...
            if is_escaped_code_start(unescaped, ext):
                source[pos] = unescaped
        parser.read_line(line)
    return source
