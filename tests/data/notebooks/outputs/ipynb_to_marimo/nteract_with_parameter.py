import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell
def _():
    # Cell tags: parameters
    param = 4
    return (param,)


@app.cell
def _():
    import pandas as pd
    return (pd,)


@app.cell
def _(param, pd):
    df = pd.DataFrame({'A': [1, 2], 'B': [3 + param, 4]},
                      index=pd.Index(['x0', 'x1'], name='x'))
    df
    return (df,)


@app.cell
def _(df):
    # '%matplotlib inline' command supported automatically in marimo
    df.plot(kind='bar')
    return


if __name__ == "__main__":
    app.run()
