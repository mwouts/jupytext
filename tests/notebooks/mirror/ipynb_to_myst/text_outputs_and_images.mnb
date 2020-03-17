---
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

This notebook contains outputs of many different types: text, HTML, plots and errors.

+++

# Text outputs

Using `print`, `sys.stdout` and `sys.stderr`

```{code-cell} ipython3
import sys
print('using print')
sys.stdout.write('using sys.stdout.write')
sys.stderr.write('using sys.stderr.write')
```

```{code-cell} ipython3
import logging
logging.debug('Debug')
logging.info('Info')
logging.warning('Warning')
logging.error('Error')
```

# HTML outputs

Using `pandas`. Here we find two representations: both text and HTML.

```{code-cell} ipython3
import pandas as pd
pd.DataFrame([4])
```

```{code-cell} ipython3
from IPython.display import display
display(pd.DataFrame([5]))
display(pd.DataFrame([6]))
```

# Images

```{code-cell} ipython3
%matplotlib inline
```

```{code-cell} ipython3
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

# Errors

```{code-cell} ipython3
undefined_variable
```
