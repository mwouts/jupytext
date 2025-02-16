---
kernelspec:
  display_name: Python 3
  language: python
  name: python3
language_info:
  codemirror_mode:
    name: ipython
    version: 3
  file_extension: .py
  mimetype: text/x-python
  name: python
  nbconvert_exporter: python
  pygments_lexer: ipython3
  version: 3.6.6
---

```{code-cell} ipython3
%%html
<p><a href="https://github.com/mwouts/jupytext", style="color: rgb(0,0,255)">Jupytext</a> on GitHub</p>
```

```{code-cell} ipython3
%%latex
$\frac{\pi}{2}$
```

```{code-cell} ipython3
%load_ext rpy2.ipython
```

```{code-cell} ipython3
%%R
library(ggplot2)
ggplot(data=data.frame(x=c('A', 'B'), y=c(5, 2)), aes(x,weight=y)) + geom_bar()
```

```{code-cell} ipython3
%matplotlib inline
import pandas as pd
pd.Series({'A':5, 'B':2}).plot(figsize=(3,2), kind='bar')
```
