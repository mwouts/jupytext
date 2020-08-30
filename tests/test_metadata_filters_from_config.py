import nbformat
from nbformat.v4.nbbase import new_notebook, new_markdown_cell
from jupytext.cli import jupytext as jupytext_cli
from jupytext.compare import compare, compare_notebooks


def test_metadata_filters_from_config(tmpdir):
    cfg_file = tmpdir.join("jupytext.toml")
    nb_file = tmpdir.join("notebook.ipynb")
    md_file = tmpdir.join("notebook.md")

    cfg_file.write(
        """default_notebook_metadata_filter = "-all"
default_cell_metadata_filter = "-all"
"""
    )
    nb = new_notebook(
        cells=[new_markdown_cell("A markdown cell")],
        metadata={
            "kernelspec": {
                "display_name": "Python [conda env:.conda-week1]",
                "language": "python",
                "name": "conda-env-.conda-week1-py",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.3",
            },
            "nbsphinx": {"execute": "never"},
        },
    )
    nbformat.write(nb, str(nb_file))

    jupytext_cli([str(nb_file), "--to", "md"])
    md = md_file.read()

    compare(md, "A markdown cell\n")

    jupytext_cli([str(md_file), "--to", "notebook", "--update"])
    nb2 = nbformat.read(str(nb_file), as_version=4)

    del nb2.metadata["jupytext"]
    compare_notebooks(nb2, nb)
