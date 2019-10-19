# ---
# jupyter:
#   kernel_info:
#     name: python3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

param = 4

""
import pandas as pd

""
df = pd.DataFrame({'A': [1, 2], 'B': [3 + param, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df

""
# %matplotlib inline
df.plot(kind='bar')
