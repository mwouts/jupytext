from jupytext.stringparser import StringParser


def test_long_string(
    text="""'''This is a multiline
comment with "quotes", 'single quotes'
# and comments
and line breaks


and it ends here'''


1 + 1
""",
):
    quoted = []
    sp = StringParser("python")
    for i, line in enumerate(text.splitlines()):
        if sp.is_quoted():
            quoted.append(i)
        sp.read_line(line)

    assert quoted == [1, 2, 3, 4, 5, 6]


def test_single_chars(
    text="""'This is a single line comment'''
'and another one'
# and comments
"and line breaks"


"and it ends here'''"


1 + 1
""",
):
    sp = StringParser("python")
    for line in text.splitlines():
        assert not sp.is_quoted()
        sp.read_line(line)


def test_long_string_with_four_quotes(
    text="""''''This is a multiline
comment that starts with four quotes
'''

1 + 1
""",
):
    quoted = []
    sp = StringParser("python")
    for i, line in enumerate(text.splitlines()):
        if sp.is_quoted():
            quoted.append(i)
        sp.read_line(line)

    assert quoted == [1, 2]


def test_long_string_ends_with_four_quotes(
    text="""'''This is a multiline
comment that ends with four quotes
''''

1 + 1
""",
):
    quoted = []
    sp = StringParser("python")
    for i, line in enumerate(text.splitlines()):
        if sp.is_quoted():
            quoted.append(i)
        sp.read_line(line)

    assert quoted == [1, 2]
