import os
import pytest
from shutil import copyfile
from testfixtures import compare
from nbformat.v4.nbbase import new_notebook, new_code_cell
from .utils import list_notebooks, requires_black, requires_flake8, requires_autopep8

from jupytext import readf, writef
from jupytext.cli import system, jupytext, pipe_notebook
from jupytext.combine import black_invariant


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
        assert black_invariant(c1.source) == black_invariant(c2.source)
        # python representation is pep8
        assert 'lines_to_next_cell' not in c2.metadata
        # outputs are preserved
        assert c1.cell_type == c2.cell_type
        if c1.cell_type == 'code':
            compare(c1.outputs, c2.outputs)

    compare(nb1.metadata, nb2.metadata)


@requires_black
def test_pipe_into_black():
    nb_org = new_notebook(cells=[new_code_cell('1        +1')])
    nb_dest = new_notebook(cells=[new_code_cell('1 + 1')])

    nb_pipe = pipe_notebook(nb_org, 'black')
    compare(nb_dest, nb_pipe)


@requires_autopep8
def test_pipe_into_autopep8():
    nb_org = new_notebook(cells=[new_code_cell('1        +1')])
    nb_dest = new_notebook(cells=[new_code_cell('1 + 1')])

    nb_pipe = pipe_notebook(nb_org, 'autopep8 -')
    compare(nb_dest, nb_pipe)


@requires_flake8
def test_pipe_into_flake8():
    # Notebook OK
    nb = new_notebook(cells=[new_code_cell('# correct code\n1 + 1')])
    pipe_notebook(nb, 'flake8', update=False)

    # Notebook not OK
    nb = new_notebook(cells=[new_code_cell('incorrect code')])
    with pytest.raises(SystemExit):
        pipe_notebook(nb, 'flake8', update=False)


@requires_black
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py')[:1])
def test_apply_black_through_jupytext(tmpdir, nb_file):
    # Load real notebook metadata to get the 'auto' extension in --pipe-fmt to work
    metadata = readf(nb_file).metadata

    nb_org = new_notebook(cells=[new_code_cell('1        +1')], metadata=metadata)
    nb_black = new_notebook(cells=[new_code_cell('1 + 1')], metadata=metadata)

    os.makedirs(str(tmpdir.join('notebook_folder')))
    os.makedirs(str(tmpdir.join('script_folder')))

    tmp_ipynb = str(tmpdir.join('notebook_folder').join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('script_folder').join('notebook.py'))

    # Black in place
    writef(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, '--pipe', 'black'])
    nb_now = readf(tmp_ipynb)
    compare(nb_black, nb_now)

    # Write to another folder using dots
    script_fmt = os.path.join('..', 'script_folder//py:percent')
    writef(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, '--to', script_fmt, '--pipe', 'black'])
    assert os.path.isfile(tmp_py)
    nb_now = readf(tmp_py)
    nb_now.metadata = metadata
    compare(nb_black, nb_now)
    os.remove(tmp_py)

    # Map to another folder based on file name
    writef(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, '--from', 'notebook_folder//ipynb', '--to', 'script_folder//py:percent',
              '--pipe', 'black', '--check', 'flake8'])
    assert os.path.isfile(tmp_py)
    nb_now = readf(tmp_py)
    nb_now.metadata = metadata
    compare(nb_black, nb_now)


@requires_black
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py')[:1])
def test_apply_black_and_sync_on_paired_notebook(tmpdir, nb_file):
    # Load real notebook metadata to get the 'auto' extension in --pipe-fmt to work
    metadata = readf(nb_file).metadata
    metadata['jupytext'] = {'formats': 'ipynb,py'}
    assert 'language_info' in metadata

    nb_org = new_notebook(cells=[new_code_cell('1        +1')], metadata=metadata)
    nb_black = new_notebook(cells=[new_code_cell('1 + 1')], metadata=metadata)

    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))

    # Black in place
    writef(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, '--pipe', 'black', '--sync'])

    nb_now = readf(tmp_ipynb)
    compare(nb_black, nb_now)
    assert 'language_info' in nb_now.metadata

    nb_now = readf(tmp_py)
    nb_now.metadata['jupytext'].pop('text_representation')
    nb_black.metadata.pop('language_info')
    compare(nb_black, nb_now)
