import pytest
from jupytext.compare import compare
from jupytext.contentsmanager import TextFileContentsManager
from jupytext.paired_paths import InconsistentPath, paired_paths, base_path
from jupytext.formats import long_form_one_format, long_form_multiple_formats, short_form_multiple_formats


def test_simple_pair():
    formats = long_form_multiple_formats('ipynb,py')
    expected_paths = ['notebook.ipynb', 'notebook.py']
    compare(list(zip(expected_paths, formats)), paired_paths('notebook.ipynb', 'ipynb', formats))
    compare(list(zip(expected_paths, formats)), paired_paths('notebook.py', 'py', formats))


def test_base_path():
    fmt = long_form_one_format('dir/prefix_/ipynb')
    assert base_path('dir/prefix_NAME.ipynb', fmt) == 'NAME'
    with pytest.raises(InconsistentPath):
        base_path('dir/incorrect_prefix_NAME.ipynb', fmt)


def test_many_and_suffix():
    formats = long_form_multiple_formats('ipynb,.pct.py,_lgt.py')
    expected_paths = ['notebook.ipynb', 'notebook.pct.py', 'notebook_lgt.py']
    for fmt, path in zip(formats, expected_paths):
        compare(list(zip(expected_paths, formats)), paired_paths(path, fmt, formats))

    with pytest.raises(InconsistentPath):
        paired_paths('wrong_suffix.py', 'py', formats)


def test_prefix_and_suffix():
    short_formats = 'notebook_folder/notebook_prefix_/_notebook_suffix.ipynb,' \
                    'script_folder//_in_percent_format.py:percent,' \
                    'script_folder//_in_light_format.py'

    formats = long_form_multiple_formats(short_formats)
    assert short_form_multiple_formats(formats) == short_formats

    expected_paths = ['parent/notebook_folder/notebook_prefix_NOTEBOOK_NAME_notebook_suffix.ipynb',
                      'parent/script_folder/NOTEBOOK_NAME_in_percent_format.py',
                      'parent/script_folder/NOTEBOOK_NAME_in_light_format.py']
    for fmt, path in zip(formats, expected_paths):
        compare(list(zip(expected_paths, formats)), paired_paths(path, fmt, formats))

    # without the parent folder
    expected_paths = [path[7:] for path in expected_paths]
    for fmt, path in zip(formats, expected_paths):
        compare(list(zip(expected_paths, formats)), paired_paths(path, fmt, formats))

    # Not the expected parent folder
    with pytest.raises(InconsistentPath):
        paired_paths('script_folder_incorrect/NOTEBOOK_NAME_in_percent_format.py', formats[1], formats)

    # Not the expected suffix
    with pytest.raises(InconsistentPath):
        paired_paths('parent/script_folder/NOTEBOOK_NAME_in_LIGHT_format.py', formats[2], formats)

    # Not the expected extension
    with pytest.raises(InconsistentPath):
        paired_paths('notebook_folder/notebook_prefix_NOTEBOOK_NAME_notebook_suffix.py', formats[0], formats)


def test_prefix_on_root_174():
    short_formats = 'ipynb,python//py:percent'

    formats = long_form_multiple_formats(short_formats)
    assert short_form_multiple_formats(formats) == short_formats

    expected_paths = ['/Untitled.ipynb', '/python/Untitled.py']
    for fmt, path in zip(formats, expected_paths):
        compare(list(zip(expected_paths, formats)), paired_paths(path, fmt, formats))


def test_duplicated_paths():
    formats = long_form_multiple_formats('ipynb,py:percent,py:light')
    with pytest.raises(InconsistentPath):
        paired_paths('notebook.ipynb', 'ipynb', formats)


def test_cm_paired_paths():
    cm = TextFileContentsManager()
    cm.paired_notebooks = dict()

    three = 'ipynb,py,md'
    cm.update_paired_notebooks('nb.ipynb', 'ipynb', three)
    assert cm.paired_notebooks == {'nb.' + fmt: (fmt, three) for fmt in three.split(',')}

    two = 'ipynb,Rmd'
    cm.update_paired_notebooks('nb.ipynb', 'ipynb', two)
    assert cm.paired_notebooks == {'nb.' + fmt: (fmt, two) for fmt in two.split(',')}

    one = 'ipynb'
    cm.update_paired_notebooks('nb.ipynb', 'ipynb', one)
    assert cm.paired_notebooks == {}
