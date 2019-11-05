# ---
# jupyter:
#   kernel_info:
#     name: python3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + outputHidden=false inputHidden=false tags=["parameters"]
param = 4

# + outputHidden=false inputHidden=false
import pandas as pd

# + outputHidden=false inputHidden=false
df = pd.DataFrame({'A': [1, 2], 'B': [3 + param, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df

# + outputHidden=false inputHidden=false
# %matplotlib inline
df.plot(kind='bar')
