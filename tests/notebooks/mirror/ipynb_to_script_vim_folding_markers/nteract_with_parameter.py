# ---
# jupyter:
#   jupytext:
#     cell_markers: '{{{,}}}'
#   kernel_info:
#     name: python3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# {{{ inputHidden=false outputHidden=false tags=["parameters"]
param = 4
# }}}

# {{{ inputHidden=false outputHidden=false
import pandas as pd
# }}}

# {{{ inputHidden=false outputHidden=false
df = pd.DataFrame({'A': [1, 2], 'B': [3 + param, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df
# }}}

# {{{ inputHidden=false outputHidden=false
# %matplotlib inline
df.plot(kind='bar')
# }}}
