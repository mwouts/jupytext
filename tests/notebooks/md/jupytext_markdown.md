---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Markdown, code and raw cells

## Markdown cells

This is a Markdown cell. Markdown cells end with either a code cell, or two consecutive blank lines in the text.

If you prefer that Markdown headings define new cells, have a look at the `split_at_heading` option.

Indented code is accepted, and consecutive blank lines there do not break Markdown cells:

    def f(x):
        return 1


    def h(x):
        return f(x)+2


## Code cells

```python
"""This code cell starts with ` ```python`"""
1 + 1
```

## Raw cells

Raw cells are delimited with `<!-- #raw -->` and <!-- #endraw -->, like here:
<!-- #raw -->
this is a raw cell
<!-- #endraw -->

# Protected Markdown cells

If you want to include code blocks (or two consecutive blank lines) in a Markdown cell, use explicit Markdown cell delimiters `<!-- #region -->` and `<!-- #endregion -->`.

<!-- #region -->
This Markdown cell has two consecutive blank lines


And then a code block which is not a Jupyter code cell:
```python
2 + 2
```
<!-- #endregion -->

# Metadata

Metadata are supported for all cell types.

## Markdown cells

<!-- #region Region title key="value" -->
A cell with a title and additional metadata.
<!-- #endregion -->

## Code cells

```python tags=["parameters"]
a = 2
```
