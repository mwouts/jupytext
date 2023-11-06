# %%
1 + 1

# %%
import pandas as pd
pd.Series({'A':5, 'B':2}).plot()

# %%
%matplotlib inline
pd.Series({'A':5, 'B':2}).plot(figsize=(3,2))

# %%
%%html
<p><a href="https://github.com/mwouts/jupytext", style="color: rgb(0,0,255)">Jupytext</a> on GitHub</p>

# %%
%load_ext rpy2.ipython

# %%
%%R -w 400 -h 200
library(ggplot2)
ggplot(data=data.frame(x=c('A', 'B'), y=c(5, 2)), aes(x,weight=y)) + geom_bar()

# %%
%%latex
$\frac{\pi}{2}$
