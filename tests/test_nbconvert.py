import nbrmd
import pytest
from .utils import list_all_notebooks
import subprocess
import os


@pytest.mark.skipif(isinstance(nbrmd.RMarkdownExporter, str),
                    reason=nbrmd.RMarkdownExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_and_read(nb_file):
    # Load notebook
    nb = nbrmd.readf(nb_file)

    # Export to Rmd using nbrmd package
    rmd1 = nbrmd.writes(nb)

    # Export to Rmd using nbconvert exporter
    rmd_exporter = nbrmd.RMarkdownExporter()
    (rmd2, resources) = rmd_exporter.from_notebook_node(nb)

    assert rmd1 == rmd2


pytest.importorskip('jupyter')


@pytest.mark.skipif(isinstance(nbrmd.RMarkdownExporter, str),
                    reason=nbrmd.RMarkdownExporter)
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_nbconvert_cmd_line(nb_file, tmpdir):
    rmd_file = str(tmpdir.join('notebook.Rmd'))

    subprocess.call(['jupyter', 'nbconvert', '--to', 'rmarkdown',
                     nb_file, '--output', rmd_file])

    assert os.path.isfile(rmd_file)

    nb = nbrmd.readf(nb_file)
    rmd1 = nbrmd.writes(nb)
    with open(rmd_file) as fp:
        rmd2 = fp.read()

    assert rmd1 == rmd2
