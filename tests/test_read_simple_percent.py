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

# %%% sub-cell title
# This is a sub-cell

# %%%% sub-sub-cell title
# This is a sub-sub-cell

# %% And now a code cell
1 + 2 + 3 + 4
5
6
# %%magic # this is a commented magic, not a cell

7
"""):
    nb = jupytext.reads(script, ext='.py', format_name='percent')
    assert len(nb.cells) == 6
    assert nb.cells[0].cell_type == 'raw'
    assert nb.cells[0].source == '---\ntitle: Simple file\n---'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[1].source == 'This is a markdown cell'
    assert nb.cells[2].cell_type == 'raw'
    assert nb.cells[2].source == 'This is a raw cell'
    assert nb.cells[3].cell_type == 'code'
    assert nb.cells[3].source == '# This is a sub-cell'
    assert nb.cells[3].metadata['title'] == 'sub-cell title'
    assert nb.cells[4].cell_type == 'code'
    assert nb.cells[4].source == '# This is a sub-sub-cell'
    assert nb.cells[4].metadata['title'] == 'sub-sub-cell title'
    assert nb.cells[5].cell_type == 'code'
    compare(nb.cells[5].source, '''1 + 2 + 3 + 4
5
6
# %%magic # this is a commented magic, not a cell

7''')
    assert nb.cells[5].metadata == {'title': 'And now a code cell'}

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


def test_read_remove_blank_lines(script="""# %%
import pandas as pd

# %% Display a data frame
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df

# %% Pandas plot {"tags": ["parameters"]}
df.plot(kind='bar')


# %% sample class
class MyClass:
    pass


# %% a function
def f(x):
    return 42 * x

"""):
    nb = jupytext.reads(script, ext='.py')
    assert len(nb.cells) == 5
    for i in range(5):
        assert nb.cells[i].cell_type == 'code'
        assert not nb.cells[i].source.startswith('\n')
        assert not nb.cells[i].source.endswith('\n')

    script2 = jupytext.writes(nb, ext='.py', format_name='percent')
    compare(script, script2)


def test_no_crash_on_square_bracket(script="""# %% In [2]
print('Hello')
"""):
    nb = jupytext.reads(script, ext='.py')
    script2 = jupytext.writes(nb, ext='.py', format_name='percent')
    compare(script, script2)
