---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Part one - various cells

<!-- #region -->
Here we have a markdown cell


with two blank lines
<!-- #endregion -->

<!-- #region -->
Now we have a markdown cell
with a code block inside it

```python
1 + 1
```

After that cell we'll have a code cell
<!-- #endregion -->

```python
2 + 2


3 + 3
```

Followed by a raw cell

<!-- #raw -->
This is 
the content
of the raw cell
<!-- #endraw -->

# Part two - cell metadata

<!-- #region key="value" -->
This is a markdown cell with cell metadata `{"key": "value"}`
<!-- #endregion -->

```python .class tags=["parameters"]
"""This is a code cell with metadata `{"tags":["parameters"], ".class":null}`"""
```

<!-- #raw key="value" -->
This is a raw cell with cell metadata `{"key": "value"}`
<!-- #endraw -->
