import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

import jupytext
from jupytext.compare import compare, compare_notebooks


@pytest.mark.parametrize("blank_lines", range(1, 6))
def test_file_with_blank_lines(blank_lines):
    py_script = """# Markdown cell{0}
# Another one{0}
""".format(
        "\n".join([""] * blank_lines)
    )

    notebook = jupytext.reads(py_script, "py")
    py_script2 = jupytext.writes(notebook, "py")
    compare(py_script2, py_script)


@pytest.mark.parametrize("blank_cells", range(1, 3))
def test_notebook_with_empty_cells(blank_cells):
    notebook = new_notebook(
        cells=[new_markdown_cell("markdown cell one")]
        + [new_code_cell("") for i in range(blank_cells)]
        + [new_markdown_cell("markdown cell two")]
        + [new_code_cell("") for i in range(blank_cells)],
        metadata={"jupytext": {"main_language": "python"}},
    )

    script = jupytext.writes(notebook, "py")
    notebook2 = jupytext.reads(script, "py")

    compare_notebooks(notebook2, notebook)
