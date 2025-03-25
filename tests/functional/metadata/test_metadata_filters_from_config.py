import nbformat
import pytest
import yaml
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

from jupytext.cli import jupytext as jupytext_cli
from jupytext.compare import compare, compare_notebooks
from jupytext.header import _JUPYTER_METADATA_NAMESPACE


def test_metadata_filters_from_config(tmpdir):
    cfg_file = tmpdir.join("jupytext.toml")
    nb_file = tmpdir.join("notebook.ipynb")
    md_file = tmpdir.join("notebook.md")

    cfg_file.write(
        """notebook_metadata_filter = "-all"
cell_metadata_filter = "-all"
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
    compare_notebooks(nb2, nb)


@pytest.mark.requires_myst
def test_root_level_metadata_filters_from_config(tmpdir):
    cfg_file = tmpdir.join("jupytext.toml")
    nb_file = tmpdir.join("notebook.ipynb")
    md_file = tmpdir.join("notebook.md")

    cfg_file.write(
        """root_level_metadata_filter = "-all"
"""
    )
    nb = new_notebook(
        cells=[new_code_cell("1 + 1")],
        metadata={
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
    )
    nbformat.write(nb, str(nb_file))

    jupytext_cli([str(nb_file), "--to", "md:myst"])
    header = next(yaml.safe_load_all(md_file.read()))
    assert list(header) == [_JUPYTER_METADATA_NAMESPACE]

    jupytext_cli([str(md_file), "--to", "notebook", "--update"])
    nb2 = nbformat.read(str(nb_file), as_version=4)
    compare_notebooks(nb2, nb)
