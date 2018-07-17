from .cell_metadata import _ignore_metadata


def combine_inputs_with_outputs(nb_source, nb_outputs):
    '''Copy outputs of the second notebook into
    the first one, for cells that have matching inputs'''

    remaining_output_cells = nb_outputs.cells
    for cell in nb_source.cells:
        if cell.cell_type != 'code':
            continue

        # Remove outputs to warranty that trust of returned
        # notebook is that of second notebook
        cell.execution_count = None
        cell.outputs = []

        # Fill outputs with that of second notebook
        for i, ocell in enumerate(remaining_output_cells):
            if ocell.cell_type == 'code' and cell.source == ocell.source:
                cell.execution_count = ocell.execution_count
                cell.outputs = ocell.outputs

                m = ocell.metadata
                cell.metadata.update({k: m[k] for k in m
                                      if m in _ignore_metadata})
                remaining_output_cells = remaining_output_cells[(i + 1):]
                break
