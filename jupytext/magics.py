"""Escape Jupyter magics when converting to other formats"""

import re
from .stringparser import StringParser
from .languages import _SCRIPT_EXTENSIONS, _COMMENT

# A magic expression is a line or cell or metakernel magic (#94, #61) escaped zero, or multiple times
_MAGIC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*(%|%%|%%%)[a-zA-Z]".format(_SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_MAGIC_FORCE_ESC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*(%|%%|%%%)[a-zA-Z](.*){0}\s*escape".format(
        _SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_MAGIC_NOT_ESC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*(%|%%|%%%)[a-zA-Z](.*){0}\s*noescape".format(
        _SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_LINE_CONTINUATION_RE = re.compile(r'.*\\\s*$')

# Commands starting with a question or exclamation mark have to be escaped
_PYTHON_HELP_OR_BASH_CMD = re.compile(r"^(# |#)*(\?|!)\s*[A-Za-z]")

_PYTHON_MAGIC_CMD = re.compile(r"^(# |#)*({})(\s|$)".format('|'.join(
    # posix
    ['cat', 'cp', 'mv', 'rm', 'rmdir', 'mkdir'] +
    # windows
    ['copy', 'ddir', 'echo', 'ls', 'ldir', 'mkdir', 'ren', 'rmdir'])))


def is_magic(line, language, global_escape_flag=True):
    """Is the current line a (possibly escaped) Jupyter magic, and should it be commented?"""
    if language in ['octave', 'matlab']:
        return False
    if _MAGIC_FORCE_ESC_RE.get(language, _MAGIC_FORCE_ESC_RE['python']).match(line):
        return True
    if not global_escape_flag or _MAGIC_NOT_ESC_RE.get(language, _MAGIC_NOT_ESC_RE['python']).match(line):
        return False
    if _MAGIC_RE.get(language, _MAGIC_RE['python']).match(line):
        return True
    if language != 'python':
        return False
    if _PYTHON_HELP_OR_BASH_CMD.match(line):
        return True
    return _PYTHON_MAGIC_CMD.match(line)


def comment_magic(source, language='python', global_escape_flag=True):
    """Escape Jupyter magics with '# '"""
    parser = StringParser(language)
    next_is_magic = False
    for pos, line in enumerate(source):
        if not parser.is_quoted() and (next_is_magic or is_magic(line, language, global_escape_flag)):
            source[pos] = _COMMENT[language] + ' ' + line
            next_is_magic = language == 'python' and _LINE_CONTINUATION_RE.match(line)
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
    next_is_magic = False
    for pos, line in enumerate(source):
        if not parser.is_quoted() and (next_is_magic or is_magic(line, language, global_escape_flag)):
            source[pos] = unesc(line, language)
            next_is_magic = language == 'python' and _LINE_CONTINUATION_RE.match(line)
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
