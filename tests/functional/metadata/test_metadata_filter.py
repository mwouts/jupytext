from copy import deepcopy

import pytest
from nbformat.v4.nbbase import new_code_cell, new_notebook

from jupytext import reads, writes
from jupytext.cli import jupytext as jupytext_cli
from jupytext.compare import compare, compare_notebooks
from jupytext.metadata_filter import filter_metadata, metadata_filter_as_dict


def to_dict(keys):
    return {key: None for key in keys}


@pytest.mark.parametrize(
    "metadata_filter_string,metadata_filter_dict",
    [
        (
            "all, -widgets,-varInspector",
            {"additional": "all", "excluded": ["widgets", "varInspector"]},
        ),
        ("toc", {"additional": ["toc"]}),
        ("+ toc", {"additional": ["toc"]}),
        ("preserve,-all", {"additional": ["preserve"], "excluded": "all"}),
        (
            "ExecuteTime, autoscroll, -hide_output",
            {"additional": ["ExecuteTime", "autoscroll"], "excluded": ["hide_output"]},
        ),
    ],
)
def test_string_to_dict_conversion(metadata_filter_string, metadata_filter_dict):
    assert metadata_filter_as_dict(metadata_filter_string) == metadata_filter_dict


def test_metadata_filter_as_dict():
    assert metadata_filter_as_dict(True) == metadata_filter_as_dict("all")
    assert metadata_filter_as_dict(False) == metadata_filter_as_dict("-all")
    assert metadata_filter_as_dict({"excluded": "all"}) == metadata_filter_as_dict(
        "-all"
    )


def test_metadata_filter_default():
    assert filter_metadata(
        to_dict(["technical", "user", "preserve"]), None, "-technical"
    ) == to_dict(["user", "preserve"])
    assert filter_metadata(
        to_dict(["technical", "user", "preserve"]), None, "preserve,-all"
    ) == to_dict(["preserve"])


def test_metadata_filter_user_plus_default():
    assert filter_metadata(
        to_dict(["technical", "user", "preserve"]), "-user", "-technical"
    ) == to_dict(["preserve"])
    assert filter_metadata(
        to_dict(["technical", "user", "preserve"]), "all,-user", "-technical"
    ) == to_dict(["preserve", "technical"])
    assert filter_metadata(
        to_dict(["technical", "user", "preserve"]), "user", "preserve,-all"
    ) == to_dict(["user", "preserve"])


def test_metadata_filter_user_overrides_default():
    assert filter_metadata(
        to_dict(["technical", "user", "preserve"]), "all,-user", "-technical"
    ) == to_dict(["technical", "preserve"])
    assert filter_metadata(
        to_dict(["technical", "user", "preserve"]), "user,-all", "preserve"
    ) == to_dict(["user"])


def test_negative_cell_metadata_filter():
    assert filter_metadata(to_dict(["exectime"]), "-linesto", "-exectime") == to_dict(
        []
    )


def test_cell_metadata_filter_is_updated():
    text = """---
jupyter:
  jupytext:
    cell_metadata_filter: -all
---

```{r cache=FALSE}
1+1
```
"""
    nb = reads(text, "Rmd")
    assert nb.metadata["jupytext"]["cell_metadata_filter"] == "cache,-all"

    text2 = writes(nb, "Rmd")
    assert text.splitlines()[-3:] == text2.splitlines()[-3:]


def test_notebook_metadata_all():
    nb = new_notebook(
        metadata={
            "user_metadata": [1, 2, 3],
            "jupytext": {"notebook_metadata_filter": "all"},
        }
    )
    text = writes(nb, "md")
    assert "user_metadata" in text


def test_notebook_metadata_none():
    nb = new_notebook(metadata={"jupytext": {"notebook_metadata_filter": "-all"}})
    text = writes(nb, "md")
    assert "---" not in text


def test_filter_nested_metadata():
    metadata = {"I": {"1": {"a": 1, "b": 2}}}

    assert filter_metadata(metadata, "I", "-all") == {"I": {"1": {"a": 1, "b": 2}}}
    assert filter_metadata(metadata, "-I") == {}

    assert filter_metadata(metadata, "I.1.a", "-all") == {"I": {"1": {"a": 1}}}
    assert filter_metadata(metadata, "-I.1.b") == {"I": {"1": {"a": 1}}}

    assert filter_metadata(metadata, "-I.1.b", "I") == {"I": {"1": {"a": 1}}}

    # That one is not supported yet
    # assert filter_metadata(metadata, 'I.1.a', '-I') == {'I': {'1': {'a': 1}}}


def test_filter_out_execution_metadata():
    nb = new_notebook(
        cells=[
            new_code_cell(
                "1 + 1",
                metadata={
                    "execution": {
                        "iopub.execute_input": "2020-10-12T19:13:45.306603Z",
                        "iopub.status.busy": "2020-10-12T19:13:45.306233Z",
                        "iopub.status.idle": "2020-10-12T19:13:45.316103Z",
                        "shell.execute_reply": "2020-10-12T19:13:45.315429Z",
                        "shell.execute_reply.started": "2020-10-12T19:13:45.306577Z",
                    }
                },
            )
        ]
    )

    text = writes(nb, fmt="py:percent")
    assert "execution" not in text


def test_default_config_has_priority_over_current_metadata(
    tmpdir,
    text="""# %% some_metadata_key=5
1 + 1
""",
):
    py_file = tmpdir.join("notebook.py")
    py_file.write(text)

    cfg_file = tmpdir.join("jupytext.toml")
    cfg_file.write(
        """cell_metadata_filter = "-some_metadata_key"
"""
    )

    jupytext_cli([str(py_file), "--to", "py"])
    assert (
        py_file.read()
        == """# %%
1 + 1
"""
    )


@pytest.mark.requires_myst
def test_metadata_filter_in_notebook_757():
    md = """---
nbhosting:
  title: 'Exercice: Taylor'
jupytext:
  cell_metadata_filter: all,-hidden,-heading_collapsed
  notebook_metadata_filter: all,-language_info,-toc,-jupytext.text_representation.jupytext_version,-jupytext.text_representation.format_version
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

```python
1 + 1
```
"""  # noqa
    nb = reads(md, fmt="md:myst")
    assert nb.metadata["jupytext"]["notebook_metadata_filter"] == ",".join(
        [
            "all",
            "-language_info",
            "-toc",
            "-jupytext.text_representation.jupytext_version",
            "-jupytext.text_representation.format_version",
        ]
    )
    md2 = writes(nb, fmt="md:myst")
    compare(md2, md)

    for fmt in ["py:light", "py:percent", "md"]:
        text = writes(nb, fmt=fmt)
        nb2 = reads(text, fmt=fmt)
        compare_notebooks(nb2, nb, fmt=fmt)
        ref_metadata = deepcopy(nb.metadata)
        del ref_metadata["jupytext"]["text_representation"]
        del nb2.metadata["jupytext"]["text_representation"]
        compare(nb2.metadata, ref_metadata)
