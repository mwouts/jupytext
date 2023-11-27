---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  nbformat: 4
  nbformat_minor: 2
---

::: {#cell-1 .cell .code}
``` python
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

::: {#cell-2 .cell .code}
``` python
import yaml
print(yaml.dump(yaml.load(c)))
```
:::

::: {#cell-3 .cell .code}
``` python
?next
```
:::
