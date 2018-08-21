import os
import shutil
import pytest
from nbrmd.contentsmanager import RmdFileContentsManager
from .utils import list_all_notebooks


@pytest.mark.parametrize('nb_file', list_all_notebooks('.py'))
def test_py_notebooks_are_trusted(nb_file):
    cm = RmdFileContentsManager()
    root, file = os.path.split(nb_file)
    cm.root_dir = root
    nb = cm.get(file)
    assert cm.notary.check_cells(nb['content'])


@pytest.mark.parametrize('nb_file', list_all_notebooks('.Rmd'))
def test_rmd_notebooks_are_trusted(nb_file):
    cm = RmdFileContentsManager()
    root, file = os.path.split(nb_file)
    cm.root_dir = root
    nb = cm.get(file)
    assert cm.notary.check_cells(nb['content'])


@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_ipynb_notebooks_can_be_trusted(nb_file, tmpdir):
    cm = RmdFileContentsManager()
    root, file = os.path.split(nb_file)
    tmp_ipynb = str(tmpdir.join(file))
    py_file = file.replace('.ipynb', '.py')
    tmp_py = str(tmpdir.join(py_file))
    shutil.copy(nb_file, tmp_ipynb)

    cm.default_nbrmd_formats = 'ipynb,py'
    cm.root_dir = str(tmpdir)
    nb = cm.get(file)

    # Sign notebook explicitely (save it, and reload without
    # validating to remove 'trusted' metadata in cells)
    cm.save(nb, py_file)
    nb = cm._read_notebook(tmp_py)
    cm.notary.sign(nb)

    nb = cm.get(file)
    assert cm.notary.check_cells(nb['content'])

    # Remove py file, content should be the same
    os.remove(tmp_py)
    nb2 = cm.get(file)
    assert cm.notary.check_cells(nb2['content'])

    assert nb['content'] == nb2['content']
