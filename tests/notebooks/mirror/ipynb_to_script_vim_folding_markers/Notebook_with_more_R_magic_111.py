# ---
# jupyter:
#   jupytext:
#     cell_markers: '{{{,}}}'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# {{{
# %load_ext rpy2.ipython
import pandas as pd

df = pd.DataFrame(
    {
        "Letter": ["a", "a", "a", "b", "b", "b", "c", "c", "c"],
        "X": [4, 3, 5, 2, 1, 7, 7, 5, 9],
        "Y": [0, 4, 3, 6, 7, 10, 11, 9, 13],
        "Z": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    }
)
# }}}

# {{{ magic_args="-i df" language="R"
# library("ggplot2")
# ggplot(data = df) + geom_point(aes(x = X, y = Y, color = Letter, size = Z))
# }}}
