import nbformat
from nbformat.v4.nbbase import new_notebook
from jupytext.compare import compare
import jupytext


def test_save_ipynb_with_jupytext_has_final_newline(tmpdir):
    nb = new_notebook()
    file_jupytext = str(tmpdir.join("jupytext.ipynb"))
    file_nbformat = str(tmpdir.join("nbformat.ipynb"))

    jupytext.write(nb, file_jupytext)
    with open(file_nbformat, "w") as fp:
        nbformat.write(nb, fp)

    with open(file_jupytext) as fp:
        text_jupytext = fp.read()

    with open(file_nbformat) as fp:
        text_nbformat = fp.read()

    compare(text_jupytext, text_nbformat)
