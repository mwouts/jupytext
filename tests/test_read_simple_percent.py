# -*- coding: utf-8 -*-

from testfixtures import compare
import jupytext

jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER = False


def test_read_simple_file(script="""# ---
# title: Simple file
# ---

# %% [markdown]
# This is a markdown cell

# %% [raw]
# This is a raw cell

# %%%
# This is a sub-cell

# %% And now a code cell
1 + 2 + 3 + 4
5
6

7
"""):
    nb = jupytext.reads(script, ext='.py', format_name='percent')
    assert len(nb.cells) == 5
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'This is a markdown cell'
    assert nb.cells[2].cell_type == 'raw'
    assert nb.cells[2].source == 'This is a raw cell'
    assert nb.cells[3].cell_type == 'code'
    assert nb.cells[3].source == '# This is a sub-cell'
    assert nb.cells[4].cell_type == 'code'
    compare(nb.cells[4].source, '''1 + 2 + 3 + 4
5
6

7''')
    assert nb.cells[4].metadata == {'title': 'And now a code cell'}

    script2 = jupytext.writes(nb, ext='.py', format_name='percent')
    compare(script, script2)


def test_read_cell_with_metadata(
        script="""# %% a code cell with parameters {"tags": ["parameters"]}
a = 3
"""):
    nb = jupytext.reads(script, ext='.py', format_name='percent')
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == 'code'
    assert nb.cells[0].source == 'a = 3'
    assert nb.cells[0].metadata == {
        'title': 'a code cell with parameters',
        'tags': ['parameters']}

    script2 = jupytext.writes(nb, ext='.py', format_name='percent')
    compare(script, script2)


def test_read_nbconvert_script(script="""
# coding: utf-8

# A markdown cell

# In[1]:


import pandas as pd

pd.options.display.max_rows = 6
pd.options.display.max_columns = 20


# Another markdown cell

# In[2]:


1 + 1


# Again, a markdown cell

# In[33]:


2 + 2


# <codecell>


3 + 3
"""):
    assert jupytext.formats.guess_format(script, '.py') == 'percent'
    nb = jupytext.reads(script, '.py')
    assert len(nb.cells) == 5
