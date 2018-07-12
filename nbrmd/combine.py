from .chunk_options import _ignore_metadata


def combine_inputs_with_outputs(nb_source, nb_outputs):
    '''Copy outputs of the second notebook into
    the first one, for cells that have matching inputs'''

    remaining_output_cells = nb_outputs.cells
    for cell in nb_source.cells:
        for i, ocell in enumerate(remaining_output_cells):
            if cell.cell_type == 'code' \
                    and ocell.cell_type == 'code' \
                    and cell.source == ocell.source:
                cell.execution_count = ocell.execution_count
                cell.outputs = ocell.outputs

                m = ocell.metadata
                cell.metadata.update({k: m[k] for k in m
                                      if m in _ignore_metadata})
                remaining_output_cells = remaining_output_cells[(i + 1):]
                break
