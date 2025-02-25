import pytest

import jupytext
from jupytext.compare import compare


@pytest.mark.parametrize("lang", ["cs", "c#", "csharp"])
def test_simple_cs(lang):
    source = """// A Hello World! program in C#.
Console.WriteLine("Hello World!");
"""
    md = """```{lang}
{source}
```
""".format(
        lang=lang, source=source
    )
    nb = jupytext.reads(md, "md")
    assert nb.metadata["jupytext"]["main_language"] == "csharp"
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"

    cs = jupytext.writes(nb, "cs")
    assert source in cs
    if lang != "csharp":
        assert cs.startswith(f'// %% language="{lang}"')

    md2 = jupytext.writes(nb, "md")
    compare(md2, md)


@pytest.mark.parametrize("lang", ["cs", "c#", "csharp"])
def test_csharp_magics(no_jupytext_version_number, lang):
    md = """```{lang}
#!html
<b>Hello!</b>
```
""".format(
        lang=lang
    )
    nb = jupytext.reads(md, "md")
    nb.metadata["jupytext"].pop("notebook_metadata_filter")
    nb.metadata["jupytext"].pop("cell_metadata_filter")
    assert nb.metadata["jupytext"]["main_language"] == "csharp"
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"

    cs = jupytext.writes(nb, "cs")
    assert all(line.startswith("//") for line in cs.splitlines()), cs

    md2 = jupytext.writes(nb, "md")
    md_expected = """---
jupyter:
  jupytext:
    main_language: csharp
---

```html
<b>Hello!</b>
```
"""
    compare(md2, md_expected)


def test_read_html_cell_from_md(no_jupytext_version_number):
    md = """---
jupyter:
  jupytext:
    main_language: csharp
---

```html
<b>Hello!</b>
```
"""

    nb = jupytext.reads(md, "md")
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"
    compare(nb.cells[0].source, "#!html\n<b>Hello!</b>")

    md2 = jupytext.writes(nb, "md")
    compare(md2, md)
