import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    print('asdf')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        Thanks for jupytext!
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
