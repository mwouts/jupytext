import pytest
from jupytext import read, reads, writes
from jupytext.formats import JupytextFormatError, auto_ext_from_metadata
from .utils import list_notebooks


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R') + list_notebooks('ipynb_py'))
def test_auto_in_fmt(nb_file):
    nb = read(nb_file)
    auto_ext = auto_ext_from_metadata(nb.metadata)
    fmt = auto_ext[1:] + ':percent'
    text = writes(nb, 'auto:percent')

    assert 'auto' not in text

    nb2 = reads(text, fmt)
    assert nb2.metadata['jupytext']['text_representation']['extension']
    assert nb2.metadata['jupytext']['text_representation']['format_name'] == 'percent'

    del nb.metadata['language_info']
    with pytest.raises(JupytextFormatError):
        writes(nb, 'auto:percent')


@pytest.mark.parametrize('nb_file', list_notebooks('ipynb_R') + list_notebooks('ipynb_py'))
def test_auto_in_formats(nb_file):
    nb = read(nb_file)
    nb.metadata['jupytext'] = {'formats': 'ipynb,auto:percent'}
    fmt = auto_ext_from_metadata(nb.metadata)[1:] + ':percent'
    expected_formats = 'ipynb,' + fmt

    text = writes(nb, 'ipynb')
    assert 'auto' not in text
    nb2 = reads(text, 'ipynb')
    assert nb2.metadata['jupytext']['formats'] == expected_formats

    text = writes(nb, 'auto:percent')
    assert 'auto' not in text
    nb2 = reads(text, fmt)
    assert nb2.metadata['jupytext']['formats'] == expected_formats

    del nb.metadata['language_info']
    with pytest.raises(JupytextFormatError):
        writes(nb, 'ipynb')
    with pytest.raises(JupytextFormatError):
        writes(nb, 'auto:percent')
