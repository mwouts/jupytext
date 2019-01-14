import pytest
from testfixtures import compare
from jupytext.paired_paths import InconsistentPath, paired_paths
from jupytext.formats import long_form_multiple_formats


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
        compare(zip(expected_paths, formats), paired_paths('wrong_suffix.py', formats))
