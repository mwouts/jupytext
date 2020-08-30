import nbformat
from nbformat.v4.nbbase import new_notebook, new_code_cell
from jupytext.cli import jupytext as jupytext_cli
from jupytext.languages import _JUPYTER_LANGUAGES_LOWER_AND_UPPER
from jupytext.compare import compare_notebooks


def test_custom_cell_magics(
    tmpdir,
    nb=new_notebook(
        cells=[
            new_code_cell("%%sql -o tables -q\n SHOW TABLES"),
            new_code_cell(
                """%%configure -f
{"executorMemory": "3072M", "executorCores": 4, "numExecutors":10}"""
            ),
            new_code_cell("%%local\na=1"),
        ]
    ),
):
    cfg_file = tmpdir.join("jupytext.toml")
    nb_file = tmpdir.join("notebook.ipynb")
    py_file = tmpdir.join("notebook.py")

    cfg_file.write('custom_cell_magics = "configure,local"')
    assert "configure" not in _JUPYTER_LANGUAGES_LOWER_AND_UPPER
    assert "logs" not in _JUPYTER_LANGUAGES_LOWER_AND_UPPER

    nbformat.write(nb, str(nb_file))

    jupytext_cli([str(nb_file), "--to", "py"])
    py = py_file.read()

    for line in py.splitlines():
        if line:
            assert line.startswith("# "), line

    jupytext_cli([str(py_file), "--to", "notebook"])
    nb2 = nbformat.read(str(nb_file), as_version=4)

    compare_notebooks(nb2, nb)
