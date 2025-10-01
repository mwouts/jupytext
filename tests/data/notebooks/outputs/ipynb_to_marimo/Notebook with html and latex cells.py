import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell
def _(mo):
    mo.Html('<p><a href="https://github.com/mwouts/jupytext", style="color: rgb(0,0,255)">Jupytext</a> on GitHub</p>')
    return


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %%latex
    # $\frac{\pi}{2}$
    return


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %load_ext rpy2.ipython
    return


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %%R
    # library(ggplot2)
    # ggplot(data=data.frame(x=c('A', 'B'), y=c(5, 2)), aes(x,weight=y)) + geom_bar()
    return


@app.cell
def _():
    # '%matplotlib inline' command supported automatically in marimo
    import pandas as pd
    pd.Series({'A':5, 'B':2}).plot(figsize=(3,2), kind='bar')
    return


if __name__ == "__main__":
    app.run()
