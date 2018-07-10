def combine_inputs_with_outputs(nb_source, nb_outputs):
    '''Copy outputs of the second notebook into
    the first one, for cells that have matching inputs'''

    remaining_output_cells = nb_outputs.get('cells', [])
    for cell in nb_source.get('cells', []):
        for i, ocell in enumerate(remaining_output_cells):
            if cell.get('cell_type') == 'code' \
                    and ocell.get('cell_type') == 'code' \
                    and cell.get('source') == ocell.get('source'):
                cell['execution_count'] = ocell.get('execution_count')
                cell['outputs'] = ocell.get('outputs', None)
                remaining_output_cells = remaining_output_cells[(i + 1):]
                break
