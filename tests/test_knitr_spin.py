import sys
import pytest
import nbrmd
from .utils import list_all_notebooks

nbrmd.file_format_version.FILE_FORMAT_VERSION = {}


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('r_file',
                         list_all_notebooks('.R'))
def test_nbrmd_same_as_knitr_spin(r_file, tmpdir):
    nb = nbrmd.readf(r_file)
    rmd_nbrmd = nbrmd.writes(nb, ext='.Rmd')

    # Rmd file generated with spin(hair='R/spin.R', knit=FALSE)
    rmd_file = r_file.replace('.R', '.Rmd')

    with open(rmd_file) as fp:
        rmd_spin = fp.read()

    assert rmd_spin == rmd_nbrmd
