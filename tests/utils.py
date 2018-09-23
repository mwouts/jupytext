import os
import sys
import pytest

skip_if_dict_is_not_ordered = pytest.mark.skipif(
    sys.version_info < (3, 6),
    reason="unordered dict result in changes in chunk options")


def list_notebooks(path='ipynb', skip=''):
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
    notebooks = [os.path.join(nb_path, nb_file) for nb_file in
                 os.listdir(nb_path) if not skip or skip not in nb_file]

    assert notebooks
    return notebooks
