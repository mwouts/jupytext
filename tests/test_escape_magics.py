import pytest
from jupytext.magics import comment_magic, uncomment_magic, unesc


def test_unesc():
    assert unesc('# comment', 'python') == 'comment'
    assert unesc('#comment', 'python') == 'comment'
    assert unesc('comment', 'python') == 'comment'


@pytest.mark.parametrize('line', ['%matplotlib inline', '#%matplotlib inline',
                                  '##%matplotlib inline', '%%HTML',
                                  '%autoreload', '%store'])
def test_escape(line):
    assert comment_magic([line]) == ['# ' + line]
    assert uncomment_magic(comment_magic([line])) == [line]


@pytest.mark.parametrize('line', ['%pytest.fixture'])
def test_escape_magic_only(line):
    assert comment_magic([line]) == [line]


@pytest.mark.parametrize('line', ['%matplotlib inline #noescape'])
def test_force_noescape(line):
    assert comment_magic([line]) == [line]


@pytest.mark.parametrize('line', ['%pytest.fixture #escape'])
def test_force_escape(line):
    assert comment_magic([line]) == ['# ' + line]
