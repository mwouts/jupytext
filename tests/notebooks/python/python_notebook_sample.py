# # Specifications for Jupyter notebooks as python scripts

# ## Markdown cells

# Markdown cells are escaped with a single quote. Two consecutive
# cells are separated with a blank line.

# ## Code cells

# Python code and adjacent comments are mapped to cell codes.

# For instance, this is a code cell that starts with a
# code comment, where we define a variable
a = 1

# A cell with another variable
b = 2


# In this cell we define a function
def f(x):
    return x + 1


# Now simple function calls
c = f(b)
a * b + c


# Line breaks in code cells are supported but then the cell need to have
# metadata and an end-of-cell marker. Metadata information in json format,
# escaped with '#+' or '# +'

# +
def g(x):
    return x + 2


d = 4
# -

# One more cell
a * b + g(c) + d

# ## Raw cells, and cells active in py or ipynb only

# Raw cells are commented code cells with metadata "active": "".

# + {"active": ""}
# This is a raw cell
# -

# Actually, using the "active" key you can have cells active in Jupyter
# and inactive in python scripts

# + {"active": "py"}
1 + 1  # done only in py script, inactive (raw) in ipynb

# + {"active": "ipynb"}
# 2 + 2 # active in ipynb only
