# -*- coding: utf-8 -*-

import nbrmd
from testfixtures import compare


def test_read_simple_file(py="""# ---
# title: Simple file
# ---

# Here we have some text
# And below we have a some python code

def f(x):
    return x+1


def h(y):
    return y-1
"""):
    nb = nbrmd.reads(py, ext='.py')
    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'Here we have some text\n' \
                                 'And below we have a some python code'
    assert nb.cells[2].cell_type == 'code'
    compare(nb.cells[2].source, '''def f(x):
    return x+1''')
    assert nb.cells[3].cell_type == 'code'
    compare(nb.cells[3].source, '''def h(y):
    return y-1''')

    py2 = nbrmd.writes(nb, ext='.py')
    compare(py, py2)


def test_read_less_simple_file(py="""# ---
# title: Less simple file
# ---

# Here we have some text
# And below we have a some python code

# This is a comment about function f
def f(x):
    return x+1


# And a comment on h
def h(y):
    return y-1
"""):
    nb = nbrmd.reads(py, ext='.py')

    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Less simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'Here we have some text\n' \
                                 'And below we have a some python code'
    assert nb.cells[2].cell_type == 'code'
    compare(nb.cells[2].source,
            '# This is a comment about function f\n'
            'def f(x):\n'
            '    return x+1')
    assert nb.cells[3].cell_type == 'code'
    compare(nb.cells[3].source,
            '''# And a comment on h\ndef h(y):\n    return y-1''')

    py2 = nbrmd.writes(nb, ext='.py')
    compare(py, py2)


def test_no_space_after_code(py=u"""# -*- coding: utf-8 -*-
# Markdown cell

def f(x):
    return x+1

# And a new cell, and non ascii contênt
"""):
    nb = nbrmd.reads(py, ext='.py')

    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[0].source == 'Markdown cell'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == 'def f(x):\n    return x+1'
    assert nb.cells[2].cell_type == 'markdown'
    assert nb.cells[2].source == u'And a new cell, and non ascii contênt'

    py2 = nbrmd.writes(nb, ext='.py')
    compare(py, py2)


def test_read_write_script(py="""#!/usr/bin/env python
# coding=utf-8
print('Hello world')
"""):
    nb = nbrmd.reads(py, ext='.py')
    py2 = nbrmd.writes(nb, ext='.py')
    compare(py, py2)
