import os
import pytest
from shutil import copyfile
from jupytext.compare import compare
from nbformat.v4.nbbase import new_notebook, new_code_cell
from .utils import list_notebooks, requires_black, requires_flake8, requires_autopep8

from jupytext import read, write
from jupytext.cli import system, jupytext, pipe_notebook
from jupytext.combine import black_invariant
from jupytext.header import _DEFAULT_NOTEBOOK_METADATA


@requires_black
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_apply_black_on_python_notebooks(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))
    copyfile(nb_file, tmp_ipynb)

    jupytext(args=[tmp_ipynb, "--to", "py:percent"])
    system("black", tmp_py)
    jupytext(args=[tmp_py, "--to", "ipynb", "--update"])

    nb1 = read(nb_file)
    nb2 = read(tmp_ipynb)
    nb3 = read(tmp_py)

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


@requires_black
def test_pipe_into_black():
    nb_org = new_notebook(cells=[new_code_cell("1        +1")])
    nb_dest = new_notebook(cells=[new_code_cell("1 + 1")])

    nb_pipe = pipe_notebook(nb_org, "black")
    compare(nb_pipe, nb_dest)


@requires_autopep8
def test_pipe_into_autopep8():
    nb_org = new_notebook(cells=[new_code_cell("1        +1")])
    nb_dest = new_notebook(cells=[new_code_cell("1 + 1")])

    nb_pipe = pipe_notebook(nb_org, "autopep8 -")
    compare(nb_pipe, nb_dest)


@requires_flake8
def test_pipe_into_flake8():
    # Notebook OK
    nb = new_notebook(cells=[new_code_cell("# correct code\n1 + 1")])
    pipe_notebook(nb, "flake8", update=False)

    # Notebook not OK
    nb = new_notebook(cells=[new_code_cell("incorrect code")])
    with pytest.raises(SystemExit):
        pipe_notebook(nb, "flake8", update=False)


@requires_black
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py")[:1])
def test_apply_black_through_jupytext(tmpdir, nb_file):
    # Load real notebook metadata to get the 'auto' extension in --pipe-fmt to work
    metadata = read(nb_file).metadata

    nb_org = new_notebook(cells=[new_code_cell("1        +1")], metadata=metadata)
    nb_black = new_notebook(cells=[new_code_cell("1 + 1")], metadata=metadata)

    os.makedirs(str(tmpdir.join("notebook_folder")))
    os.makedirs(str(tmpdir.join("script_folder")))

    tmp_ipynb = str(tmpdir.join("notebook_folder").join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("script_folder").join("notebook.py"))

    # Black in place
    write(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, "--pipe", "black"])
    nb_now = read(tmp_ipynb)
    compare(nb_now, nb_black)

    # Write to another folder using dots
    script_fmt = os.path.join("..", "script_folder//py:percent")
    write(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, "--to", script_fmt, "--pipe", "black"])
    assert os.path.isfile(tmp_py)
    nb_now = read(tmp_py)
    nb_now.metadata = metadata
    compare(nb_now, nb_black)
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
    compare(nb_now, nb_black)


@requires_black
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_apply_black_and_sync_on_paired_notebook(tmpdir, nb_file):
    # Load real notebook metadata to get the 'auto' extension in --pipe-fmt to work
    metadata = read(nb_file).metadata
    metadata["jupytext"] = {"formats": "ipynb,py"}
    assert "language_info" in metadata

    nb_org = new_notebook(cells=[new_code_cell("1        +1")], metadata=metadata)
    nb_black = new_notebook(cells=[new_code_cell("1 + 1")], metadata=metadata)

    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    # Black in place
    write(nb_org, tmp_ipynb)
    jupytext([tmp_ipynb, "--pipe", "black", "--sync"])

    nb_now = read(tmp_ipynb)
    compare(nb_now, nb_black)
    assert "language_info" in nb_now.metadata

    nb_now = read(tmp_py)
    nb_now.metadata["jupytext"].pop("text_representation")
    nb_black.metadata = {
        key: nb_black.metadata[key]
        for key in nb_black.metadata
        if key in _DEFAULT_NOTEBOOK_METADATA.split(",")
    }
    compare(nb_now, nb_black)


@requires_black
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
    compare(nb.cells, [new_code_cell("1 + 2 + 3 + 4")])


@requires_black
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
