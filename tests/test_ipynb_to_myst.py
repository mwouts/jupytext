try:
    import unittest.mock as mock
except ImportError:
    import mock
from textwrap import dedent
import pytest

from jupytext.formats import get_format_implementation, JupytextFormatError
from jupytext.myst import (
    myst_to_notebook,
    CODE_DIRECTIVE,
    MystMetadataParsingError,
    matches_mystnb,
    myst_extensions,
)
from .utils import requires_myst


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
