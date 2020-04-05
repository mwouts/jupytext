"""Combine source and outputs from two notebooks
"""
import re
from .cell_metadata import _IGNORE_CELL_METADATA
from .header import _DEFAULT_NOTEBOOK_METADATA
from .metadata_filter import restore_filtered_metadata
from .formats import long_form_one_format

_BLANK_LINE = re.compile(r"^\s*$")


def black_invariant(text, chars=None):
    """Remove characters that may be changed when reformatting the text with black"""
    if chars is None:
        chars = [" ", "\t", "\n", ",", "'", '"', "(", ")", "\\"]

    for char in chars:
        text = text.replace(char, "")
    return text


def same_content(ref, test, endswith=False):
    """Is the content of two cells the same, up to reformating by black"""
    ref = black_invariant(ref)
    test = black_invariant(test)

    if endswith and test:
        return ref.endswith(test)
    return ref == test


def combine_inputs_with_outputs(nb_source, nb_outputs, fmt=None):
    """Copy outputs and metadata of the second notebook into the first one."""
    # nbformat version number taken from the notebook with outputs
    assert (
        nb_outputs.nbformat == nb_source.nbformat
    ), "The notebook with outputs is in format {}.{}, please upgrade it to {}.x".format(
        nb_outputs.nbformat, nb_outputs.nbformat_minor, nb_source.nbformat
    )
    nb_source.nbformat_minor = nb_outputs.nbformat_minor

    fmt = long_form_one_format(fmt)
    text_repr = nb_source.metadata.get("jupytext", {}).get("text_representation", {})
    ext = fmt.get("extension") or text_repr.get("extension")
    format_name = fmt.get("format_name") or text_repr.get("format_name")

    nb_source.metadata = restore_filtered_metadata(
        nb_source.metadata,
        nb_outputs.metadata,
        nb_source.metadata.get("jupytext", {}).get("notebook_metadata_filter"),
        _DEFAULT_NOTEBOOK_METADATA,
    )

    source_is_md_version_one = (
        ext in [".md", ".markdown", ".Rmd"] and text_repr.get("format_version") == "1.0"
    )
    if nb_source.metadata.get("jupytext", {}).get("formats") or ext in [
        ".md",
        ".markdown",
        ".Rmd",
    ]:
        nb_source.metadata.get("jupytext", {}).pop("text_representation", None)

    if not nb_source.metadata.get("jupytext", {}):
        nb_source.metadata.pop("jupytext", {})

    if format_name in ["nomarker", "sphinx"] or source_is_md_version_one:
        cell_metadata_filter = "-all"
    else:
        cell_metadata_filter = nb_source.metadata.get("jupytext", {}).get(
            "cell_metadata_filter"
        )

    outputs_map = map_outputs_to_inputs(nb_source.cells, nb_outputs.cells)

    for cell, j in zip(nb_source.cells, outputs_map):
        # Remove outputs to warranty that trust of returned notebook is that of second notebook
        if cell.cell_type == "code":
            cell.execution_count = None
            cell.outputs = []

            if j is not None:
                ocell = nb_outputs.cells[j]
                cell.execution_count = ocell.execution_count
                cell.outputs = ocell.outputs

                # Restore the filtered output cell metadata
                cell.metadata = restore_filtered_metadata(
                    cell.metadata,
                    ocell.metadata,
                    cell_metadata_filter,
                    _IGNORE_CELL_METADATA,
                )
        else:
            if j is not None:
                ocell = nb_outputs.cells[j]

                # The 'spin' format does not allow metadata on non-code cells
                cell.metadata = restore_filtered_metadata(
                    cell.metadata,
                    ocell.metadata,
                    "-all" if format_name == "spin" else cell_metadata_filter,
                    _IGNORE_CELL_METADATA,
                )

    return nb_source


def map_outputs_to_inputs(cells_inputs, cells_outputs):
    """Returns a map i->(j or None) that maps the cells with outputs to the input cells"""
    n_in = len(cells_inputs)
    n_out = len(cells_outputs)
    outputs_map = [None] * n_in

    # First rule: match based on cell type, content, in increasing order, for each cell type
    first_unmatched_output_per_cell_type = {}
    for i in range(n_in):
        cell_input = cells_inputs[i]
        for j in range(
            first_unmatched_output_per_cell_type.get(cell_input.cell_type, 0), n_out
        ):
            cell_output = cells_outputs[j]
            if cell_input.cell_type == cell_output.cell_type and same_content(
                cell_input.source, cell_output.source
            ):
                outputs_map[i] = j
                first_unmatched_output_per_cell_type[cell_input.cell_type] = j + 1
                break

    # Second rule: match unused outputs based on cell type and content
    # Third rule: is the new cell the final part of a previous cell with outputs?
    unused_ouputs = set(range(n_out)).difference(outputs_map)
    for endswith in [False, True]:
        if not unused_ouputs:
            return outputs_map

        for i in range(n_in):
            if outputs_map[i] is not None:
                continue
            cell_input = cells_inputs[i]
            for j in unused_ouputs:
                cell_output = cells_outputs[j]
                if cell_input.cell_type == cell_output.cell_type and same_content(
                    cell_output.source, cell_input.source, endswith
                ):
                    outputs_map[i] = j
                    unused_ouputs.remove(j)
                    break

    # Fourth rule: match based on increasing index (and cell type) for non-empty cells
    if not unused_ouputs:
        return outputs_map

    prev_j = -1
    for i in range(n_in):
        if outputs_map[i] is not None:
            prev_j = outputs_map[i]
            continue

        j = prev_j + 1
        if j not in unused_ouputs:
            continue

        cell_input = cells_inputs[i]
        cell_output = cells_outputs[j]
        if (
            cell_input.cell_type == cell_output.cell_type
            and cell_input.source.strip() != ""
        ):
            outputs_map[i] = j
            unused_ouputs.remove(j)
            prev_j = j

    return outputs_map
