"""Combine source and outputs from two notebooks
"""
import re
from .cell_metadata import _IGNORE_CELL_METADATA
from .header import _DEFAULT_NOTEBOOK_METADATA
from .metadata_filter import restore_filtered_metadata
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
    """Copy outputs and metadata of the second notebook into
    the first one, for cells that have matching inputs"""

    output_code_cells = [cell for cell in nb_outputs.cells if cell.cell_type == 'code']
    output_other_cells = [cell for cell in nb_outputs.cells if cell.cell_type != 'code']

    # nbformat version number taken from the notebook with outputs
    assert nb_outputs.nbformat == nb_source.nbformat, \
        "The notebook with outputs is in format {}.{}, please upgrade it to {}.x".format(
            nb_outputs.nbformat, nb_outputs.nbformat_minor, nb_source.nbformat)
    nb_source.nbformat_minor = nb_outputs.nbformat_minor

    fmt = long_form_one_format(fmt)
    text_repr = nb_source.metadata.get('jupytext', {}).get('text_representation', {})
    ext = fmt.get('extension') or text_repr.get('extension')
    format_name = fmt.get('format_name') or text_repr.get('format_name')

    nb_source.metadata = restore_filtered_metadata(
        nb_source.metadata,
        nb_outputs.metadata,
        nb_source.metadata.get('jupytext', {}).get('notebook_metadata_filter'),
        _DEFAULT_NOTEBOOK_METADATA)

    source_is_md_version_one = ext in ['.md', '.markdown', '.Rmd'] and text_repr.get('format_version') == '1.0'
    if nb_source.metadata.get('jupytext', {}).get('formats') or ext in ['.md', '.markdown', '.Rmd']:
        nb_source.metadata.get('jupytext', {}).pop('text_representation', None)

    if not nb_source.metadata.get('jupytext', {}):
        nb_source.metadata.pop('jupytext', {})

    if format_name in ['nomarker', 'sphinx'] or source_is_md_version_one:
        cell_metadata_filter = '-all'
    else:
        cell_metadata_filter = nb_source.metadata.get('jupytext', {}).get('cell_metadata_filter')

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

                    # Restore the filtered output cell metadata
                    cell.metadata = restore_filtered_metadata(cell.metadata, ocell.metadata,
                                                              cell_metadata_filter, _IGNORE_CELL_METADATA)

                    output_code_cells = output_code_cells[(i + 1):]
                    break
        else:
            for i, ocell in enumerate(output_other_cells):
                if cell.cell_type == ocell.cell_type and same_content(cell.source, ocell.source):
                    # The 'spin' format does not allow metadata on non-code cells
                    cell.metadata = restore_filtered_metadata(cell.metadata, ocell.metadata,
                                                              '-all' if format_name == 'spin' else cell_metadata_filter,
                                                              _IGNORE_CELL_METADATA)

                    output_other_cells = output_other_cells[(i + 1):]
                    break

    return nb_source
