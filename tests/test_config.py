import os
import pytest
from jupytext.config import (
    find_jupytext_configuration_file,
    load_jupytext_configuration_file,
    JupytextConfiguration,
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
    ["jupytext", "jupytext.toml", "jupytext.yml", "jupytext.json", "jupytext.py"],
)
def test_load_jupytext_configuration_file(tmpdir, config_file):
    full_config_path = tmpdir.join(config_file)

    if config_file.endswith(("jupytext", ".toml")):
        full_config_path.write(
            """default_jupytext_formats = "ipynb,py:percent"
default_notebook_metadata_filter = "all"
default_cell_metadata_filter = "all"
"""
        )
    elif config_file.endswith(".yml"):
        full_config_path.write(
            """default_jupytext_formats: ipynb,py:percent
default_notebook_metadata_filter: all
default_cell_metadata_filter: all
"""
        )
    elif config_file.endswith(".json"):
        full_config_path.write(
            """{"default_jupytext_formats": "ipynb,py:percent",
"default_notebook_metadata_filter": "all",
"default_cell_metadata_filter": "all"
}
"""
        )
    elif config_file.endswith(".py"):
        full_config_path.write(
            """c.default_jupytext_formats = "ipynb,py:percent"
c.default_notebook_metadata_filter = "all"
c.default_cell_metadata_filter = "all"
"""
        )

    config = load_jupytext_configuration_file(str(full_config_path))
    config = JupytextConfiguration(**config)
    assert config.default_jupytext_formats == "ipynb,py:percent"
    assert config.default_notebook_metadata_filter == "all"
    assert config.default_cell_metadata_filter == "all"
