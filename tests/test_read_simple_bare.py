from nbformat.v4.nbbase import new_notebook, new_code_cell, new_markdown_cell
from jupytext.compare import compare
from jupytext import reads, writes
from jupytext.combine import combine_inputs_with_outputs


def test_write_reload_simple_notebook():
    nb1 = new_notebook(cells=[
        new_markdown_cell('A markdown cell', metadata={'md': 'value'}),
        new_code_cell('1 + 1'),
        new_markdown_cell('A markdown cell', metadata={'md': 'value'}),
        new_code_cell("""def f(x):
    return x""", metadata={'md': 'value'}),
        new_markdown_cell('A markdown cell', metadata={'md': 'value'}),
        new_code_cell("""def g(x):
    return x


def h(x):
    return x
""", metadata={'md': 'value'})])

    text = writes(nb1, 'py:bare')
    nb2 = reads(text, 'py:bare')
    combine_inputs_with_outputs(nb2, nb1, 'py:bare')
    nb2.metadata.pop('jupytext')

    assert len(nb2.cells) == 7
    nb1.cells = nb1.cells[:5]
    nb2.cells = nb2.cells[:5]
    compare(nb2, nb1)
