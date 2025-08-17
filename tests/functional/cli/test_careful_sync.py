import itertools
import os
import time

import nbformat
import pytest

from jupytext import read, write
from jupytext.cli import careful_sync, read_contents_and_timestamp
import jupytext.combine
import jupytext.cli


@pytest.fixture
def temp_notebook():
    """Create a temporary notebook with jupytext metadata"""
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_code_cell("print('hello world')"),
        nbformat.v4.new_markdown_cell("# Test notebook"),
    ]
    nb.cells[0].outputs = [nbformat.v4.new_output("execute_result", data={"text/plain": "'hello world'"})]
    nb.metadata.jupytext = {"formats": "ipynb,py:percent"}
    return nb


@pytest.fixture
def temp_pairs(tmp_path, temp_notebook):
    """Write a temporary notebook and its paired file"""
    ipynb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    write(temp_notebook, str(ipynb_path))
    write(temp_notebook, str(py_path))

    t = ipynb_path.stat().st_mtime
    os.utime(py_path, (t, t))
    os.utime(ipynb_path, (t, t))

    return dict(ipynb=ipynb_path, py=py_path)


EXTS = ["ipynb", "py"]


@pytest.mark.parametrize("call_with", EXTS)
def test_careful_sync_no_action_ipynb(temp_pairs, call_with):
    contents = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}

    careful_sync(str(temp_pairs[call_with]))

    new_contents = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}
    assert new_contents == contents


@pytest.mark.parametrize("call_with,source", itertools.product(EXTS, EXTS))
def test_careful_sync_changes_only_older(temp_notebook, temp_pairs, call_with, source):
    time.sleep(0.1)  # Ensure different timestamps
    new_temp_notebook = temp_notebook.copy()
    new_temp_notebook.cells[0].source = "print('updated content')"
    write(new_temp_notebook, str(temp_pairs[source]))

    contents_before = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}

    careful_sync(str(temp_pairs[call_with]))

    new_contents = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}

    for ext in EXTS:
        if ext == source:
            assert new_contents[ext] == contents_before[ext]
        else:
            assert new_contents[ext][0] != contents_before[ext][0]
            assert new_contents[ext][1] == new_contents[source][1] == contents_before[source][1]


def test_careful_sync_external_rewrite_source(temp_notebook, temp_pairs):
    py = str(temp_pairs["py"])
    time.sleep(0.1)  # Ensure different timestamps
    new_temp_notebook = temp_notebook.copy()
    new_temp_notebook.cells[0].source = "print('updated content')"
    write(new_temp_notebook, py)

    contents_before = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}

    # Simulate an external rewrite of the source file
    # while the sync is in progress

    new_new_temp_notebook = new_temp_notebook.copy()
    new_new_temp_notebook.cells[0].source = "print('further updated content')"
    overwritten_details = None

    original_combine_inputs_with_outputs = jupytext.combine.combine_inputs_with_outputs

    def my_combine_inputs_with_outputs(*args, **kwargs):
        nonlocal overwritten_details
        write(new_new_temp_notebook, py)
        overwritten_details = read_contents_and_timestamp(py)
        return original_combine_inputs_with_outputs(*args, **kwargs)

    with pytest.MonkeyPatch.context() as m:
        m.setattr(jupytext.cli, "combine_inputs_with_outputs", my_combine_inputs_with_outputs)
        assert careful_sync(py) == 0
    assert overwritten_details is not None, "Expected the source file to be rewritten during sync"

    new_contents = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}
    assert new_contents["py"] == overwritten_details
    assert new_contents["ipynb"][1] == contents_before["py"][1], "ipynb timestamp should match py timestamp before overwrite"
    assert new_contents["ipynb"][0] != contents_before["ipynb"][0], "ipynb should have been updated with first pass"
    assert new_contents["ipynb"][0] != overwritten_details[0], "ipynb should not have been overwritten with second pass"


def test_careful_sync_external_rewrite_target(temp_notebook, temp_pairs):
    py = str(temp_pairs["py"])
    ipynb = str(temp_pairs["ipynb"])
    time.sleep(0.1)  # Ensure different timestamps
    new_temp_notebook = temp_notebook.copy()
    new_temp_notebook.cells[0].source = "print('updated content')"
    write(new_temp_notebook, py)

    contents_before = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}

    # Simulate an external rewrite of the source file
    # while the sync is in progress

    new_new_temp_notebook = new_temp_notebook.copy()
    new_new_temp_notebook.cells[0].source = "print('further updated content')"
    overwritten_details = None

    original_combine_inputs_with_outputs = jupytext.combine.combine_inputs_with_outputs

    def my_combine_inputs_with_outputs(*args, **kwargs):
        nonlocal overwritten_details
        time.sleep(0.1)  # Ensure different timestamps
        write(new_new_temp_notebook, ipynb)
        overwritten_details = read_contents_and_timestamp(ipynb)
        return original_combine_inputs_with_outputs(*args, **kwargs)

    with pytest.MonkeyPatch.context() as m:
        m.setattr(jupytext.cli, "combine_inputs_with_outputs", my_combine_inputs_with_outputs)
        assert careful_sync(py) != 0
    assert overwritten_details is not None, "Expected the source file to be rewritten during sync"

    new_contents = {k: read_contents_and_timestamp(v) for k, v in temp_pairs.items()}
    assert new_contents["ipynb"] == overwritten_details, "should not clobber the ipynb with the py content"
    assert new_contents["py"] == contents_before["py"], "py content is source so don't change"
