import os

import pytest

from jupytext.config import (
    find_jupytext_configuration_file,
    load_jupytext_configuration_file,
)


def test_find_jupytext_configuration_file(tmpdir):
    nested = tmpdir.mkdir("nested")

    # Start with no configuration
    assert find_jupytext_configuration_file(str(nested)) is None

    # Configuration file in the parent directory
    root_config = tmpdir.join("jupytext.yml")
    root_config.write("\n")
    assert os.path.samefile(
        find_jupytext_configuration_file(str(tmpdir)), str(root_config)
    )
    assert os.path.samefile(
        find_jupytext_configuration_file(str(nested)), str(root_config)
    )

    # Local pyproject file
    pyproject_config = nested.join("pyproject.toml")
    pyproject_config.write("[tool.jupytext]\n")
    assert os.path.samefile(
        find_jupytext_configuration_file(str(tmpdir)), str(root_config)
    )
    assert os.path.samefile(
        find_jupytext_configuration_file(str(nested)), str(pyproject_config)
    )

    # Local configuration file
    local_config = nested.join(".jupytext")
    local_config.write("\n")
    assert os.path.samefile(
        find_jupytext_configuration_file(str(tmpdir)), str(root_config)
    )
    assert os.path.samefile(
        find_jupytext_configuration_file(str(nested)), str(local_config)
    )


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


def test_deprecated_formats_cause_warning(
    tmpdir, content_toml="default_jupytext_formats = 'ipynb,md'"
):
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
