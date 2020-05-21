import pytest
from nbformat.v4.nbbase import new_notebook, new_code_cell
from jupytext.cli import jupytext
from jupytext.jupytext import read, write
from jupytext.header import header_to_metadata_and_cell


def test_default_jupytext_formats(tmpdir):
    tmpdir.join(".jupytext").write(
        '''# Default pairing
default_jupytext_formats = "ipynb,py"'''
    )
    test = tmpdir.join("test.py")
    test.write("1 + 1\n")

    jupytext([str(test), "--sync"])

    assert tmpdir.join("test.ipynb").isfile()


def test_default_jupytext_formats_with_suffix(tmpdir):
    tmpdir.join(".jupytext").write('default_jupytext_formats = "ipynb,.nb.py"')
    test = tmpdir.join("test.py")
    test.write("1 + 1\n")

    test_nb = tmpdir.join("test.nb.py")
    test_nb.write("1 + 1\n")

    jupytext([str(test), "--sync"])
    assert not tmpdir.join("test.ipynb").isfile()

    jupytext([str(test_nb), "--sync"])
    assert tmpdir.join("test.ipynb").isfile()


def test_default_jupytext_formats_does_not_apply_to_config_file(tmpdir):
    config = tmpdir.join(".jupytext.py")
    config.write('c.default_jupytext_formats = "ipynb,py"')
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
    metadata, _, _, _ = header_to_metadata_and_cell(text_jl.splitlines(), "#")
    assert metadata["jupytext"]["formats"] == "ipynb,jl:percent"


@pytest.mark.parametrize(
    "config",
    [
        # Way 1: preferred_jupytext_formats_save + default_jupytext_formats
        """preferred_jupytext_formats_save: "python//py:percent"
default_jupytext_formats: "ipynb,python//py"
""",
        # Way 2: default_jupytext_formats
        "default_jupytext_formats: ipynb,python//py:percent",
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
