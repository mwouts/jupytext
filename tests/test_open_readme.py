import os
import shutil
import pytest
import nbrmd


@pytest.fixture()
def readme():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'README.md')


def test_open_readme(readme, tmpdir):
    rmd_file = str(tmpdir.join('README.Rmd'))
    shutil.copyfile(readme, rmd_file)
    nb = nbrmd.readf(rmd_file)
