from .utils import requires_nbconvert, requires_ir_kernel
import pytest
from jupytext import read
from jupytext.cli import jupytext


def skip_if_timeout(caplog, capsys):
    """Skip the test if a timeout occurs when executing the notebook. See Issue 489"""
    if "Timeout" in caplog.text:
        pytest.skip(caplog.text)

    _, err = capsys.readouterr()
    if "Timeout" in err:
        pytest.skip(err)


@requires_nbconvert
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
            "jupyter nbconvert --stdin --stdout --to notebook --execute --NotebookClient.iopub_timeout=60",
        ]
    )

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"] == {"text/plain": "3"}


@requires_nbconvert
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
            "jupyter nbconvert --stdin --stdout --to notebook --execute --NotebookClient.iopub_timeout=60",
        ]
    )

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"] == {"text/plain": "3"}


@requires_nbconvert
def test_execute(tmpdir, caplog, capsys):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    with open(tmp_py, "w") as fp:
        fp.write(
            """1 + 2
"""
        )

    jupytext(args=[tmp_py, "--to", "ipynb", "--execute"])
    skip_if_timeout(caplog, capsys)

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
def test_execute_sync(tmpdir, caplog, capsys):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    with open(tmp_py, "w") as fp:
        fp.write(
            """1 + 2
"""
        )

    jupytext(args=[tmp_py, "--set-formats", "py,ipynb", "--sync", "--execute"])
    skip_if_timeout(caplog, capsys)

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"] == {"text/plain": "3"}


@requires_nbconvert
@requires_ir_kernel
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
    skip_if_timeout(caplog, capsys)

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 1
    assert nb.cells[0].outputs[0]["data"]["text/markdown"] == "6"


@requires_nbconvert
def test_execute_in_subfolder(tmpdir, caplog, capsys):
    tmpdir.mkdir("subfolder")

    tmp_csv = str(tmpdir.join("subfolder", "inputs.csv"))
    tmp_py = str(tmpdir.join("subfolder", "notebook.py"))
    tmp_ipynb = str(tmpdir.join("subfolder", "notebook.ipynb"))

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
    skip_if_timeout(caplog, capsys)

    nb = read(tmp_ipynb)
    assert len(nb.cells) == 3
    assert nb.cells[2].outputs[0]["data"] == {"text/plain": "3"}
