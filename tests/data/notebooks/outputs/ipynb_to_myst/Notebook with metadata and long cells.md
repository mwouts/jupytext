---
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Part one - various cells

+++

Here we have a markdown cell


with two blank lines

+++

Now we have a markdown cell
with a code block inside it

```python
1 + 1
```

After that cell we'll have a code cell

```{code-cell} ipython3
2 + 2


3 + 3
```

Followed by a raw cell

```{raw-cell}
This is 
the content
of the raw cell
```

# Part two - cell metadata

+++ {"key": "value"}

This is a markdown cell with cell metadata `{"key": "value"}`

```{code-cell} ipython3
---
.class: null
tags: [parameters]
---
"""This is a code cell with metadata `{"tags":["parameters"], ".class":null}`"""
```

```{raw-cell}
:key: value

This is a raw cell with cell metadata `{"key": "value"}`
```
