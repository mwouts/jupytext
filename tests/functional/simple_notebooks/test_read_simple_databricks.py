from nbformat.v4.nbbase import (
    new_code_cell,
    new_markdown_cell,
)

import jupytext
from jupytext.compare import compare, compare_cells


def test_read_code_cell(
    py="""# Databricks notebook source
# COMMAND ----------

import plotly.graph_objs as go

data = go.Bar(x=['A', 'B', 'C'], y=[10, 20, 15])
go.Figure(data=[data])

""",
):
    nb = jupytext.reads(py, "py:databricks")
    assert nb.metadata["jupytext"]["main_language"] == "python"
    compare_cells(
        nb.cells,
        [
            new_code_cell("""import plotly.graph_objs as go

data = go.Bar(x=['A', 'B', 'C'], y=[10, 20, 15])
go.Figure(data=[data])"""),
        ],
        compare_ids=False,
        cell_metadata_filter="-all",
    )

    py2 = jupytext.writes(nb, "py:databricks")
    compare(py2, py)


def test_read_magic_code_cell(
    py="""# Databricks notebook source
# COMMAND ----------

# MAGIC %pip install plotly
""",
):
    nb = jupytext.reads(py, "py:databricks")
    assert nb.metadata["jupytext"]["main_language"] == "python"
    compare_cells(
        nb.cells,
        [
            new_code_cell("%pip install plotly"),
        ],
        compare_ids=False,
        cell_metadata_filter="-all",
    )

    py2 = jupytext.writes(nb, "py:databricks")
    compare(py2, py)


def test_read_markdown_cell(
    py="""# Databricks notebook source
# MAGIC %md
# MAGIC This is an example notebook

""",
):
    nb = jupytext.reads(py, "py:databricks")
    assert nb.metadata["jupytext"]["main_language"] == "python"
    compare_cells(
        nb.cells,
        [
            new_markdown_cell("This is an example notebook"),
        ],
        compare_ids=False,
        cell_metadata_filter="-all",
    )

    py2 = jupytext.writes(nb, "py:databricks")
    compare(py2, py)
