::: {.cell .code execution_count="1"}
``` {.python}
%load_ext rpy2.ipython
import pandas as pd

df = pd.DataFrame(
    {
        "Letter": ["a", "a", "a", "b", "b", "b", "c", "c", "c"],
        "X": [4, 3, 5, 2, 1, 7, 7, 5, 9],
        "Y": [0, 4, 3, 6, 7, 10, 11, 9, 13],
        "Z": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    }
)
```
:::

::: {.cell .code execution_count="2"}
``` {.python}
%%R -i df
library("ggplot2")
ggplot(data = df) + geom_point(aes(x = X, y = Y, color = Letter, size = Z))
```

::: {.output .stream .stderr}
    C:\Users\Marco\AppData\Local\conda\conda\envs\python3\lib\site-packages\rpy2-2.9.4-py3.6-win-amd64.egg\rpy2\robjects\pandas2ri.py:191: FutureWarning: from_items is deprecated. Please use DataFrame.from_dict(dict(items), ...) instead. DataFrame.from_dict(OrderedDict(items)) may be used to preserve the key order.
      res = PandasDataFrame.from_items(items)
:::

::: {.output .display_data}
![](7d03ea06cc5a2be89de49cf90faff680e9b93dfa.png)
:::
:::
