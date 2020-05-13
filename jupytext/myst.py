"""
This module contains round-trip conversion between
myst formatted text documents and notebooks.
"""
import json
import warnings

import nbformat as nbf
import yaml
from .reraise import reraise

try:
    import myst_parser
    from myst_parser.main import default_parser
    from myst_parser.parse_directives import DirectiveParsingError, parse_directive_text
except ImportError as err:
    myst_parser = None
    DirectiveParsingError = Exception
    default_parser = parse_directive_text = reraise(err)

MYST_FORMAT_NAME = "myst"
CODE_DIRECTIVE = "{code-cell}"
RAW_DIRECTIVE = "{raw-cell}"


def is_myst_available():
    """Whether the myst-parser package is available."""
    if myst_parser is None:
        return False
    major, minor = myst_parser.__version__.split(".")[:2]
    if int(major) < 1 and int(minor) < 8:
        warnings.warn("The installed myst-parser version is less than the required 0.8")
        return False
    return True


def myst_version():
    """The major version of myst parser."""
    return ".".join(myst_parser.__version__.split(".")[:2])


def myst_extensions(no_md=False):
    """The allowed extensions for the myst format."""
    if no_md:
        return [".myst", ".mystnb", ".mnb"]
    return [".md", ".myst", ".mystnb", ".mnb"]


def matches_mystnb(
    text,
    ext=None,
    requires_meta=True,
    code_directive=CODE_DIRECTIVE,
    raw_directive=RAW_DIRECTIVE,
):
    """Attempt to distinguish a file as myst, only given its extension and content.

    :param ext: the extension of the file
    :param requires_meta: requires the file to contain top matter metadata
    :param code_directive: the name of the directive to search for containing code cells
    :param raw_directive: the name of the directive to search for containing raw cells
    """
    # is the extension uniquely associated with myst (i.e. not just .md)
    if ext and "." + ("." + ext).rsplit(".", 1)[1] in myst_extensions(no_md=True):
        return True

    # might the text contain metadata front matter
    if requires_meta and not text.startswith("---"):
        return False

    try:
        # parse markdown file up to the block level (i.e. don't worry about inline text)
        parser = default_parser("html", disable_syntax=["inline"])
        tokens = parser.parse(text + "\n")
    except (TypeError, ValueError) as err:
        warnings.warn("myst-parse failed unexpectedly: {}".format(err))
        return False

    # Is the format information available in the jupytext text representation?
    if tokens and tokens[0].type == "front_matter":
        try:
            metadata = yaml.safe_load(tokens[0].content)
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            pass
        else:
            try:
                if (
                    metadata.get("jupytext", {})
                    .get("text_representation", {})
                    .get("format_name", "")
                    == MYST_FORMAT_NAME
                ):
                    return True
            except AttributeError:
                pass

    # is there at least on fenced code block with a code/raw directive language
    for token in tokens:
        if token.type == "fence" and (
            token.info.startswith(code_directive)
            or token.info.startswith(raw_directive)
        ):
            return True

    return False


class CompactDumper(yaml.SafeDumper):
    """This YAML dumper creates a more compact style for lists"""


def represent_list(self, data):
    """Compact lists"""
    flow_style = not any(isinstance(i, dict) for i in data)
    return self.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow_style)


def represent_dict(self, data):
    """Compact dicts"""
    return self.represent_mapping("tag:yaml.org,2002:map", data, flow_style=False)


CompactDumper.add_representer(list, represent_list)
CompactDumper.add_representer(dict, represent_dict)


def dump_yaml_blocks(data, compact=True):
    """Where possible, we try to use a more compact metadata style.

    For blocks with no nested dicts, the block is denoted by starting colons::

        :other: true
        :tags: [hide-output, show-input]

    For blocks with nesting the block is enlosed by ``---``::

        ---
        other:
            more: true
        tags: [hide-output, show-input]
        ---
    """
    string = yaml.dump(data, Dumper=CompactDumper)
    lines = string.splitlines()
    if compact and all(line and line[0].isalpha() for line in lines):
        return "\n".join([":{}".format(line) for line in lines]) + "\n\n"
    return "---\n{}---\n".format(string)


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


class MystMetadataParsingError(Exception):
    """Error when parsing metadata from myst formatted text"""


def strip_blank_lines(text):
    """Remove initial blank lines"""
    text = text.rstrip()
    while text and text.startswith("\n"):
        text = text[1:]
    return text


def read_fenced_cell(token, cell_index, cell_type):
    """Return cell options and body"""
    try:
        _, options, body_lines = parse_directive_text(
            directive_class=MockDirective,
            argument_str="",
            content=token.content,
            validate_options=False,
        )
    except DirectiveParsingError as err:
        raise MystMetadataParsingError(
            "{0} cell {1} at line {2} could not be read: {3}".format(
                cell_type, cell_index, token.map[0] + 1, err
            )
        )
    return options, body_lines


def read_cell_metadata(token, cell_index):
    """Return cell metadata"""
    metadata = {}
    if token.content:
        try:
            metadata = json.loads(token.content.strip())
        except Exception as err:
            raise MystMetadataParsingError(
                "Markdown cell {0} at line {1} could not be read: {2}".format(
                    cell_index, token.map[0] + 1, err
                )
            )
        if not isinstance(metadata, dict):
            raise MystMetadataParsingError(
                "Markdown cell {0} at line {1} is not a dict".format(
                    cell_index, token.map[0] + 1
                )
            )

    return metadata


def myst_to_notebook(
    text,
    code_directive=CODE_DIRECTIVE,
    raw_directive=RAW_DIRECTIVE,
    add_source_map=False,
):
    """Convert text written in the myst format to a notebook.

    :param text: the file text
    :param code_directive: the name of the directive to search for containing code cells
    :param raw_directive: the name of the directive to search for containing raw cells
    :param add_source_map: add a `source_map` key to the notebook metadata,
        which is a list of the starting source line number for each cell.

    :raises MystMetadataParsingError if the metadata block is not valid JSON/YAML

    NOTE: we assume here that all of these directives are at the top-level,
    i.e. not nested in other directives.
    """
    # parse markdown file up to the block level (i.e. don't worry about inline text)
    parser = default_parser("html", disable_syntax=["inline"])
    tokens = parser.parse(text + "\n")
    lines = text.splitlines()
    md_start_line = 0

    # get the document metadata
    metadata_nb = {}
    if tokens[0].type == "front_matter":
        metadata = tokens.pop(0)
        md_start_line = metadata.map[1]
        try:
            metadata_nb = yaml.safe_load(metadata.content)
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
            raise MystMetadataParsingError("Notebook metadata: {}".format(error))

    # create an empty notebook
    nbf_version = nbf.v4
    kwargs = {"metadata": nbf.from_dict(metadata_nb)}
    notebook = nbf_version.new_notebook(**kwargs)
    source_map = []  # this is a list of the starting line number for each cell

    def _flush_markdown(start_line, token, md_metadata):
        """When we find a cell we check if there is preceding text.o"""
        endline = token.map[0] if token else len(lines)
        md_source = strip_blank_lines("\n".join(lines[start_line:endline]))
        meta = nbf.from_dict(md_metadata)
        if md_source:
            source_map.append(start_line)
            notebook.cells.append(
                nbf_version.new_markdown_cell(source=md_source, metadata=meta)
            )

    # iterate through the tokens to identify notebook cells
    nesting_level = 0
    md_metadata = {}

    for token in tokens:

        nesting_level += token.nesting

        if nesting_level != 0:
            # we ignore fenced block that are nested, e.g. as part of lists, etc
            continue

        if token.type == "fence" and token.info.startswith(code_directive):
            _flush_markdown(md_start_line, token, md_metadata)
            options, body_lines = read_fenced_cell(token, len(notebook.cells), "Code")
            meta = nbf.from_dict(options)
            source_map.append(token.map[0] + 1)
            notebook.cells.append(
                nbf_version.new_code_cell(source="\n".join(body_lines), metadata=meta)
            )
            md_metadata = {}
            md_start_line = token.map[1]

        elif token.type == "fence" and token.info.startswith(raw_directive):
            _flush_markdown(md_start_line, token, md_metadata)
            options, body_lines = read_fenced_cell(token, len(notebook.cells), "Raw")
            meta = nbf.from_dict(options)
            source_map.append(token.map[0] + 1)
            notebook.cells.append(
                nbf_version.new_raw_cell(source="\n".join(body_lines), metadata=meta)
            )
            md_metadata = {}
            md_start_line = token.map[1]

        elif token.type == "myst_block_break":
            _flush_markdown(md_start_line, token, md_metadata)
            md_metadata = read_cell_metadata(token, len(notebook.cells))
            md_start_line = token.map[1]

    _flush_markdown(md_start_line, None, md_metadata)

    if add_source_map:
        notebook.metadata["source_map"] = source_map
    return notebook


def notebook_to_myst(
    nb, code_directive=CODE_DIRECTIVE, raw_directive=RAW_DIRECTIVE, default_lexer=None,
):
    """Parse a notebook to a MyST formatted text document.

    :param nb: the notebook to parse
    :param code_directive: the name of the directive to use for code cells
    :param raw_directive: the name of the directive to use for raw cells
    :param default_lexer: a lexer name to use for annotating code cells
        (if ``nb.metadata.language_info.pygments_lexer`` is not available)
    """
    string = ""

    nb_metadata = from_nbnode(nb.metadata)

    # we add the pygments lexer as a directive argument, for use by syntax highlighters
    pygments_lexer = nb_metadata.get("language_info", {}).get("pygments_lexer", None)
    if pygments_lexer is None:
        pygments_lexer = default_lexer

    if nb_metadata:
        string += dump_yaml_blocks(nb_metadata, compact=False)

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
            string += "\n```{}".format(
                code_directive if cell.cell_type == "code" else raw_directive
            )
            if pygments_lexer and cell.cell_type == "code":
                string += " {}".format(pygments_lexer)
            string += "\n"
            metadata = from_nbnode(cell.metadata)
            if metadata:
                string += dump_yaml_blocks(metadata)
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
