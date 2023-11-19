import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook
from pre_commit.main import main as pre_commit

from jupytext import read, write


@pytest.mark.requires_pandoc
def test_pre_commit_hook_sync_reformat_code_and_markdown(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    jupytext_repo_root,
    jupytext_repo_rev,
    notebook_with_outputs,
):
    """Here we sync the ipynb notebook with a py:percent file and also apply black and pandoc to reformat both
    code and markdown cells.

    Note: the new cell ids introduced in nbformat 5.1.0 are not yet supported by all the programs that treat
    ipynb files. Consequently we pin the version of nbformat to 5.0.8 in all the environments below (and you
    will have to do the same on the environment in which you edit the notebooks).
    """
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [--sync, --pipe-fmt, ipynb, --pipe, 'pandoc --from ipynb --to ipynb --markdown-headings=atx', --show-changes]
    additional_dependencies:
    - nbformat==5.0.8  # because pandoc 2.11.4 does not preserve yet the new cell ids
  - id: jupytext
    args: [--sync, --pipe, black, --show-changes]
    additional_dependencies:
    - black==22.3.0  # Matches black hook below
    - nbformat==5.0.8  # for compatibility with the pandoc hook above

- repo: https://github.com/psf/black
  rev: 22.3.0
  hooks:
  - id: black
"""
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)

    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    tmpdir.join("jupytext.toml").write('formats = "ipynb,py:percent"')
    tmp_repo.git.add("jupytext.toml")
    tmp_repo.index.commit("pair notebooks")

    # write a test notebook
    notebook = new_notebook(
        cells=[
            new_code_cell("1+1"),
            new_markdown_cell(
                """This is a complex markdown cell

# With a h1 header
## And a h2 header

| And       | A  | Table |
| --------- | ---| ----- |
| 0         | 1  | 2     |

!!!WARNING!!! This hook does not seem compatible with
explicit paragraph breaks (two spaces at the end of a line).

And a VERY long line.
""".replace(
                    "VERY ", "very " * 51
                )
            ),
        ],
        metadata=notebook_with_outputs.metadata,
    )

    # We write the notebook in version 4.4, i.e. with the equivalent of nbformat version 5.0.8
    notebook.nbformat = 4
    notebook.nbformat_minor = 4
    write(notebook, "test.ipynb")

    # try to commit it, should fail because
    # 1. the py version hasn't been added
    # 2. the first cell is '1+1' which is not black compliant
    # 3. the second cell needs to be wrapped
    tmp_repo.git.add("test.ipynb")
    with pytest.raises(
        HookExecutionError,
        match="files were modified by this hook",
    ):
        tmp_repo.index.commit("failing")

    # Add the two files
    tmp_repo.git.add("test.ipynb")
    tmp_repo.git.add("test.py")

    # now the commit will succeed
    tmp_repo.index.commit("passing")
    assert "test.ipynb" in tmp_repo.tree()
    assert "test.py" in tmp_repo.tree()

    # both the code and the markdown cells were reformatted
    nb = read("test.ipynb")
    assert nb.cells[0].source == "1 + 1"

    print(nb.cells[1].source)
    assert (
        nb.cells[1].source
        == """This is a complex markdown cell

# With a h1 header

## And a h2 header

| And | A   | Table |
|-----|-----|-------|
| 0   | 1   | 2     |

!!!WARNING!!! This hook does not seem compatible with explicit paragraph
breaks (two spaces at the end of a line).

And a very very very very very very very very very very very very very
very very very very very very very very very very very very very very
very very very very very very very very very very very very very very
very very very very very very very very very very long line."""
    )
