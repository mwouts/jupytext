import os

def list_all_notebooks(ext):
    """
    :ext: desired extension
    :return: all notebooks in the directory of this script, with the desired extension
    """
    nb_path = os.path.dirname(os.path.abspath(__file__))
    notebooks = []
    for nb_file in os.listdir(nb_path):
        file, nb_ext = os.path.splitext(nb_file)
        if nb_ext.lower() == ext.lower():
            notebooks.append(os.path.join(nb_path, nb_file))
    return notebooks