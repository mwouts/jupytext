from jupytext.stringparser import StringParser


def test_long_string(text="""'''This is a multiline
comment with "quotes", 'single quotes'
# and comments
and line breaks


and it ends here'''


1 + 1
"""):
    quoted = []
    sp = StringParser('python')
    for i, line in enumerate(text.splitlines()):
        if sp.is_quoted():
            quoted.append(i)
        sp.read_line(line)

    assert quoted == [1, 2, 3, 4, 5, 6]


def test_single_chars(text="""'This is a single line comment'''
'and another one'
# and comments
"and line breaks"


"and it ends here'''"


1 + 1
"""):
    quoted = []
    sp = StringParser('python')
    for i, line in enumerate(text.splitlines()):
        assert not sp.is_quoted()
