import pytest
import jupytext

try:
    import unittest.mock as mock
except ImportError:
    import mock


@pytest.fixture
def no_jupytext_version_number():
    with mock.patch("jupytext.header.INSERT_AND_CHECK_VERSION_NUMBER", False):
        yield


# Pytest's tmpdir is in /tmp (at least for me), so this helps avoiding interferences between
# global configuration on HOME and the test collection
jupytext.config.JUPYTEXT_CEILING_DIRECTORIES = ["/tmp/"]
