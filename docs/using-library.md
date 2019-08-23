# Using the Jupytext Python library

Jupytext provides the same `read`, `write`, `reads` and `writes` functions as `nbformat`.
You can use `jupytext`'s functions as drop-in replacements for `nbformat`'s ones.

## Reading notebooks from many text formats

To read text files as notebooks, simply provide the path to a Jupytext-supported
format.
```python
import jupytext

# Read a notebook from a file 
ntbk = jupytext.read('notebook.md')

# Read a notebook from a string
jupytext.reads(text, fmt='md')
```

Jupytext will read in the content and infer metadata about the file
from the YAML header (if there is one). If there is no Jupytext header,
then Jupytext will make some assumptions about the format based on the
file extension.

This function returns an instance of an `nbformat` `NotebookNode`. You
can find more information for working with this notebook representation
in the [nbformat documentation](https://nbformat.readthedocs.io).

## Writing notebooks to many text files

You can also write in-memory notebooks to a variety of text formats by
using `jupytext.write`.

Jupytext's implementation provides an additional `fmt` argument,
which can be any of the accepted Jupytext extensions (e.g., `py`, `md`, `jl:percent`)
If not explicitly provided, the argument is inferred from the file extension.

```python
# Return the text representation of a notebook
jupytext.writes(notebook, fmt='py:percent')

# Write a notebook to a file in the desired format
jupytext.write(notebook, 'notebook.py')
jupytext.write(notebook, 'notebook.py', fmt='py:percent')
```
