import os
import sys
import subprocess
import pytest
import mock
import nbrmd
from .utils import list_all_notebooks


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(nbrmd.RMarkdownExporter, str),
                    reason=nbrmd.RMarkdownExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_and_read(nb_file):
    # Load notebook
    nb = nbrmd.readf(nb_file)

    # Export to Rmd using nbrmd package
    rmd1 = nbrmd.writes(nb, ext='.Rmd')

    # Export to Rmd using nbconvert exporter
    rmd_exporter = nbrmd.RMarkdownExporter()
    (rmd2, resources) = rmd_exporter.from_notebook_node(nb)

    assert rmd1 == rmd2


@pytest.mark.skipif(isinstance(nbrmd.PyNotebookExporter, str),
                    reason=nbrmd.PyNotebookExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_and_read_py(nb_file):
    # Load notebook
    nb = nbrmd.readf(nb_file)

    # Export to py using nbrmd package
    py1 = nbrmd.writes(nb, ext='.py')

    # Export to py using nbconvert exporter
    py_exporter = nbrmd.PyNotebookExporter()
    (py2, resources) = py_exporter.from_notebook_node(nb)

    assert py1 == py2


@pytest.mark.skipif(isinstance(nbrmd.PyNotebookExporter, str),
                    reason=nbrmd.PyNotebookExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_and_read_r(nb_file):
    # Load notebook
    nb = nbrmd.readf(nb_file)

    # Export to py using nbrmd package
    r1 = nbrmd.writes(nb, ext='.R')

    # Export to py using nbconvert exporter
    r_exporter = nbrmd.RNotebookExporter()
    (r2, resources) = r_exporter.from_notebook_node(nb)

    assert r1 == r2


pytest.importorskip('jupyter')


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(nbrmd.RMarkdownExporter, str),
                    reason=nbrmd.RMarkdownExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_cmd_line(nb_file, tmpdir):
    rmd_file = str(tmpdir.join('notebook.Rmd'))

    subprocess.call(['jupyter', 'nbconvert', '--to', 'rmarkdown',
                     nb_file, '--output', rmd_file])

    assert os.path.isfile(rmd_file)

    nb = nbrmd.readf(nb_file)
    with mock.patch('nbrmd.file_format_version.FILE_FORMAT_VERSION',
                    nbrmd.file_format_version.FILE_FORMAT_VERSION_ORG):
        rmd1 = nbrmd.writes(nb, ext='.Rmd')
    with open(rmd_file) as fp:
        rmd2 = fp.read()

    assert rmd1 == rmd2


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(nbrmd.PyNotebookExporter, str),
                    reason=nbrmd.PyNotebookExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_cmd_line_py(nb_file, tmpdir):
    py_file = str(tmpdir.join('notebook.py'))

    subprocess.call(['jupyter', 'nbconvert', '--to', 'pynotebook',
                     nb_file, '--output', py_file])

    assert os.path.isfile(py_file)

    nb = nbrmd.readf(nb_file)
    with mock.patch('nbrmd.file_format_version.FILE_FORMAT_VERSION',
                    nbrmd.file_format_version.FILE_FORMAT_VERSION_ORG):
        py1 = nbrmd.writes(nb, ext='.py')
    with open(py_file) as fp:
        py2 = fp.read()

    assert py1 == py2


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.skipif(isinstance(nbrmd.RNotebookExporter, str),
                    reason=nbrmd.RNotebookExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_cmd_line_R(nb_file, tmpdir):
    r_file = str(tmpdir.join('notebook.R'))

    subprocess.call(['jupyter', 'nbconvert', '--to', 'rnotebook',
                     nb_file, '--output', r_file])

    assert os.path.isfile(r_file)

    nb = nbrmd.readf(nb_file)
    with mock.patch('nbrmd.file_format_version.FILE_FORMAT_VERSION',
                    nbrmd.file_format_version.FILE_FORMAT_VERSION_ORG):
        r = nbrmd.writes(nb, ext='.R')
    with open(r_file) as fp:
        r2 = fp.read()

    assert r == r2
