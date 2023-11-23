import pytest
from git import Repo


@pytest.fixture
def tmp_repo(tmpdir):
    repo = Repo.init(str(tmpdir))
    return repo
