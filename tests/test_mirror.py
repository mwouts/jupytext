"""Here we generate mirror representation of py, Rmd and ipynb files
as py or ipynb, and make sure that these representations minimally
change on new releases.
"""

import os
import sys
import pytest
from testfixtures import compare
import nbrmd
from .utils import list_all_notebooks, list_r_notebooks

nbrmd.file_format_version.FILE_FORMAT_VERSION = {}


def mirror_file(nb_file):
    dir, file = os.path.split(nb_file)
    if nb_file.endswith('.py'):
        return os.path.join(dir, 'mirror', file.replace('.py', '.ipynb'))
    if nb_file.endswith('.Rmd'):
        return os.path.join(dir, 'mirror', file.replace('.Rmd', '.ipynb'))
    return os.path.join(dir, 'mirror', file.replace('.ipynb', '.py'))


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('py_file',
                         [py_file for py_file in list_all_notebooks('.py')
                          if py_file.find('notebook_sample') > 0])
def test_py_unchanged_py(py_file):
    with open(py_file, encoding='utf-8') as fp:
        py = fp.read()

    ipynb_file = mirror_file(py_file)

    if not os.path.isfile(ipynb_file):
        nb = nbrmd.readf(py_file)
        nbrmd.writef(nb, ipynb_file)

    py_ref = nbrmd.writes(nbrmd.readf(ipynb_file), ext='.py')
    compare(py, py_ref)


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('rmd_file', list_all_notebooks('.Rmd'))
def test_rmd_unchanged(rmd_file):
    with open(rmd_file, encoding='utf-8') as fp:
        rmd = fp.read()

    ipynb_file = mirror_file(rmd_file)

    if not os.path.isfile(ipynb_file):
        nb = nbrmd.readf(rmd_file)
        nbrmd.writef(nb, ipynb_file)

    rmd_ref = nbrmd.writes(nbrmd.readf(ipynb_file), ext='.Rmd')
    compare(rmd, rmd_ref)


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('nb_file', list_all_notebooks('.ipynb'))
def test_py_unchanged_ipynb(nb_file):
    py_file = mirror_file(nb_file)

    if not os.path.isfile(py_file):
        nb = nbrmd.readf(nb_file)
        nbrmd.writef(nb, py_file)

    with open(py_file, encoding='utf-8') as fp:
        py_ref = fp.read()

    py = nbrmd.writes(nbrmd.readf(nb_file), ext='.py')
    compare(py, py_ref)


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('nb_file', list_r_notebooks('.ipynb'))
def test_R_unchanged_ipynb(nb_file):
    r_file = mirror_file(nb_file).replace('.py', '.R')

    if not os.path.isfile(r_file):
        nb = nbrmd.readf(nb_file)
        nbrmd.writef(nb, r_file)

    with open(r_file, encoding='utf-8') as fp:
        r_ref = fp.read()

    r = nbrmd.writes(nbrmd.readf(nb_file), ext='.R')
    compare(r, r_ref)
