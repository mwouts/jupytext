# -*- coding: utf-8 -*-

import nbrmd
from testfixtures import compare

nbrmd.file_format_version.FILE_FORMAT_VERSION = {}


def test_read_simple_file(rnb="""#' ---
#' title: Simple file
#' ---

#' Here we have some text
#' And below we have some R code

f <- function(x) {
    x + 1
    }


h <- function(y)
    y + 1
"""):
    nb = nbrmd.reads(rnb, ext='.R')
    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'Here we have some text\n' \
                                 'And below we have some R code'
    assert nb.cells[2].cell_type == 'code'
    compare(nb.cells[2].source, '''f <- function(x) {
    x + 1
    }''')
    assert nb.cells[3].cell_type == 'code'
    compare(nb.cells[3].source, '''h <- function(y)
    y + 1''')

    rnb2 = nbrmd.writes(nb, ext='.R')
    compare(rnb, rnb2)


def test_read_less_simple_file(rnb="""#' ---
#' title: Less simple file
#' ---

#' Here we have some text
#' And below we have some R code

# This is a comment about function f
def f(x):
    return x+1


# And a comment on h
def h(y):
    return y-1
"""):
    nb = nbrmd.reads(rnb, ext='.R')

    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Less simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'Here we have some text\n' \
                                 'And below we have some R code'
    assert nb.cells[2].cell_type == 'code'
    compare(nb.cells[2].source,
            """# This is a comment about function f
def f(x):
    return x+1""")
    assert nb.cells[3].cell_type == 'code'
    compare(nb.cells[3].source,
            '''# And a comment on h
def h(y):
    return y-1''')

    rnb2 = nbrmd.writes(nb, ext='.R')
    compare(rnb, rnb2)


def test_no_space_after_code(rnb=u"""# -*- coding: utf-8 -*-
#' Markdown cell

f <- function(x)
{
    return(x+1)
}

#' And a new cell, and non ascii contênt
"""):
    nb = nbrmd.reads(rnb, ext='.R')

    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[0].source == 'Markdown cell'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == """f <- function(x)
{
    return(x+1)
}"""
    assert nb.cells[2].cell_type == 'markdown'
    assert nb.cells[2].source == u'And a new cell, and non ascii contênt'

    rnb2 = nbrmd.writes(nb, ext='.R')
    compare(rnb, rnb2)


def test_read_write_script(rnb="""#!/usr/bin/env Rscript
# coding=utf-8
print('Hello world')
"""):
    nb = nbrmd.reads(rnb, ext='.R')
    rnb2 = nbrmd.writes(nb, ext='.R')
    compare(rnb, rnb2)
