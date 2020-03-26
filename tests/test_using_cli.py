import os
import re
import shutil
import shlex
import pytest
import jupytext
from jupytext.cli import jupytext as jupytext_cli
from .utils import list_notebooks

doc_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..', 'docs')


@pytest.mark.skipif(not os.path.isdir(doc_path), reason='Documentation folder is missing')
@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_py')[-1:])
def test_jupytext_commands_in_the_documentation_work(tmpdir, nb_file):
    # Read the documentation as a bash notebook
    using_cli = os.path.join(doc_path, 'using-cli.md')
    assert os.path.isfile(using_cli)
    using_cli_nb = jupytext.read(using_cli)

    # Run the commands in tmpdir on a sample notebook
    shutil.copy(nb_file, tmpdir.join('notebook.ipynb'))
    os.chdir(tmpdir)

    cmd_tested = 0
    for cell in using_cli_nb.cells:
        if cell.cell_type != 'code':
            continue
        if not cell.source.startswith('jupytext'):
            continue
        for cmd in cell.source.splitlines():
            if not cmd.startswith('jupytext'):
                continue
            if 'read ipynb from stdin' in cmd:
                continue
            if 'pytest {}' in cmd:
                continue
            print('Testing: {}'.format(cmd))
            args = shlex.split(re.sub(r'#.*', '', cmd))[1:]
            assert not jupytext_cli(args), cmd
            cmd_tested += 1

    assert cmd_tested >= 10
