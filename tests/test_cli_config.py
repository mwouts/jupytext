import nbformat
import pytest
from nbformat.v4.nbbase import new_code_cell, new_notebook

from jupytext.cli import jupytext
from jupytext.compare import compare
from jupytext.header import header_to_metadata_and_cell
from jupytext.jupytext import read, write


def test_pairing_through_config_leaves_ipynb_unmodified(tmpdir):
    cfg_file = tmpdir.join(".jupytext.yml")
    nb_file = tmpdir.join("notebook.ipynb")
    py_file = tmpdir.join("notebook.py")

    cfg_file.write("formats: 'ipynb,py'\n")
    nbformat.write(new_notebook(), str(nb_file))

    jupytext([str(nb_file), "--sync"])

    assert nb_file.isfile()
    assert py_file.isfile()

    nb = nbformat.read(nb_file, as_version=4)
    assert "jupytext" not in nb.metadata


def test_formats(tmpdir):
    tmpdir.join(".jupytext").write(
        '''# Default pairing
formats = "ipynb,py"'''
    )
    test = tmpdir.join("test.py")
    test.write("1 + 1\n")

    jupytext([str(test), "--sync"])

    assert tmpdir.join("test.ipynb").isfile()


def test_formats_with_suffix(tmpdir):
    tmpdir.join(".jupytext").write('formats = "ipynb,.nb.py"')
    test = tmpdir.join("test.py")
    test.write("1 + 1\n")

    test_nb = tmpdir.join("test.nb.py")
    test_nb.write("1 + 1\n")

    jupytext([str(test), "--sync"])
    assert not tmpdir.join("test.ipynb").isfile()

    jupytext([str(test_nb), "--sync"])
    assert tmpdir.join("test.ipynb").isfile()


def test_formats_does_not_apply_to_config_file(tmpdir):
    config = tmpdir.join(".jupytext.py")
    config.write('c.formats = "ipynb,py"')
    test = tmpdir.join("test.py")
    test.write("1 + 1\n")

    jupytext([str(test), str(config), "--sync"])

    assert tmpdir.join("test.ipynb").isfile()
    assert not tmpdir.join(".jupytext.ipynb").isfile()


def test_preferred_jupytext_formats_save(tmpdir):
    tmpdir.join(".jupytext.yml").write("preferred_jupytext_formats_save: jl:percent")
    tmp_ipynb = tmpdir.join("notebook.ipynb")
    tmp_jl = tmpdir.join("notebook.jl")

    nb = new_notebook(
        cells=[new_code_cell("1 + 1")], metadata={"jupytext": {"formats": "ipynb,jl"}}
    )

    write(nb, str(tmp_ipynb))
    jupytext([str(tmp_ipynb), "--sync"])

    with open(str(tmp_jl)) as stream:
        text_jl = stream.read()

    # Parse the YAML header
    metadata, _, _, _ = header_to_metadata_and_cell(text_jl.splitlines(), "#", "")
    assert metadata["jupytext"]["formats"] == "ipynb,jl:percent"


@pytest.mark.parametrize(
    "config",
    [
        # Way 1: preferred_jupytext_formats_save + formats
        """preferred_jupytext_formats_save: "python//py:percent"
formats: "ipynb,python//py"
""",
        # Way 2: formats
        "formats: ipynb,python//py:percent",
    ],
)
def test_save_using_preferred_and_default_format(config, tmpdir):
    tmpdir.join(".jupytext.yml").write(config)
    tmp_ipynb = tmpdir.join("notebook.ipynb")
    tmp_py = tmpdir.join("python").join("notebook.py")

    nb = new_notebook(cells=[new_code_cell("1 + 1")])

    write(nb, str(tmp_ipynb))
    jupytext([str(tmp_ipynb), "--sync"])

    # read py file
    nb_py = read(str(tmp_py))
    assert nb_py.metadata["jupytext"]["text_representation"]["format_name"] == "percent"


def test_hide_notebook_metadata(tmpdir, no_jupytext_version_number):
    tmpdir.join(".jupytext").write("hide_notebook_metadata = true")
    tmp_ipynb = tmpdir.join("notebook.ipynb")
    tmp_md = tmpdir.join("notebook.md")

    nb = new_notebook(
        cells=[new_code_cell("1 + 1")], metadata={"jupytext": {"formats": "ipynb,md"}}
    )

    write(nb, str(tmp_ipynb))
    jupytext([str(tmp_ipynb), "--sync"])

    with open(str(tmp_md)) as stream:
        text_md = stream.read()

    compare(
        text_md,
        """<!--

---
jupyter:
  jupytext:
    formats: ipynb,md
    hide_notebook_metadata: true
---

-->

```python
1 + 1
```
""",
    )


def test_cli_config_on_windows_issue_629(tmpdir):
    cfg_file = tmpdir.join("jupytext.yml")
    cfg_file.write(
        """formats: "notebooks///ipynb,scripts///py:percent"
notebook_metadata_filter: "jupytext"
"""
    )

    tmpdir.mkdir("scripts").join("test.py").write("# %%\n 1+1\n")

    jupytext(["--sync", str(tmpdir.join("scripts").join("*.py"))])

    assert tmpdir.join("notebooks").join("test.ipynb").exists()


def test_sync_config_does_not_create_formats_metadata(
    tmpdir, cwd_tmpdir, python_notebook
):
    tmpdir.join("jupytext.yml").write(
        """formats: "ipynb,py:percent"
"""
    )

    write(python_notebook, "test.ipynb")
    jupytext(["--sync", "test.ipynb"])

    nb = read("test.py")
    assert "formats" not in nb.metadata["jupytext"]


def test_multiple_formats_771(tmpdir, cwd_tmpdir, python_notebook):
    tmpdir.join("jupytext.toml").write(
        """formats = "notebooks///ipynb,notebooks///py,scripts///py:percent"
"""
    )
    notebooks_dir = tmpdir.mkdir("notebooks")
    scripts_dir = tmpdir.join("scripts")

    write(python_notebook, str(notebooks_dir.join("notebook.ipynb")))
    jupytext(["--sync", "notebooks/notebook.ipynb"])

    assert notebooks_dir.join("notebook.py").isfile()
    assert scripts_dir.join("notebook.py").isfile()

    notebooks_dir.join("module.py").write("1 + 1\n")
    jupytext(["--sync", "notebooks/module.py"])

    assert notebooks_dir.join("module.ipynb").isfile()
    assert scripts_dir.join("module.py").isfile()
