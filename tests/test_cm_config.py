import os

try:
    import unittest.mock as mock
except ImportError:
    import mock
from nbformat.v4.nbbase import new_notebook, new_markdown_cell, new_code_cell
import jupytext

SAMPLE_NOTEBOOK = new_notebook(
    cells=[new_markdown_cell("A Markdown cell"), new_code_cell("# A code cell\n1 + 1")]
)


def test_local_config_overrides_cm_config(tmpdir):
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = "ipynb,py"

    nested = tmpdir.mkdir("nested")
    with open(str(nested.join(".jupytext.yml")), "w") as fp:
        fp.write("default_jupytext_formats: ''\n")

    cm.save(dict(type="notebook", content=SAMPLE_NOTEBOOK), "notebook.ipynb")
    assert os.path.isfile(str(tmpdir.join("notebook.ipynb")))
    assert os.path.isfile(str(tmpdir.join("notebook.py")))

    cm.save(dict(type="notebook", content=SAMPLE_NOTEBOOK), "nested/notebook.ipynb")
    assert os.path.isfile(str(nested.join("notebook.ipynb")))
    assert not os.path.isfile(str(nested.join("notebook.py")))


def test_config_file_is_called_just_once(tmpdir, n=2):
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    nb_files = [str(tmpdir.join("notebook{}.ipynb".format(i))) for i in range(n)]

    for nb_file in nb_files:
        jupytext.write(SAMPLE_NOTEBOOK, nb_file)

    mock_config = mock.MagicMock(return_value=None)

    with mock.patch("jupytext.contentsmanager.load_jupytext_config", mock_config):
        for i in range(n):
            cm.get("notebook{}.ipynb".format(i), content=False)

    # Listing the contents should not call the config more than once
    assert mock_config.call_count == 1
