::: {.cell .code execution_count="1"}
``` {.python}
%%html
<p><a href="https://github.com/mwouts/jupytext", style="color: rgb(0,0,255)">Jupytext</a> on GitHub</p>
```

::: {.output .display_data}
<p><a href="https://github.com/mwouts/jupytext", style="color: rgb(0,0,255)">Jupytext</a> on GitHub</p>
:::
:::

::: {.cell .code execution_count="2"}
``` {.python}
%%latex
$\frac{\pi}{2}$
```

::: {.output .display_data}
$\frac{\pi}{2}$
:::
:::

::: {.cell .code execution_count="3"}
``` {.python}
%load_ext rpy2.ipython
```
:::

::: {.cell .code execution_count="4"}
``` {.python}
%%R
library(ggplot2)
ggplot(data=data.frame(x=c('A', 'B'), y=c(5, 2)), aes(x,weight=y)) + geom_bar()
```

::: {.output .display_data}
![](7f97cecde4f72e650de2f3937ac4999467e76306.png)
:::
:::

::: {.cell .code execution_count="5"}
``` {.python}
%matplotlib inline
import pandas as pd
pd.Series({'A':5, 'B':2}).plot(figsize=(3,2), kind='bar')
```

::: {.output .execute_result execution_count="5"}
    <matplotlib.axes._subplots.AxesSubplot at 0x2da0c41a9e8>
:::

::: {.output .display_data}
![](9344ac2b35133877848c9a89b2fbbcc3dcce81e0.png)
:::
:::
