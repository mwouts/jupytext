---
kernelspec:
  display_name: Python 2
  language: python
  name: python2
language_info:
  codemirror_mode:
    name: ipython
    version: 2
  file_extension: .py
  mimetype: text/x-python
  name: python
  nbconvert_exporter: python
  pygments_lexer: ipython2
  version: 2.7.11
---

# A notebook with R cells

This notebook shows the use of R cells to generate plots

```{code-cell} ipython2
%load_ext rpy2.ipython
```

```{code-cell} ipython2
%%R
suppressMessages(require(tidyverse))
```

```{code-cell} ipython2
%%R
ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
```

The default plot dimensions are not good for us, so we use the -w and -h parameters in %%R magic to set the plot size

```{code-cell} ipython2
%%R -w 400 -h 240
ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
```
