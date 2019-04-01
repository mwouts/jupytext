import os
import sys
import re
import pytest
from jupytext.cli import system
from jupytext.cell_reader import rst2md

skip_if_dict_is_not_ordered = pytest.mark.skipif(
    sys.version_info < (3, 6),
    reason="unordered dict result in changes in chunk options")


def tool_version(tool):
    try:
        return system(tool, '--version')
    except OSError, SystemExit:  # pragma: no cover
        return None


requires_jupytext_installed = pytest.mark.skipif(not tool_version('jupytext'), reason='jupytext not installed')
requires_black = pytest.mark.skipif(not tool_version('black'), reason='black not found')
requires_flake8 = pytest.mark.skipif(not tool_version('flake8'), reason='flake8 not found')
requires_autopep8 = pytest.mark.skipif(not tool_version('autopep8'), reason='autopep8 not found')
requires_sphinx_gallery = pytest.mark.skipif(not rst2md, reason='sphinx_gallery not available')


def list_notebooks(path='ipynb', skip='World'):
    """All notebooks in the directory notebooks/path,
    or in the package itself"""
    if path == 'ipynb':
        return list_notebooks('ipynb_julia', skip=skip) + \
               list_notebooks('ipynb_py', skip=skip) + \
               list_notebooks('ipynb_R', skip=skip)

    nb_path = os.path.dirname(os.path.abspath(__file__))
    if path.startswith('.'):
        nb_path = os.path.join(nb_path, path)
    else:
        nb_path = os.path.join(nb_path, 'notebooks', path)

    if skip:
        skip_re = re.compile('.*' + skip + '.*')
        notebooks = [os.path.join(nb_path, nb_file) for nb_file in os.listdir(nb_path) if not skip_re.match(nb_file)]
    else:
        notebooks = [os.path.join(nb_path, nb_file) for nb_file in os.listdir(nb_path)]

    assert notebooks
    return notebooks
