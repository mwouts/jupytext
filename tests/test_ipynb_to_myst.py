from textwrap import dedent
import pytest
from jupytext.myst import (
    myst_to_notebook,
    CODE_DIRECTIVE,
    MystMetadataParsingError,
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
            ```{{{0}}}
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
