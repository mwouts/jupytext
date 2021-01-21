import unittest.mock as mock
from pathlib import Path

import pytest
from git import Repo

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
