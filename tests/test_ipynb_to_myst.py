try:
    import unittest.mock as mock
except ImportError:
    import mock
from textwrap import dedent
import pytest
from nbformat.v4.nbbase import new_notebook
from tornado.web import HTTPError
from jupytext.formats import (
    get_format_implementation,
    JupytextFormatError,
    guess_format,
)
from jupytext.myst import (
    myst_to_notebook,
    CODE_DIRECTIVE,
    MystMetadataParsingError,
    matches_mystnb,
    myst_extensions,
)
from jupytext.cli import jupytext as jupytext_cli
import jupytext
from .utils import requires_myst, requires_no_myst


@requires_myst
def test_bad_notebook_metadata():
    """Test exception raised if notebook metadata cannot be parsed."""
    with pytest.raises(MystMetadataParsingError):
        myst_to_notebook(
            dedent(
                """\
            ---
            {{a
            ---
            """
            )
        )


@requires_myst
def test_bad_code_metadata():
    """Test exception raised if cell metadata cannot be parsed."""
    with pytest.raises(MystMetadataParsingError):
        myst_to_notebook(
            dedent(
                """\
            ```{0}
            ---
            {{a
            ---
            ```
            """
            ).format(CODE_DIRECTIVE)
        )


@requires_myst
def test_bad_markdown_metadata():
    """Test exception raised if markdown metadata cannot be parsed."""
    with pytest.raises(MystMetadataParsingError):
        myst_to_notebook(
            dedent(
                """\
            +++ {{a
            """
            )
        )


@requires_myst
def test_bad_markdown_metadata2():
    """Test exception raised if markdown metadata is not a dict."""
    with pytest.raises(MystMetadataParsingError):
        myst_to_notebook(
            dedent(
                """\
            +++ [1, 2]
            """
            )
        )


@requires_myst
def test_matches_mystnb():
    assert matches_mystnb("") is False
    assert matches_mystnb("```{code-cell}\n```") is False
    assert matches_mystnb("---\njupytext: true\n---") is False
    for ext in myst_extensions(no_md=True):
        assert matches_mystnb("", ext=ext) is True
    text = dedent(
        """\
        ---
        {{a
        ---
        ```{code-cell}
        :b: {{c
        ```
        """
    )
    assert matches_mystnb(text) is True
    text = dedent(
        """\
        ---
        jupytext:
            text_representation:
                format_name: myst
                extension: .md
        ---
        """
    )
    assert matches_mystnb(text) is True
    text = dedent(
        """\
        ---
        a: 1
        ---
        > ```{code-cell}
          ```
        """
    )
    assert matches_mystnb(text) is True
    assert guess_format(text, ".md") == ("myst", {})


def test_not_installed():
    with mock.patch("jupytext.formats.JUPYTEXT_FORMATS", return_value=[]):
        with pytest.raises(JupytextFormatError):
            get_format_implementation(".myst")


@requires_myst
def test_add_source_map():
    notebook = myst_to_notebook(
        dedent(
            """\
            ---
            a: 1
            ---
            abc
            +++
            def
            ```{0}
            ---
            b: 2
            ---
            c = 3
            ```
            xyz
            """
        ).format(CODE_DIRECTIVE),
        add_source_map=True,
    )
    assert notebook.metadata.source_map == [3, 5, 7, 12]


PLEASE_INSTALL_MYST = "The MyST Markdown format requires .*"


@requires_no_myst
def test_meaningfull_error_write_myst_missing(tmpdir):
    nb_file = tmpdir.join("notebook.ipynb")
    jupytext.write(new_notebook(), str(nb_file))

    with pytest.raises(ImportError, match=PLEASE_INSTALL_MYST):
        jupytext_cli([str(nb_file), "--to", "md:myst"])


@requires_no_myst
def test_meaningfull_error_open_myst_missing(tmpdir):
    md_file = tmpdir.join("notebook.md")
    md_file.write(
        """---
jupytext:
  text_representation:
    extension: '.md'
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

1 + 1
"""
    )

    with pytest.raises(ImportError, match=PLEASE_INSTALL_MYST):
        jupytext_cli([str(md_file), "--to", "ipynb"])

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    with pytest.raises(HTTPError, match=PLEASE_INSTALL_MYST):
        cm.get("notebook.md")
