import os
import nbrmd
import nbformat


def update_rmd_and_ipynb(model, path, format=['.ipynb', '.Rmd'], **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks under the alternative form.
    When the notebook has extension '.ipynb', this creates a '.Rmd' file
    When the notebook has extension '.Rmd', this creates a '.ipynb' file
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param format: list of alternative formats
    :param kwargs: not used
    :return:
    """

    # only run on notebooks
    if model['type'] != 'notebook':
        return

    # only run on nbformat v4
    nb = model['content']
    if nb['nbformat'] != 4:
        return

    format = nb.get('metadata', {}).get('nbrmd_formats', format)
    if not isinstance(format, list) or not set(format).issubset(['.Rmd', '.md', '.ipynb']):
        raise TypeError("Notebook metadata 'nbrmd_formats' should be subset of ['.Rmd', '.md', '.ipynb']")

    file, ext = os.path.splitext(path)

    for alt_ext in format:
        if ext != alt_ext:
            nbrmd.writef(nbformat.notebooknode.from_dict(nb), file + alt_ext)


def update_rmd(model, path, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks in '.Rmd' format when
    the notebook has extension '.ipynb'
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param kwargs: not used
    :return:
    """
    update_rmd_and_ipynb(model, path, format=['.Rmd'], **kwargs)


def update_ipynb(model, path, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks in '.Rmd' format when
    the notebook has extension '.ipynb'
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param kwargs: not used
    :return:
    """
    update_rmd_and_ipynb(model, path, format=['.ipynb'], **kwargs)


def update_selected_formats(model, path, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks in the formats selected in
    notebook metadata 'nbrmd_formats', that should be a list
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param kwargs: not used
    :return:
    """

    update_rmd_and_ipynb(model, path, format=[], **kwargs)
