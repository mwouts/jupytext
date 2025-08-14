import time
import pytest

from jupytext.cli import read_contents_and_timestamp, write_if_unchanged_since
import os


def test_read_contents_and_timestamp(tmp_path):
    path = tmp_path / "test.txt"
    path.write_text("Hello, world!")

    content, timestamp = read_contents_and_timestamp(path)

    assert content == "Hello, world!"
    assert timestamp == path.stat().st_mtime


def test_read_contents_and_timestamp_nonexistent(tmp_path):
    path = tmp_path / "nonexistent.txt"

    with pytest.raises(FileNotFoundError):
        read_contents_and_timestamp(path)


def test_read_contents_and_timestamp_concurrent_deletion(tmp_path):
    path = tmp_path / "test.txt"
    path.write_text("Hello, world!")

    desired_content = path.read_text()
    original_timestamp = path.stat().st_mtime

    real_fdopen = os.fdopen

    def my_fdopen(fd, *args, **kwargs):
        path.unlink()  # Simulate concurrent deletion
        return real_fdopen(fd, *args, **kwargs)

    with pytest.MonkeyPatch.context() as m:
        m.setattr(os, "fdopen", my_fdopen)
        content, timestamp = read_contents_and_timestamp(path)

    assert content == desired_content
    assert timestamp == original_timestamp


@pytest.mark.parametrize("timestamp_delta", [-60, 0, 60])
def test_write_if_unchanged_since_nonexistent(tmp_path, timestamp_delta):
    path = tmp_path / "test.txt"
    content = "Hello, world!"
    target_timestamp = time.time() + timestamp_delta
    original_timestamp = 17  # Arbitrary value, since the file does not exist

    write_if_unchanged_since(
        path=path, content=content, original_timestamp=original_timestamp, target_timestamp=target_timestamp
    )

    assert path.read_text() == content
    assert os.stat(path).st_mtime == target_timestamp


@pytest.mark.parametrize("timestamp_delta", [0, -60, 60])
def test_write_if_unchanged_since_unchanged(tmp_path, timestamp_delta):
    path = tmp_path / "test.txt"
    content = "Hello, world!"
    path.write_text(content)
    original_timestamp = path.stat().st_mtime

    new_content = "Goodbye!"
    target_timestamp = original_timestamp + timestamp_delta

    assert write_if_unchanged_since(
        path=path, content=new_content, original_timestamp=original_timestamp, target_timestamp=target_timestamp
    )

    assert path.read_text() == new_content
    assert os.stat(path).st_mtime == target_timestamp


@pytest.mark.parametrize("timestamp_delta", [60])
def test_write_if_unchanged_since_changed(tmp_path, timestamp_delta):
    path = tmp_path / "test.txt"
    content = "Hello, world!"
    path.write_text(content)
    original_timestamp = path.stat().st_mtime

    time.sleep(0.1)

    alt_content = "Hello, universe!"
    path.write_text(alt_content)  # Simulate a change
    alt_timestamp = path.stat().st_mtime

    new_content = "Goodbye!"
    target_timestamp = original_timestamp + timestamp_delta

    assert not write_if_unchanged_since(
        path=path, content=new_content, original_timestamp=original_timestamp, target_timestamp=target_timestamp
    )

    assert path.read_text() == alt_content
    assert os.stat(path).st_mtime == alt_timestamp
