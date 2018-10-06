"""Escape Jupyter magics when converting to other formats"""

import re
from .stringparser import StringParser
from .languages import _SCRIPT_EXTENSIONS

# Line magics retrieved manually (Aug 18) with %lsmagic
_LINE_MAGICS = '%alias  %alias_magic  %autocall  %automagic  %autosave  ' \
               '%bookmark  %cd  %clear  %cls  %colors  %config  ' \
               '%connect_info  %copy  %ddir  %debug  %dhist  %dirs  ' \
               '%doctest_mode  %echo  %ed  %edit  %env  %gui  %hist  ' \
               '%history  %killbgscripts  %ldir  %less  %load  %load_ext  ' \
               '%loadpy  %logoff  %logon  %logstart  %logstate  %logstop  ' \
               '%ls  %lsmagic  %macro  %magic  %matplotlib  %mkdir  %more  ' \
               '%notebook  %page  %pastebin  %pdb  %pdef  %pdoc  %pfile  ' \
               '%pinfo  %pinfo2  %popd  %pprint  %precision  %profile  ' \
               '%prun  %psearch  %psource  %pushd  %pwd  %pycat  %pylab  ' \
               '%qtconsole  %quickref  %recall  %rehashx  %reload_ext  ' \
               '%ren  %rep  %rerun  %reset  %reset_selective  %rmdir  %run  ' \
               '%save  %sc  %set_env  %store  %sx  %system  %tb  %time  ' \
               '%timeit  %unalias  %unload_ext  %who  %who_ls  %whos  ' \
               '%xdel  %xmode'.split('  ')

# Add classical line magics
_LINE_MAGICS += ('%autoreload %aimport '  # autoreload
                 '%R %Rpush %Rpull %Rget '  # rmagic
                 '%store '  # storemagic
                 ).split(' ')

# Remove any blank line
_LINE_MAGICS = [magic for magic in _LINE_MAGICS if magic.startswith('%')]

# A magic expression is a line or cell magic escaped zero, or multiple times
_FORCE_ESC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*%(.*)({0}| )escape".format(_SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_FORCE_NOT_ESC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*%(.*)({0}| )noescape".format(_SCRIPT_EXTENSIONS[ext]['comment'])) for ext in _SCRIPT_EXTENSIONS}
_MAGIC_RE = {_SCRIPT_EXTENSIONS[ext]['language']: re.compile(
    r"^({0} |{0})*(%%[a-zA-Z]|{1})".format(
        _SCRIPT_EXTENSIONS[ext]['comment'], '|'.join(_LINE_MAGICS))) for ext in _SCRIPT_EXTENSIONS}
_COMMENT = {_SCRIPT_EXTENSIONS[ext]['language']: _SCRIPT_EXTENSIONS[ext]['comment'] for ext in _SCRIPT_EXTENSIONS}

# Commands starting with a question marks have to be escaped
_HELP_RE = re.compile(r"^(# |#)*\?")


def is_magic(line, language):
    """Is the current line a (possibly escaped) Jupyter magic?"""
    if _FORCE_ESC_RE.get(language, _FORCE_ESC_RE['python']).match(line):
        return True
    if not _FORCE_NOT_ESC_RE.get(language, _FORCE_ESC_RE['python']).match(line) and \
            _MAGIC_RE.get(language, _FORCE_ESC_RE['python']).match(line):
        return True
    if language == 'python':
        return _HELP_RE.match(line)
    return False


def comment_magic(source, language='python'):
    """Escape Jupyter magics with '# '"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_magic(line, language):
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


def uncomment_magic(source, language='python'):
    """Unescape Jupyter magics"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_magic(line, language):
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
