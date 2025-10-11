import os
from pathlib import Path
from contextlib import contextmanager

import pytest

from jupytext.config import (
    find_jupytext_configuration_file,
    load_jupytext_configuration_file,
    notebook_formats,
)
from jupytext.jupytext import load_jupytext_config, read


@contextmanager
def change_dir(path):
    """Context manager to temporarily change directory."""
    old_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_cwd)


@pytest.fixture
def temp_folder_tree(tmp_path):
    """
    Fixture that creates a temporary folder tree.
    tmp_path is a pytest built-in fixture that auto-cleans up.
    """
    # Create folder structure
    (tmp_path / "subdir").mkdir()

    # Create some files
    (tmp_path / "jupytext.toml").write_text("")
    (tmp_path / "subdir" / "notebook.ipynb").write_text("")

    return tmp_path


def test_issue_1440(temp_folder_tree):
    """Test that jupytext finds the config file even in parent of cwd"""
    notebook = Path("notebook.ipynb")
    notebook_str = str(notebook)
    expected_toml = str(temp_folder_tree / "jupytext.toml")
    with change_dir(temp_folder_tree / "subdir"):
        assert notebook.exists()
        config_file_from_path = find_jupytext_configuration_file(notebook)
        assert config_file_from_path == expected_toml
        config_file_from_str = find_jupytext_configuration_file(notebook_str)
        assert config_file_from_str == expected_toml


def test_find_jupytext_configuration_file(tmpdir):
    nested = tmpdir.mkdir("nested")

    # Start with no configuration
    assert find_jupytext_configuration_file(str(nested)) is None

    # Configuration file in the parent directory
    root_config = tmpdir.join("jupytext.yml")
    root_config.write("\n")
    assert os.path.samefile(find_jupytext_configuration_file(str(tmpdir)), str(root_config))
    assert os.path.samefile(find_jupytext_configuration_file(str(nested)), str(root_config))

    # Local pyproject file
    pyproject_config = nested.join("pyproject.toml")
    pyproject_config.write("[tool.jupytext]\n")
    assert os.path.samefile(find_jupytext_configuration_file(str(tmpdir)), str(root_config))
    assert os.path.samefile(find_jupytext_configuration_file(str(nested)), str(pyproject_config))

    # Local configuration file
    local_config = nested.join(".jupytext")
    local_config.write("\n")
    assert os.path.samefile(find_jupytext_configuration_file(str(tmpdir)), str(root_config))
    assert os.path.samefile(find_jupytext_configuration_file(str(nested)), str(local_config))


def test_jupytext_py_is_not_a_configuration_file(tmpdir):
    jupytext_py = tmpdir.join("jupytext.py")
    jupytext_py.write("# Not a config file!")

    assert find_jupytext_configuration_file(str(tmpdir)) is None

    dot_jupytext_py = tmpdir.join(".jupytext.py")
    dot_jupytext_py.write("# This is a config file!")

    assert find_jupytext_configuration_file(str(tmpdir)) == str(dot_jupytext_py)


@pytest.mark.parametrize(
    "config_file",
    [
        "pyproject.toml",
        "jupytext",
        "jupytext.toml",
        "jupytext.yml",
        "jupytext.json",
        "jupytext.py",
    ],
)
def test_load_jupytext_configuration_file(tmpdir, config_file):
    full_config_path = tmpdir.join(config_file)

    if config_file == "pyproject.toml":
        full_config_path.write(
            """[tool.jupytext]
formats = "ipynb,py:percent"
notebook_metadata_filter = "all"
cell_metadata_filter = "all"
"""
        )
    elif config_file.endswith(("jupytext", ".toml")):
        full_config_path.write(
            """formats = "ipynb,py:percent"
notebook_metadata_filter = "all"
cell_metadata_filter = "all"
"""
        )
    elif config_file.endswith(".yml"):
        full_config_path.write(
            """formats: ipynb,py:percent
notebook_metadata_filter: all
cell_metadata_filter: all
"""
        )
    elif config_file.endswith(".json"):
        full_config_path.write(
            """{"formats": "ipynb,py:percent",
"notebook_metadata_filter": "all",
"cell_metadata_filter": "all"
}
"""
        )
    elif config_file.endswith(".py"):
        full_config_path.write(
            """c.formats = "ipynb,py:percent"
c.notebook_metadata_filter = "all"
c.cell_metadata_filter = "all"
"""
        )

    config = load_jupytext_configuration_file(str(full_config_path))
    assert config.formats == "ipynb,py:percent"
    assert config.notebook_metadata_filter == "all"
    assert config.cell_metadata_filter == "all"


@pytest.mark.parametrize(
    "content_toml,formats_short_form",
    [
        (
            """# always pair ipynb notebooks to py:percent files
formats = "ipynb,py:percent"
""",
            "ipynb,py:percent",
        ),
        (
            """# always pair ipynb notebooks to py:percent files
formats = ['ipynb', 'py:percent']
""",
            "ipynb,py:percent",
        ),
        (
            """# always pair ipynb notebooks to py:percent files
formats = ["ipynb", "py:percent"]
""",
            "ipynb,py:percent",
        ),
        (
            """# always pair ipynb notebooks to py:percent files
formats = "ipynb,py:percent"
""",
            "ipynb,py:percent",
        ),
        (
            """# Pair notebooks in subfolders of 'notebooks' to scripts in subfolders of 'scripts'
[formats]
"notebooks/" = "ipynb"
"scripts/" = "py:percent"
""",
            "notebooks///ipynb,scripts///py:percent",
        ),
        (
            """# Pair notebooks in subfolders of 'notebooks' to scripts in subfolders of 'scripts'
[formats]
"notebooks" = "ipynb"
"scripts" = "py:percent"
""",
            "notebooks///ipynb,scripts///py:percent",
        ),
        (
            """# Pair local notebooks to scripts in 'notebooks_py' and md files in 'notebooks_md'
[formats]
"" = "ipynb"
"notebooks_py" = "py:percent"
"notebooks_md" = "md:myst"
""",
            "ipynb,notebooks_py///py:percent,notebooks_md///md:myst",
        ),
    ],
)
def test_jupytext_formats(tmpdir, content_toml, formats_short_form):
    jupytext_toml = tmpdir.join("jupytext.toml")
    jupytext_toml.write(content_toml)

    config = load_jupytext_configuration_file(str(jupytext_toml))
    assert config.formats == formats_short_form


def test_deprecated_formats_cause_warning(tmpdir, content_toml="default_jupytext_formats = 'ipynb,md'"):
    jupytext_toml = tmpdir.join("jupytext.toml")
    jupytext_toml.write(content_toml)

    config = load_jupytext_configuration_file(str(jupytext_toml))
    with pytest.warns(FutureWarning, match="use 'formats'"):
        assert config.default_formats(str(tmpdir.join("test.md"))) == "ipynb,md"


@pytest.mark.parametrize(
    "option_name",
    ["notebook_metadata_filter", "cell_metadata_filter", "cell_markers"],
)
def test_deprecated_options_cause_warning(tmpdir, option_name):
    jupytext_toml = tmpdir.join("jupytext.toml")
    jupytext_toml.write(f"default_{option_name} = 'value'")
    config = load_jupytext_configuration_file(str(jupytext_toml))
    fmt = {}
    with pytest.warns(FutureWarning, match=f"use '{option_name}'"):
        config.set_default_format_options(fmt)
        assert fmt[option_name] == "value"


def test_simple_py_file_is_not_paired(tmp_path):
    py_file = tmp_path / "simple.py"
    py_file.write_text('print("Hello, world!")')

    config_file = tmp_path / "jupytext.toml"
    config_file.write_text('formats = "ipynb,py:percent"')

    notebook = read(str(py_file))
    config_file = load_jupytext_config(str(config_file))

    formats = notebook_formats(notebook, config_file, str(py_file))
    assert formats == [{"extension": ".py", "format_name": "light"}], formats


def test_pairing_groups(tmpdir):
    """Test format groups for subset-specific pairing"""
    jupytext_toml = tmpdir.join("jupytext.toml")
    jupytext_toml.write("""
[formats]
"notebooks/" = "ipynb"
"scripts/" = "py:percent"

[pairing_groups.tutorials]
"notebooks/tutorials/" = "ipynb"
"docs/tutorials/" = "md"
"scripts/tutorials/" = "py:percent"
""")

    config = load_jupytext_configuration_file(str(jupytext_toml))

    # Main formats should be parsed correctly
    assert config.formats == "notebooks///ipynb,scripts///py:percent"

    # Format groups should be parsed and processed
    assert "tutorials" in config.pairing_groups
    assert (
        config.pairing_groups["tutorials"] == "notebooks/tutorials///ipynb,docs/tutorials///md,scripts/tutorials///py:percent"
    )

    # Test that default_formats returns the correct formats based on path
    # Regular notebook should use main formats
    regular_notebook = str(tmpdir.join("notebooks/hello.ipynb"))
    assert config.default_formats(regular_notebook) == "notebooks///ipynb,scripts///py:percent"

    # Tutorial notebook should use group formats
    tutorial_notebook = str(tmpdir.join("notebooks/tutorials/getting_started.ipynb"))
    assert (
        config.default_formats(tutorial_notebook)
        == "notebooks/tutorials///ipynb,docs/tutorials///md,scripts/tutorials///py:percent"
    )


def test_pairing_groups_multiple_groups(tmpdir):
    """Test multiple format groups"""
    jupytext_toml = tmpdir.join("jupytext.toml")
    jupytext_toml.write("""
[formats]
"notebooks/" = "ipynb"
"scripts/" = "py:percent"

[pairing_groups.tutorials]
"notebooks/tutorials/" = "ipynb"
"docs/tutorials/" = "md"

[pairing_groups.examples]
"notebooks/examples/" = "ipynb"
"docs/examples/" = "md:myst"
""")

    config = load_jupytext_configuration_file(str(jupytext_toml))

    # Check both groups exist
    assert "tutorials" in config.pairing_groups
    assert "examples" in config.pairing_groups

    # Test that the correct group is selected based on path
    tutorial_notebook = str(tmpdir.join("notebooks/tutorials/intro.ipynb"))
    assert config.default_formats(tutorial_notebook) == "notebooks/tutorials///ipynb,docs/tutorials///md"

    example_notebook = str(tmpdir.join("notebooks/examples/demo.ipynb"))
    assert config.default_formats(example_notebook) == "notebooks/examples///ipynb,docs/examples///md:myst"

    # Regular notebook should still use main formats
    regular_notebook = str(tmpdir.join("notebooks/regular.ipynb"))
    assert config.default_formats(regular_notebook) == "notebooks///ipynb,scripts///py:percent"


def test_pairing_groups_without_main_formats(tmpdir):
    """Test format groups can work without main formats"""
    jupytext_toml = tmpdir.join("jupytext.toml")
    jupytext_toml.write("""
[pairing_groups.tutorials]
"notebooks/tutorials/" = "ipynb"
"docs/tutorials/" = "md"
""")

    config = load_jupytext_configuration_file(str(jupytext_toml))

    # No main formats
    assert config.formats == ""

    # But group formats should work
    tutorial_notebook = str(tmpdir.join("notebooks/tutorials/getting_started.ipynb"))
    assert config.default_formats(tutorial_notebook) == "notebooks/tutorials///ipynb,docs/tutorials///md"

    # Non-matching notebook should return None
    other_notebook = str(tmpdir.join("notebooks/other.ipynb"))
    assert config.default_formats(other_notebook) is None


def test_pairing_groups_yaml(tmpdir):
    """Test format groups with YAML config"""
    jupytext_yml = tmpdir.join("jupytext.yml")
    jupytext_yml.write("""
formats:
  notebooks/: ipynb
  scripts/: py:percent
pairing_groups:
  tutorials:
    notebooks/tutorials/: ipynb
    docs/tutorials/: md
""")

    config = load_jupytext_configuration_file(str(jupytext_yml))

    # Main formats should be parsed correctly
    assert config.formats == "notebooks///ipynb,scripts///py:percent"

    # Format groups should be parsed
    assert "tutorials" in config.pairing_groups
    assert config.pairing_groups["tutorials"] == "notebooks/tutorials///ipynb,docs/tutorials///md"


def test_pairing_groups_json(tmpdir):
    """Test format groups with JSON config"""
    jupytext_json = tmpdir.join("jupytext.json")
    jupytext_json.write("""{
  "formats": {
    "notebooks/": "ipynb",
    "scripts/": "py:percent"
  },
  "pairing_groups": {
    "tutorials": {
      "notebooks/tutorials/": "ipynb",
      "docs/tutorials/": "md"
    }
  }
}
""")

    config = load_jupytext_configuration_file(str(jupytext_json))

    # Main formats should be parsed correctly
    assert config.formats == "notebooks///ipynb,scripts///py:percent"

    # Format groups should be parsed
    assert "tutorials" in config.pairing_groups
    assert config.pairing_groups["tutorials"] == "notebooks/tutorials///ipynb,docs/tutorials///md"
