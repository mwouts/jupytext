::: {.cell .code execution_count="6"}
``` {.python}
c = '''
title: "Quick test"
output:
  ioslides_presentation:
    widescreen: true
    smaller: true
editor_options:
     chunk_output_type console
'''
```
:::

::: {.cell .code execution_count="7"}
``` {.python}
import yaml
print(yaml.dump(yaml.load(c)))
```

::: {.output .stream .stdout}
    author: Marc Wouts
    date: June 15, 2018
    editor_options: chunk_output_type console
    output:
      ioslides_presentation: {smaller: true, widescreen: true}
    subtitle: Slides generated using R, python and ioslides
    title: Quick ioslides
:::
:::

::: {.cell .code execution_count="7"}
``` {.python}
?next
```
:::
