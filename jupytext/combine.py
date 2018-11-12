"""Combine source and outputs from two notebooks
"""
import re
from copy import copy
from .cell_metadata import _IGNORE_CELL_METADATA, _JUPYTEXT_CELL_METADATA
from .header import _DEFAULT_NOTEBOOK_METADATA
from .metadata_filter import filter_metadata

_BLANK_LINE = re.compile(r'^\s*$')


def same_content(ref, test):
    """Is the content of two cells the same, except for blank lines?"""
    ref = [line for line in ref.splitlines() if not _BLANK_LINE.match(line)]
    test = [line for line in test.splitlines() if not _BLANK_LINE.match(line)]
    return ref == test


def combine_inputs_with_outputs(nb_source, nb_outputs):
    """Copy outputs of the second notebook into
    the first one, for cells that have matching inputs"""

    output_code_cells = [cell for cell in nb_outputs.cells if cell.cell_type == 'code']
    output_other_cells = [cell for cell in nb_outputs.cells if cell.cell_type != 'code']

    text_representation = nb_source.metadata.get('jupytext', {}).get('text_representation', {})
    ext = text_representation.get('extension')
    format_name = text_representation.get('format_name')

    nb_outputs_filtered_metadata = copy(nb_outputs.metadata)
    filter_metadata(nb_outputs_filtered_metadata,
                    nb_source.metadata.get('jupytext', {}).get('metadata_filter', {}).get('notebook'),
                    _DEFAULT_NOTEBOOK_METADATA)

    for key in nb_outputs.metadata:
        if key not in nb_outputs_filtered_metadata:
            nb_source.metadata[key] = nb_outputs.metadata[key]

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
                    if (ext and ext.endswith('.md')) or format_name == 'sphinx':
                        ocell_filtered_metadata = {}
                    else:
                        ocell_filtered_metadata = copy(ocell.metadata)
                        filter_metadata(ocell_filtered_metadata,
                                        nb_source.metadata.get('jupytext', {}).get('metadata_filter', {}).get('cells'),
                                        _IGNORE_CELL_METADATA)

                    for key in ocell.metadata:
                        if key not in ocell_filtered_metadata and key not in _JUPYTEXT_CELL_METADATA:
                            cell.metadata[key] = ocell.metadata[key]

                    output_code_cells = output_code_cells[(i + 1):]
                    break
        else:
            for i, ocell in enumerate(output_other_cells):
                if cell.cell_type == ocell.cell_type and same_content(cell.source, ocell.source):
                    if (ext and (ext.endswith('.md') or ext.endswith('.Rmd'))) \
                            or format_name in ['spin', 'sphinx', 'sphinx']:
                        ocell_filtered_metadata = {}
                    else:
                        ocell_filtered_metadata = copy(ocell.metadata)
                        filter_metadata(ocell_filtered_metadata,
                                        nb_source.metadata.get('jupytext', {}).get('metadata_filter', {}).get('cells'),
                                        _IGNORE_CELL_METADATA)

                    for key in ocell.metadata:
                        if key not in ocell_filtered_metadata:
                            cell.metadata[key] = ocell.metadata[key]

                    output_other_cells = output_other_cells[(i + 1):]
                    break
