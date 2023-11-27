---
jupyter:
  kernelspec:
    display_name: Python 2
    language: python
    name: python2
  nbformat: 4
  nbformat_minor: 2
---

::: {.cell .markdown}
# A notebook with R cells

This notebook shows the use of R cells to generate plots
:::

::: {#cell-1 .cell .code}
``` python
%load_ext rpy2.ipython
```
:::

::: {#cell-2 .cell .code}
``` python
%%R
suppressMessages(require(tidyverse))
```
:::

::: {#cell-3 .cell .code}
``` python
%%R
ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
```
:::

::: {.cell .markdown}
The default plot dimensions are not good for us, so we use the -w and -h parameters in %%R magic to set the plot size
:::

::: {#cell-4 .cell .code}
``` python
%%R -w 400 -h 240
ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
```
:::
