import pytest
from jupytext.compare import compare
from jupytext.cell_metadata import (
    rmd_options_to_metadata,
    metadata_to_rmd_options,
    parse_rmd_options,
    parse_key_equal_value,
)
from jupytext.cell_metadata import (
    _IGNORE_CELL_METADATA,
    RMarkdownOptionParsingError,
    try_eval_metadata,
)
from jupytext.cell_metadata import text_to_metadata, metadata_to_text
from jupytext.metadata_filter import filter_metadata
from .utils import skip_if_dict_is_not_ordered

SAMPLES = [
    ("r", ("R", {})),
    (
        'r plot_1, dpi=72, fig.path="fig_path/"',
        ("R", {"name": "plot_1", "dpi": 72, "fig.path": "fig_path/"}),
    ),
    (
        'r plot_1, bool=TRUE, fig.path="fig_path/"',
        ("R", {"name": "plot_1", "bool": True, "fig.path": "fig_path/"}),
    ),
    ("r echo=FALSE", ("R", {"tags": ["remove_input"]})),
    ("r plot_1, echo=TRUE", ("R", {"name": "plot_1", "echo": True})),
    (
        "python echo=if a==5 then TRUE else FALSE",
        ("python", {"echo": "#R_CODE#if a==5 then TRUE else FALSE"}),
    ),
    (
        'python noname, tags=c("a", "b", "c"), echo={sum(a+c(1,2))>1}',
        (
            "python",
            {
                "name": "noname",
                "tags": ["a", "b", "c"],
                "echo": "#R_CODE#{sum(a+c(1,2))>1}",
            },
        ),
    ),
    ('python active="ipynb,py"', ("python", {"active": "ipynb,py"})),
    (
        'python include=FALSE, active="Rmd"',
        ("python", {"active": "Rmd", "tags": ["remove_cell"]}),
    ),
    (
        'r chunk_name, include=FALSE, active="Rmd"',
        ("R", {"name": "chunk_name", "active": "Rmd", "tags": ["remove_cell"]}),
    ),
    ('python tags=c("parameters")', ("python", {"tags": ["parameters"]})),
]


@pytest.mark.parametrize("options,language_and_metadata", SAMPLES)
def test_parse_rmd_options(options, language_and_metadata):
    compare(rmd_options_to_metadata(options), language_and_metadata)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("options,language_and_metadata", SAMPLES)
def test_build_options(options, language_and_metadata):
    compare(metadata_to_rmd_options(*language_and_metadata), options)


@pytest.mark.parametrize("options,language_and_metadata", SAMPLES)
def test_build_options_random_order(options, language_and_metadata):
    # Older python has no respect for order...
    # assert to_chunk_options(metadata) == options

    def split_and_strip(opt):
        set([o.strip() for o in opt.split(",")])

    assert split_and_strip(
        metadata_to_rmd_options(*language_and_metadata)
    ) == split_and_strip(options)


@pytest.mark.parametrize("options", ["a={)", "name, name2", "a=}", "b=]", "c=["])
def test_parsing_error(options):
    with pytest.raises(RMarkdownOptionParsingError):
        parse_rmd_options(options)


def test_ignore_metadata():
    metadata = {"trusted": True, "tags": ["remove_input"]}
    metadata = filter_metadata(metadata, None, _IGNORE_CELL_METADATA)
    assert metadata_to_rmd_options("R", metadata) == "r echo=FALSE"


def test_filter_metadata():
    assert filter_metadata({"scrolled": True}, None, _IGNORE_CELL_METADATA) == {}


def test_try_eval_metadata():
    metadata = {"list": 'list("a",5)', "c": "c(1,2,3)"}
    try_eval_metadata(metadata, "list")
    try_eval_metadata(metadata, "c")
    assert metadata == {"list": ["a", 5], "c": [1, 2, 3]}


pytestmark = skip_if_dict_is_not_ordered


def test_language_no_metadata(text="python", value=("python", {})):
    compare(text_to_metadata(text), value)
    assert metadata_to_text(*value) == text.strip()


def test_only_metadata(text='key="value"', value=("", {"key": "value"})):
    compare(text_to_metadata(text), value)
    assert metadata_to_text(*value) == text


def test_only_metadata_2(text='key="value"', value=("", {"key": "value"})):
    compare(text_to_metadata(text, allow_title=True), value)
    assert metadata_to_text(*value) == text


def test_no_language(text=".class", value=("", {".class": None})):
    compare(text_to_metadata(text), value)
    assert metadata_to_text(*value) == text


def test_language_metadata_no_space(text='python{"a":1}', value=("python", {"a": 1})):
    compare(text_to_metadata(text), value)
    assert metadata_to_text(*value) == "python a=1"


def test_title_no_metadata(text="title", value=("title", {})):
    compare(text_to_metadata(text, allow_title=True), value)
    assert metadata_to_text(*value) == text.strip()


def test_simple_metadata(
    text='python string="value" number=1.0 array=["a", "b"]',
    value=("python", {"string": "value", "number": 1.0, "array": ["a", "b"]}),
):
    compare(text_to_metadata(text), value)
    assert metadata_to_text(*value) == text


def test_simple_metadata_with_spaces(
    text='python string = "value" number = 1.0 array = ["a",  "b"]',
    value=("python", {"string": "value", "number": 1.0, "array": ["a", "b"]}),
):
    compare(text_to_metadata(text), value)
    assert (
        metadata_to_text(*value) == 'python string="value" number=1.0 array=["a", "b"]'
    )


def test_title_and_relax_json(
    text="cell title string='value' number=1.0 array=['a', \"b\"]",
    value=("cell title", {"string": "value", "number": 1.0, "array": ["a", "b"]}),
):
    compare(text_to_metadata(text, allow_title=True), value)
    assert (
        metadata_to_text(*value)
        == 'cell title string="value" number=1.0 array=["a", "b"]'
    )


def test_title_and_json_dict(
    text='cell title {"string": "value", "number": 1.0, "array": ["a", "b"]}',
    value=("cell title", {"string": "value", "number": 1.0, "array": ["a", "b"]}),
):
    compare(text_to_metadata(text, allow_title=True), value)
    assert (
        metadata_to_text(*value)
        == 'cell title string="value" number=1.0 array=["a", "b"]'
    )


@pytest.mark.parametrize("allow_title", [True, False])
def test_attribute(allow_title):
    text = ".class"
    value = ("", {".class": None})
    compare(text_to_metadata(text, allow_title), value)
    assert metadata_to_text(*value) == text


def test_language_and_attribute(
    text="python .class", value=("python", {".class": None})
):
    compare(text_to_metadata(text), value)
    assert metadata_to_text(*value) == text


def test_title_and_attribute(
    text="This is my title. .class", value=("This is my title.", {".class": None})
):
    compare(text_to_metadata(text, allow_title=True), value)
    assert metadata_to_text(*value) == text


def test_values_with_equal_signs_inside(
    text='python string="value=5"', value=("python", {"string": "value=5"})
):
    compare(text_to_metadata(text), value)
    assert metadata_to_text(*value) == text


def test_incorrectly_encoded(text="this is an incorrect expression d={{4 b=3"):
    value = text_to_metadata(text, allow_title=True)
    assert metadata_to_text(*value) == text


def test_incorrectly_encoded_json(text='this is an incorrect expression {"d": "}'):
    value = text_to_metadata(text, allow_title=True)
    assert metadata_to_text(*value) == text


def test_parse_key_value():
    assert parse_key_equal_value("key='value' key2=5.0") == {
        "key": "value",
        "key2": 5.0,
    }


def test_parse_key_value_key():
    assert parse_key_equal_value("key='value' key2") == {
        "key": "value",
        "key2": None,
    }
