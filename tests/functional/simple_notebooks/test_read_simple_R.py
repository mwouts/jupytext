import pytest

import jupytext
from jupytext.compare import compare


@pytest.mark.parametrize("ext", [".r", ".R"])
def test_read_simple_file(
    ext,
    rnb="""#' ---
#' title: Simple file
#' ---

#' Here we have some text
#' And below we have some R code

f <- function(x) {
    x + 1
    }


h <- function(y)
    y + 1
""",
):
    nb = jupytext.reads(rnb, ext)
    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[0].source == "---\ntitle: Simple file\n---"
    assert nb.cells[1].cell_type == "markdown"
    assert (
        nb.cells[1].source == "Here we have some text\n" "And below we have some R code"
    )
    assert nb.cells[2].cell_type == "code"
    compare(
        nb.cells[2].source,
        """f <- function(x) {
    x + 1
    }""",
    )
    assert nb.cells[3].cell_type == "code"
    compare(
        nb.cells[3].source,
        """h <- function(y)
    y + 1""",
    )

    rnb2 = jupytext.writes(nb, ext)
    compare(rnb2, rnb)


@pytest.mark.parametrize("ext", [".r", ".R"])
def test_read_less_simple_file(
    ext,
    rnb="""#' ---
#' title: Less simple file
#' ---

#' Here we have some text
#' And below we have some R code

# This is a comment about function f
f <- function(x) {

    return(x+1)}


# And a comment on h
h <- function(y) {
    return(y-1)
}
""",
):
    nb = jupytext.reads(rnb, ext)

    assert len(nb.cells) == 4
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[0].source == "---\ntitle: Less simple file\n---"
    assert nb.cells[1].cell_type == "markdown"
    assert (
        nb.cells[1].source == "Here we have some text\n" "And below we have some R code"
    )
    assert nb.cells[2].cell_type == "code"
    compare(
        nb.cells[2].source,
        """# This is a comment about function f
f <- function(x) {

    return(x+1)}""",
    )
    assert nb.cells[3].cell_type == "code"
    compare(
        nb.cells[3].source,
        """# And a comment on h
h <- function(y) {
    return(y-1)
}""",
    )

    rnb2 = jupytext.writes(nb, ext)
    compare(rnb2, rnb)


@pytest.mark.parametrize("ext", [".r", ".R"])
def test_no_space_after_code(
    ext,
    rnb="""# -*- coding: utf-8 -*-
#' Markdown cell

f <- function(x)
{
    return(x+1)
}

#' And a new cell, and non ascii contênt
""",
):
    nb = jupytext.reads(rnb, ext)

    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "Markdown cell"
    assert nb.cells[1].cell_type == "code"
    assert (
        nb.cells[1].source
        == """f <- function(x)
{
    return(x+1)
}"""
    )
    assert nb.cells[2].cell_type == "markdown"
    assert nb.cells[2].source == "And a new cell, and non ascii contênt"

    rnb2 = jupytext.writes(nb, ext)
    compare(rnb2, rnb)


@pytest.mark.parametrize("ext", [".r", ".R"])
def test_read_write_script(
    ext,
    rnb="""#!/usr/bin/env Rscript
# coding=utf-8
print('Hello world')
""",
):
    nb = jupytext.reads(rnb, ext)
    rnb2 = jupytext.writes(nb, ext)
    compare(rnb2, rnb)


@pytest.mark.parametrize("ext", [".r", ".R"])
def test_escape_start_pattern(
    ext,
    rnb="""#' The code start pattern '#+' can
#' appear in code and markdown cells.

#' In markdown cells it is escaped like here:
#' #+ fig.width=12

# In code cells like this one, it is also escaped
# #+ cell_name language="python"
1 + 1
""",
):
    nb = jupytext.reads(rnb, ext)
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[2].cell_type == "code"
    assert (
        nb.cells[1].source
        == """In markdown cells it is escaped like here:
#+ fig.width=12"""
    )
    assert (
        nb.cells[2].source
        == """# In code cells like this one, it is also escaped
#+ cell_name language="python"
1 + 1"""
    )
    rnb2 = jupytext.writes(nb, ext)
    compare(rnb2, rnb)


@pytest.mark.parametrize("ext", [".r", ".R"])
def test_read_simple_r(
    ext,
    text="""# This is a very simple R file
# I expect to get three cells here.
#
# The first one is markdown. The two others
# are code cells

cars

plot(cars)
""",
):
    nb = jupytext.reads(text, ext)
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[2].cell_type == "code"
    assert nb.cells[1].source == "cars"
    assert nb.cells[2].source == "plot(cars)"
    text2 = jupytext.writes(nb, ext)
    compare(text2, text)
