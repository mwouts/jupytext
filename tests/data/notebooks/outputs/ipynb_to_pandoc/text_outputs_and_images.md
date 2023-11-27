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
This notebook contains outputs of many different types: text, HTML, plots and errors.
:::

::: {.cell .markdown}
# Text outputs

Using `print`, `sys.stdout` and `sys.stderr`
:::

::: {#cell-1 .cell .code}
``` python
import sys
print('using print')
sys.stdout.write('using sys.stdout.write')
sys.stderr.write('using sys.stderr.write')
```
:::

::: {#cell-2 .cell .code}
``` python
import logging
logging.debug('Debug')
logging.info('Info')
logging.warning('Warning')
logging.error('Error')
```
:::

::: {.cell .markdown}
# HTML outputs

Using `pandas`. Here we find two representations: both text and HTML.
:::

::: {#cell-3 .cell .code}
``` python
import pandas as pd
pd.DataFrame([4])
```
:::

::: {#cell-4 .cell .code}
``` python
from IPython.display import display
display(pd.DataFrame([5]))
display(pd.DataFrame([6]))
```
:::

::: {.cell .markdown}
# Images
:::

::: {#cell-5 .cell .code}
``` python
%matplotlib inline
```
:::

::: {#cell-6 .cell .code}
``` python
# First plot
from matplotlib import pyplot as plt
import numpy as np
w, h = 3, 3
data = np.zeros((h, w, 3), dtype=np.uint8)
data[0,:] = [0,255,0]
data[1,:] = [0,0,255]
data[2,:] = [0,255,0]
data[1:3,1:3] = [255, 0, 0]
plt.imshow(data)
plt.axis('off')
plt.show()
# Second plot
data[1:3,1:3] = [255, 255, 0]
plt.imshow(data)
plt.axis('off')
plt.show()
```
:::

::: {.cell .markdown}
# Errors
:::

::: {#cell-7 .cell .code}
``` python
undefined_variable
```
:::
