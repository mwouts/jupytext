import pytest
from nbrmd.magics import escape_magic, unescape_magic


@pytest.mark.parametrize('line', ['%matplotlib inline', '#%matplotlib inline',
                                  '##%matplotlib inline', '%%HTML',
                                  '%autoreload', '%store'])
def test_escape(line):
    assert escape_magic([line]) == ['# ' + line]
    assert unescape_magic(escape_magic([line])) == [line]


@pytest.mark.parametrize('line', ['%pytest.fixture'])
def test_escape_magic_only(line):
    assert escape_magic([line]) == [line]


@pytest.mark.parametrize('line', ['%matplotlib inline #noescape'])
def test_force_noescape(line):
    assert escape_magic([line]) == [line]


@pytest.mark.parametrize('line', ['%pytest.fixture #escape'])
def test_force_escape(line):
    assert escape_magic([line]) == ['# ' + line]
