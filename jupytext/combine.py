"""Combine source and outputs from two notebooks
"""
import re
from .cell_metadata import _IGNORE_METADATA

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

    for cell in nb_source.cells:
        # Remove outputs to warranty that trust of returned notebook is that of second notebook
        if cell.cell_type == 'code':
            cell.execution_count = None
            cell.outputs = []

            for i, ocell in enumerate(output_code_cells):
                if same_content(cell.source, ocell.source):
                    cell.execution_count = ocell.execution_count
                    cell.outputs = ocell.outputs

                    ometadata = ocell.metadata
                    cell.metadata.update({k: ometadata[k] for k in ometadata if k in _IGNORE_METADATA})
                    output_code_cells = output_code_cells[(i + 1):]
                    break
        else:
            # Fill outputs with that of second notebook
            for i, ocell in enumerate(output_other_cells):
                if cell.cell_type == ocell.cell_type and same_content(cell.source, ocell.source):
                    ometadata = ocell.metadata
                    cell.metadata.update({k: ometadata[k] for k in ometadata if k in _IGNORE_METADATA})

                    output_other_cells = output_other_cells[(i + 1):]
                    break
