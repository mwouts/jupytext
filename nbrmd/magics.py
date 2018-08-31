"""Escape Jupyter magics when converting to other formats"""

import re
from .stringparser import StringParser

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
_FORCE_ESC_RE = re.compile(r"^(# |#)*%(.*)(#| )escape")
_FORCE_NOT_ESC_RE = re.compile(r"^(# |#)*%(.*)noescape")
_MAGIC_RE = re.compile(r"^(# |#)*(%%|{})".format('|'.join(_LINE_MAGICS)))


def is_magic(line):
    """Is the current line a (possibly escaped) Jupyter magic?"""
    return (_FORCE_ESC_RE.match(line) or (not _FORCE_NOT_ESC_RE.match(line)
                                          and _MAGIC_RE.match(line)))


def escape_magic(source, language='python'):
    """Escape Jupyter magics with '# '"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_magic(line):
            source[pos] = '# ' + line
        parser.read_line(line)
    return source


def unesc(line):
    """Uncomment once a commented line"""
    if line.startswith('# '):
        return line[2:]
    if line.startswith('#'):
        return line[1:]
    return line


def unescape_magic(source, language='python'):
    """Unescape Jupyter magics"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_magic(line):
            source[pos] = unesc(line)
        parser.read_line(line)
    return source


_ESCAPED_CODE_START = {'.R': re.compile(r"^(# |#)*#\+"),
                       '.Rmd': re.compile(r"^(# |#)*```{.*}"),
                       '.md': re.compile(r"^(# |#)*```"),
                       '.py': re.compile(r"^(# |#)*(#|# )\+(\s*){.*}")}


def is_escaped_code_start(line, ext):
    """Is the current line a possibly commented code start marker?"""
    return _ESCAPED_CODE_START[ext].match(line)


def escape_code_start(source, ext, language='python'):
    """Escape code start with '# '"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_escaped_code_start(line, ext):
            source[pos] = '# ' + line
        parser.read_line(line)
    return source


def unescape_code_start(source, ext, language='python'):
    """Unescape code start"""
    parser = StringParser(language)
    for pos, line in enumerate(source):
        if not parser.is_quoted() and is_escaped_code_start(line, ext):
            unescaped = unesc(line)
            # don't remove comment char if we break the code start...
            if is_escaped_code_start(unescaped, ext):
                source[pos] = unescaped
        parser.read_line(line)
    return source
