import pytest
from testfixtures import compare
from nbformat.v4.nbbase import new_notebook, new_code_cell, new_markdown_cell
import jupytext

jupytext.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('blank_lines', range(1, 6))
def test_file_with_blank_lines(blank_lines):
    py_script = """# Markdown cell{0}
# Another one{0}
""".format('\n'.join([''] * blank_lines))

    notebook = jupytext.reads(py_script, ext='.py')
    py_script2 = jupytext.writes(notebook, ext='.py')
    compare(py_script, py_script2)


@pytest.mark.parametrize('blank_cells', range(1, 3))
def test_notebook_with_empty_cells(blank_cells):
    notebook = new_notebook(cells=[new_markdown_cell('markdown cell one')] +
                                  [new_code_cell('')] * blank_cells +
                                  [new_markdown_cell('markdown cell two')] +
                                  [new_code_cell('')] * blank_cells,
                            metadata={'main_language': 'python'})

    script = jupytext.writes(notebook, ext='.py')
    notebook2 = jupytext.reads(script, ext='.py')

    compare(notebook, notebook2)
