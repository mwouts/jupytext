"""
This module contains round-trip conversion between
myst formatted text documents and notebooks.
"""
import json
import logging
from typing import List, Union

import nbformat as nbf
import yaml

MYST_FORMAT_NAME = "mystnb"
CODE_DIRECTIVE = "nb-code"
RAW_DIRECTIVE = "nb-raw"

LOGGER = logging.getLogger(__name__)


def is_myst_available():
    try:
        import myst_parser  # noqa
    except ImportError:
        return False
    return True


def myst_version():
    from myst_parser import __version__

    return __version__


def myst_extensions():
    return [".mystnb"]


def from_nbnode(value):
    """Recursively convert NotebookNode to dict."""
    if isinstance(value, nbf.NotebookNode):
        return {k: from_nbnode(v) for k, v in value.items()}
    return value


class MockDirective:
    option_spec = {"options": True}
    required_arguments = 0
    optional_arguments = 1
    has_content = True


def _fmt_md(text):
    text = text.rstrip()
    while text and text.startswith("\n"):
        text = text[1:]
    return text


def myst_to_notebook(
    text: Union[str, List[str]],
    code_directive: str = CODE_DIRECTIVE,
    raw_directive: str = RAW_DIRECTIVE,
    logger=None,
) -> nbf.NotebookNode:
    """Convert text written in the myst format to a notebook.

    :param text: the file text
    :directive: the name of the directive to search for.

    NOTE: we assume here that all of these directives are at the top-level,
    i.e. not nested in other directives.
    """
    from mistletoe.base_elements import SourceLines
    from mistletoe.parse_context import (
        ParseContext,
        get_parse_context,
        set_parse_context,
    )
    from mistletoe.block_tokens import Document, CodeFence

    from myst_parser.block_tokens import BlockBreak
    from myst_parser.parse_directives import parse_directive_text
    from myst_parser.docutils_renderer import DocutilsRenderer

    code_directive = "{{{0}}}".format(code_directive)
    raw_directive = "{{{0}}}".format(raw_directive)
    logger = logger or LOGGER

    original_context = get_parse_context()
    parse_context = ParseContext(
        find_blocks=DocutilsRenderer.default_block_tokens,
        find_spans=DocutilsRenderer.default_span_tokens,
    )

    if isinstance(text, SourceLines):
        lines = text
    else:
        lines = SourceLines(text, standardize_ends=True)

    try:
        set_parse_context(parse_context)
        doc = Document.read(lines, front_matter=True)

        metadata_nb = doc.front_matter.get_data() if doc.front_matter else {}
        nbformat = metadata_nb.pop("nbformat", None)
        nbformat_minor = metadata_nb.pop("nbformat_minor", None)
        kwargs = {"metadata": nbf.from_dict(metadata_nb)}
        if nbformat is not None:
            kwargs["nbformat"] = nbformat
        if nbformat_minor is not None:
            kwargs["nbformat_minor"] = nbformat_minor

        notebook = nbf.v4.new_notebook(**kwargs)

        current_line = 0 if not doc.front_matter else doc.front_matter.position.line_end
        md_metadata = {}

        for item in doc.walk(["CodeFence", "BlockBreak"]):
            if isinstance(item.node, BlockBreak):
                token = item.node  # type: BlockBreak
                source = _fmt_md(
                    "".join(lines.lines[current_line : token.position.line_start - 1])
                )
                if source:
                    notebook.cells.append(
                        nbf.v4.new_markdown_cell(
                            source=source, metadata=nbf.from_dict(md_metadata),
                        )
                    )
                if token.content:
                    try:
                        md_metadata = json.loads(token.content.strip())
                    except Exception:
                        logger.warning(
                            "markdown cell metadata could not be read: {}".format(
                                token.position
                            )
                        )
                        md_metadata = {}
                    if not isinstance(md_metadata, dict):
                        logger.warning(
                            "markdown cell metadata is not a dict: {}".format(
                                token.position
                            )
                        )
                        md_metadata = {}
                else:
                    md_metadata = {}
                current_line = token.position.line_start
            if isinstance(item.node, CodeFence) and item.node.language in [
                code_directive,
                raw_directive,
            ]:
                token = item.node  # type: CodeFence
                # Note: we ignore anything after the directive on the first line
                # this is reserved for the optional lexer name
                # TODO: could log warning about if token.arguments != lexer name

                _, options, body_lines = parse_directive_text(
                    directive_class=MockDirective,
                    argument_str="",
                    content=token.children[0].content,
                    validate_options=False,
                )

                md_source = _fmt_md(
                    "".join(lines.lines[current_line : token.position.line_start - 1])
                )
                if md_source:
                    notebook.cells.append(
                        nbf.v4.new_markdown_cell(
                            source=md_source, metadata=nbf.from_dict(md_metadata),
                        )
                    )
                current_line = token.position.line_end
                md_metadata = {}

                if item.node.language == code_directive:
                    notebook.cells.append(
                        nbf.v4.new_code_cell(
                            source="\n".join(body_lines),
                            metadata=nbf.from_dict(options),
                        )
                    )
                if item.node.language == raw_directive:
                    notebook.cells.append(
                        nbf.v4.new_raw_cell(
                            source="\n".join(body_lines),
                            metadata=nbf.from_dict(options),
                        )
                    )

        # add the final markdown cell (if present)
        if lines.lines[current_line:]:
            notebook.cells.append(
                nbf.v4.new_markdown_cell(
                    source=_fmt_md("".join(lines.lines[current_line:])),
                    metadata=nbf.from_dict(md_metadata),
                )
            )

    finally:
        set_parse_context(original_context)

    return notebook


def notebook_to_myst(
    nb: nbf.NotebookNode,
    code_directive: str = CODE_DIRECTIVE,
    raw_directive: str = RAW_DIRECTIVE,
):
    string = ""

    nb_metadata = from_nbnode(nb.metadata)
    nb_metadata["nbformat"] = nb.nbformat
    nb_metadata["nbformat_minor"] = nb.nbformat_minor

    # we add the pygments lexer as a directive argument, for use by syntax highlighters
    pygments_lexer = nb_metadata.get("language_info", {}).get("pygments_lexer", None)

    string += "---\n"
    string += yaml.safe_dump(nb_metadata)
    string += "---\n"

    last_cell_md = False
    for i, cell in enumerate(nb.cells):

        if cell.cell_type == "markdown":
            metadata = from_nbnode(cell.metadata)
            if metadata or last_cell_md:
                if metadata:
                    string += "\n+++ {}\n".format(json.dumps(metadata))
                else:
                    string += "\n+++\n"
            string += "\n" + cell.source
            if not cell.source.endswith("\n"):
                string += "\n"
            last_cell_md = True

        elif cell.cell_type in ["code", "raw"]:
            string += "\n```{{{}}}".format(
                code_directive if cell.cell_type == "code" else raw_directive
            )
            if pygments_lexer and cell.cell_type == "code":
                string += " {}".format(pygments_lexer)
            string += "\n"
            metadata = from_nbnode(cell.metadata)
            if metadata:
                string += "---\n"
                string += yaml.safe_dump(metadata)
                string += "---\n"
            elif cell.source.startswith("---") or cell.source.startswith(":"):
                string += "\n"
            string += cell.source
            if not cell.source.endswith("\n"):
                string += "\n"
            string += "```\n"
            last_cell_md = False

        else:
            raise NotImplementedError("cell {}, type: {}".format(i, cell.cell_type))

    return string.rstrip() + "\n"
