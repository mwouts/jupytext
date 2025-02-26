"""Jupytext should refuse to open a file with invalid content"""

from pathlib import Path

import pytest
from jupyter_server.utils import ensure_async
from tornado.web import HTTPError

from jupytext import read
from jupytext.cli import jupytext as jupytext_cli


@pytest.fixture
def invalid_md_file():
    return Path(__file__).parent / "invalid_file_896.md"


@pytest.mark.skip_on_windows
def test_read_invalid_md_file_fails(invalid_md_file):
    with open(invalid_md_file) as fp:
        with pytest.raises(UnicodeDecodeError):
            read(fp)


def test_convert_invalid_md_file_fails(invalid_md_file):
    with pytest.raises(UnicodeDecodeError):
        jupytext_cli(["--to", "ipynb", str(invalid_md_file)])


@pytest.mark.asyncio
async def test_open_invalid_md_file_fails(invalid_md_file, tmp_path, cm):
    cm.root_dir = str(invalid_md_file.parent)

    with pytest.raises(HTTPError, match="invalid_file_896.md is not UTF-8 encoded"):
        await ensure_async(cm.get(invalid_md_file.name))
