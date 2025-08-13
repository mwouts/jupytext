import time

import nbformat
import pytest

from jupytext import read, write
from jupytext.cli import propagate_changes


@pytest.fixture
def temp_notebook():
    """Create a temporary notebook with jupytext metadata"""
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_code_cell("print('hello world')"),
        nbformat.v4.new_markdown_cell("# Test notebook"),
    ]
    nb.metadata.jupytext = {"formats": "ipynb,py:percent"}
    return nb


def test_propagate_changes_creates_py_file(temp_notebook, tmp_path):
    """Test that propagate_changes creates a paired .py file"""
    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    write(temp_notebook, str(nb_path))
    propagate_changes(str(nb_path))

    assert py_path.exists()
    py_content = read(str(py_path))
    assert len(py_content.cells) == 2


def test_propagate_changes_no_pairing_info(tmp_path):
    """Test that function exits early when notebook has no pairing info"""
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("print('test')")]

    nb_path = tmp_path / "unpaired.ipynb"
    write(nb, str(nb_path))

    # Should not raise an error, just exit early
    propagate_changes(str(nb_path))

    assert list(tmp_path.iterdir()) == [nb_path]


def test_propagate_changes_preserves_outputs(temp_notebook, tmp_path):
    """Test that outputs are preserved when updating from .py to .ipynb"""
    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    # Add output to notebook
    temp_notebook.cells[0].outputs = [
        nbformat.v4.new_output("execute_result", data={"text/plain": "'hello world'"})
    ]

    write(temp_notebook, str(nb_path))
    write(temp_notebook, str(py_path), fmt="py:percent")

    # Modify the .py file
    py_nb = read(str(py_path))
    py_nb.cells[0].source = "print('modified')"
    write(py_nb, str(py_path), fmt="py:percent")

    # Update from .py file
    propagate_changes(str(py_path))

    # Check that .ipynb was updated with new source but kept outputs
    updated_nb = read(str(nb_path))
    assert updated_nb.cells[0].source == "print('modified')"
    assert len(updated_nb.cells[0].outputs) == 1


def test_propagate_changes_skips_newer_files(temp_notebook, tmp_path):
    """Test that newer paired files are not overwritten"""
    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    write(temp_notebook, str(nb_path), fmt="ipynb")
    write(temp_notebook, str(py_path), fmt="py:percent")

    # Make the .py file newer by modifying its timestamp
    time.sleep(0.1)
    py_path.touch()

    propagate_changes(str(nb_path))

    # Should create a backup file instead of overwriting
    py_files = list(tmp_path.glob("*.py"))
    assert len(py_files) == 2, py_files


def test_propagate_changes_multiple_formats(tmp_path):
    """Test updating with multiple paired formats"""
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("x = 1")]
    nb.metadata.jupytext = {"formats": "ipynb,py:percent,md"}

    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"
    md_path = tmp_path / "test.md"

    write(nb, str(nb_path))
    propagate_changes(str(nb_path))

    assert py_path.exists()
    assert md_path.exists()


def test_propagate_changes_with_config_file(tmp_path):
    """Test that propagate_changes works with jupytext config file"""
    # Create a jupytext config file
    config_content = """
formats = "ipynb,py:percent"
"""
    config_path = tmp_path / "jupytext.toml"
    config_path.write_text(config_content)

    # Create a notebook without pairing metadata
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("print('config test')")]

    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    write(nb, str(nb_path))
    propagate_changes(str(nb_path))

    assert py_path.exists()
    py_content = read(str(py_path))
    assert len(py_content.cells) == 1
    assert py_content.cells[0].source == "print('config test')"


def test_propagate_changes_config_with_subdirectory(tmp_path):
    """Test that propagate_changes works with config in parent directory"""
    # Create a jupytext config file in parent directory
    config_content = """
formats = "ipynb,py:percent"
"""
    config_path = tmp_path / "jupytext.toml"
    config_path.write_text(config_content)

    # Create a subdirectory with notebook
    subdir = tmp_path / "notebooks"
    subdir.mkdir()

    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("print('subdir test')")]

    nb_path = subdir / "test.ipynb"
    py_path = subdir / "test.py"

    write(nb, str(nb_path))
    propagate_changes(str(nb_path))

    assert py_path.exists()
    py_content = read(str(py_path))
    assert py_content.cells[0].source == "print('subdir test')"


def test_propagate_changes_config_file_missing_no_metadata(tmp_path):
    """Test that function exits early when no config file and no metadata"""
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("print('no config')")]

    nb_path = tmp_path / "test.ipynb"
    write(nb, str(nb_path))

    # Should not raise an error, just exit early
    propagate_changes(str(nb_path))

    # Only the original notebook should exist
    assert list(tmp_path.iterdir()) == [nb_path]


def test_propagate_changes_config_with_format_options(tmp_path):
    """Test that propagate_changes respects format options from config"""
    # Create a jupytext config file with format options
    config_content = """
formats = "ipynb,py:percent"
comment_magics = false
"""
    config_path = tmp_path / "jupytext.toml"
    config_path.write_text(config_content)

    # Create a notebook with magic commands
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("%matplotlib inline\nprint('magic test')")]

    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    write(nb, str(nb_path))
    propagate_changes(str(nb_path))

    assert py_path.exists()
    py_content = py_path.read_text()

    # With comment_magics=false, magic commands should not be commented
    assert "# %matplotlib inline" not in py_content
    assert "%matplotlib inline" in py_content


def test_propagate_changes_ipynb_newer_than_py(temp_notebook, tmp_path):
    """Test that when ipynb is newer than py file, py file gets updated"""
    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    # Create both files initially
    write(temp_notebook, str(nb_path))
    write(temp_notebook, str(py_path), fmt="py:percent")

    # Modify the ipynb file and make it newer
    temp_notebook.cells[0].source = "print('modified in ipynb')"
    time.sleep(0.1)
    write(temp_notebook, str(nb_path))

    # Propagate changes from the newer ipynb file
    propagate_changes(str(nb_path))

    # Check that py file was updated with ipynb content
    py_content = read(str(py_path))
    assert py_content.cells[0].source == "print('modified in ipynb')"

    # Verify that py file is now at least as recent as ipynb
    nb_mtime = nb_path.stat().st_mtime
    py_mtime = py_path.stat().st_mtime
    assert py_mtime >= nb_mtime


def test_propagate_changes_py_newer_than_ipynb_preserves_outputs(
    temp_notebook, tmp_path
):
    """Test that when py is newer than ipynb, ipynb gets updated but preserves outputs"""
    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    # Add outputs to notebook and create both files
    temp_notebook.cells[0].outputs = [
        nbformat.v4.new_output(
            "execute_result", data={"text/plain": "'original output'"}
        )
    ]
    write(temp_notebook, str(nb_path))
    write(temp_notebook, str(py_path), fmt="py:percent")

    # Modify the py file and make it newer
    py_nb = read(str(py_path))
    py_nb.cells[0].source = "print('modified in py')"
    time.sleep(0.1)
    write(py_nb, str(py_path), fmt="py:percent")

    # Propagate changes from the newer py file
    propagate_changes(str(py_path))

    # Check that ipynb was updated with py content but kept outputs
    updated_nb = read(str(nb_path))
    assert updated_nb.cells[0].source == "print('modified in py')"
    assert len(updated_nb.cells[0].outputs) == 1
    assert updated_nb.cells[0].outputs[0].data["text/plain"] == "'original output'"

    # Verify that ipynb is not newer than py
    nb_mtime = nb_path.stat().st_mtime
    py_mtime = py_path.stat().st_mtime
    assert nb_mtime <= py_mtime


def test_propagate_changes_multiple_text_files_different_ages(tmp_path):
    """Test propagation when multiple text files have different modification times"""
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("x = 1")]
    nb.metadata.jupytext = {"formats": "ipynb,py:percent,md"}

    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"
    md_path = tmp_path / "test.md"

    # Create all files initially
    write(nb, str(nb_path))
    write(nb, str(py_path), fmt="py:percent")
    write(nb, str(md_path), fmt="md")

    # Modify py file and make it newest
    py_nb = read(str(py_path))
    py_nb.cells[0].source = "x = 'modified in py'"
    time.sleep(0.1)
    write(py_nb, str(py_path), fmt="py:percent")

    # Propagate changes from the py file
    propagate_changes(str(py_path))

    # All files should now have the updated content
    updated_nb = read(str(nb_path))
    updated_md = read(str(md_path))

    assert updated_nb.cells[0].source == "x = 'modified in py'"
    assert updated_md.cells[0].source == "x = 'modified in py'"

    # All files should be at least as recent as the original py file
    py_mtime = py_path.stat().st_mtime
    nb_mtime = nb_path.stat().st_mtime
    md_mtime = md_path.stat().st_mtime

    assert nb_mtime >= py_mtime
    assert md_mtime >= py_mtime


def test_propagate_changes_prevents_ipynb_being_newer(temp_notebook, tmp_path):
    """Test that after propagation, ipynb is never newer than text files"""
    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    # Create files with ipynb being newer initially
    write(temp_notebook, str(py_path), fmt="py:percent")
    time.sleep(0.1)
    write(temp_notebook, str(nb_path))

    # Record initial timestamps
    initial_nb_mtime = nb_path.stat().st_mtime
    initial_py_mtime = py_path.stat().st_mtime

    assert initial_nb_mtime > initial_py_mtime, "Setup: ipynb should be newer initially"

    # Propagate changes
    propagate_changes(str(nb_path))

    # After propagation, py should be at least as recent as ipynb
    final_nb_mtime = nb_path.stat().st_mtime
    final_py_mtime = py_path.stat().st_mtime

    assert (
        final_py_mtime >= final_nb_mtime
    ), "py file should be at least as recent as ipynb after propagation"


def test_propagate_changes_concurrent_modifications_creates_backup(
    temp_notebook, tmp_path
):
    """Test that when files are modified concurrently, backup files are created"""
    nb_path = tmp_path / "test.ipynb"
    py_path = tmp_path / "test.py"

    # Create both files
    write(temp_notebook, str(nb_path))
    write(temp_notebook, str(py_path), fmt="py:percent")

    # Modify both files to create a conflict scenario
    temp_notebook.cells[0].source = "print('modified in ipynb')"
    write(temp_notebook, str(nb_path))

    # Make py file newer with different content
    py_nb = read(str(py_path))
    py_nb.cells[0].source = "print('modified in py')"
    time.sleep(0.1)
    write(py_nb, str(py_path), fmt="py:percent")

    # Propagate changes - this should detect the conflict
    propagate_changes(str(nb_path))

    # Should create backup files for conflicting content
    all_files = list(tmp_path.iterdir())
    backup_files = [
        f for f in all_files if "_" in f.name and f.suffix in [".ipynb", ".py"]
    ]

    assert (
        len(backup_files) > 0
    ), f"Expected backup files, but found: {[f.name for f in all_files]}"

    # Original files should exist
    assert nb_path.exists()
    assert py_path.exists()
