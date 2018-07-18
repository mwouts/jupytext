# # Specifications for Jupyter notebooks as python scripts

# ## Markdown (and raw) cells

# Markdown cells are escaped with a single quote. Two consecutive
# cells are separated with a blank line. Raw cells are not
# distinguished from markdown.

# ## Code cells

# Code cells are separated by one blank line from markdown cells.
# If a code cells follows a comment, then that comment belong to the
# code cell.

# For instance, this is a code cell that starts with a
# code comment, split on multiple lines
1 + 2

# Code cells are terminated with either
# - end of file
# - two blank lines if followed by an other code cell
# - one blank line if followed by a markdown cell

# Code cells can have blank lines, but no two consecutive blank lines (that's
# a cell break!). Below we have a cell with multiple instructions:

a = 3

a + 1

# ## Metadata in code cells

# In case a code cell has metadata information, it
# is represented in json format, escaped with '#+' or '# +'

# + {"scrolled": true}
a + 2
