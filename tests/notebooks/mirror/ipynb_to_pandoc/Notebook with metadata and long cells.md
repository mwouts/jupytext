---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  nbformat: 4
  nbformat_minor: 2
---

::: {.cell .markdown}
# Part one - various cells
:::

::: {.cell .markdown}
Here we have a markdown cell

with two blank lines
:::

::: {.cell .markdown}
Now we have a markdown cell
with a code block inside it

``` {.python}
1 + 1
```

After that cell we\'ll have a code cell
:::

::: {.cell .code}
``` {.python}
2 + 2


3 + 3
```
:::

::: {.cell .markdown}
Followed by a raw cell
:::

::: {.cell .raw}
```{=ipynb}
This is 
the content
of the raw cell
```
:::

::: {.cell .markdown}
# Part two - cell metadata
:::

::: {.cell .markdown key="value"}
This is a markdown cell with cell metadata `{"key": "value"}`
:::

::: {.cell .code .class="null" tags="[\"parameters\"]"}
``` {.python}
"""This is a code cell with metadata `{"tags":["parameters"], ".class":null}`"""
```
:::

::: {.cell .raw key="value"}
```{=ipynb}
This is a raw cell with cell metadata `{"key": "value"}`
```
:::
