from nbformat.v4.nbbase import new_notebook, new_code_cell
from jupytext.compare import compare, compare_notebooks
import jupytext


def test_hide_code_tag(
    no_jupytext_version_number,
    nb=new_notebook(
        metadata={"jupytext": {"main_language": "matlab"}},
        cells=[new_code_cell("1 + 1", metadata={"tags": ["hide_code"]})],
    ),
    text="""% + tags=["hide_code"]
1 + 1
""",
):
    text2 = jupytext.writes(nb, "m")
    compare(text2, text)
    nb2 = jupytext.reads(text, "m")
    compare_notebooks(nb2, nb)


def test_hide_code_tag_percent_format(
    no_jupytext_version_number,
    nb=new_notebook(
        metadata={"jupytext": {"main_language": "matlab"}},
        cells=[new_code_cell("1 + 1", metadata={"tags": ["hide_code"]})],
    ),
    text="""% %% tags=["hide_code"]
1 + 1
""",
):
    text2 = jupytext.writes(nb, "m:percent")
    compare(text2, text)
    nb2 = jupytext.reads(text, "m:percent")
    compare_notebooks(nb2, nb)
