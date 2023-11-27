---
jupyter:
  kernel_info:
    name: python3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  nbformat: 4
  nbformat_minor: 2
---

::: {#cell-1 .cell .code inputHidden="false" outputHidden="false" tags="[\"parameters\"]"}
``` python
param = 4
```
:::

::: {#cell-2 .cell .code inputHidden="false" outputHidden="false"}
``` python
import pandas as pd
```
:::

::: {#cell-3 .cell .code inputHidden="false" outputHidden="false"}
``` python
df = pd.DataFrame({'A': [1, 2], 'B': [3 + param, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df
```
:::

::: {#cell-4 .cell .code inputHidden="false" outputHidden="false"}
``` python
%matplotlib inline
df.plot(kind='bar')
```
:::
