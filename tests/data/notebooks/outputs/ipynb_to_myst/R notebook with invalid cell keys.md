---
kernelspec:
  display_name: R
  language: R
  name: ir
---

This notebook was created with IRKernel 0.8.12, and is not completely valid, as the code cell below contains an unexpected 'source' entry. This did cause https://github.com/mwouts/jupytext/issues/234. Note that the problem is solved when one upgrades to IRKernel 1.0.0.

```{code-cell} r
library("ggplot2")
ggplot(mtcars, aes(mpg)) + stat_ecdf()
```
