# -*- coding: utf-8 -*-

from jupytext.compare import compare
import jupytext


def test_read_simple_file(
    script='''# -*- coding: utf-8 -*-
"""
This is a markdown cell
"""

1 + 2 + 3 + 4
5
6

""
7

#################################
# Another markdown cell

def f(x):
   """Sample docstring"""
   return 4
''',
):
    nb = jupytext.reads(script, "py:sphinx")
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "%matplotlib inline"

    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[1].source == "This is a markdown cell"

    assert nb.cells[2].cell_type == "code"
    compare(
        nb.cells[2].source,
        """1 + 2 + 3 + 4
5
6""",
    )

    assert nb.cells[3].cell_type == "code"
    assert nb.cells[3].source == "7"

    assert nb.cells[4].cell_type == "markdown"
    assert nb.cells[4].source == "Another markdown cell"

    assert nb.cells[5].cell_type == "code"
    assert (
        nb.cells[5].source
        == '''def f(x):
   """Sample docstring"""
   return 4'''
    )
    assert len(nb.cells) == 6

    script2 = jupytext.writes(nb, "py:sphinx")
    compare(script2, script)


def test_read_more_complex_file(
    script="""'''This is a markdown cell'''

1 + 2 + 3 + 4
5
6

'''
Another markdown cell'''
#################################
# A third one

'''
Another markdown cell'''
1 + 2 + 3 + 4

# ################################
# A fifth one

'''And a last one
'''
""",
):
    nb = jupytext.reads(script, "py:sphinx")

    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "%matplotlib inline"

    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[1].source == "This is a markdown cell"

    assert nb.cells[2].cell_type == "code"
    compare(
        nb.cells[2].source,
        """1 + 2 + 3 + 4
5
6""",
    )
    assert nb.cells[3].cell_type == "markdown"
    assert nb.cells[3].source == "Another markdown cell"

    assert nb.cells[4].cell_type == "markdown"
    assert nb.cells[4].source == "A third one"

    assert nb.cells[5].cell_type == "markdown"
    assert nb.cells[5].source == "Another markdown cell"

    assert nb.cells[6].cell_type == "code"
    assert nb.cells[6].source == "1 + 2 + 3 + 4"

    assert nb.cells[7].cell_type == "markdown"
    assert nb.cells[7].source == "A fifth one"

    assert nb.cells[8].cell_type == "markdown"
    assert nb.cells[8].source == "And a last one"

    assert len(nb.cells) == 9


def test_read_empty_code_cell(
    script='''"""
Markdown cell
"""


''',
):
    nb = jupytext.reads(script, "py:sphinx")

    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "%matplotlib inline"

    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[1].source == "Markdown cell"

    assert nb.cells[2].cell_type == "code"
    assert nb.cells[2].source == ""

    assert len(nb.cells) == 3

    assert jupytext.writes(nb, "py:sphinx") == script
