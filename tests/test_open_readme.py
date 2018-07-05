import nbrmd
import pytest
import os


@pytest.fixture()
def readme():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'README.md')


def test_open_readme(readme):
    nb = nbrmd.readf(readme)
