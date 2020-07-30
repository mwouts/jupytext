# -*- coding: utf-8 -*-
import pytest
from jupytext.compare import compare
from nbformat.v4.nbbase import new_notebook, new_markdown_cell
from jupytext.compare import compare_notebooks
from jupytext.cli import jupytext as jupytext_cli
from jupytext.pandoc import PandocError
import jupytext
from .utils import requires_pandoc, requires_no_pandoc


@requires_pandoc
def test_pandoc_implicit(
    markdown="""# Lorem ipsum

**Lorem ipsum** dolor sit amet, consectetur adipiscing elit. Nunc luctus
bibendum felis dictum sodales.

``` code
print("hello")
```
""",
):
    nb = jupytext.reads(markdown, "md:pandoc")
    markdown2 = jupytext.writes(nb, "md")

    nb2 = jupytext.reads(markdown2, "md")
    compare_notebooks(nb2, nb)

    markdown3 = jupytext.writes(nb2, "md")
    compare(markdown3, markdown2)


@requires_pandoc
def test_pandoc_explicit(
    markdown="""::: {.cell .markdown}
# Lorem

**Lorem ipsum** dolor sit amet, consectetur adipiscing elit. Nunc luctus
bibendum felis dictum sodales.
:::""",
):
    nb = jupytext.reads(markdown, "md")

    markdown2 = jupytext.writes(nb, "md")
    compare("\n".join(markdown2.splitlines()[12:]), markdown)


@requires_pandoc
def test_pandoc_utf8_in_md(
    markdown="""::: {.cell .markdown}
# Utf-8 support

This is the greek letter $\\pi$: π
:::""",
):
    nb = jupytext.reads(markdown, "md")

    markdown2 = jupytext.writes(nb, "md")
    compare("\n".join(markdown2.splitlines()[12:]), markdown)


@requires_pandoc
def test_pandoc_utf8_in_nb(
    nb=new_notebook(
        cells=[
            new_markdown_cell(
                """# Utf-8 support

This is the greek letter $\\pi$: π"""
            )
        ]
    ),
):
    markdown = jupytext.writes(nb, "md:pandoc")
    nb2 = jupytext.reads(markdown, "md:pandoc")
    nb2.metadata.pop("jupytext")
    compare_notebooks(nb, nb2, "md:pandoc")


@requires_no_pandoc
def test_meaningfull_error_when_pandoc_is_missing(tmpdir):
    nb_file = tmpdir.join("notebook.ipynb")
    jupytext.write(new_notebook(), str(nb_file))

    with pytest.raises(
        PandocError, match="The Pandoc Markdown format requires 'pandoc>=2.7.2'"
    ):
        jupytext_cli([str(nb_file), "--to", "md:pandoc"])
