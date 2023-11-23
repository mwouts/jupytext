import os
from copy import deepcopy
from shutil import copyfile

import pytest
from nbformat.v4.nbbase import new_code_cell, new_notebook

from jupytext import read, write
from jupytext.cli import jupytext, pipe_notebook, system
from jupytext.combine import black_invariant
from jupytext.compare import compare, compare_cells, compare_notebooks
from jupytext.header import _DEFAULT_NOTEBOOK_METADATA


@pytest.mark.requires_black
def test_apply_black_on_python_notebooks(tmpdir, cwd_tmpdir, ipynb_py_file):
    if "cell metadata" in ipynb_py_file:
        pytest.skip()
    copyfile(ipynb_py_file, "notebook.ipynb")

    jupytext(args=["notebook.ipynb", "--to", "py:percent"])
    system("black", "notebook.py")
    jupytext(args=["notebook.py", "--to", "ipynb", "--update"])

    nb1 = read(ipynb_py_file)
    nb2 = read("notebook.ipynb")
    nb3 = read("notebook.py")

    assert len(nb1.cells) == len(nb2.cells)
    assert len(nb1.cells) == len(nb3.cells)
    for c1, c2 in zip(nb1.cells, nb2.cells):
        # same content (almost)
        assert black_invariant(c1.source) == black_invariant(c2.source)
        # python representation is pep8
        assert "lines_to_next_cell" not in c2.metadata
        # outputs are preserved
        assert c1.cell_type == c2.cell_type
        if c1.cell_type == "code":
            compare(c1.outputs, c2.outputs)

    compare(nb1.metadata, nb2.metadata)


def test_black_invariant():
    text_org = """long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \\
              "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
"""
    text_black = """long_string = (
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
)
"""
    assert black_invariant(text_org) == black_invariant(text_black)


@pytest.mark.requires_black
def test_pipe_into_black():
    nb_org = new_notebook(cells=[new_code_cell("1        +1", id="cell-id")])
    nb_dest = new_notebook(cells=[new_code_cell("1 + 1", id="cell-id")])

    nb_pipe = pipe_notebook(nb_org, "black")
    compare_notebooks(
        nb_pipe, nb_dest, allow_expected_differences=False, compare_ids=True
    )


@pytest.mark.requires_autopep8
def test_pipe_into_autopep8():
    nb_org = new_notebook(cells=[new_code_cell("1        +1", id="cell-id")])
    nb_dest = new_notebook(cells=[new_code_cell("1 + 1", id="cell-id")])

    nb_pipe = pipe_notebook(nb_org, "autopep8 -")
    compare_notebooks(
        nb_pipe, nb_dest, allow_expected_differences=False, compare_ids=True
    )


@pytest.mark.requires_flake8
def test_pipe_into_flake8():
    # Notebook OK
    nb = new_notebook(cells=[new_code_cell("# correct code\n1 + 1")])
    pipe_notebook(nb, "flake8", update=False)

    # Notebook not OK
    nb = new_notebook(cells=[new_code_cell("incorrect code")])
    with pytest.raises(SystemExit):
        pipe_notebook(nb, "flake8", update=False)


@pytest.mark.requires_black
@pytest.mark.requires_flake8
def test_apply_black_through_jupytext(tmpdir, python_notebook):
    # Load real notebook metadata to get the 'auto' extension in --pipe-fmt to work
    metadata = python_notebook.metadata

    nb_org = new_notebook(
        cells=[new_code_cell("1        +1", id="cell-id")], metadata=metadata
    )
    nb_black = new_notebook(
        cells=[new_code_cell("1 + 1", id="cell-id")], metadata=metadata
    )

    tmp_ipynb = str(tmpdir.mkdir("notebook_folder").join("notebook.ipynb"))
    tmp_py = str(tmpdir.mkdir("script_folder").join("notebook.py"))

    # Black in place
    write(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, "--pipe", "black"])
    nb_now = read(tmp_ipynb)
    compare_notebooks(nb_now, nb_black, compare_ids=True)

    # Write to another folder using dots
    write(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, "--to", "../script_folder//py:percent", "--pipe", "black"])
    assert os.path.isfile(tmp_py)
    nb_now = read(tmp_py)
    nb_now.metadata = metadata
    compare_notebooks(nb_now, nb_black)
    os.remove(tmp_py)

    # Map to another folder based on file name
    write(nb_org, tmp_ipynb)
    jupytext(
        [
            tmp_ipynb,
            "--from",
            "notebook_folder//ipynb",
            "--to",
            "script_folder//py:percent",
            "--pipe",
            "black",
            "--check",
            "flake8",
        ]
    )
    assert os.path.isfile(tmp_py)
    nb_now = read(tmp_py)
    nb_now.metadata = metadata
    compare_notebooks(nb_now, nb_black)


@pytest.mark.requires_black
def test_apply_black_and_sync_on_paired_notebook(tmpdir, cwd_tmpdir, python_notebook):
    # Load real notebook metadata to get the 'auto' extension in --pipe-fmt to work
    metadata = python_notebook.metadata
    metadata["jupytext"] = {"formats": "ipynb,py"}
    assert "language_info" in metadata

    nb_org = new_notebook(
        cells=[new_code_cell("1        +1", id="cell-id")], metadata=metadata
    )
    nb_black = new_notebook(
        cells=[new_code_cell("1 + 1", id="cell-id")], metadata=metadata
    )

    # Black in place
    write(nb_org, "notebook.ipynb")
    jupytext(["notebook.ipynb", "--pipe", "black", "--sync"])

    nb_now = read("notebook.ipynb")
    compare_notebooks(nb_now, nb_black, compare_ids=True)
    assert "language_info" in nb_now.metadata

    nb_now = read("notebook.py")
    nb_now.metadata["jupytext"].pop("text_representation")
    nb_black.metadata = {
        key: nb_black.metadata[key]
        for key in nb_black.metadata
        if key in _DEFAULT_NOTEBOOK_METADATA.split(",")
    }
    compare_notebooks(nb_now, nb_black)


@pytest.mark.requires_black
def test_apply_black_on_markdown_notebook(tmpdir):
    text = """---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 3
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython3
    version: 3.7.4
---

```python
1    +     \
2+3\
+4
```
"""
    tmp_md = str(tmpdir.join("test.md"))
    with open(tmp_md, "w") as fp:
        fp.write(text)

    jupytext([tmp_md, "--pipe", "black"])

    nb = read(tmp_md)
    compare_cells(nb.cells, [new_code_cell("1 + 2 + 3 + 4")], compare_ids=False)


@pytest.mark.requires_black
def test_black_through_tempfile(
    tmpdir,
    text="""```python
1 +    2 \
+ 3
```
""",
    black="""```python
1 + 2 + 3
```
""",
):
    tmp_md = str(tmpdir.join("notebook.md"))
    with open(tmp_md, "w") as fp:
        fp.write(text)
    jupytext([tmp_md, "--pipe", "black {}"])
    with open(tmp_md) as fp:
        compare(fp.read(), black)


@pytest.mark.requires_black
def test_pipe_black_removes_lines_to_next_cell_metadata(
    tmpdir,
    cwd_tmpdir,
    text="""# %%
def func():
    return 42
# %%
func()""",
):
    tmpdir.join("notebook.py").write(text)
    jupytext(["--set-formats", "ipynb,py:percent", "notebook.py"])

    nb = read(tmpdir.join("notebook.ipynb"))
    assert nb.cells[0].metadata["lines_to_next_cell"] == 0

    jupytext(["--sync", "notebook.py", "--pipe", "black"])
    nb = read(tmpdir.join("notebook.ipynb"))
    assert "lines_to_next_cell" not in nb.cells[0].metadata

    new_text = tmpdir.join("notebook.py").read()
    assert "\n\n# %%\nfunc()" in new_text


@pytest.mark.requires_black
@pytest.mark.parametrize(
    "code,black_should_fail",
    [("myvar = %dont_format_me", False), ("incomplete_instruction = (...", True)],
)
def test_pipe_black_uses_warn_only_781(
    tmpdir, cwd_tmpdir, code, black_should_fail, python_notebook, capsys
):
    nb = python_notebook
    nb.cells.append(new_code_cell(code))
    write(nb, "notebook.ipynb")

    if not black_should_fail:
        jupytext(["--pipe", "black", "notebook.ipynb"])
        return

    with pytest.raises(SystemExit):
        jupytext(["--pipe", "black", "notebook.ipynb"])

    out, err = capsys.readouterr()
    assert "Error: The command 'black -' exited with code" in err
    assert "--warn-only" in err

    # With warn-only we just get a warning
    jupytext(["--pipe", "black", "notebook.ipynb", "--warn-only"])
    out, err = capsys.readouterr()
    assert "Warning: The command 'black -' exited with code" in err

    # If black fails the notebook should be left unchanged
    actual = read("notebook.ipynb")
    compare_notebooks(actual, nb)


@pytest.mark.requires_black
def test_pipe_black_preserve_outputs(notebook_with_outputs, tmpdir, cwd_tmpdir, capsys):
    write(notebook_with_outputs, "test.ipynb")
    jupytext(["--pipe", "black", "test.ipynb"])

    # Outputs are preserved
    nb = read("test.ipynb")
    expected = deepcopy(notebook_with_outputs)
    expected.cells[0].source = "1 + 1"
    compare_notebooks(nb, expected)

    # No mention of --update
    out, err = capsys.readouterr()
    assert not err
    assert "replaced" not in out
    assert "--update" not in out
