import pytest
from nbformat.v4.nbbase import new_notebook, new_markdown_cell, new_code_cell, new_raw_cell
from jupytext.compare import compare_notebooks, NotebookDifference, test_round_trip_conversion as round_trip_conversion


def test_raise_on_different_metadata():
    ref = new_notebook(metadata={'kernelspec': {'language': 'python', 'name': 'python', 'display_name': 'Python'}},
                       cells=[new_markdown_cell('Cell one')])
    test = new_notebook(metadata={'kernelspec': {'language': 'R', 'name': 'R', 'display_name': 'R'}},
                        cells=[new_markdown_cell('Cell one')])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.md')


def test_raise_on_different_cell_count():
    ref = new_notebook(cells=[new_markdown_cell('Cell one'), new_code_cell('Cell two')])
    test = new_notebook(cells=[new_markdown_cell('Cell one')])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.md')


def test_raise_on_different_cell_type():
    ref = new_notebook(cells=[new_markdown_cell('Cell one'), new_code_cell('Cell two')])
    test = new_notebook(cells=[new_markdown_cell('Cell one'), new_raw_cell('Cell two')])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.md')


def test_raise_on_different_cell_content():
    ref = new_notebook(cells=[new_markdown_cell('Cell one'), new_code_cell('Cell two')])
    test = new_notebook(cells=[new_markdown_cell('Cell one'), new_code_cell('Modified cell two')])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.md')


def test_raise_on_incomplete_markdown_cell():
    ref = new_notebook(cells=[new_markdown_cell('Cell one\n\n\nsecond line')])
    test = new_notebook(cells=[new_markdown_cell('Cell one')])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.md')


def test_does_not_raise_on_split_markdown_cell():
    ref = new_notebook(cells=[new_markdown_cell('Cell one\n\n\nsecond line')])
    test = new_notebook(cells=[new_markdown_cell('Cell one'),
                               new_markdown_cell('second line')])
    compare_notebooks(ref, test, ext='.md')


def test_does_raise_on_split_markdown_cell():
    ref = new_notebook(cells=[new_markdown_cell('Cell one\n\n\nsecond line')])
    test = new_notebook(cells=[new_markdown_cell('Cell one'),
                               new_markdown_cell('second line')])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.md', allow_expected_differences=False)


def test_raise_on_different_cell_metadata():
    ref = new_notebook(cells=[new_code_cell('1+1')])
    test = new_notebook(cells=[new_code_cell('1+1', metadata={'metakey': 'value'})])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.py', format_name='light')


def test_does_not_raise_on_blank_line_removed():
    ref = new_notebook(cells=[new_code_cell('1+1\n    ')])
    test = new_notebook(cells=[new_code_cell('1+1')])
    compare_notebooks(ref, test, ext='.py', format_name='light')


def test_strict_raise_on_blank_line_removed():
    ref = new_notebook(cells=[new_code_cell('1+1\n')])
    test = new_notebook(cells=[new_code_cell('1+1')])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.py', format_name='light', allow_expected_differences=False)


def test_dont_raise_on_different_outputs():
    ref = new_notebook(cells=[new_code_cell('1+1')])
    test = new_notebook(cells=[new_code_cell('1+1', outputs=[
        {
            "data": {
                "text/plain": [
                    "2"
                ]
            },
            "execution_count": 1,
            "metadata": {},
            "output_type": "execute_result"
        }
    ])])
    compare_notebooks(ref, test, ext='.md')


def test_raise_on_different_outputs():
    ref = new_notebook(cells=[new_code_cell('1+1')])
    test = new_notebook(cells=[new_code_cell('1+1', outputs=[
        {
            "data": {
                "text/plain": [
                    "2"
                ]
            },
            "execution_count": 1,
            "metadata": {},
            "output_type": "execute_result"
        }
    ])])
    with pytest.raises(NotebookDifference):
        compare_notebooks(ref, test, ext='.md', compare_outputs=True)


def test_test_round_trip_conversion():
    notebook = new_notebook(cells=[new_code_cell('1+1', outputs=[
        {
            "data": {
                "text/plain": [
                    "2"
                ]
            },
            "execution_count": 1,
            "metadata": {},
            "output_type": "execute_result"
        }
    ])], metadata={'main_language': 'python'})

    round_trip_conversion(notebook, '.py', None, update=True)
