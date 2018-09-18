# %%
import pandas as pd

# %% Display a data frame
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df

# %% Pandas plot {"tags": ["parameters"]}
df.plot(kind='bar')
