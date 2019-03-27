::: {.cell .markdown}
# Part one - various cells
:::

::: {.cell .markdown}
Here we have a markdown cell

with two blank lines
:::

::: {.cell .markdown}
Now we have a markdown cell with a code block inside it

``` {.python}
1 + 1
```

After that cell we\'ll have a code cell
:::

::: {.cell .code execution_count="1"}
``` {.python}
2 + 2


3 + 3
```

::: {.output .execute_result execution_count="1"}
    6
:::
:::

::: {.cell .markdown}
Followed by a raw cell
:::

::: {.cell .raw}
```{=}
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

::: {.cell .code execution_count="2" .class="null" tags="["parameters"]"}
``` {.python}
"""This is a code cell with metadata `{"tags":["parameters"], ".class":null}`"""
```

::: {.output .execute_result execution_count="2"}
    'This is a code cell with metadata `{"tags":["parameters"], ".class":null}`'
:::
:::

::: {.cell .raw key="value"}
```{=}
This is a raw cell with cell metadata `{"key": "value"}`
```
:::
