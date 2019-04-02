from testfixtures import compare
import jupytext


# region Folding markers as cell boundaries
# region Sub-region with metadata {"key": "value"}
def test_mark_cell_with_vim_folding_markers(
        script="""# This is a markdown cell

# {{{ And this is a foldable code region with metadata {"key": "value"}
a = 1

b = 2

c = 3
# }}}
"""):
    nb = jupytext.reads(script, 'py')
    assert nb.metadata['jupytext']['cell_markers'] == '{{{,}}}'
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[0].source == 'This is a markdown cell'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == 'a = 1\n\nb = 2\n\nc = 3'
    assert nb.cells[1].metadata == {'title': 'And this is a foldable code region with metadata', 'key': 'value'}

    script2 = jupytext.writes(nb, 'py')
    compare(script, script2)


# endregion


def test_mark_cell_with_vscode_pycharm_folding_markers(
        script="""# This is a markdown cell

# region And this is a foldable code region with metadata {"key": "value"}
a = 1

b = 2

c = 3
# endregion
"""):
    nb = jupytext.reads(script, 'py')
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[0].source == 'This is a markdown cell'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].source == 'a = 1\n\nb = 2\n\nc = 3'
    assert nb.cells[1].metadata == {'title': 'And this is a foldable code region with metadata', 'key': 'value'}

    script2 = jupytext.writes(nb, 'py')
    compare(script, script2)


def test_mark_cell_with_no_title_and_inner_region(
        script="""# This is a markdown cell

# region {"key": "value"}
a = 1

# region An inner region
b = 2
# endregion

c = 3
# endregion
"""):
    nb = jupytext.reads(script, 'py')
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == 'markdown'
    assert nb.cells[0].source == 'This is a markdown cell'
    assert nb.cells[1].cell_type == 'code'
    assert nb.cells[1].metadata == {'key': 'value'}

    script2 = jupytext.writes(nb, 'py')
    compare(script, script2)
# endregion
