import pytest
from shutil import copyfile
from testfixtures import compare
from .utils import list_notebooks
from jupytext import readf
from jupytext.cli import system, jupytext


def black_version():
    try:
        return system('black', ['--version'])
    except FileNotFoundError:  # pragma: no cover
        return None


requires_black = pytest.mark.skipif(not black_version(), reason='black not found')


def remove_spaces_and_commas(text, chars=[' ', '\n', ',', "'", '"']):
    for char in chars:
        text = text.replace(char, '')
    return text


@requires_black
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_apply_black_on_python_notebooks(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    copyfile(nb_file, tmp_ipynb)

    jupytext(args=[tmp_ipynb, '--to', 'py:percent'])
    system('black', tmp_py)
    jupytext(args=[tmp_py, '--to', 'ipynb', '--update'])

    nb1 = readf(nb_file)
    nb2 = readf(tmp_ipynb)

    assert len(nb1.cells) == len(nb2.cells)
    for c1, c2 in zip(nb1.cells, nb2.cells):
        # same content (almost)
        assert remove_spaces_and_commas(c1.source) == remove_spaces_and_commas(c2.source)
        # python representation is pep8
        assert 'lines_to_next_cell' not in c2.metadata

    compare(nb1.metadata, nb2.metadata)
