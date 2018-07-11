from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook
from nbrmd.combine import combine_inputs_with_outputs


def test_combine():
    nb_source = new_notebook(
        cells=[new_markdown_cell('Markdown text'),
               new_code_cell('a=3'),
               new_code_cell('a+1'),
               new_code_cell('a+1'),
               new_markdown_cell('Markdown text'),
               new_code_cell('a+2')])

    nb_outputs = new_notebook(
        cells=[new_markdown_cell('Markdown text'),
               new_code_cell('a=3'),
               new_code_cell('a+1'),
               new_code_cell('a+2'),
               new_markdown_cell('Markdown text')])

    nb_outputs.cells[2].outputs = ['4']
    nb_outputs.cells[3].outputs = ['5']

    combine_inputs_with_outputs(nb_source, nb_outputs)

    assert nb_source.cells[2].outputs == ['4']
    assert nb_source.cells[3].outputs == []
    assert nb_source.cells[5].outputs == ['5']
