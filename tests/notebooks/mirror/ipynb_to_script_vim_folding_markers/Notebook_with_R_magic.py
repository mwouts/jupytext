# ---
# jupyter:
#   jupytext:
#     cell_markers: '{{{,}}}'
#   kernelspec:
#     display_name: Python 2
#     language: python
#     name: python2
# ---

# # A notebook with R cells
#
# This notebook shows the use of R cells to generate plots

# %load_ext rpy2.ipython

# {{{ language="R"
# suppressMessages(require(tidyverse))
# }}}

# {{{ language="R"
# ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
# }}}

# The default plot dimensions are not good for us, so we use the -w and -h parameters in %%R magic to set the plot size

# {{{ magic_args="-w 400 -h 240" language="R"
# ggplot(iris, aes(x = Sepal.Length, y = Petal.Length, color=Species)) + geom_point()
# }}}
