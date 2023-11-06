# ---
# jupyter:
#   jupytext:
#     cell_markers: region,endregion
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

# region
2 + 2


3 + 3
# endregion

# Followed by a raw cell

# region active=""
# This is 
# the content
# of the raw cell
# endregion

# # Part two - cell metadata

# region [markdown] key="value"
# This is a markdown cell with cell metadata `{"key": "value"}`
# endregion

# region .class tags=["parameters"]
"""This is a code cell with metadata `{"tags":["parameters"], ".class":null}`"""
# endregion

# region key="value" active=""
# This is a raw cell with cell metadata `{"key": "value"}`
# endregion
