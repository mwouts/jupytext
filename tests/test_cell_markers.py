from nbformat.v4.nbbase import new_raw_cell

from jupytext import reads, writes
from jupytext.cli import jupytext


def test_set_cell_markers_cli(tmpdir, cwd_tmpdir):
    tmpdir.join("test.py").write("# %% [markdown]\n# A Markdown cell\n")
    jupytext(["--format-options", 'cell_markers="""', "test.py"])
    py = tmpdir.join("test.py").read()
    assert py.endswith('# %% [markdown]\n"""\nA Markdown cell\n"""\n')


def test_add_cell_to_script_with_cell_markers(
    no_jupytext_version_number,
    py='''# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     cell_markers: '"""'
# ---
''',
):
    nb = reads(py, fmt="py:percent")
    nb.cells = [new_raw_cell("A raw cell")]
    py2 = writes(nb, fmt="py:percent")
    assert py2.endswith(
        '''# %% [raw]
"""
A raw cell
"""
'''
    )
