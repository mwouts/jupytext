"""Escape Jupyter magics when converting to other formats"""

import re

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

# A magic expression is a line or cell magic escaped zero, or multiple times
_PERCENT_RE = re.compile(r"^(# |#)*%")
_FORCE_ESC_RE = re.compile(r"^(# |#)*%(.*)(#| )escape")
_FORCE_NOT_ESC_RE = re.compile(r"^(# |#)*%(.*)noescape")
_MAGIC_RE = re.compile(r"^(# |#)*(%%|{})".format('|'.join(_LINE_MAGICS)))


def escape_magic(source):
    """Escape Jupyter magics with '# '"""
    return ['# ' + s if _FORCE_ESC_RE.match(s) or
                        (not _FORCE_NOT_ESC_RE.match(s) and _MAGIC_RE.match(s))
            else s for s in source]


def unesc(line):
    """Uncomment once a commented line"""
    if line.startswith('# '):
        return line[2:]
    elif line.startswith('#'):
        return line[1:]
    else:
        return line


def unescape_magic(source):
    """Unescape Jupyter magics"""
    return [unesc(s) if _FORCE_ESC_RE.match(s) or
                        (not _FORCE_NOT_ESC_RE.match(s) and _MAGIC_RE.match(s))
            else s for s in source]
