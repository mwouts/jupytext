import os
import stat
import mock
import pytest
from shutil import copyfile
from testfixtures import compare
from argparse import ArgumentTypeError
from nbformat.v4.nbbase import new_notebook
from jupytext import __version__
from jupytext import readf, writef, writes
from jupytext.cli import convert_notebook_files, cli_jupytext, jupytext, system, str2bool
from jupytext.compare import compare_notebooks
from jupytext.paired_paths import paired_paths
from .utils import list_notebooks


def test_str2bool():
    assert str2bool('d') is None
    assert str2bool('TRUE') is True
    assert str2bool('0') is False
    with pytest.raises(ArgumentTypeError):
        str2bool('UNEXPECTED')


@pytest.mark.parametrize('nb_file', list_notebooks())
def test_cli_single_file(nb_file):
    assert cli_jupytext([nb_file] + ['--to', 'py']).notebooks == [nb_file]


@pytest.mark.parametrize('nb_files', [list_notebooks()])
def test_cli_multiple_files(nb_files):
    assert cli_jupytext(nb_files + ['--to', 'py']).notebooks == nb_files


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_convert_single_file_in_place(nb_file, tmpdir):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    base, ext = os.path.splitext(nb_org)
    nb_other = base + '.py'

    copyfile(nb_file, nb_org)
    convert_notebook_files([nb_org], fmt='py')

    nb1 = readf(nb_org)
    nb2 = readf(nb_other)

    compare_notebooks(nb1, nb2)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb') + list_notebooks('Rmd'))
def test_convert_single_file(nb_file, capsys):
    nb1 = readf(nb_file)
    pynb = writes(nb1, 'py')
    convert_notebook_files([nb_file], fmt='py', output='-')

    out, err = capsys.readouterr()
    assert err == ''
    compare(out, pynb)


def test_jupytext_version(capsys):
    jupytext(['--version'])

    out, err = capsys.readouterr()
    assert err == ''
    compare(out, __version__ + '\n')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_cpp'))
def test_to_cpluplus(nb_file, capsys):
    nb1 = readf(nb_file)
    text_cpp = writes(nb1, 'cpp')
    jupytext([nb_file, '--to', 'c++', '--output', '-'])

    out, err = capsys.readouterr()
    assert err == ''
    compare(out, text_cpp)


@pytest.mark.parametrize('nb_files', [list_notebooks('ipynb_py')])
def test_convert_multiple_file(nb_files, tmpdir):
    nb_orgs = []
    nb_others = []

    for nb_file in nb_files:
        nb_org = str(tmpdir.join(os.path.basename(nb_file)))
        base, ext = os.path.splitext(nb_org)
        nb_other = base + '.py'
        copyfile(nb_file, nb_org)
        nb_orgs.append(nb_org)
        nb_others.append(nb_other)

    convert_notebook_files(nb_orgs, fmt='py')

    for nb_org, nb_other in zip(nb_orgs, nb_others):
        nb1 = readf(nb_org)
        nb2 = readf(nb_other)
        compare_notebooks(nb1, nb2)


def test_error_not_notebook_ext_input(nb_file='notebook.ext'):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], fmt='py')


def test_error_not_notebook_ext_dest1(nb_file=list_notebooks()[0]):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], fmt='ext')


def test_error_not_notebook_ext_output(
        nb_file=list_notebooks()[0]):
    with pytest.raises(TypeError):
        cli_jupytext([nb_file, '-o', 'not.ext'])


def test_error_no_ext(nb_file=list_notebooks()[0]):
    with pytest.raises(ValueError):
        cli_jupytext([nb_file])


def test_error_not_same_ext(nb_file=list_notebooks()[0]):
    with pytest.raises(TypeError):
        convert_notebook_files([nb_file], fmt='py', output='not.ext')


def test_error_update_not_ipynb(nb_file=list_notebooks()[0]):
    with pytest.raises(ValueError):
        cli_jupytext([nb_file, '--to', 'py', '--update'])


def test_error_multiple_input(nb_files=list_notebooks()):
    with pytest.raises(ValueError):
        convert_notebook_files(nb_files, fmt='py', output='notebook.py')


def test_combine_same_version_ok(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))

    with open(tmp_nbpy, 'w') as fp:
        fp.write("""# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '1.2'
# ---

# New cell
""")

    nb = new_notebook(metadata={'jupytext_formats': 'ipynb,py'})
    writef(nb, tmp_ipynb)

    # to jupyter notebook
    jupytext(args=[tmp_nbpy, '--to', 'ipynb', '--update'])
    # test round trip
    jupytext(args=[tmp_nbpy, '--to', 'notebook', '--test'])
    # test ipynb to rmd
    jupytext(args=[tmp_ipynb, '--to', 'rmarkdown'])

    nb = readf(tmp_ipynb)
    cells = nb['cells']
    assert len(cells) == 1
    assert cells[0].cell_type == 'markdown'
    assert cells[0].source == 'New cell'

    nb = readf(tmp_rmd)
    cells = nb['cells']
    assert len(cells) == 1
    assert cells[0].cell_type == 'markdown'
    assert cells[0].source == 'New cell'


def test_combine_lower_version_raises(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    with open(tmp_nbpy, 'w') as fp:
        fp.write("""# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '0.0'
# ---

# New cell
""")

    nb = new_notebook(metadata={'jupytext_formats': 'ipynb,py'})
    writef(nb, tmp_ipynb)

    with pytest.raises(SystemExit):
        jupytext(args=[tmp_nbpy, '--to', 'ipynb', '--update'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_ipynb_to_py_then_update_test(nb_file, tmpdir):
    """Reproduce https://github.com/mwouts/jupytext/issues/83"""
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    copyfile(nb_file, tmp_ipynb)

    jupytext(['--to', 'py', tmp_ipynb])
    jupytext(['--test', '--update', '--to', 'ipynb', tmp_nbpy])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_convert_to_percent_format(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    copyfile(nb_file, tmp_ipynb)

    jupytext(['--to', 'py:percent', tmp_ipynb])

    with open(tmp_nbpy) as stream:
        py_script = stream.read()
        assert 'format_name: percent' in py_script

    nb1 = readf(tmp_ipynb)
    nb2 = readf(tmp_nbpy)

    compare_notebooks(nb1, nb2)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_convert_to_percent_format_and_keep_magics(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    copyfile(nb_file, tmp_ipynb)

    jupytext(['--to', 'py:percent', '--comment-magics', 'no', tmp_ipynb])

    with open(tmp_nbpy) as stream:
        py_script = stream.read()
        assert 'format_name: percent' in py_script
        assert '# %%time' not in py_script

    nb1 = readf(tmp_ipynb)
    nb2 = readf(tmp_nbpy)

    compare_notebooks(nb1, nb2)


def test_pre_commit_hook(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    nb = new_notebook(cells=[])

    def git(*args):
        print(system('git', *args, cwd=str(tmpdir)))

    git('init')
    git('status')
    hook = str(tmpdir.join('.git/hooks/pre-commit'))
    with open(hook, 'w') as fp:
        fp.write('#!/bin/sh\n'
                 'jupytext --to py:light --pre-commit\n')

    st = os.stat(hook)
    os.chmod(hook, st.st_mode | stat.S_IEXEC)

    writef(nb, tmp_ipynb)
    assert os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)

    git('add', 'notebook.ipynb')
    git('status')
    git('commit', '-m', 'created')
    git('status')

    assert os.path.isfile(tmp_py)

    git('rm', 'notebook.ipynb')
    git('status')
    git('commit', '-m', 'deleted')
    git('status')

    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)


def test_pre_commit_hook_py_to_ipynb_and_md(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_md = str(tmpdir.join('notebook.md'))
    nb = new_notebook(cells=[])

    def git(*args):
        print(system('git', *args, cwd=str(tmpdir)))

    git('init')
    git('status')
    hook = str(tmpdir.join('.git/hooks/pre-commit'))
    with open(hook, 'w') as fp:
        fp.write('#!/bin/sh\n'
                 'jupytext --from py:light --to ipynb --pre-commit\n'
                 'jupytext --from py:light --to md --pre-commit\n')

    st = os.stat(hook)
    os.chmod(hook, st.st_mode | stat.S_IEXEC)

    writef(nb, tmp_py)
    assert os.path.isfile(tmp_py)
    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_md)

    git('add', 'notebook.py')
    git('status')
    git('commit', '-m', 'created')
    git('status')

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_md)

    git('rm', 'notebook.py')
    git('status')
    git('commit', '-m', 'deleted')
    git('status')

    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)
    assert not os.path.isfile(tmp_md)


def test_manual_call_of_pre_commit_hook(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    nb = new_notebook(cells=[])
    os.chdir(str(tmpdir))

    def system_in_tmpdir(*args):
        return system(*args, cwd=str(tmpdir))

    def git(*args):
        print(system_in_tmpdir('git', *args))

    git('init')
    git('status')

    def hook():
        with mock.patch('jupytext.cli.system', system_in_tmpdir):
            jupytext(['--to', 'py', '--pre-commit'])

    writef(nb, tmp_ipynb)
    assert os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)

    git('add', 'notebook.ipynb')
    git('status')
    hook()
    git('commit', '-m', 'created')
    git('status')

    assert os.path.isfile(tmp_py)

    git('rm', 'notebook.ipynb')
    git('status')
    hook()
    git('commit', '-m', 'deleted')
    git('status')

    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)


@pytest.mark.parametrize('py_file', list_notebooks('python'))
def test_set_formats(py_file, tmpdir):
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    copyfile(py_file, tmp_py)

    jupytext(['--to', 'ipynb', tmp_py, '--set-formats', 'ipynb,py:light'])

    nb = readf(tmp_ipynb)
    assert nb.metadata['jupytext']['formats'] == 'ipynb,py:light'


@pytest.mark.parametrize('py_file', list_notebooks('python'))
def test_update_metadata(py_file, tmpdir, capsys):
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    copyfile(py_file, tmp_py)

    jupytext(['--to', 'ipynb', tmp_py, '--update-metadata', '{"jupytext":{"formats":"ipynb,py:light"}}'])

    nb = readf(tmp_ipynb)
    assert nb.metadata['jupytext']['formats'] == 'ipynb,py:light'

    jupytext(['--to', 'py', tmp_ipynb, '--update-metadata', '{"jupytext":{"formats":null}}'])

    nb = readf(tmp_py)
    assert 'formats' not in nb.metadata['jupytext']

    with pytest.raises(SystemExit):
        jupytext(['--to', 'ipynb', tmp_py, '--update-metadata', '{"incorrect": "JSON"'])

    out, err = capsys.readouterr()
    assert 'invalid' in err


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_paired_paths(nb_file, tmpdir, capsys):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    nb = readf(nb_file)
    nb.metadata.setdefault('jupytext', {})['formats'] = 'ipynb,_light.py,_percent.py:percent'
    writef(nb, tmp_ipynb)

    jupytext(['--paired-paths', tmp_ipynb])

    out, err = capsys.readouterr()
    assert not err

    formats = nb.metadata.get('jupytext', {}).get('formats')
    assert set(out.splitlines()).union([tmp_ipynb]) == set([path for path, _ in paired_paths(tmp_ipynb, formats)])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_sync(nb_file, tmpdir, capsys):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))
    nb = readf(nb_file)
    writef(nb, tmp_ipynb)

    # Test that sync works (does nothing) when notebook is not paired
    jupytext(['--sync', tmp_ipynb])
    out, err = capsys.readouterr()
    assert 'not paired' in err

    # Now with a pairing information
    nb.metadata.setdefault('jupytext', {})['formats'] = 'ipynb,py,Rmd'
    writef(nb, tmp_ipynb)

    # Test that missing files are created
    jupytext(['--sync', tmp_ipynb])

    assert os.path.isfile(tmp_py)
    compare_notebooks(nb, readf(tmp_py))

    assert os.path.isfile(tmp_rmd)
    compare_notebooks(nb, readf(tmp_rmd), 'Rmd')

    # Now we keep only the first four cells and save to Rmd
    nb.cells = nb.cells[:4]
    writef(nb, tmp_rmd, 'Rmd')
    jupytext(['--sync', tmp_ipynb])

    nb2 = readf(tmp_ipynb)
    compare_notebooks(nb, nb2, 'Rmd', compare_outputs=True)

    # Now we keep only the first two cells and save to py
    nb.cells = nb.cells[:4]
    writef(nb, tmp_py, 'py')
    jupytext(['--sync', tmp_ipynb])

    nb2 = readf(tmp_ipynb)
    compare_notebooks(nb, nb2, compare_outputs=True)


@pytest.mark.parametrize('nb_file,ext',
                         [(nb_file, '.py') for nb_file in list_notebooks('ipynb_py')] +
                         [(nb_file, '.R') for nb_file in list_notebooks('ipynb_R')] +
                         [(nb_file, '.jl') for nb_file in list_notebooks('ipynb_julia')])
def test_cli_can_infer_jupytext_format(nb_file, ext, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_text = str(tmpdir.join('notebook' + ext))
    nb = readf(nb_file)

    # Light format to Jupyter notebook
    writef(nb, tmp_text)
    jupytext(['--to', 'notebook', tmp_text])
    nb2 = readf(tmp_ipynb)
    compare_notebooks(nb, nb2)

    # Percent format to Jupyter notebook
    writef(nb, tmp_text, ext + ':percent')
    jupytext(['--to', 'notebook', tmp_text])
    nb2 = readf(tmp_ipynb)
    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_cli_can_infer_jupytext_format_from_stdin(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))
    nb = readf(nb_file)

    # read ipynb notebook on stdin, write to python
    with open(nb_file) as fp, mock.patch('sys.stdin', fp):
        jupytext(['--to', 'py:percent', '-o', tmp_py])
    nb2 = readf(tmp_py)
    compare_notebooks(nb, nb2)

    # read python notebook on stdin, write to ipynb
    with open(tmp_py) as fp, mock.patch('sys.stdin', fp):
        jupytext(['-o', tmp_ipynb])
    nb2 = readf(tmp_ipynb)
    compare_notebooks(nb, nb2)

    # read ipynb notebook on stdin, write to R markdown
    with open(nb_file) as fp, mock.patch('sys.stdin', fp):
        jupytext(['-o', tmp_rmd])
    nb2 = readf(tmp_rmd)
    compare_notebooks(nb, nb2, 'Rmd')

    # read markdown notebook on stdin, write to ipynb
    with open(tmp_rmd) as fp, mock.patch('sys.stdin', fp):
        jupytext(['-o', tmp_ipynb])
    nb2 = readf(tmp_ipynb)
    compare_notebooks(nb, nb2, 'Rmd')


def test_cli_expect_errors():
    with pytest.raises(ValueError):
        cli_jupytext([])
    with pytest.raises(ValueError):
        cli_jupytext(['--sync'])
    with pytest.raises(ValueError):
        cli_jupytext(['--paired-paths'])
    with pytest.raises(ValueError):
        cli_jupytext(['--pre-commit', 'notebook.ipynb'])
    with pytest.raises(ValueError):
        cli_jupytext(['--pre-commit', '--test'])
    with pytest.raises(SystemExit):
        jupytext(['notebook.ipynb', '--from', 'py:percent', '--to', 'md'])
    with pytest.raises((SystemExit, TypeError)):  # SystemExit on Windows, TypeError on Linux
        system('jupytext', ['notebook.ipynb', '--from', 'py:percent', '--to', 'md'])
