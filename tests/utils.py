import os
import copy


def list_all_notebooks(ext):
    """
    :ext: desired extension
    :return: all notebooks in the directory of this script,
     with the desired extension
    """
    nb_path = os.path.dirname(os.path.abspath(__file__))
    notebooks = []
    for nb_file in os.listdir(nb_path):
        file, nb_ext = os.path.splitext(nb_file)
        if nb_ext.lower() == ext.lower():
            notebooks.append(os.path.join(nb_path, nb_file))
    return notebooks


def remove_outputs(nb):
    nb = copy.deepcopy(nb)
    for cell in nb.cells:
        cell.outputs = None
        cell.execution_count = None
        if 'trusted' in cell['metadata']:
            del cell['metadata']['trusted']

    for k in ['nbformat', 'nbformat_minor']:
        if k in nb:
            del nb[k]

    return nb


def remove_outputs_and_header(nb):
    nb = remove_outputs(nb)
    nb['metadata'] = {}
    return nb
