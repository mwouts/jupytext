import pytest
import jupytext
from jupytext.compare import compare


@pytest.mark.parametrize('lang', ['cs', 'c#', 'csharp'])
def test_simple_cs(lang):
    source = """// A Hello World! program in C#.
Console.WriteLine("Hello World!");
"""
    md = """```{lang}
{source}
```
""".format(lang=lang, source=source)
    nb = jupytext.reads(md, 'md')
    assert nb.metadata['jupytext']['main_language'] == 'csharp'
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == 'code'

    cs = jupytext.writes(nb, 'cs')
    assert source in cs
    if lang != 'csharp':
        assert cs.startswith('// + language="{lang}"'.format(lang=lang))

    md2 = jupytext.writes(nb, 'md')
    compare(md2, md)


@pytest.mark.parametrize('lang', ['cs', 'c#', 'csharp'])
def test_csharp_magics(lang):
    md = """```{lang}
#!html
<b>Hello!</b>
```
""".format(lang=lang)
    nb = jupytext.reads(md, 'md')
    assert nb.metadata['jupytext']['main_language'] == 'csharp'
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == 'code'

    cs = jupytext.writes(nb, 'cs')
    assert all(line.startswith('//') for line in cs.splitlines()), cs

    md2 = jupytext.writes(nb, 'md')
    md_expected = """```html
<b>Hello!</b>
```
"""
    compare(md2, md_expected)
