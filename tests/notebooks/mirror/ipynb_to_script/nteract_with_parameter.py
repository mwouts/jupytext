# ---
# jupyter:
#   kernel_info:
#     name: python3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
#   nteract:
#     version: 0.11.6
# ---

# + {"outputHidden": false, "inputHidden": false, "tags": ["parameters"]}
param = 4

# + {"outputHidden": false, "inputHidden": false}
import pandas as pd

# + {"outputHidden": false, "inputHidden": false}
df = pd.DataFrame({'A': [1, 2], 'B': [3 + param, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df

# + {"outputHidden": false, "inputHidden": false}
# %matplotlib inline
df.plot(kind='bar')
