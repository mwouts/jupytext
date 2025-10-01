import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell
def _():
    c = '''
    title: "Quick test"
    output:
      ioslides_presentation:
        widescreen: true
        smaller: true
    editor_options:
         chunk_output_type console
    '''
    return (c,)


@app.cell
def _(c):
    import yaml
    print(yaml.dump(yaml.load(c)))
    return


app._unparsable_cell(
    r"""
    ?next
    """,
    name="_"
)


if __name__ == "__main__":
    app.run()
