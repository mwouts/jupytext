"""Find and read Jupytext configuration files"""
import os

VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES = [
    "jupytext",
    "jupytext.toml",
    "jupytext.yml",
    "jupytext.yaml",
    "jupytext.json",
]

VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES.extend(
    ["." + filename for filename in VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES]
)


def find_jupytext_configuration_file(dir):
    """Return the first jupytext configuration file in the current directory, or any parent directory"""
    for filename in VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES:
        full_path = os.path.join(dir, filename)
        if os.path.isfile(full_path):
            return full_path
    parent_dir = os.path.dirname(dir)
    if os.path.samefile(dir, parent_dir):
        return None
    return find_jupytext_configuration_file(parent_dir)
