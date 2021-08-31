import json
import os
import re
import sys
from pathlib import Path

import pytest
from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec

from jupytext.cell_reader import rst2md
from jupytext.cli import system
from jupytext.myst import is_myst_available
from jupytext.pandoc import is_pandoc_available
from jupytext.quarto import is_quarto_available


def tool_version(tool):
    try:
        args = tool.split(" ")
        args.append("--version")
        return system(*args)
    except (OSError, SystemExit):  # pragma: no cover
        return None


def isort_version():
    try:
        import isort

        return isort.__version__
    except ImportError:
        return None


requires_jupytext_installed = pytest.mark.skipif(
    not tool_version("jupytext"), reason="jupytext is not installed"
)
requires_black = pytest.mark.skipif(not tool_version("black"), reason="black not found")
requires_isort = pytest.mark.skipif(
    not isort_version() or isort_version() <= "5.3.0",
    reason="isort not found",
)
requires_flake8 = pytest.mark.skipif(
    not tool_version("flake8"), reason="flake8 not found"
)
requires_autopep8 = pytest.mark.skipif(
    not tool_version("autopep8"), reason="autopep8 not found"
)
requires_nbconvert = pytest.mark.skipif(
    not tool_version("jupyter nbconvert"), reason="nbconvert not found"
)
requires_sphinx_gallery = pytest.mark.skipif(
    not rst2md, reason="sphinx_gallery is not available"
)
requires_pandoc = pytest.mark.skipif(
    # The mirror files changed slightly when Pandoc 2.11 was introduced
    # https://github.com/mwouts/jupytext/commit/c07d919702999056ce47f92b74f63a15c8361c5d
    not is_pandoc_available(min_version="2.11"),
    reason="pandoc>=2.11 is not available",
)
requires_quarto = pytest.mark.skipif(
    not is_quarto_available(min_version="0.2.0"), reason="quarto>=0.2 is not available"
)
requires_no_pandoc = pytest.mark.skipif(
    is_pandoc_available(), reason="Pandoc is installed"
)
requires_ir_kernel = pytest.mark.skipif(
    not any(get_kernel_spec(name).language == "R" for name in find_kernel_specs()),
    reason="irkernel is not installed",
)
requires_user_kernel_python3 = pytest.mark.skipif(
    "python_kernel" not in find_kernel_specs(),
    reason="Please run 'python -m ipykernel install --name python_kernel --user'",
)
requires_myst = pytest.mark.skipif(
    not is_myst_available(), reason="myst_parser not found"
)
requires_no_myst = pytest.mark.skipif(is_myst_available(), reason="myst is available")
skip_on_windows = pytest.mark.skipif(sys.platform.startswith("win"), reason="Issue 489")
skip_pre_commit_tests_on_windows = pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="OSError: [WinError 193] %1 is not a valid Win32 application",
)
skip_pre_commit_tests_when_jupytext_folder_is_not_a_git_repo = pytest.mark.skipif(
    not (Path(__file__).parent.parent / ".git").is_dir(),
    reason="Jupytext folder is not a git repository #814",
)


def list_notebooks(path="ipynb", skip="World"):
    """All notebooks in the directory notebooks/path,
    or in the package itself"""
    if path == "ipynb":
        return (
            list_notebooks("ipynb_julia", skip=skip)
            + list_notebooks("ipynb_py", skip=skip)
            + list_notebooks("ipynb_R", skip=skip)
        )

    if path == "ipynb_all":
        all_notebooks = []

        nb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")
        for dir in os.listdir(nb_path):
            if dir.startswith("ipynb_"):
                all_notebooks.extend(list_notebooks(dir, skip=skip))

        return all_notebooks

    nb_path = os.path.dirname(os.path.abspath(__file__))
    if path.startswith("."):
        nb_path = os.path.join(nb_path, path)
    else:
        nb_path = os.path.join(nb_path, "notebooks", path)

    if skip:
        skip_re = re.compile(".*" + skip + ".*")
        notebooks = [
            os.path.join(nb_path, nb_file)
            for nb_file in os.listdir(nb_path)
            if not skip_re.match(nb_file)
        ]
    else:
        notebooks = [os.path.join(nb_path, nb_file) for nb_file in os.listdir(nb_path)]

    # ignore ".ipynb_checkpoints" sub-folder
    return [nb_file for nb_file in notebooks if os.path.isfile(nb_file)]


def notebook_model(nb):
    """Return a notebook model, with content a dictionary rather than a notebook object"""
    return dict(type="notebook", content=json.loads(json.dumps(nb)))
