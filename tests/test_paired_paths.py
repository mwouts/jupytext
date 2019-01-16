import pytest
from testfixtures import compare
from jupytext.paired_paths import InconsistentPath, paired_paths
from jupytext.formats import long_form_multiple_formats, short_form_multiple_formats


def test_simple_pair():
    formats = long_form_multiple_formats('ipynb,py')
    expected_paths = ['notebook.ipynb', 'notebook.py']
    compare(zip(expected_paths, formats), paired_paths('notebook.ipynb', formats))
    compare(zip(expected_paths, formats), paired_paths('notebook.py', formats))


def test_many_and_suffix():
    formats = long_form_multiple_formats('ipynb,.pct.py,_lgt.py')
    expected_paths = ['notebook.ipynb', 'notebook.pct.py', 'notebook_lgt.py']
    for path in expected_paths:
        compare(zip(expected_paths, formats), paired_paths(path, formats))

    with pytest.raises(InconsistentPath):
        paired_paths('wrong_suffix.py', formats)


def test_prefix_and_suffix():
    short_formats = 'notebook_folder/notebook_prefix_/_notebook_suffix.ipynb,' \
                    'script_folder//_in_percent_format.py:percent,' \
                    'script_folder//_in_light_format.py'

    formats = long_form_multiple_formats(short_formats)
    assert short_form_multiple_formats(formats) == short_formats

    expected_paths = ['parent/notebook_folder/notebook_prefix_NOTEBOOK_NAME_notebook_suffix.ipynb',
                      'parent/script_folder/NOTEBOOK_NAME_in_percent_format.py',
                      'parent/script_folder/NOTEBOOK_NAME_in_light_format.py']
    for path in expected_paths:
        compare(zip(expected_paths, formats), paired_paths(path, formats))

    # without the parent folder
    expected_paths = [path[7:] for path in expected_paths]
    for path in expected_paths:
        compare(zip(expected_paths, formats), paired_paths(path, formats))

    # Not the expected parent folder
    with pytest.raises(InconsistentPath):
        paired_paths('script_folder_incorrect/NOTEBOOK_NAME_in_percent_format.py', formats)

    # Not the expected suffix
    with pytest.raises(InconsistentPath):
        paired_paths('parent/script_folder/NOTEBOOK_NAME_in_LIGHT_format.py', formats)

    # Not the expected extension
    with pytest.raises(InconsistentPath):
        paired_paths('notebook_folder/notebook_prefix_NOTEBOOK_NAME_notebook_suffix.py', formats)


def test_duplicated_paths():
    formats = long_form_multiple_formats('ipynb,py:percent,py:light')
    with pytest.raises(InconsistentPath):
        paired_paths('notebook.ipynb', formats)
