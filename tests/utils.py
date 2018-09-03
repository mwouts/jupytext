import os
import copy


def list_all_notebooks(ext, path=None):
    """
    :ext: desired extension
    :return: all notebooks in the directory of this script,
     with the desired extension
    """
    nb_path = os.path.dirname(os.path.abspath(__file__))
    if path:
        nb_path = os.path.join(nb_path, path)
    notebooks = []
    for nb_file in os.listdir(nb_path):
        _, nb_ext = os.path.splitext(nb_file)
        if nb_ext.lower() == ext.lower() and \
                (not nb_file.startswith('ir_notebook')
                 or nb_file.startswith('R_sample')):
            notebooks.append(os.path.join(nb_path, nb_file))
    return notebooks


def list_r_notebooks(ext):
    """
    :ext: desired extension
    :return: all R notebooks in the directory of this script,
     with the desired extension
    """
    nb_path = os.path.dirname(os.path.abspath(__file__))
    notebooks = []
    for nb_file in os.listdir(nb_path):
        _, nb_ext = os.path.splitext(nb_file)
        if nb_ext.lower() == ext.lower() and \
                (nb_file.startswith('ir_notebook')
                 or nb_file.startswith('R_sample')):
            notebooks.append(os.path.join(nb_path, nb_file))
    return notebooks


def list_julia_notebooks(ext):
    """
    :ext: desired extension
    :return: all Julia notebooks in the directory of this script,
     with the desired extension
    """
    nb_path = os.path.dirname(os.path.abspath(__file__))
    notebooks = []
    for nb_file in os.listdir(nb_path):
        _, nb_ext = os.path.splitext(nb_file)
        if nb_ext.lower() == ext.lower() and nb_file.startswith('julia_'):
            notebooks.append(os.path.join(nb_path, nb_file))
    return notebooks


def list_py_notebooks(ext):
    """
    :ext: desired extension
    :return: all Python notebooks in the directory of this script,
     with the desired extension
    """
    nb_path = os.path.dirname(os.path.abspath(__file__))
    notebooks = []
    for nb_file in os.listdir(nb_path):
        _, nb_ext = os.path.splitext(nb_file)
        if nb_ext.lower() == ext.lower() and not (
                nb_file.startswith('julia_')
                or nb_file.startswith('ir_notebook')
                or nb_file.startswith('R_sample')):
            notebooks.append(os.path.join(nb_path, nb_file))
    return notebooks
