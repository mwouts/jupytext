# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Part one - various cells

# %% [markdown]
# Here we have a markdown cell
#
#
# with two blank lines

# %% [markdown]
# Now we have a markdown cell
# with a code block inside it
#
# ```python
# 1 + 1
# ```
#
# After that cell we'll have a code cell

# %%
2 + 2


3 + 3

# %% [markdown]
# Followed by a raw cell

# %% [raw]
# This is 
# the content
# of the raw cell

# %% [markdown]
# # Part two - cell metadata

# %% [markdown] key="value"
# This is a markdown cell with cell metadata `{"key": "value"}`

# %% .class tags=["parameters"]
"""This is a code cell with metadata `{"tags":["parameters"], ".class":null}`"""

# %% [raw] key="value"
# This is a raw cell with cell metadata `{"key": "value"}`
