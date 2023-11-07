from nbformat.v4.nbbase import new_code_cell


def test_cell_id_is_not_random():
    id1 = new_code_cell().id
    id2 = new_code_cell().id

    n1 = int(id1.split("-")[1])
    n2 = int(id2.split("-")[1])
    assert n2 == n1 + 1
