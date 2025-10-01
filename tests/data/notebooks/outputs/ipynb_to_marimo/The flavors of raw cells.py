import marimo

__generated_with = "0.15.2"
app = marimo.App()


app._unparsable_cell(
    r"""
    $1+1$
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    :math:`1+1`
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    <b>Bold text<b>
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    **Bold text**
    """,
    name="_"
)


@app.cell
def _():
    1 + 1
    return


app._unparsable_cell(
    r"""
    Not formatted
    """,
    name="_"
)


if __name__ == "__main__":
    app.run()
