import unittest.mock as mock
from pathlib import Path

import pytest
from git import Repo
from nbformat.v4 import nbbase
from nbformat.v4.nbbase import (
    new_code_cell,
    new_markdown_cell,
    new_notebook,
    new_output,
)

import jupytext
from jupytext.cli import system

# Pytest's tmpdir is in /tmp (at least for me), so this helps avoiding interferences between
# global configuration on HOME and the test collection
jupytext.config.JUPYTEXT_CEILING_DIRECTORIES = ["/tmp/"]


@pytest.fixture
def no_jupytext_version_number():
    with mock.patch("jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER", False):
        yield


@pytest.fixture
def tmp_repo(tmpdir):
    repo = Repo.init(str(tmpdir))
    return repo


@pytest.fixture
def cwd_tmpdir(tmpdir):
    # Run the whole test from inside tmpdir
    with tmpdir.as_cwd():
        yield tmpdir


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
                        data={"text/plain": ["2"]},
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


"""To make sure that cell ids are distinct we use a global counter.
    This solves https://github.com/mwouts/jupytext/issues/747"""
global_cell_count = 0


def generate_corpus_id():
    global global_cell_count
    global_cell_count += 1
    return f"cell-{global_cell_count}"


nbbase.random_cell_id = generate_corpus_id
