"""Issue #712"""
import pytest
from nbformat.v4.nbbase import new_code_cell, new_notebook

from jupytext import reads, writes
from jupytext.cell_to_text import three_backticks_or_more
from jupytext.compare import compare, compare_notebooks


def test_three_backticks_or_more():
    assert three_backticks_or_more([""]) == "```"
    assert three_backticks_or_more(["``"]) == "```"
    assert three_backticks_or_more(["```python"]) == "````"
    assert three_backticks_or_more(["```"]) == "````"
    assert three_backticks_or_more(["`````python"]) == "``````"
    assert three_backticks_or_more(["`````"]) == "``````"


def test_triple_backticks_in_code_cell(
    no_jupytext_version_number,
    nb=new_notebook(
        metadata={"main_language": "python"},
        cells=[
            new_code_cell(
                '''a = """
```
foo
```
"""'''
            )
        ],
    ),
    text='''---
jupyter:
  jupytext:
    main_language: python
---

````python
a = """
```
foo
```
"""
````
''',
):
    actual_text = writes(nb, fmt="md")
    compare(actual_text, text)

    actual_nb = reads(text, fmt="md")
    compare_notebooks(actual_nb, nb)


@pytest.mark.requires_myst
def test_triple_backticks_in_code_cell_myst(
    no_jupytext_version_number,
    nb=new_notebook(
        metadata={"jupytext": {"default_lexer": "ipython3"}},
        cells=[
            new_code_cell(
                '''a = """
```
foo
```
"""'''
            )
        ],
    ),
    text='''````{code-cell} ipython3
a = """
```
foo
```
"""
````
''',
):
    actual_text = writes(nb, fmt="md:myst")
    compare(actual_text, text)

    actual_nb = reads(text, fmt="md:myst")
    compare_notebooks(actual_nb, nb)


def test_alternate_tree_four_five_backticks(
    no_jupytext_version_number,
    nb=new_notebook(
        metadata={"main_language": "python"},
        cells=[
            new_code_cell('a = """\n```\n"""'),
            new_code_cell("b = 2"),
            new_code_cell('c = """\n````\n"""'),
        ],
    ),
    text='''---
jupyter:
  jupytext:
    main_language: python
---

````python
a = """
```
"""
````

```python
b = 2
```

`````python
c = """
````
"""
`````
''',
):
    actual_text = writes(nb, fmt="md")
    compare(actual_text, text)

    actual_nb = reads(text, fmt="md")
    compare_notebooks(actual_nb, nb)
