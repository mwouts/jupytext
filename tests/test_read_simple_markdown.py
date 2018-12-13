from testfixtures import compare
import jupytext


def test_read_mostly_py_markdown_file(markdown="""---
title: Simple file
---

```python
import numpy as np
x = np.arange(0, 2*math.pi, eps)
```

```python
x = np.arange(0,1,eps)
y = np.abs(x)-.5
```

```
# this is a raw cell
```

```R
ls()
```

```R
cat(stringi::stri_rand_lipsum(3), sep='\n\n')
```
"""):
    nb = jupytext.reads(markdown, ext='.md')
    assert nb.metadata['jupytext']['main_language'] == 'python'
    compare(nb.cells, [{'cell_type': 'raw',
                        'source': '---\ntitle: Simple file\n---',
                        'metadata': {}},
                       {'cell_type': 'code',
                        'metadata': {},
                        'execution_count': None,
                        'source': 'import numpy as np\n'
                                  'x = np.arange(0, 2*math.pi, eps)',
                        'outputs': []},
                       {'cell_type': 'code',
                        'metadata': {},
                        'execution_count': None,
                        'source': 'x = np.arange(0,1,eps)\ny = np.abs(x)-.5',
                        'outputs': []},
                       {'cell_type': 'raw',
                        'metadata': {},
                        'source': '# this is a raw cell'},
                       {'cell_type': 'code',
                        'metadata': {},
                        'execution_count': None,
                        'source': '%%R\nls()',
                        'outputs': []},
                       {'cell_type': 'code',
                        'metadata': {},
                        'execution_count': None,
                        'source': "%%R\ncat(stringi::"
                                  "stri_rand_lipsum(3), sep='\n\n')",
                        'outputs': []}])

    markdown2 = jupytext.writes(nb, ext='.md')
    compare(markdown, markdown2)


def test_escape_start_pattern(markdown="""The code start pattern '```{}' can
appear in code and markdown cells.


In markdown cells it is escaped like here:
# ```r

```python sample_python_cell
# In code cells like this one, it is also escaped
# ```python cell_name
1 + 1
%matplotlib inline
```
"""):
    nb = jupytext.reads(markdown, ext='.md')
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[1].cell_type == 'markdown'
    assert nb.cells[2].cell_type == 'code'
    assert nb.cells[1].source == '''In markdown cells it is escaped like here:
```r'''
    assert (nb.cells[2].source ==
            '''# In code cells like this one, it is also escaped
```python cell_name
1 + 1
%matplotlib inline''')
    markdown2 = jupytext.writes(nb, ext='.md')
    compare(markdown, markdown2)


def test_read_julia_notebook(markdown="""```julia
1 + 1
```
"""):
    nb = jupytext.reads(markdown, ext='.md')
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == 'code'
    markdown2 = jupytext.writes(nb, ext='.md')
    compare(markdown, markdown2)
