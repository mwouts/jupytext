import os
import pytest
from nbformat.v4.nbbase import new_notebook, new_code_cell, new_markdown_cell
from jupytext.compare import compare
from jupytext import reads, writes, write
from jupytext.combine import combine_inputs_with_outputs
from jupytext.cli import jupytext as jupytext_cli


def test_write_reload_simple_notebook():
    nb1 = new_notebook(
        cells=[
            new_markdown_cell("A markdown cell", metadata={"md": "value"}),
            new_code_cell("1 + 1"),
            new_markdown_cell("A markdown cell", metadata={"md": "value"}),
            new_code_cell(
                """def f(x):
    return x""",
                metadata={"md": "value"},
            ),
            new_markdown_cell("A markdown cell", metadata={"md": "value"}),
            new_code_cell(
                """def g(x):
    return x


def h(x):
    return x
""",
                metadata={"md": "value"},
            ),
        ]
    )

    text = writes(nb1, "py:nomarker")
    nb2 = reads(text, "py:nomarker")
    nb2 = combine_inputs_with_outputs(nb2, nb1, "py:nomarker")
    nb2.metadata.pop("jupytext")

    assert len(nb2.cells) == 7
    nb1.cells = nb1.cells[:5]
    nb2.cells = nb2.cells[:5]
    compare(nb2, nb1)

    with pytest.warns(DeprecationWarning, match="nomarker"):
        text = writes(nb2, "py:bare")
    with pytest.warns(DeprecationWarning, match="nomarker"):
        nb3 = reads(text, "py:bare")
    with pytest.warns(DeprecationWarning, match="nomarker"):
        nb3 = combine_inputs_with_outputs(nb3, nb2, "py:bare")
    nb3.metadata.pop("jupytext")

    compare(nb3, nb2)


def test_jupytext_cli_bare(tmpdir):
    tmp_py = str(tmpdir.join("test.py"))
    tmp_ipynb = str(tmpdir.join("test.ipynb"))
    write(new_notebook(cells=[new_code_cell("1 + 1")]), tmp_ipynb)
    with pytest.warns(DeprecationWarning, match="nomarker"):
        jupytext_cli([tmp_ipynb, "--to", "py:bare"])
    assert os.path.isfile(tmp_py)
