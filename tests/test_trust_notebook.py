import os
import shutil
import pytest
import jupytext
from jupytext.contentsmanager import TextFileContentsManager
from .utils import list_all_notebooks

jupytext.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.parametrize('nb_file', list_all_notebooks('.py'))
def test_py_notebooks_are_trusted(nb_file):
    cm = TextFileContentsManager()
    root, file = os.path.split(nb_file)
    cm.root_dir = root
    nb = cm.get(file)
    for cell in nb['content'].cells:
        assert cell.metadata.get('trusted', True)


@pytest.mark.parametrize('nb_file', list_all_notebooks('.Rmd'))
def test_rmd_notebooks_are_trusted(nb_file):
    cm = TextFileContentsManager()
    root, file = os.path.split(nb_file)
    cm.root_dir = root
    nb = cm.get(file)
    for cell in nb['content'].cells:
        assert cell.metadata.get('trusted', True)


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_ipynb_notebooks_can_be_trusted(nb_file, tmpdir):
    cm = TextFileContentsManager()
    root, file = os.path.split(nb_file)
    tmp_ipynb = str(tmpdir.join(file))
    py_file = file.replace('.ipynb', '.py')
    tmp_py = str(tmpdir.join(py_file))
    shutil.copy(nb_file, tmp_ipynb)

    cm.default_jupytext_formats = 'ipynb,py'
    cm.root_dir = str(tmpdir)
    nb = cm.get(file)

    # Sign notebook explicitely (save it, and reload without
    # validating to remove 'trusted' metadata in cells)
    cm.save(nb, py_file)
    cm.trust_notebook(py_file)

    nb = cm.get(file)
    for cell in nb['content'].cells:
        assert cell.metadata.get('trusted', True)

    # Remove py file, content should be the same
    os.remove(tmp_py)
    nb2 = cm.get(file)
    for cell in nb2['content'].cells:
        assert cell.metadata.get('trusted', True)

    assert nb['content'] == nb2['content']
