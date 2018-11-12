import pytest
from nbformat.v4.nbbase import new_code_cell, new_notebook
from jupytext.magics import comment_magic, uncomment_magic, unesc
from jupytext.formats import parse_one_format
from jupytext.compare import compare_notebooks
import jupytext


def test_unesc():
    assert unesc('# comment', 'python') == 'comment'
    assert unesc('#comment', 'python') == 'comment'
    assert unesc('comment', 'python') == 'comment'


@pytest.mark.parametrize('line', ['%matplotlib inline', '#%matplotlib inline',
                                  '##%matplotlib inline', '%%HTML', '%autoreload', '%store'])
def test_escape(line):
    assert comment_magic([line]) == ['# ' + line]
    assert uncomment_magic(comment_magic([line])) == [line]


@pytest.mark.parametrize('line', ['@pytest.fixture'])
def test_escape_magic_only(line):
    assert comment_magic([line]) == [line]


@pytest.mark.parametrize('line', ['%matplotlib inline #noescape'])
def test_force_noescape(line):
    assert comment_magic([line]) == [line]


@pytest.mark.parametrize('line', ['%matplotlib inline #noescape'])
def test_force_noescape_with_gbl_esc_flag(line):
    assert comment_magic([line], global_escape_flag=True) == [line]


@pytest.mark.parametrize('ext_and_format_name,commented',
                         zip(['md', 'Rmd', 'py:light', 'py:percent', 'py:sphinx', 'R', 'ss:light', 'ss:percent'],
                             [False, True, True, False, True, True, True, False]))
def test_magics_commented_default(ext_and_format_name, commented):
    ext, format_name = parse_one_format(ext_and_format_name)
    nb = new_notebook(cells=[new_code_cell('%pylab inline')])

    text = jupytext.writes(nb, ext, format_name)
    assert ('%pylab inline' in text.splitlines()) != commented
    nb2 = jupytext.reads(text, ext, format_name)

    if format_name == 'sphinx':
        nb2.cells = nb2.cells[1:]

    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('ext_and_format_name',
                         ['md', 'Rmd', 'py:light', 'py:percent', 'py:sphinx', 'R', 'ss:light', 'ss:percent'])
def test_magics_are_commented(ext_and_format_name):
    ext, format_name = parse_one_format(ext_and_format_name)
    nb = new_notebook(cells=[new_code_cell('%pylab inline')],
                      metadata={'jupytext': {'comment_magics': True,
                                             'main_language': 'R' if ext in ['.r', '.R']
                                             else 'scheme' if ext == '.ss' else 'python'}})

    text = jupytext.writes(nb, ext, format_name)
    assert '%pylab inline' not in text.splitlines()
    nb2 = jupytext.reads(text, ext, format_name)

    if format_name == 'sphinx':
        nb2.cells = nb2.cells[1:]

    compare_notebooks(nb, nb2)


@pytest.mark.parametrize('ext_and_format_name',
                         ['md', 'Rmd', 'py:light', 'py:percent', 'py:sphinx', 'R', 'ss:light', 'ss:percent'])
def test_magics_are_not_commented(ext_and_format_name):
    ext, format_name = parse_one_format(ext_and_format_name)
    nb = new_notebook(cells=[new_code_cell('%pylab inline')],
                      metadata={'jupytext': {'comment_magics': False,
                                             'main_language': 'R' if ext in ['.r', '.R']
                                             else 'scheme' if ext == '.ss' else 'python'}})

    text = jupytext.writes(nb, ext, format_name)
    assert '%pylab inline' in text.splitlines()
    nb2 = jupytext.reads(text, ext, format_name)

    if format_name == 'sphinx':
        nb2.cells = nb2.cells[1:]
    compare_notebooks(nb, nb2)


def test_force_comment_using_contents_manager(tmpdir):
    tmp_py = 'notebook.py'

    cm = jupytext.TextFileContentsManager()
    cm.preferred_jupytext_formats_save = 'py:percent'
    cm.root_dir = str(tmpdir)

    nb = new_notebook(cells=[new_code_cell('%pylab inline')])

    cm.save(model=dict(type='notebook', content=nb), path=tmp_py)
    with open(str(tmpdir.join(tmp_py))) as stream:
        assert '%pylab inline' in stream.read().splitlines()

    cm.comment_magics = True
    cm.save(model=dict(type='notebook', content=nb), path=tmp_py)
    with open(str(tmpdir.join(tmp_py))) as stream:
        assert '# %pylab inline' in stream.read().splitlines()
