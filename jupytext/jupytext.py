"""Read and write Jupyter notebooks as text files"""

import os
import io
import sys
import logging
from copy import copy, deepcopy
from nbformat.v4.rwbase import NotebookReader, NotebookWriter
from nbformat.v4.nbbase import new_notebook, new_code_cell, NotebookNode
import nbformat
from .formats import _VALID_FORMAT_OPTIONS
from .formats import (
    read_format_from_metadata,
    update_jupytext_formats_metadata,
    rearrange_jupytext_metadata,
)
from .formats import (
    format_name_for_ext,
    guess_format,
    divine_format,
    get_format_implementation,
    long_form_one_format,
)
from .header import (
    header_to_metadata_and_cell,
    metadata_and_cell_to_header,
    insert_jupytext_info_and_filter_metadata,
)
from .header import encoding_and_executable, insert_or_test_version_number
from .metadata_filter import update_metadata_filters, filter_metadata
from .cell_metadata import _IGNORE_CELL_METADATA
from .languages import (
    default_language_from_metadata_and_ext,
    set_main_and_cell_language,
)
from .pep8 import pep8_lines_between_cells
from .pandoc import md_to_notebook, notebook_to_md
from .myst import myst_extensions, myst_to_notebook, notebook_to_myst, MYST_FORMAT_NAME


class TextNotebookConverter(NotebookReader, NotebookWriter):
    """A class that can read or write a Jupyter notebook as text"""

    def __init__(self, fmt):
        self.fmt = copy(long_form_one_format(fmt))
        self.ext = self.fmt["extension"]
        self.implementation = get_format_implementation(
            self.ext, self.fmt.get("format_name")
        )

    def update_fmt_with_notebook_options(self, metadata):
        """Update format options with the values in the notebook metadata, and record those
        options in the notebook metadata"""
        # format options in notebook have precedence over that in fmt
        for opt in _VALID_FORMAT_OPTIONS:
            if opt in metadata.get("jupytext", {}):
                self.fmt.setdefault(opt, metadata["jupytext"][opt])
            if opt in self.fmt:
                metadata.setdefault("jupytext", {}).setdefault(opt, self.fmt[opt])

        # Is this format the same as that documented in the YAML header? If so, we want to know the format version
        file_fmt = metadata.get("jupytext", {}).get("text_representation", {})
        if self.fmt.get("extension") == file_fmt.get("extension") and self.fmt.get(
            "format_name"
        ) == file_fmt.get("format_name"):
            self.fmt.update(file_fmt)

        # rST to md conversion should happen only once
        if metadata.get("jupytext", {}).get("rst2md") is True:
            metadata["jupytext"]["rst2md"] = False

    def reads(self, s, **_):
        """Read a notebook represented as text"""
        if self.fmt.get("format_name") == "pandoc":
            return md_to_notebook(s)

        if self.fmt.get("format_name") == MYST_FORMAT_NAME:
            return myst_to_notebook(s)

        lines = s.splitlines()

        cells = []
        metadata, jupyter_md, header_cell, pos = header_to_metadata_and_cell(
            lines,
            self.implementation.header_prefix,
            self.implementation.extension,
            self.fmt.get("root_level_metadata_as_raw_cell", True),
        )
        default_language = default_language_from_metadata_and_ext(
            metadata, self.implementation.extension
        )
        self.update_fmt_with_notebook_options(metadata)

        if header_cell:
            cells.append(header_cell)

        lines = lines[pos:]

        if (
            self.implementation.format_name
            and self.implementation.format_name.startswith("sphinx")
        ):
            cells.append(new_code_cell(source="%matplotlib inline"))

        cell_metadata_json = False

        while lines:
            reader = self.implementation.cell_reader_class(self.fmt, default_language)
            cell, pos = reader.read(lines)
            cells.append(cell)
            cell_metadata_json = cell_metadata_json or reader.cell_metadata_json
            if pos <= 0:
                raise Exception(
                    "Blocked at lines " + "\n".join(lines[:6])
                )  # pragma: no cover
            lines = lines[pos:]

        custom_cell_magics = self.fmt.get("custom_cell_magics", "").split(",")
        set_main_and_cell_language(
            metadata, cells, self.implementation.extension, custom_cell_magics
        )
        cell_metadata = set()
        for cell in cells:
            cell_metadata.update(cell.metadata.keys())
        update_metadata_filters(metadata, jupyter_md, cell_metadata)

        if cell_metadata_json:
            metadata.setdefault("jupytext", {}).setdefault("cell_metadata_json", True)

        if (
            self.implementation.format_name
            and self.implementation.format_name.startswith("sphinx")
        ):
            filtered_cells = []
            for i, cell in enumerate(cells):
                if (
                    cell.source == ""
                    and i > 0
                    and i + 1 < len(cells)
                    and cells[i - 1].cell_type != "markdown"
                    and cells[i + 1].cell_type != "markdown"
                ):
                    continue
                filtered_cells.append(cell)
            cells = filtered_cells

        return new_notebook(cells=cells, metadata=metadata)

    def writes(self, nb, metadata=None, **kwargs):
        """Return the text representation of the notebook"""
        if self.fmt.get("format_name") == "pandoc":
            metadata = insert_jupytext_info_and_filter_metadata(
                metadata, self.ext, self.implementation
            )

            cells = []
            for cell in nb.cells:
                cell_metadata = filter_metadata(
                    cell.metadata,
                    self.fmt.get("cell_metadata_filter"),
                    _IGNORE_CELL_METADATA,
                )
                if cell.cell_type == "code":
                    cells.append(
                        new_code_cell(source=cell.source, metadata=cell_metadata)
                    )
                else:
                    cells.append(
                        NotebookNode(
                            source=cell.source,
                            metadata=cell_metadata,
                            cell_type=cell.cell_type,
                        )
                    )

            return notebook_to_md(
                NotebookNode(
                    nbformat=nb.nbformat,
                    nbformat_minor=nb.nbformat_minor,
                    metadata=metadata,
                    cells=cells,
                )
            )

        if self.fmt.get(
            "format_name"
        ) == MYST_FORMAT_NAME or self.ext in myst_extensions(no_md=True):
            pygments_lexer = metadata.get("language_info", {}).get(
                "pygments_lexer", None
            )
            metadata = insert_jupytext_info_and_filter_metadata(
                metadata, self.ext, self.implementation
            )

            cells = []
            for cell in nb.cells:
                cell_metadata = filter_metadata(
                    cell.metadata,
                    self.fmt.get("cell_metadata_filter"),
                    _IGNORE_CELL_METADATA,
                )
                if cell.cell_type == "code":
                    cells.append(
                        new_code_cell(source=cell.source, metadata=cell_metadata)
                    )
                else:
                    cells.append(
                        NotebookNode(
                            source=cell.source,
                            metadata=cell_metadata,
                            cell_type=cell.cell_type,
                        )
                    )
            return notebook_to_myst(
                NotebookNode(
                    nbformat=nb.nbformat,
                    nbformat_minor=nb.nbformat_minor,
                    metadata=metadata,
                    cells=cells,
                ),
                default_lexer=pygments_lexer,
            )

        # Copy the notebook, in order to be sure we do not modify the original notebook
        nb = NotebookNode(
            nbformat=nb.nbformat,
            nbformat_minor=nb.nbformat_minor,
            metadata=deepcopy(metadata or nb.metadata),
            cells=nb.cells,
        )

        metadata = nb.metadata
        default_language = (
            default_language_from_metadata_and_ext(
                metadata, self.implementation.extension, True
            )
            or "python"
        )
        self.update_fmt_with_notebook_options(nb.metadata)
        if "use_runtools" not in self.fmt:
            for cell in nb.cells:
                if cell.metadata.get("hide_input", False) or cell.metadata.get(
                    "hide_output", False
                ):
                    self.fmt["use_runtools"] = True
                    break

        header = encoding_and_executable(nb, metadata, self.ext)
        header_content, header_lines_to_next_cell = metadata_and_cell_to_header(
            nb,
            metadata,
            self.implementation,
            self.ext,
            self.fmt.get("root_level_metadata_as_raw_cell", True),
        )
        header.extend(header_content)

        cell_exporters = []
        looking_for_first_markdown_cell = (
            self.implementation.format_name
            and self.implementation.format_name.startswith("sphinx")
        )
        split_at_heading = self.fmt.get("split_at_heading", False)

        for cell in nb.cells:
            if looking_for_first_markdown_cell and cell.cell_type == "markdown":
                cell.metadata.setdefault("cell_marker", '"""')
                looking_for_first_markdown_cell = False

            cell_exporters.append(
                self.implementation.cell_exporter_class(
                    cell, default_language, self.fmt
                )
            )

        texts = [cell.cell_to_text() for cell in cell_exporters]
        lines = []

        # concatenate cells in reverse order to determine how many blank lines (pep8)
        for i, cell in reversed(list(enumerate(cell_exporters))):
            text = cell.remove_eoc_marker(texts[i], lines)

            if (
                i == 0
                and self.implementation.format_name
                and self.implementation.format_name.startswith("sphinx")
                and (text in [["%matplotlib inline"], ["# %matplotlib inline"]])
            ):
                continue

            lines_to_next_cell = cell.lines_to_next_cell
            if lines_to_next_cell is None:
                lines_to_next_cell = pep8_lines_between_cells(
                    text, lines, self.implementation.extension
                )

            text.extend([""] * lines_to_next_cell)

            # two blank lines between markdown cells in Rmd when those do not have explicit region markers
            if self.ext in [".md", ".markdown", ".Rmd"] and not cell.is_code():
                if (
                    i + 1 < len(cell_exporters)
                    and not cell_exporters[i + 1].is_code()
                    and not texts[i][0].startswith("<!-- #")
                    and not texts[i + 1][0].startswith("<!-- #")
                    and (
                        not split_at_heading
                        or not (texts[i + 1] and texts[i + 1][0].startswith("#"))
                    )
                ):
                    text.append("")

            # "" between two consecutive code cells in sphinx
            if self.implementation.format_name.startswith("sphinx") and cell.is_code():
                if i + 1 < len(cell_exporters) and cell_exporters[i + 1].is_code():
                    text.append('""')

            lines = text + lines

        if header_lines_to_next_cell is None:
            header_lines_to_next_cell = pep8_lines_between_cells(
                header_content, lines, self.implementation.extension
            )

        header.extend([""] * header_lines_to_next_cell)

        return "\n".join(header + lines)


def reads(text, fmt, as_version=nbformat.NO_CONVERT, **kwargs):
    """
    Read a notebook from a string

    :param text: the text representation of the notebook
    :param fmt: (optional) the jupytext format like `md`, `py:percent`, ...
    :param as_version: see nbformat.reads
    :param kwargs: (not used) additional parameters for nbformat.reads
    :return: the notebook
    """
    fmt = copy(fmt) if fmt else divine_format(text)
    fmt = long_form_one_format(fmt)
    ext = fmt["extension"]

    if ext == ".ipynb":
        return nbformat.reads(text, as_version, **kwargs)

    format_name = read_format_from_metadata(text, ext) or fmt.get("format_name")

    if format_name:
        format_options = {}
    else:
        format_name, format_options = guess_format(text, ext)

    if format_name:
        fmt["format_name"] = format_name

    fmt.update(format_options)
    reader = TextNotebookConverter(fmt)
    notebook = reader.reads(text, **kwargs)
    rearrange_jupytext_metadata(notebook.metadata)

    if format_name and insert_or_test_version_number():
        notebook.metadata.setdefault("jupytext", {}).setdefault(
            "text_representation", {}
        ).update({"extension": ext, "format_name": format_name})

    return notebook


def read(fp, as_version=nbformat.NO_CONVERT, fmt=None, **kwargs):
    """Read a notebook from a file name or a file object

    :param fp: a file name or a file object
    :param as_version: see nbformat.read
    :param fmt: (optional) the jupytext format like `md`, `py:percent`, ...
    :param kwargs: (not used) additional parameters for nbformat.read
    :return: the notebook
    """
    if as_version != nbformat.NO_CONVERT and not isinstance(as_version, int):
        raise TypeError(
            "Second argument 'as_version' should be either nbformat.NO_CONVERT, or an integer."
        )

    if fp == "-":
        text = sys.stdin.read()
        return reads(text, fmt)

    if not hasattr(fp, "read"):
        # Treat fp as a file name
        fp = str(fp)
        _, ext = os.path.splitext(fp)
        fmt = copy(fmt or {})
        if not isinstance(fmt, dict):
            fmt = long_form_one_format(fmt)
        fmt.update({"extension": ext})
        with io.open(fp, encoding="utf-8") as stream:
            return read(stream, as_version=as_version, fmt=fmt, **kwargs)

    if fmt is not None:
        fmt = long_form_one_format(fmt)
        if fmt["extension"] == ".ipynb":
            notebook = nbformat.read(fp, as_version, **kwargs)
            rearrange_jupytext_metadata(notebook.metadata)
            return notebook

    return reads(fp.read(), fmt, **kwargs)


def writes(notebook, fmt, version=nbformat.NO_CONVERT, **kwargs):
    """Return text representation of the notebook

    :param notebook: the notebook
    :param fmt: the jupytext format like `md`, `py:percent`, ...
    :param version: see nbformat.writes
    :param kwargs: (not used) additional parameters for nbformat.writes
    :return: the text representation of the notebook
    """
    metadata = deepcopy(notebook.metadata)
    rearrange_jupytext_metadata(metadata)
    fmt = copy(fmt)
    fmt = long_form_one_format(fmt, metadata)
    ext = fmt["extension"]
    format_name = fmt.get("format_name")

    jupytext_metadata = metadata.get("jupytext", {})

    if ext == ".ipynb":
        # Remove jupytext section if empty
        jupytext_metadata.pop("text_representation", {})
        if not jupytext_metadata:
            metadata.pop("jupytext", {})
        return nbformat.writes(
            NotebookNode(
                nbformat=notebook.nbformat,
                nbformat_minor=notebook.nbformat_minor,
                metadata=metadata,
                cells=notebook.cells,
            ),
            version,
            **kwargs
        )

    if not format_name:
        format_name = format_name_for_ext(metadata, ext, explicit_default=False)

    if format_name:
        fmt["format_name"] = format_name
        update_jupytext_formats_metadata(metadata, fmt)

    writer = TextNotebookConverter(fmt)
    return writer.writes(notebook, metadata)


def write(nb, fp, version=nbformat.NO_CONVERT, fmt=None, **kwargs):
    """Write a notebook to a file name or a file object

    :param nb: the notebook
    :param fp: a file name or a file object
    :param version: see nbformat.write
    :param fmt: (optional if fp is a file name) the jupytext format like `md`, `py:percent`, ...
    :param kwargs: (not used) additional parameters for nbformat.write
    """
    if fp == "-":
        # Use sys.stdout.buffer when possible, and explicit utf-8 encoding, cf. #331
        content = writes(nb, version=version, fmt=fmt, **kwargs)
        try:
            # Python 3
            sys.stdout.buffer.write(content.encode("utf-8"))
        except AttributeError:
            sys.stdout.write(content.encode("utf-8"))
        return

    if not hasattr(fp, "write"):
        # Treat fp as a file name
        fp = str(fp)
        _, ext = os.path.splitext(fp)
        fmt = copy(fmt or {})
        fmt = long_form_one_format(fmt, update={"extension": ext})
        create_prefix_dir(fp, fmt)

        with io.open(fp, "w", encoding="utf-8") as stream:
            write(nb, stream, version=version, fmt=fmt, **kwargs)
            return
    else:
        assert (
            fmt is not None
        ), "'fmt' argument in jupytext.write is mandatory unless fp is a file name"

    content = writes(nb, version=version, fmt=fmt, **kwargs)
    if isinstance(content, bytes):
        content = content.decode("utf8")
    fp.write(content)
    if not content.endswith(u"\n"):
        fp.write(u"\n")


def create_prefix_dir(nb_file, fmt):
    """Create directory if fmt has a prefix"""
    if "prefix" in fmt:
        nb_dir = os.path.dirname(nb_file) + os.path.sep
        if not os.path.isdir(nb_dir):
            logging.log(
                logging.WARNING, "[jupytext] creating missing directory %s", nb_dir
            )
            os.makedirs(nb_dir)
