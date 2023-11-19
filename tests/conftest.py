import sys
import unittest.mock as mock
from pathlib import Path

import pytest
from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec
from nbformat.v4 import nbbase
from nbformat.v4.nbbase import (
    new_code_cell,
    new_markdown_cell,
    new_notebook,
    new_output,
)

import jupytext
from jupytext.cell_reader import rst2md
from jupytext.cli import system
from jupytext.myst import is_myst_available
from jupytext.pandoc import is_pandoc_available
from jupytext.quarto import is_quarto_available

from .utils import formats_with_support_for_cell_metadata, tool_version

# Pytest's tmpdir is in /tmp (at least for me), so this helps to avoid interferences between
# global configuration on HOME and the test collection
jupytext.config.JUPYTEXT_CEILING_DIRECTORIES = ["/tmp/"]


@pytest.fixture
def no_jupytext_version_number():
    with mock.patch("jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER", False):
        yield


@pytest.fixture
def cwd_tmpdir(tmpdir):
    # Run the whole test from inside tmpdir
    with tmpdir.as_cwd():
        yield tmpdir


@pytest.fixture()
def cwd_tmp_path(tmp_path):
    # Run the whole test from inside tmp_path
    with tmp_path.cwd():
        yield tmp_path


@pytest.fixture
def jupytext_repo_root():
    """The local path of this repo, to use in .pre-commit-config.yaml in tests"""
    return str(Path(__file__).parent.parent.resolve())


@pytest.fixture
def jupytext_repo_rev(jupytext_repo_root):
    """The local revision of this repo, to use in .pre-commit-config.yaml in tests"""
    return system("git", "rev-parse", "HEAD", cwd=jupytext_repo_root).strip()


@pytest.fixture()
def python_notebook():
    return new_notebook(
        cells=[new_markdown_cell("A short notebook")],
        # We need a Python kernel here otherwise Jupytext is going to add
        # the information that this is a Python notebook when we sync the
        # .py and .ipynb files
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python_kernel",
            }
        },
    )


@pytest.fixture()
def notebook_with_outputs():
    return new_notebook(
        cells=[
            new_code_cell(
                "1+1",
                execution_count=1,
                outputs=[
                    new_output(
                        data={"text/plain": "2"},
                        execution_count=1,
                        output_type="execute_result",
                    )
                ],
            )
        ],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python_kernel",
            }
        },
    )


@pytest.fixture(params=list(formats_with_support_for_cell_metadata()))
def fmt_with_cell_metadata(request):
    return request.param


def pytest_runtest_setup(item):
    for mark in item.iter_markers():
        for tool in [
            "jupytext",
            "black",
            "isort",
            "flake8",
            "autopep8",
            "jupyter nbconvert",
        ]:
            if mark.name == f"requires_{tool.replace(' ', '_')}":
                if not tool_version(tool):
                    pytest.skip(f"{tool} is not installed")
        if mark.name == "requires_sphinx_gallery":
            if not rst2md:
                pytest.skip("sphinx_gallery is not available")
        if mark.name == "requires_pandoc":
            # The mirror files changed slightly when Pandoc 2.11 was introduced
            # https://github.com/mwouts/jupytext/commit/c07d919702999056ce47f92b74f63a15c8361c5d
            # The mirror files changed again when Pandoc 2.16 was introduced
            # https://github.com/mwouts/jupytext/pull/919/commits/1fa1451ecdaa6ad8d803bcb6fb0c0cf09e5371bf
            if not is_pandoc_available(min_version="2.16.2", max_version="2.16.2"):
                pytest.skip("pandoc==2.16.2 is not available")
        if mark.name == "requires_quarto":
            if not is_quarto_available(min_version="0.2.0"):
                pytest.skip("quarto>=0.2 is not available")
        if mark.name == "requires_no_pandoc":
            if is_pandoc_available():
                pytest.skip("Pandoc is installed")
        if mark.name == "requires_ir_kernel":
            if not any(
                get_kernel_spec(name).language == "R" for name in find_kernel_specs()
            ):
                pytest.skip("irkernel is not installed")
        if mark.name == "requires_user_kernel_python3":
            if "python_kernel" not in find_kernel_specs():
                pytest.skip(
                    "Please run 'python -m ipykernel install --name python_kernel --user'"
                )
        if mark.name == "requires_myst":
            if not is_myst_available():
                pytest.skip("myst_parser not found")
        if mark.name == "requires_no_myst":
            if is_myst_available():
                pytest.skip("myst is available")
        if mark.name == "skip_on_windows":
            if sys.platform.startswith("win"):
                pytest.skip("Issue 489")
        if mark.name == "pre_commit":
            if sys.platform.startswith("win"):
                pytest.skip(
                    "OSError: [WinError 193] %1 is not a valid Win32 application"
                )
            if not (Path(__file__).parent.parent / ".git").is_dir():
                pytest.skip("Jupytext folder is not a git repository #814")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if (
            config.rootdir / "tests" / "functional" / "pre_commit"
        ) in item.path.parents:
            item.add_marker(pytest.mark.pre_commit)


"""To make sure that cell ids are distinct we use a global counter.
    This solves https://github.com/mwouts/jupytext/issues/747"""
global_cell_count = 0


def generate_corpus_id():
    global global_cell_count
    global_cell_count += 1
    return f"cell-{global_cell_count}"


nbbase.random_cell_id = generate_corpus_id
