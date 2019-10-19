# ---
# jupyter:
#   jupytext:
#     cell_markers: region,endregion
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# region language="html"
# <p><a href="https://github.com/mwouts/jupytext", style="color: rgb(0,0,255)">Jupytext</a> on GitHub</p>
# endregion

# region language="latex"
# $\frac{\pi}{2}$
# endregion

# %load_ext rpy2.ipython

# region language="R"
# library(ggplot2)
# ggplot(data=data.frame(x=c('A', 'B'), y=c(5, 2)), aes(x,weight=y)) + geom_bar()
# endregion

# %matplotlib inline
import pandas as pd
pd.Series({'A':5, 'B':2}).plot(figsize=(3,2), kind='bar')
