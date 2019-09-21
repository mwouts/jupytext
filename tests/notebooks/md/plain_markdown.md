---
title: A sample document
---

This document is a plain Markdown document that was not created from a notebook.
We use this document to test that inputing a Markdown file into Jupytext, and then converting the
resulting notebook to a Markdown file using nbconvert, is the identity

Another paragraph

# A header

Indented code

    def f(x):
        return 1


    def h(x):
        return f(x)+2


A Python code snippet

```python
"""This code cell starts with ` ```python`"""
1 + 1
```

Code snippet without an explicit language
```
echo 'Hello world'
```

Markdown comments
<!-- #comment -->

VS Code region markers

<!-- #region -->
This Markdown cell has two consecutive blank lines


And continues here
<!-- #endregion -->
