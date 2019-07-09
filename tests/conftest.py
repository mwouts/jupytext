import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock


@pytest.fixture
def header_insert_and_check_version_number_patch():
    m = mock.patch('jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER', False)
    m.start()
    yield m
    m.stop()
