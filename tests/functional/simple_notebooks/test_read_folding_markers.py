import jupytext
from jupytext.compare import compare


# region Folding markers as cell boundaries
# region Sub-region with metadata {"key": "value"}
def test_mark_cell_with_vim_folding_markers(
    script="""# This is a markdown cell

# {{{ And this is a foldable code region with metadata {"key": "value"}
a = 1

b = 2

c = 3
# }}}
""",
):
    nb = jupytext.reads(script, "py")
    assert nb.metadata["jupytext"]["cell_markers"] == "{{{,}}}"
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "This is a markdown cell"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "a = 1\n\nb = 2\n\nc = 3"
    assert nb.cells[1].metadata == {
        "title": "And this is a foldable code region with metadata",
        "key": "value",
    }

    script2 = jupytext.writes(nb, "py")
    compare(script2, script)


# endregion


def test_mark_cell_with_vscode_pycharm_folding_markers(
    script="""# This is a markdown cell

# region And this is a foldable code region with metadata {"key": "value"}
a = 1

b = 2

c = 3
# endregion
""",
):
    nb = jupytext.reads(script, "py")
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "This is a markdown cell"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "a = 1\n\nb = 2\n\nc = 3"
    assert nb.cells[1].metadata == {
        "title": "And this is a foldable code region with metadata",
        "key": "value",
    }

    script2 = jupytext.writes(nb, "py")
    compare(script2, script)


def test_mark_cell_with_no_title_and_inner_region(
    script="""# This is a markdown cell

# region {"key": "value"}
a = 1

# region An inner region
b = 2
# endregion

def f(x):
    return x + 1


# endregion


d = 4
""",
):
    nb = jupytext.reads(script, "py")
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "This is a markdown cell"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == '# region {"key": "value"}\na = 1'
    assert nb.cells[2].cell_type == "code"
    assert nb.cells[2].metadata["title"] == "An inner region"
    assert nb.cells[2].source == "b = 2"
    assert nb.cells[3].cell_type == "code"
    assert nb.cells[3].source == "def f(x):\n    return x + 1"
    assert nb.cells[4].cell_type == "code"
    assert nb.cells[4].source == "# endregion"
    assert nb.cells[5].cell_type == "code"
    assert nb.cells[5].source == "d = 4"
    assert len(nb.cells) == 6

    script2 = jupytext.writes(nb, "py")
    compare(script2, script)


# endregion


def test_adjacent_regions(
    script="""# region global
# region innermost
a = 1

b = 2
# endregion
# endregion
""",
):
    nb = jupytext.reads(script, "py")
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "# region global"
    assert nb.cells[1].cell_type == "code"
    assert nb.cells[1].source == "a = 1\n\nb = 2"
    assert nb.cells[2].cell_type == "code"
    assert nb.cells[2].source == "# endregion"

    script2 = jupytext.writes(nb, "py")
    compare(script2, script)


def test_indented_markers_are_ignored(
    script="""# region global
    # region indented
a = 1

b = 2
    # endregion
# endregion
""",
):
    nb = jupytext.reads(script, "py")
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"

    script2 = jupytext.writes(nb, "py")
    compare(script2, script)
