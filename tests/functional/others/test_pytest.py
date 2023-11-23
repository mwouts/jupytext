import pytest

from jupytext.cli import jupytext


def test_run_pytest_ok(
    tmpdir,
    text="""This is a notebook with a test that is supposed to pass
```python
def test_ok():
    assert True
```
""",
):
    tmp_md = str(tmpdir.join("notebook.md"))
    with open(tmp_md, "w") as fp:
        fp.write(text)
    jupytext([tmp_md, "--check", "pytest"])


def test_run_pytest_fail(
    tmpdir,
    capsys,
    text="""This is a notebook with a test that should not pass
```python
def test_fail():
    assert False
```
""",
):
    tmp_md = str(tmpdir.join("notebook.md"))
    with open(tmp_md, "w") as fp:
        fp.write(text)
    with pytest.raises(SystemExit):
        jupytext([tmp_md, "--check", "pytest"])
