::: {.cell .markdown}
# A notebook with R cells

This notebook shows the use of R cells to generate plots
:::

::: {.cell .code execution_count="1"}
``` {.python}
%load_ext rpy2.ipython
```
:::

::: {.cell .code execution_count="2"}
``` {.python}
%%R
suppressMessages(require(tidyverse))
```
:::

::: {.cell .code execution_count="3"}
``` {.python}
%%R
ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
```

::: {.output .display_data}
![](3fc4493185b3637a4127483394ece754faff16c7.png)
:::
:::

::: {.cell .markdown}
The default plot dimensions are not good for us, so we use the -w and -h
parameters in %%R magic to set the plot size
:::

::: {.cell .code execution_count="4"}
``` {.python}
%%R -w 400 -h 240
ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
```

::: {.output .display_data}
![](92a00f6aa6af61f269e4b4a9db7fe31d5f8b1dbb.png)
:::
:::
