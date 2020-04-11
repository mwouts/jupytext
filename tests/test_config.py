import os
from jupytext.config import find_jupytext_configuration_file


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
