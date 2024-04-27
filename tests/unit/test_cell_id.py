from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_raw_cell


def test_cell_id_is_not_random():
    assert new_code_cell().id == "cell-1"
    assert new_code_cell().id == "cell-2"
    assert new_markdown_cell().id == "cell-3"
    assert new_raw_cell().id == "cell-4"
