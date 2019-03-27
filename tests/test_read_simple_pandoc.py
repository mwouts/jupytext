from testfixtures import compare
import jupytext


def test_pandoc_implicit(markdown='''# Lorem ipsum

**Lorem ipsum** dolor sit amet, consectetur adipiscing elit. Nunc luctus
bibendum felis dictum sodales.

``` code
print("hello")
```
'''):
    nb = jupytext.reads(markdown, 'md:pandoc')
    markdown2 = jupytext.writes(nb, 'md')

    nb2 = jupytext.reads(markdown2, 'md')
    compare(nb, nb2)

    markdown3 = jupytext.writes(nb2, 'md')
    compare(markdown2, markdown3)


def test_pandoc_explicit(markdown='''::: {.cell .markdown}
Lorem
=====

**Lorem ipsum** dolor sit amet, consectetur adipiscing elit. Nunc luctus
bibendum felis dictum sodales.
:::
'''):
    nb = jupytext.reads(markdown, 'md')
    markdown2 = jupytext.writes(nb, 'md').replace('\r\n', '\n')
    compare(markdown, markdown2)
