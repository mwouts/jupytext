# -*- coding: utf-8 -*-

import jupytext
from testfixtures import compare
from .python_notebook_sample import f, g

jupytext.file_format_version.FILE_FORMAT_VERSION = {}


def test_python_notebook_sample():
    assert f(1) == 2
    assert g(2) == 4


def test_read_simple_file(pynb="""# ---
# title: Simple file
# ---

# Here we have some text
# And below we have some python code

def f(x):
    return x+1


def h(y):
    return y-1
"""):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'Here we have some text\n' \
                                 'And below we have some python code'
    assert nb.cells[2].cell_type == 'code'
    compare(nb.cells[2].source, '''def f(x):
    return x+1''')
    assert nb.cells[3].cell_type == 'code'
    compare(nb.cells[3].source, '''def h(y):
    return y-1''')

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_less_simple_file(pynb="""# ---
# title: Less simple file
# ---

# Here we have some text
# And below we have some python code

# This is a comment about function f
def f(x):
    return x+1


# And a comment on h
def h(y):
    return y-1
"""):
    nb = jupytext.reads(pynb, ext='.py')

    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Less simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'Here we have some text\n' \
                                 'And below we have some python code'
    assert nb.cells[2].cell_type == 'code'
    compare(nb.cells[2].source,
            '# This is a comment about function f\n'
            'def f(x):\n'
            '    return x+1')
    assert nb.cells[3].cell_type == 'code'
    compare(nb.cells[3].source,
            '''# And a comment on h\ndef h(y):\n    return y-1''')

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_non_pep8_file(pynb="""# ---
# title: Non-pep8 file
# ---

# This file is non-pep8 as the function below has
# two consecutive blank lines in its body

def f(x):


    return x+1
"""):
    nb = jupytext.reads(pynb, ext='.py')

    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Non-pep8 file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'This file is non-pep8 as ' \
                                 'the function below has\n' \
                                 'two consecutive blank lines ' \
                                 'in its body'
    assert nb.cells[2].cell_type == 'code'
    compare(nb.cells[2].source,
            'def f(x):\n\n\n'
            '    return x+1')

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_cell_two_blank_lines(pynb="""# ---
# title: cell with two consecutive blank lines
# ---

# + {}
a = 1


a + 2
"""):
    nb = jupytext.reads(pynb, ext='.py')

    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: cell with two ' \
                                 'consecutive blank lines\n---'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == 'a = 1\n\n\na + 2'

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_cell_explicit_start(pynb='''
import pandas as pd
# + {}
def data():
    return pd.DataFrame({'A': [0, 1]})


data()
'''):
    nb = jupytext.reads(pynb, ext='.py')
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_complex_cells(pynb='''import pandas as pd

# + {}
def data():
    return pd.DataFrame({'A': [0, 1]})


data()

# + {}
def data2():
    return pd.DataFrame({'B': [0, 1]})


data2()

# + {}
# Finally we have a cell with only comments
# This cell should remain a code cell and not get converted
# to markdown

# + {"endofcell": "--"}
# This cell has an enumeration in it that should not
# match the endofcell marker!
# - item 1
# - item 2
# -
# --
'''):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 5
    assert nb.cells[0].cell_type == 'code'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[2].cell_type == 'code'
    assert nb.cells[3].cell_type == 'code'
    assert nb.cells[4].cell_type == 'code'
    assert (nb.cells[3].source ==
            '''# Finally we have a cell with only comments
# This cell should remain a code cell and not get converted
# to markdown''')
    assert (nb.cells[4].source ==
            '''# This cell has an enumeration in it that should not
# match the endofcell marker!
# - item 1
# - item 2
# -''')

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_prev_function(
        pynb="""def test_read_cell_explicit_start_end(pynb='''
import pandas as pd
# + {}
def data():
    return pd.DataFrame({'A': [0, 1]})


data()
'''):
    nb = jupytext.reads(pynb, ext='.py')
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)
"""):
    nb = jupytext.reads(pynb, ext='.py')
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_cell_with_one_blank_line_end(pynb="""import pandas

"""):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 1
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_code_cell_fully_commented(pynb="""# + {}
# This is a code cell that
# only contains comments
"""):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == 'code'
    assert nb.cells[0].source == """# This is a code cell that
# only contains comments"""
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_file_with_two_blank_line_end(pynb="""import pandas


"""):
    nb = jupytext.reads(pynb, ext='.py')
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_one_blank_lines_after_endofcell(pynb="""# + {}
# This is a code cell with explicit end of cell
1 + 1

2 + 2
# -

# This cell is a cell with implicit start
1 + 1
"""):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'code'
    assert (nb.cells[0].source ==
            '''# This is a code cell with explicit end of cell
1 + 1

2 + 2''')
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == '''# This cell is a cell with implicit start
1 + 1'''
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_two_cells_with_explicit_start(pynb="""# + {}
# Cell one
1 + 1

1 + 1

# + {}
# Cell two
2 + 2

2 + 2
"""):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'code'
    assert nb.cells[0].source == '''# Cell one
1 + 1

1 + 1'''
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == '''# Cell two
2 + 2

2 + 2'''
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_escape_start_pattern(pynb="""# The code start pattern '# + {}' can
# appear in code and markdown cells.

# In markdown cells it is escaped like here:
# # + {"sample_metadata": "value"}

# In code cells like this one, it is also escaped
# # + {"sample_metadata": "value"}
1 + 1
"""):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[2].cell_type == 'code'
    assert nb.cells[1].source == '''In markdown cells it is escaped like here:
# + {"sample_metadata": "value"}'''
    assert (nb.cells[2].source ==
            '''# In code cells like this one, it is also escaped
# + {"sample_metadata": "value"}
1 + 1''')
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_dictionary_with_blank_lines_not_broken(
        pynb="""# This is a markdown cell, and below
# we have a long dictionary with blank lines
# inside it

dictionary = {
    'a': 'A',
    'b': 'B',

    # and the end
    'z': 'Z'}
"""):
    nb = jupytext.reads(pynb, ext='.py')
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[0].source == '''This is a markdown cell, and below
we have a long dictionary with blank lines
inside it'''
    assert nb.cells[1].source == '''dictionary = {
    'a': 'A',
    'b': 'B',

    # and the end
    'z': 'Z'}'''
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_isolated_cell_with_magic(pynb="""# ---
# title: cell with isolated jupyter magic
# ---

# A magic command included in a markdown
# paragraph is code
#
# %matplotlib inline

# a code block may start with
# a magic command, like this one:

# %matplotlib inline

# or that one

# %matplotlib inline
1 + 1
"""):
    nb = jupytext.reads(pynb, ext='.py')

    assert len(nb.cells) == 6
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: cell with isolated jupyter ' \
                                 'magic\n---'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[2].cell_type == 'markdown'
    assert nb.cells[3].cell_type == 'code'
    assert nb.cells[3].source == '%matplotlib inline'
    assert nb.cells[4].cell_type == 'markdown'
    assert nb.cells[5].cell_type == 'code'
    assert nb.cells[5].source == '%matplotlib inline\n1 + 1'

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_multiline_comment(pynb="""'''This is a multiline
comment with "quotes", 'single quotes'
# and comments
and line breaks


and it ends here'''


1 + 1
"""):
    nb = jupytext.reads(pynb, ext='.py')

    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'code'
    assert nb.cells[0].source == """'''This is a multiline
comment with "quotes", 'single quotes'
# and comments
and line breaks


and it ends here'''"""
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == '1 + 1'

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_no_space_after_code(pynb=u"""# -*- coding: utf-8 -*-
# Markdown cell

def f(x):
    return x+1

# And a new cell, and non ascii contênt
"""):
    nb = jupytext.reads(pynb, ext='.py')

    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[0].source == 'Markdown cell'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == 'def f(x):\n    return x+1'
    assert nb.cells[2].cell_type == 'markdown'
    assert nb.cells[2].source == u'And a new cell, and non ascii contênt'

    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_read_write_script(pynb="""#!/usr/bin/env python
# coding=utf-8
print('Hello world')
"""):
    nb = jupytext.reads(pynb, ext='.py')
    pynb2 = jupytext.writes(nb, ext='.py')
    compare(pynb, pynb2)


def test_notebook_blank_lines(script="""# + {}
# This is a comment
# followed by two variables
a = 3

b = 4
# -

# New cell is a variable
c = 5


# + {}
# Now we have two functions
def f(x):
    return x + x


def g(x):
    return x + x + x


# -


# A commented block that is two lines away
# from previous cell

# A function again
def h(x):
    return x + 1


# variable
d = 6
"""):
    notebook = jupytext.reads(script, ext='.py')
    assert len(notebook.cells) >= 6
    for cell in notebook.cells:
        lines = cell.source.splitlines()
        if len(lines) != 1:
            assert lines[0]
            assert lines[-1]

    script2 = jupytext.writes(notebook, ext='.py')

    compare(script, script2)
