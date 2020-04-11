"""Parse header of text notebooks
"""

import re
import yaml
from yaml.representer import SafeRepresenter
import nbformat
from nbformat.v4.nbbase import new_raw_cell
from .version import __version__
from .languages import _SCRIPT_EXTENSIONS, comment_lines
from .metadata_filter import filter_metadata, _DEFAULT_NOTEBOOK_METADATA
from .pep8 import pep8_lines_between_cells

SafeRepresenter.add_representer(nbformat.NotebookNode, SafeRepresenter.represent_dict)

_HEADER_RE = re.compile(r"^---\s*$")
_BLANK_RE = re.compile(r"^\s*$")
_JUPYTER_RE = re.compile(r"^jupyter\s*:\s*$")
_LEFTSPACE_RE = re.compile(r"^\s")
_UTF8_HEADER = " -*- coding: utf-8 -*-"

# Change this to False in tests
INSERT_AND_CHECK_VERSION_NUMBER = True


def insert_or_test_version_number():
    """Should the format name and version number be inserted in text
    representations (not in tests!)"""
    return INSERT_AND_CHECK_VERSION_NUMBER


def uncomment_line(line, prefix):
    """Remove prefix (and space) from line"""
    if not prefix:
        return line
    if line.startswith(prefix + " "):
        return line[len(prefix) + 1 :]
    if line.startswith(prefix):
        return line[len(prefix) :]
    return line


def encoding_and_executable(notebook, metadata, ext):
    """Return encoding and executable lines for a notebook, if applicable"""
    lines = []
    comment = _SCRIPT_EXTENSIONS.get(ext, {}).get("comment")
    jupytext_metadata = metadata.get("jupytext", {})

    if comment is not None and "executable" in jupytext_metadata:
        lines.append("#!" + jupytext_metadata.pop("executable"))

    if "encoding" in jupytext_metadata:
        lines.append(jupytext_metadata.pop("encoding"))
    elif comment is not None:
        for cell in notebook.cells:
            try:
                cell.source.encode("ascii")
            except (UnicodeEncodeError, UnicodeDecodeError):
                lines.append(comment + _UTF8_HEADER)
                break

    return lines


def insert_jupytext_info_and_filter_metadata(metadata, ext, text_format):
    """Update the notebook metadata to include Jupytext information, and filter
    the notebook metadata according to the default or user filter"""
    if insert_or_test_version_number():
        metadata.setdefault("jupytext", {})["text_representation"] = {
            "extension": ext,
            "format_name": text_format.format_name,
            "format_version": text_format.current_version_number,
            "jupytext_version": __version__,
        }

    if "jupytext" in metadata and not metadata["jupytext"]:
        del metadata["jupytext"]

    notebook_metadata_filter = metadata.get("jupytext", {}).get(
        "notebook_metadata_filter"
    )
    return filter_metadata(
        metadata, notebook_metadata_filter, _DEFAULT_NOTEBOOK_METADATA
    )


def metadata_and_cell_to_header(notebook, metadata, text_format, ext):
    """
    Return the text header corresponding to a notebook, and remove the
    first cell of the notebook if it contained the header
    """

    header = []

    lines_to_next_cell = None
    if notebook.cells:
        cell = notebook.cells[0]
        if cell.cell_type == "raw":
            lines = cell.source.strip("\n\t ").splitlines()
            if (
                len(lines) >= 2
                and _HEADER_RE.match(lines[0])
                and _HEADER_RE.match(lines[-1])
            ):
                header = lines[1:-1]
                lines_to_next_cell = cell.metadata.get("lines_to_next_cell")
                notebook.cells = notebook.cells[1:]

    metadata = insert_jupytext_info_and_filter_metadata(metadata, ext, text_format)

    if metadata:
        header.extend(
            yaml.safe_dump({"jupyter": metadata}, default_flow_style=False).splitlines()
        )

    if header:
        header = ["---"] + header + ["---"]

    return comment_lines(header, text_format.header_prefix), lines_to_next_cell


def recursive_update(target, update):
    """ Update recursively a (nested) dictionary with the content of another.
    Inspired from https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for key in update:
        value = update[key]
        if value is None:
            del target[key]
        elif isinstance(value, dict):
            target[key] = recursive_update(target.get(key, {}), value)
        else:
            target[key] = value
    return target


def header_to_metadata_and_cell(lines, header_prefix, ext=None):
    """
    Return the metadata, a boolean to indicate if a jupyter section was found,
     the first cell of notebook if some metadata is found outside of the jupyter section, and next loc in text
    """

    header = []
    jupyter = []
    injupyter = False
    ended = False
    metadata = {}
    start = 0
    i = -1

    comment = "#" if header_prefix == "#'" else header_prefix

    encoding_re = re.compile(
        r"^[ \t\f]*{}.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)".format(comment)
    )

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("#!"):
            metadata.setdefault("jupytext", {})["executable"] = line[2:]
            start = i + 1
            continue
        if i == 0 or (i == 1 and not encoding_re.match(lines[0])):
            encoding = encoding_re.match(line)
            if encoding:
                if encoding.group(1) != "utf-8":
                    raise ValueError("Encodings other than utf-8 are not supported")
                metadata.setdefault("jupytext", {})["encoding"] = line
                start = i + 1
                continue

        if not line.startswith(header_prefix):
            break

        line = uncomment_line(line, header_prefix)

        if i == start:
            if _HEADER_RE.match(line):
                continue
            break

        if i > start and _HEADER_RE.match(line):
            ended = True
            break

        if _JUPYTER_RE.match(line):
            injupyter = True
        elif line and not _LEFTSPACE_RE.match(line):
            injupyter = False

        if injupyter:
            jupyter.append(line)
        else:
            header.append(line)

    if ended:
        if jupyter:
            recursive_update(metadata, yaml.safe_load("\n".join(jupyter))["jupyter"])

        lines_to_next_cell = 1
        if len(lines) > i + 1:
            line = uncomment_line(lines[i + 1], header_prefix)
            if not _BLANK_RE.match(line):
                lines_to_next_cell = 0
            else:
                i = i + 1
        else:
            lines_to_next_cell = 0

        if header:
            cell = new_raw_cell(
                source="\n".join(["---"] + header + ["---"]),
                metadata={}
                if lines_to_next_cell
                == pep8_lines_between_cells(["---"], lines[i + 1 :], ext)
                else {"lines_to_next_cell": lines_to_next_cell},
            )
        else:
            cell = None

        return metadata, jupyter, cell, i + 1

    return metadata, False, None, start
