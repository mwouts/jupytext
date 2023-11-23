# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Part one - various cells

# Here we have a markdown cell
#
#
# with two blank lines

# Now we have a markdown cell
# with a code block inside it
#
# ```python
# 1 + 1
# ```
#
# After that cell we'll have a code cell

# +
2 + 2


3 + 3
# -

# Followed by a raw cell

# + active=""
# This is 
# the content
# of the raw cell
# -

# # Part two - cell metadata

# + [markdown] key="value"
# This is a markdown cell with cell metadata `{"key": "value"}`

# + .class tags=["parameters"]
"""This is a code cell with metadata `{"tags":["parameters"], ".class":null}`"""

# + key="value" active=""
# This is a raw cell with cell metadata `{"key": "value"}`
