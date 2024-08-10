import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

from jupytext.compare import compare, compare_notebooks
from jupytext.config import JupytextConfiguration
from jupytext.jupytext import reads, writes


@pytest.fixture
def notebook_with_custom_ids(python_notebook):
    return new_notebook(
        metadata=python_notebook.metadata,
        cells=[
            new_markdown_cell(
                id="first_markdown_cell", source="This is a markdown cell"
            ),
            new_code_cell(id="first_code_cell", source="1 + 1"),
        ],
    )


@pytest.fixture
def py_light_with_custom_ids():
    return """# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python_kernel
# ---

# + first_markdown_cell [markdown]
# This is a markdown cell

# + first_code_cell
1 + 1
"""


@pytest.fixture
def py_percent_with_custom_ids():
    return """# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python_kernel
# ---

# %% first_markdown_cell [markdown]
# This is a markdown cell

# %% first_code_cell
1 + 1
"""


@pytest.fixture
def config():
    c = JupytextConfiguration()
    c.cell_id_to_title = True
    return c


def test_cell_id_to_py_light(
    notebook_with_custom_ids,
    py_light_with_custom_ids,
    config,
    no_jupytext_version_number,
):
    compare(
        writes(notebook_with_custom_ids, fmt="py:light", config=config),
        py_light_with_custom_ids,
    )


def test_cell_id_from_py_light(
    notebook_with_custom_ids,
    py_light_with_custom_ids,
    config,
    no_jupytext_version_number,
):
    compare_notebooks(
        reads(py_light_with_custom_ids, fmt="py:light", config=config),
        notebook_with_custom_ids,
    )


def test_cell_id_to_py_percent(
    notebook_with_custom_ids,
    py_percent_with_custom_ids,
    config,
    no_jupytext_version_number,
):
    compare(
        writes(notebook_with_custom_ids, fmt="py:percent", config=config),
        py_percent_with_custom_ids,
    )


def test_cell_id_from_py_percent(
    notebook_with_custom_ids,
    py_percent_with_custom_ids,
    config,
    no_jupytext_version_number,
):
    compare_notebooks(
        reads(py_percent_with_custom_ids, fmt="py:percent", config=config),
        notebook_with_custom_ids,
    )
