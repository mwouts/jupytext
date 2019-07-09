import os
import sys
import time
import stat

try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import nbformat
import itertools
from shutil import copyfile
from jupytext.compare import compare
from argparse import ArgumentTypeError
from nbformat.v4.nbbase import new_notebook, new_markdown_cell, new_code_cell
from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec
from jupytext import __version__
from jupytext import read, write, writes
from jupytext.cli import parse_jupytext_args, jupytext, jupytext_cli, system, str2bool
from jupytext.compare import compare_notebooks
from jupytext.paired_paths import paired_paths, InconsistentPath
from jupytext.formats import long_form_one_format, JupytextFormatError
from .utils import list_notebooks, skip_if_dict_is_not_ordered
from .utils import requires_black, requires_flake8, requires_sphinx_gallery
from .utils import requires_jupytext_installed, requires_pandoc


def test_str2bool():
    assert str2bool('d') is None
    assert str2bool('TRUE') is True
    assert str2bool('0') is False
    with pytest.raises(ArgumentTypeError):
        str2bool('UNEXPECTED')


@pytest.mark.parametrize('nb_file', list_notebooks())
def test_cli_single_file(nb_file):
    assert parse_jupytext_args([nb_file] + ['--to', 'py']).notebooks == [nb_file]


@pytest.mark.parametrize('nb_files', [list_notebooks()])
def test_cli_multiple_files(nb_files):
    assert parse_jupytext_args(nb_files + ['--to', 'py']).notebooks == nb_files


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_convert_single_file_in_place(nb_file, tmpdir):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    copyfile(nb_file, nb_org)

    base, ext = os.path.splitext(nb_org)
    nb_other = base + '.py'

    jupytext([nb_org, '--to', 'py'])

    nb1 = read(nb_org)
    nb2 = read(nb_other)

    compare_notebooks(nb1, nb2)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb') + list_notebooks('Rmd'))
def test_convert_single_file(nb_file, tmpdir, capsys):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    copyfile(nb_file, nb_org)

    nb1 = read(nb_file)
    pynb = writes(nb1, 'py')
    jupytext([nb_org, '--to', 'py', '-o', '-'])

    out, err = capsys.readouterr()
    assert err == ''
    compare(out, pynb)


def test_jupytext_version(capsys):
    jupytext(['--version'])

    out, err = capsys.readouterr()
    assert err == ''
    compare(out, __version__ + '\n')


def test_wildcard(tmpdir):
    nb1_ipynb = str(tmpdir.join('nb1.ipynb'))
    nb2_ipynb = str(tmpdir.join('nb2.ipynb'))

    nb1_py = str(tmpdir.join('nb1.py'))
    nb2_py = str(tmpdir.join('nb2.py'))

    write(new_notebook(metadata={'notebook': 1}), nb1_ipynb)
    write(new_notebook(metadata={'notebook': 2}), nb2_ipynb)

    os.chdir(str(tmpdir))
    jupytext(['nb*.ipynb', '--to', 'py'])

    assert os.path.isfile(nb1_py)
    assert os.path.isfile(nb2_py)

    with pytest.raises(IOError):
        jupytext(['nb3.ipynb', '--to', 'py'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_cpp'))
def test_to_cpluplus(nb_file, tmpdir, capsys):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    copyfile(nb_file, nb_org)
    nb1 = read(nb_org)

    text_cpp = writes(nb1, 'cpp')
    jupytext([nb_org, '--to', 'c++', '--output', '-'])

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

    jupytext(nb_orgs + ['--to', 'py'])

    for nb_org, nb_other in zip(nb_orgs, nb_others):
        nb1 = read(nb_org)
        nb2 = read(nb_other)
        compare_notebooks(nb1, nb2)


def test_error_not_notebook_ext_input(tmpdir, capsys):
    tmp_file = str(tmpdir.join('notebook.ext'))
    with open(tmp_file, 'w') as fp:
        fp.write('\n')

    with pytest.raises(JupytextFormatError, match="Extension '.ext' is not a notebook extension. Please use one of"):
        jupytext([tmp_file, '--to', 'py'])


@pytest.fixture
def tmp_ipynb(tmpdir):
    tmp_file = str(tmpdir.join('notebook.ipynb'))
    write(new_notebook(), tmp_file)
    return tmp_file


@pytest.fixture
def tmp_py(tmpdir):
    tmp_file = str(tmpdir.join('notebook.py'))
    with open(tmp_file, 'w') as fp:
        fp.write('\n')
    return tmp_file


def test_error_not_notebook_ext_to(tmp_ipynb):
    with pytest.raises(JupytextFormatError, match="Extension '.ext' is not a notebook extension. Please use one of"):
        jupytext([tmp_ipynb, '--to', 'ext'])


def test_error_not_notebook_ext_output(tmp_ipynb, tmpdir):
    with pytest.raises(JupytextFormatError, match="Extension '.ext' is not a notebook extension. Please use one of"):
        jupytext([tmp_ipynb, '-o', str(tmpdir.join('not.ext'))])


def test_error_not_same_ext(tmp_ipynb, tmpdir):
    with pytest.raises(InconsistentPath):
        jupytext([tmp_ipynb, '--to', 'py', '-o', str(tmpdir.join('not.md'))])


def test_error_no_action(tmp_ipynb):
    with pytest.raises(ValueError, match="Please select an action"):
        jupytext([tmp_ipynb])


def test_error_update_not_ipynb(tmp_py):
    with pytest.raises(ValueError, match='--update is only for ipynb files'):
        jupytext([tmp_py, '--to', 'py', '--update'])


def test_error_multiple_input(tmp_ipynb):
    with pytest.raises(ValueError, match='Please input a single notebook when using --output'):
        jupytext([tmp_ipynb, tmp_ipynb, '--to', 'py', '-o', 'notebook.py'])


def test_error_opt_missing_equal(tmp_ipynb):
    with pytest.raises(ValueError, match='key=value'):
        jupytext([tmp_ipynb, '--to', 'py', '--opt', 'missing_equal'])


def test_error_unknown_opt(tmp_ipynb):
    with pytest.raises(ValueError, match='is not a valid format option'):
        jupytext([tmp_ipynb, '--to', 'py', '--opt', 'unknown=true'])


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
    write(nb, tmp_ipynb)

    # to jupyter notebook
    jupytext([tmp_nbpy, '--to', 'ipynb', '--update'])
    # test round trip
    jupytext([tmp_nbpy, '--to', 'notebook', '--test'])
    # test ipynb to rmd
    jupytext([tmp_ipynb, '--to', 'rmarkdown'])

    nb = read(tmp_ipynb)
    cells = nb['cells']
    assert len(cells) == 1
    assert cells[0].cell_type == 'markdown'
    assert cells[0].source == 'New cell'

    nb = read(tmp_rmd)
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
    write(nb, tmp_ipynb)

    with pytest.raises(ValueError, match='Please remove one or the other file'):
        jupytext([tmp_nbpy, '--to', 'ipynb', '--update'])


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

    nb1 = read(tmp_ipynb)
    nb2 = read(tmp_nbpy)

    compare_notebooks(nb1, nb2)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_convert_to_percent_format_and_keep_magics(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_nbpy = str(tmpdir.join('notebook.py'))

    copyfile(nb_file, tmp_ipynb)

    jupytext(['--to', 'py:percent', '--opt', 'comment_magics=False', tmp_ipynb])

    with open(tmp_nbpy) as stream:
        py_script = stream.read()
        assert 'format_name: percent' in py_script
        assert 'comment_magics: false' in py_script
        assert '# %%time' not in py_script

    nb1 = read(tmp_ipynb)
    nb2 = read(tmp_nbpy)

    compare_notebooks(nb1, nb2)


def git_in_tmpdir(tmpdir):
    """Return a function that will execute git instruction in the desired directory"""

    def git(*args):
        out = system('git', *args, cwd=str(tmpdir))
        print(out)
        return out

    return git


@requires_jupytext_installed
@skip_if_dict_is_not_ordered
def test_pre_commit_hook(tmpdir):
    tmp_ipynb = str(tmpdir.join('nb with spaces.ipynb'))
    tmp_py = str(tmpdir.join('nb with spaces.py'))
    nb = new_notebook(cells=[])

    git = git_in_tmpdir(tmpdir)
    git('init')
    git('status')
    hook = str(tmpdir.join('.git/hooks/pre-commit'))
    with open(hook, 'w') as fp:
        fp.write('#!/bin/sh\n'
                 'jupytext --to py:light --pre-commit\n')

    st = os.stat(hook)
    os.chmod(hook, st.st_mode | stat.S_IEXEC)

    write(nb, tmp_ipynb)
    assert os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)

    git('add', 'nb with spaces.ipynb')
    git('status')
    git('commit', '-m', 'created')
    git('status')

    assert 'nb with spaces.py' in git('ls-tree', '-r', 'master', '--name-only')
    assert os.path.isfile(tmp_py)


@requires_jupytext_installed
@skip_if_dict_is_not_ordered
def test_pre_commit_hook_in_subfolder(tmpdir):
    tmp_ipynb = str(tmpdir.join('nb with spaces.ipynb'))
    tmp_py = str(tmpdir.join('python', 'nb with spaces.py'))
    nb = new_notebook(cells=[])

    git = git_in_tmpdir(tmpdir)
    git('init')
    git('status')
    hook = str(tmpdir.join('.git/hooks/pre-commit'))
    with open(hook, 'w') as fp:
        fp.write('#!/bin/sh\n'
                 'jupytext --from ipynb --to python//py:light --pre-commit\n')

    st = os.stat(hook)
    os.chmod(hook, st.st_mode | stat.S_IEXEC)

    write(nb, tmp_ipynb)
    assert os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)

    git('add', 'nb with spaces.ipynb')
    git('status')
    git('commit', '-m', 'created')
    git('status')

    assert 'nb with spaces.py' in git('ls-tree', '-r', 'master', '--name-only')
    assert os.path.isfile(tmp_py)


@requires_jupytext_installed
@skip_if_dict_is_not_ordered
def test_pre_commit_hook_py_to_ipynb_and_md(tmpdir):
    tmp_ipynb = str(tmpdir.join('nb with spaces.ipynb'))
    tmp_py = str(tmpdir.join('nb with spaces.py'))
    tmp_md = str(tmpdir.join('nb with spaces.md'))
    nb = new_notebook(cells=[])

    git = git_in_tmpdir(tmpdir)
    git('init')
    git('status')
    hook = str(tmpdir.join('.git/hooks/pre-commit'))
    with open(hook, 'w') as fp:
        fp.write('#!/bin/sh\n'
                 'jupytext --from py:light --to ipynb --pre-commit\n'
                 'jupytext --from py:light --to md --pre-commit\n')

    st = os.stat(hook)
    os.chmod(hook, st.st_mode | stat.S_IEXEC)

    write(nb, tmp_py)
    assert os.path.isfile(tmp_py)
    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_md)

    git('add', 'nb with spaces.py')
    git('status')
    git('commit', '-m', 'created')
    git('status')

    assert 'nb with spaces.ipynb' in git('ls-tree', '-r', 'master', '--name-only')
    assert 'nb with spaces.md' in git('ls-tree', '-r', 'master', '--name-only')

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_md)


@requires_black
@requires_flake8
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py')[:1])
def test_pre_commit_hook_sync_black_flake8(tmpdir, nb_file):
    # Load real notebook metadata to get the 'auto' extension in --pipe-fmt to work
    metadata = read(nb_file).metadata

    git = git_in_tmpdir(tmpdir)
    git('init')
    git('status')
    hook = str(tmpdir.join('.git/hooks/pre-commit'))
    with open(hook, 'w') as fp:
        fp.write('#!/bin/sh\n'
                 '# Pair ipynb notebooks to a python file, reformat content with black, and run flake8\n'
                 "# Note: this hook only acts on ipynb files. When pulling, run 'jupytext --sync' to "
                 'update the ipynb file.\n'
                 'jupytext --pre-commit --from ipynb --set-formats ipynb,py --pipe black --check flake8\n')

    st = os.stat(hook)
    os.chmod(hook, st.st_mode | stat.S_IEXEC)

    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    nb = new_notebook(cells=[new_code_cell(source='1+    1')], metadata=metadata)

    write(nb, tmp_ipynb)
    git('add', 'notebook.ipynb')
    git('status')
    git('commit', '-m', 'created')
    git('status')
    assert os.path.isfile(tmp_py)
    assert os.path.isfile(tmp_ipynb)
    with open(tmp_py) as fp:
        assert fp.read().splitlines()[-1] == '1 + 1'

    nb = new_notebook(cells=[new_code_cell(source='"""trailing   \nwhitespace"""')], metadata=metadata)
    write(nb, tmp_ipynb)
    git('add', 'notebook.ipynb')
    git('status')
    with pytest.raises(SystemExit):  # not flake8
        git('commit', '-m', 'created')


def test_manual_call_of_pre_commit_hook(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    nb = new_notebook(cells=[])
    os.chdir(str(tmpdir))

    def system_in_tmpdir(*args):
        return system(*args, cwd=str(tmpdir))

    git = git_in_tmpdir(tmpdir)
    git('init')
    git('status')

    def hook():
        with mock.patch('jupytext.cli.system', system_in_tmpdir):
            jupytext(['--to', 'py', '--pre-commit'])

    write(nb, tmp_ipynb)
    assert os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)

    git('add', 'notebook.ipynb')
    git('status')
    hook()
    git('commit', '-m', 'created')
    git('status')

    assert 'notebook.py' in git('ls-tree', '-r', 'master', '--name-only')
    assert os.path.isfile(tmp_py)


@pytest.mark.parametrize('py_file', list_notebooks('python'))
def test_set_formats(py_file, tmpdir):
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    copyfile(py_file, tmp_py)

    jupytext([tmp_py, '--set-formats', 'ipynb,py:light'])
    nb = read(tmp_ipynb)
    assert nb.metadata['jupytext']['formats'] == 'ipynb,py:light'


@pytest.mark.parametrize('py_file', list_notebooks('python'))
def test_update_metadata(py_file, tmpdir, capsys):
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    copyfile(py_file, tmp_py)

    jupytext(['--to', 'ipynb', tmp_py, '--update-metadata', '{"jupytext":{"formats":"ipynb,py:light"}}'])

    nb = read(tmp_ipynb)
    assert nb.metadata['jupytext']['formats'] == 'ipynb,py:light'

    jupytext(['--to', 'py', tmp_ipynb, '--update-metadata', '{"jupytext":{"formats":null}}'])

    nb = read(tmp_py)
    assert 'formats' not in nb.metadata['jupytext']

    with pytest.raises(SystemExit):
        jupytext(['--to', 'ipynb', tmp_py, '--update-metadata', '{"incorrect": "JSON"'])

    out, err = capsys.readouterr()
    assert 'invalid' in err


@pytest.mark.parametrize('py_file', list_notebooks('python'))
def test_set_kernel_inplace(py_file, tmpdir):
    tmp_py = str(tmpdir.join('notebook.py'))

    copyfile(py_file, tmp_py)

    jupytext([tmp_py, '--set-kernel', '-'])

    nb = read(tmp_py)
    kernel_name = nb.metadata['kernelspec']['name']
    assert get_kernel_spec(kernel_name).argv[0] in ['python', sys.executable]


@pytest.mark.parametrize('py_file', list_notebooks('python'))
def test_set_kernel_auto(py_file, tmpdir):
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    copyfile(py_file, tmp_py)

    jupytext(['--to', 'ipynb', tmp_py, '--set-kernel', '-'])

    nb = read(tmp_ipynb)
    kernel_name = nb.metadata['kernelspec']['name']
    assert get_kernel_spec(kernel_name).argv[0] in ['python', sys.executable]


@pytest.mark.parametrize('py_file', list_notebooks('python'))
def test_set_kernel_with_name(py_file, tmpdir):
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    copyfile(py_file, tmp_py)

    for kernel in find_kernel_specs():
        jupytext(['--to', 'ipynb', tmp_py, '--set-kernel', kernel])

        nb = read(tmp_ipynb)
        assert nb.metadata['kernelspec']['name'] == kernel

    with pytest.raises(KeyError):
        jupytext(['--to', 'ipynb', tmp_py, '--set-kernel', 'non_existing_env'])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_paired_paths(nb_file, tmpdir, capsys):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    nb = read(nb_file)
    nb.metadata.setdefault('jupytext', {})['formats'] = 'ipynb,_light.py,_percent.py:percent'
    write(nb, tmp_ipynb)

    jupytext(['--paired-paths', tmp_ipynb])

    out, err = capsys.readouterr()
    assert not err

    formats = nb.metadata.get('jupytext', {}).get('formats')
    assert set(out.splitlines()).union([tmp_ipynb]) == set(
        [path for path, _ in paired_paths(tmp_ipynb, 'ipynb', formats)])


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_sync(nb_file, tmpdir, capsys):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))
    nb = read(nb_file)
    write(nb, tmp_ipynb)

    # Test that sync issues a warning when the notebook is not paired
    jupytext(['--sync', tmp_ipynb])
    _, err = capsys.readouterr()
    assert 'is not a paired notebook' in err

    # Now with a pairing information
    nb.metadata.setdefault('jupytext', {})['formats'] = 'py,Rmd,ipynb'
    write(nb, tmp_ipynb)

    # Test that missing files are created
    jupytext(['--sync', tmp_ipynb])

    assert os.path.isfile(tmp_py)
    compare_notebooks(nb, read(tmp_py))

    assert os.path.isfile(tmp_rmd)
    compare_notebooks(nb, read(tmp_rmd), 'Rmd')

    write(nb, tmp_rmd, 'Rmd')
    jupytext(['--sync', tmp_ipynb])

    nb2 = read(tmp_ipynb)
    compare_notebooks(nb, nb2, 'Rmd', compare_outputs=True)

    write(nb, tmp_py, 'py')
    jupytext(['--sync', tmp_ipynb])

    nb2 = read(tmp_ipynb)
    compare_notebooks(nb, nb2, compare_outputs=True)

    # Finally we recreate the ipynb
    os.remove(tmp_ipynb)

    time.sleep(0.1)
    jupytext(['--sync', tmp_py])

    nb2 = read(tmp_ipynb)
    compare_notebooks(nb, nb2)

    # ipynb must be older than py file, otherwise our Contents Manager will complain
    assert os.path.getmtime(tmp_ipynb) <= os.path.getmtime(tmp_py)


@requires_pandoc
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py', skip='(Notebook with|flavors)'))
def test_sync_pandoc(nb_file, tmpdir, capsys):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_md = str(tmpdir.join('notebook.md'))
    nb = read(nb_file)
    write(nb, tmp_ipynb)

    # Test that sync issues a warning when the notebook is not paired
    jupytext(['--sync', tmp_ipynb])
    _, err = capsys.readouterr()
    assert 'is not a paired notebook' in err

    # Now with a pairing information
    nb.metadata.setdefault('jupytext', {})['formats'] = 'ipynb,md:pandoc'
    write(nb, tmp_ipynb)

    # Test that missing files are created
    jupytext(['--sync', tmp_ipynb])

    assert os.path.isfile(tmp_md)
    compare_notebooks(nb, read(tmp_md), 'md:pandoc')

    with open(tmp_md) as fp:
        assert 'pandoc' in fp.read()


@pytest.mark.parametrize('nb_file,ext',
                         [(nb_file, '.py') for nb_file in list_notebooks('ipynb_py')] +
                         [(nb_file, '.R') for nb_file in list_notebooks('ipynb_R')] +
                         [(nb_file, '.jl') for nb_file in list_notebooks('ipynb_julia')])
def test_cli_can_infer_jupytext_format(nb_file, ext, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_text = str(tmpdir.join('notebook' + ext))
    nb = read(nb_file)

    # Light format to Jupyter notebook
    write(nb, tmp_text)
    jupytext(['--to', 'notebook', tmp_text])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb, nb2)

    # Percent format to Jupyter notebook
    write(nb, tmp_text, ext + ':percent')
    jupytext(['--to', 'notebook', tmp_text])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('nb_file,ext',
                         [(nb_file, '.py') for nb_file in list_notebooks('ipynb_py')] +
                         [(nb_file, '.R') for nb_file in list_notebooks('ipynb_R')])
def test_cli_to_script(nb_file, ext, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_text = str(tmpdir.join('notebook' + ext))
    nb = read(nb_file)

    write(nb, tmp_ipynb)
    jupytext(['--to', 'script', tmp_ipynb])
    nb2 = read(tmp_text)
    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('nb_file,ext',
                         [(nb_file, '.py') for nb_file in list_notebooks('ipynb_py')] +
                         [(nb_file, '.R') for nb_file in list_notebooks('ipynb_R')])
def test_cli_to_auto(nb_file, ext, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_text = str(tmpdir.join('notebook' + ext))
    nb = read(nb_file)

    write(nb, tmp_ipynb)
    jupytext(['--to', 'auto', tmp_ipynb])
    nb2 = read(tmp_text)
    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py'))
def test_cli_can_infer_jupytext_format_from_stdin(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))
    nb = read(nb_file)

    # read ipynb notebook on stdin, write to python
    with open(nb_file) as fp, mock.patch('sys.stdin', fp):
        jupytext(['--to', 'py:percent', '-o', tmp_py])
    nb2 = read(tmp_py)
    compare_notebooks(nb, nb2)

    # read python notebook on stdin, write to ipynb
    with open(tmp_py) as fp, mock.patch('sys.stdin', fp):
        jupytext(['-o', tmp_ipynb])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb, nb2)

    # read ipynb notebook on stdin, write to R markdown
    with open(nb_file) as fp, mock.patch('sys.stdin', fp):
        jupytext(['-o', tmp_rmd])
    nb2 = read(tmp_rmd)
    compare_notebooks(nb, nb2, 'Rmd')

    # read markdown notebook on stdin, write to ipynb
    with open(tmp_rmd) as fp, mock.patch('sys.stdin', fp):
        jupytext(['-o', tmp_ipynb])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb, nb2, 'Rmd')


@requires_jupytext_installed
def test_cli_expect_errors(tmp_ipynb):
    with pytest.raises(ValueError):
        jupytext([])
    with pytest.raises(ValueError):
        jupytext(['--sync'])
    with pytest.raises(ValueError):
        jupytext([tmp_ipynb, tmp_ipynb, '--paired-paths'])
    with pytest.raises(ValueError):
        jupytext(['--pre-commit', 'notebook.ipynb'])
    with pytest.raises(ValueError):
        jupytext(['notebook.ipynb', '--from', 'py:percent', '--to', 'md'])
    with pytest.raises(SystemExit):
        jupytext_cli([])
    with pytest.raises((SystemExit, TypeError)):  # SystemExit on Windows, TypeError on Linux
        system('jupytext', ['notebook.ipynb', '--from', 'py:percent', '--to', 'md'])


def test_format_prefix_suffix(tmpdir):
    os.makedirs(str(tmpdir.join('notebooks')))
    tmp_ipynb = str(tmpdir.join('notebooks/notebook_name.ipynb'))
    tmp_py = str(tmpdir.join('scripts/notebook_name.py'))
    write(new_notebook(), tmp_ipynb)

    jupytext([tmp_ipynb, '--to', os.path.join('..', 'scripts//py')])
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)

    jupytext([tmp_ipynb, '--to', 'scripts//py', '--from', 'notebooks//ipynb'])
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)

    tmp_ipynb = str(tmpdir.join('notebooks/nb_prefix_notebook_name.ipynb'))
    tmp_py = str(tmpdir.join('scripts/script_prefix_notebook_name.py'))
    write(new_notebook(), tmp_ipynb)

    jupytext([tmp_ipynb, '--to', 'scripts/script_prefix_/py', '--from', 'notebooks/nb_prefix_/ipynb'])
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)

    tmp_ipynb = str(tmpdir.join('notebooks/nb_prefix_notebook_name_nb_suffix.ipynb'))
    tmp_py = str(tmpdir.join('scripts/script_prefix_notebook_name_script_suffix.py'))
    write(new_notebook(), tmp_ipynb)

    jupytext([tmp_ipynb, '--to', 'scripts/script_prefix_/_script_suffix.py',
              '--from', 'notebooks/nb_prefix_/_nb_suffix.ipynb'])
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)


def test_cli_sync_file_with_suffix(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    tmp_pct_py = str(tmpdir.join('notebook.pct.py'))
    tmp_lgt_py = str(tmpdir.join('notebook.lgt.py'))
    tmp_rmd = str(tmpdir.join('notebook.Rmd'))
    nb = new_notebook(cells=[new_code_cell(source='1+1')],
                      metadata={'jupytext': {'formats': 'ipynb,.pct.py:percent,.lgt.py:light,Rmd'}})

    write(nb, tmp_pct_py, '.pct.py:percent')
    jupytext(['--sync', tmp_pct_py])
    assert os.path.isfile(tmp_lgt_py)
    assert os.path.isfile(tmp_rmd)
    assert os.path.isfile(tmp_ipynb)

    jupytext(['--sync', tmp_lgt_py])
    jupytext(['--sync', tmp_ipynb])

    assert open(tmp_lgt_py).read().splitlines()[-2:] == ['', '1+1']
    assert open(tmp_pct_py).read().splitlines()[-3:] == ['', '# %%', '1+1']
    assert open(tmp_rmd).read().splitlines()[-4:] == ['', '```{python}', '1+1', '```']


@requires_sphinx_gallery
def test_rst2md(tmpdir):
    tmp_py = str(tmpdir.join('notebook.py'))
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))

    # Write notebook in sphinx format
    nb = new_notebook(cells=[new_markdown_cell('A short sphinx notebook'),
                             new_markdown_cell(':math:`1+1`')])
    write(nb, tmp_py, fmt='py:sphinx')

    jupytext([tmp_py, '--from', 'py:sphinx', '--to', 'ipynb',
              '--opt', 'rst2md=True', '--opt', 'cell_metadata_filter=-all'])

    assert os.path.isfile(tmp_ipynb)
    nb = read(tmp_ipynb)

    assert nb.metadata['jupytext']['cell_metadata_filter'] == '-all'
    assert nb.metadata['jupytext']['rst2md'] is False

    # Was rst to md conversion effective?
    assert nb.cells[2].source == '$1+1$'


def test_remove_jupytext_metadata(tmpdir):
    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    nb = new_notebook(metadata={'jupytext': {
        'main_language': 'python',
        'text_representation': {
            'extension': '.md',
            'format_name': 'markdown',
            'format_version': '1.0',
            'jupytext_version': '0.8.6'
        }}})

    nbformat.write(nb, tmp_ipynb, version=nbformat.NO_CONVERT)
    # Jupytext removes the 'text_representation' information from the notebook
    jupytext([tmp_ipynb, '--update-metadata', '{"jupytext":{"main_language":null}}'])
    nb2 = read(tmp_ipynb)
    assert not nb2.metadata

    nbformat.write(nb, tmp_ipynb, version=nbformat.NO_CONVERT)
    jupytext([tmp_ipynb, '--set-formats', 'ipynb,py:light'])

    nb2 = read(tmp_ipynb)
    assert nb2.metadata == {'jupytext': {'formats': 'ipynb,py:light', 'main_language': 'python'}}


@pytest.mark.parametrize('nb_file,fmt', itertools.product(list_notebooks('ipynb_py'), ['py:light', 'py:percent', 'md']))
def test_convert_and_update_preserves_notebook(nb_file, fmt, tmpdir):
    # cannot encode magic parameters in markdown yet
    if 'magic' in nb_file and fmt == 'md':
        return

    tmp_ipynb = str(tmpdir.join('notebook.ipynb'))
    copyfile(nb_file, tmp_ipynb)
    ext = long_form_one_format(fmt)['extension']
    tmp_text = str(tmpdir.join('notebook' + ext))

    jupytext(['--to', fmt, tmp_ipynb])
    jupytext(['--to', 'ipynb', '--update', tmp_text])

    nb_org = read(nb_file)
    nb_now = read(tmp_ipynb)
    compare(nb_org, nb_now)


def test_incorrect_notebook_causes_early_exit(tmpdir):
    incorrect_ipynb = str(tmpdir.join('incorrect.ipynb'))
    incorrect_md = str(tmpdir.join('incorrect.md'))
    with open(incorrect_ipynb, 'w') as fp:
        fp.write('{"nbformat": 4, "nbformat_minor": 2, "metadata": {INCORRECT}, "cells": []}')

    correct_ipynb = str(tmpdir.join('correct.ipynb'))
    correct_md = str(tmpdir.join('correct.md'))
    with open(correct_ipynb, 'w') as fp:
        fp.write('{"nbformat": 4, "nbformat_minor": 2, "metadata": {}, "cells": []}')

    with pytest.raises(nbformat.reader.NotJSONError, match='Notebook does not appear to be JSON'):
        jupytext([incorrect_ipynb, correct_ipynb, '--to', 'md'])

    assert not os.path.exists(incorrect_md)
    assert not os.path.exists(correct_md)


def test_warn_only_skips_incorrect_notebook(tmpdir, capsys):
    incorrect_ipynb = str(tmpdir.join('incorrect.ipynb'))
    incorrect_md = str(tmpdir.join('incorrect.md'))
    with open(incorrect_ipynb, 'w') as fp:
        fp.write('{"nbformat": 4, "nbformat_minor": 2, "metadata": {INCORRECT}, "cells": []}')

    correct_ipynb = str(tmpdir.join('correct.ipynb'))
    correct_md = str(tmpdir.join('correct.md'))
    with open(correct_ipynb, 'w') as fp:
        fp.write('{"nbformat": 4, "nbformat_minor": 2, "metadata": {}, "cells": []}')

    jupytext([incorrect_ipynb, correct_ipynb, '--to', 'md', '--warn-only'])

    _, err = capsys.readouterr()
    assert "Notebook does not appear to be JSON" in str(err)

    assert not os.path.exists(incorrect_md)
    assert os.path.exists(correct_md)
