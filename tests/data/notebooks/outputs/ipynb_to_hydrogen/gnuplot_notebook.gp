# ---
# jupyter:
#   kernelspec:
#     display_name: gnuplot
#     language: gnuplot
#     name: gnuplot
# ---

# %% [markdown]
# # Sample gnuplot notebook

# %% [markdown]
# ## Simple plotting

# %%
# Plot sin and cos with different linetypes

f(x) = sin(x)
g(x) = cos(x)
set xrange[0:2*pi]
set xtics(0, "{/Symbol p}" pi , "2{/Symbol p}" 2*pi)
set ytics 1
plot f(x) linewidth 2 title "sin(x)", \
    g(x) linewidth 2 dashtype "--" title "cos(x)"

# %% [markdown]
# ## Example of line magic

# %%
%gnuplot inline pngcairo enhanced background rgb "#EEEEEE" size 600, 600
# Parametric plot without border

reset
set parametric
set size ratio -1
unset border
unset tics
plot f(t), g(t) linewidth 2 notitle
