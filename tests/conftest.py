import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock


@pytest.fixture
def no_jupytext_version_number():
    with mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', False):
        yield
