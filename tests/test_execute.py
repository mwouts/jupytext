import shutil
import pytest
from jupytext import read
from jupytext.cli import jupytext
from .utils import requires_nbconvert, requires_ir_kernel, skip_on_windows


@requires_nbconvert
@skip_on_windows
def test_pipe_nbconvert_execute(tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    with open(tmp_py, "w") as fp:
        fp.write(
            """1 + 2
"""
        )

    jupytext(
        args=[
            tmp_py,
            "--to",
            "ipynb",
            "--pipe-fmt",
            "ipynb",
            "--pipe",
            "jupyter nbconvert --stdin --stdout --to notebook --execute",
        ]
    )

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"] == {"text/plain": "3"}


@requires_nbconvert
@skip_on_windows
def test_pipe_nbconvert_execute_sync(tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    with open(tmp_py, "w") as fp:
        fp.write(
            """1 + 2
"""
        )

    jupytext(
        args=[
            tmp_py,
            "--set-formats",
            "py,ipynb",
            "--sync",
            "--pipe-fmt",
            "ipynb",
            "--pipe",
            "jupyter nbconvert --stdin --stdout --to notebook --execute",
        ]
    )

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"] == {"text/plain": "3"}


@requires_nbconvert
@skip_on_windows
def test_execute(tmpdir, caplog, capsys):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    with open(tmp_py, "w") as fp:
        fp.write(
            """1 + 2
"""
        )

    jupytext(args=[tmp_py, "--to", "ipynb", "--execute"])

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"] == {"text/plain": "3"}


@requires_nbconvert
def test_execute_readme_ok(tmpdir):
    tmp_md = str(tmpdir.join("notebook.md"))

    with open(tmp_md, "w") as fp:
        fp.write(
            """
A readme with correct instructions

```python
1 + 2
```
"""
        )

    jupytext(args=[tmp_md, "--execute"])


@requires_nbconvert
@skip_on_windows
def test_execute_readme_not_ok(tmpdir):
    tmp_md = str(tmpdir.join("notebook.md"))

    with open(tmp_md, "w") as fp:
        fp.write(
            """
A readme with incorrect instructions (a is not defined)

```python
a + 1
```
"""
        )

    import nbconvert

    with pytest.raises(
        nbconvert.preprocessors.execute.CellExecutionError, match="is not defined"
    ):
        jupytext(args=[tmp_md, "--execute"])


@requires_nbconvert
@skip_on_windows
def test_execute_sync(tmpdir, caplog, capsys):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    with open(tmp_py, "w") as fp:
        fp.write(
            """1 + 2
"""
        )

    jupytext(args=[tmp_py, "--set-formats", "py,ipynb", "--sync", "--execute"])

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"] == {"text/plain": "3"}


@requires_nbconvert
@requires_ir_kernel
@skip_on_windows
def test_execute_r(tmpdir, caplog, capsys):  # pragma: no cover
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_md = str(tmpdir.join("notebook.md"))

    with open(tmp_md, "w") as fp:
        fp.write(
            """```r
1 + 2 + 3
```
"""
        )

    jupytext(args=[tmp_md, "--to", "ipynb", "--execute"])

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"]["text/markdown"] == "6"


@requires_nbconvert
@skip_on_windows
def test_execute_in_subfolder(tmpdir, caplog, capsys):
    subfolder = tmpdir.mkdir("subfolder")

    tmp_csv = str(subfolder.join("inputs.csv"))
    tmp_py = str(subfolder.join("notebook.py"))
    tmp_ipynb = str(subfolder.join("notebook.ipynb"))

    with open(tmp_csv, "w") as fp:
        fp.write("1\n2\n")

    with open(tmp_py, "w") as fp:
        fp.write(
            """import ast

with open('inputs.csv') as fp:
    text = fp.read()

sum(ast.literal_eval(line) for line in text.splitlines())
"""
        )

    jupytext(args=[tmp_py, "--to", "ipynb", "--execute"])

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 3
    assert nb.cells[2].outputs[0]["data"] == {"text/plain": "3"}

    tmp2_py = str(tmpdir.mkdir("another_folder").join("notebook.py"))
    tmp2_ipynb = str(tmpdir.join("another_folder", "notebook.ipynb"))

    shutil.copy(tmp_py, tmp2_py)

    # Executing without run-path fails
    import nbconvert

    with pytest.raises(
        nbconvert.preprocessors.execute.CellExecutionError,
        match="No such file or directory: 'inputs.csv'",
    ):
        jupytext(args=[tmp2_py, "--to", "ipynb", "--execute"])

    # Raise if folder does not exists
    with pytest.raises(ValueError, match="is not a valid path"):
        jupytext(args=[tmp2_py, "--to", "ipynb", "--run-path", "wrong_path"])

    # Execute in full path
    jupytext(args=[tmp2_py, "--to", "ipynb", "--run-path", str(subfolder)])
    nb = read(tmp2_ipynb)
    assert len(nb.cells) == 3
    assert nb.cells[2].outputs[0]["data"] == {"text/plain": "3"}

    # Execute in path relative to notebook dir
    jupytext(args=[tmp2_py, "--to", "ipynb", "--run-path", "../subfolder"])
    nb = read(tmp2_ipynb)
    assert len(nb.cells) == 3
    assert nb.cells[2].outputs[0]["data"] == {"text/plain": "3"}
