import pytest
from nbformat.v4.nbbase import new_notebook
from jupytext import reads, writes
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
