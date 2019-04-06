"""Combine source and outputs from two notebooks
"""
import re
from copy import copy
from .cell_metadata import _IGNORE_CELL_METADATA, _JUPYTEXT_CELL_METADATA
from .header import _DEFAULT_NOTEBOOK_METADATA
from .metadata_filter import filter_metadata
from .formats import long_form_one_format

_BLANK_LINE = re.compile(r'^\s*$')


def black_invariant(text, chars=None):
    """Remove characters that may be changed when reformatting the text with black"""
    if chars is None:
        chars = [' ', '\t', '\n', ',', "'", '"', '(', ')', '\\']

    for char in chars:
        text = text.replace(char, '')
    return text


def same_content(ref, test):
    """Is the content of two cells the same, up to reformating by black"""
    return black_invariant(ref) == black_invariant(test)


def combine_inputs_with_outputs(nb_source, nb_outputs, fmt=None):
    """Copy outputs of the second notebook into
    the first one, for cells that have matching inputs"""

    output_code_cells = [cell for cell in nb_outputs.cells if cell.cell_type == 'code']
    output_other_cells = [cell for cell in nb_outputs.cells if cell.cell_type != 'code']

    fmt = long_form_one_format(fmt)
    text_repr = nb_source.metadata.get('jupytext', {}).get('text_representation', {})
    ext = fmt.get('extension') or text_repr.get('extension')
    format_name = fmt.get('format_name') or text_repr.get('format_name')

    nb_outputs_filtered_metadata = copy(nb_outputs.metadata)
    filter_metadata(nb_outputs_filtered_metadata,
                    nb_source.metadata.get('jupytext', {}).get('notebook_metadata_filter'),
                    _DEFAULT_NOTEBOOK_METADATA)

    for key in nb_outputs.metadata:
        if key not in nb_outputs_filtered_metadata:
            nb_source.metadata[key] = nb_outputs.metadata[key]

    source_is_md_version_one = ext in ['.md', '.Rmd'] and text_repr.get('format_version') == '1.0'
    if nb_source.metadata.get('jupytext', {}).get('formats') or ext in ['.md', '.Rmd']:
        nb_source.metadata.get('jupytext', {}).pop('text_representation', None)

    if not nb_source.metadata.get('jupytext', {}):
        nb_source.metadata.pop('jupytext', {})

    for cell in nb_source.cells:
        # Remove outputs to warranty that trust of returned notebook is that of second notebook
        if cell.cell_type == 'code':
            cell.execution_count = None
            cell.outputs = []

            for i, ocell in enumerate(output_code_cells):
                if same_content(cell.source, ocell.source):
                    # Fill outputs with that of second notebook
                    cell.execution_count = ocell.execution_count
                    cell.outputs = ocell.outputs

                    # Append cell metadata that was filtered
                    if format_name in ['bare', 'sphinx'] or source_is_md_version_one:
                        ocell_filtered_metadata = {}
                    else:
                        ocell_filtered_metadata = copy(ocell.metadata)
                        filter_metadata(ocell_filtered_metadata,
                                        nb_source.metadata.get('jupytext', {}).get('cell_metadata_filter'),
                                        _IGNORE_CELL_METADATA)

                    for key in ocell.metadata:
                        if key not in ocell_filtered_metadata and key not in _JUPYTEXT_CELL_METADATA:
                            cell.metadata[key] = ocell.metadata[key]

                    output_code_cells = output_code_cells[(i + 1):]
                    break
        else:
            for i, ocell in enumerate(output_other_cells):
                if cell.cell_type == ocell.cell_type and same_content(cell.source, ocell.source):
                    if format_name in ['spin', 'bare', 'sphinx'] or source_is_md_version_one:
                        ocell_filtered_metadata = {}
                    else:
                        ocell_filtered_metadata = copy(ocell.metadata)
                        filter_metadata(ocell_filtered_metadata,
                                        nb_source.metadata.get('jupytext', {}).get('cell_metadata_filter'),
                                        _IGNORE_CELL_METADATA)

                    for key in ocell.metadata:
                        if key not in ocell_filtered_metadata:
                            cell.metadata[key] = ocell.metadata[key]

                    output_other_cells = output_other_cells[(i + 1):]
                    break

    return nb_source
