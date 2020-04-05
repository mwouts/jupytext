import jupytext
from jupytext.cell_metadata import parse_key_equal_value
from jupytext.compare import compare


def test_parse_metadata():
    assert parse_key_equal_value("--key value --key-2 .\\a\\b.cs") == {
        "incorrectly_encoded_metadata": "--key value --key-2 .\\a\\b.cs"
    }


def test_parse_double_hyphen_metadata():
    assert parse_key_equal_value("--key1 value1 --key2 value2") == {
        "incorrectly_encoded_metadata": "--key1 value1 --key2 value2"
    }


def test_read_dotnet_try_markdown(
    md="""This is a dotnet/try Markdown file, inspired
from this [post](https://devblogs.microsoft.com/dotnet/creating-interactive-net-documentation/)

``` cs --region methods --source-file .\\myapp\\Program.cs --project .\\myapp\\myapp.csproj
var name ="Rain";
Console.WriteLine($"Hello {name.ToUpper()}!");
```
""",
):
    # Read the notebook
    nb = jupytext.reads(md, fmt=".md")
    assert nb.metadata["jupytext"]["main_language"] == "csharp"
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "code"
    assert (
        nb.cells[1].source
        == """var name ="Rain";
Console.WriteLine($"Hello {name.ToUpper()}!");"""
    )
    compare(
        nb.cells[1].metadata,
        {
            "language": "cs",
            "incorrectly_encoded_metadata": "--region methods --source-file .\\myapp\\Program.cs --project .\\myapp\\myapp.csproj",  # noqa: E501
        },
    )

    # Round trip to Markdown
    md2 = jupytext.writes(nb, "md")
    compare(md2, md.replace("``` cs", "```cs"))
