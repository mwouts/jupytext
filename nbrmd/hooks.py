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

    file, ext = os.path.splitext(path)

    if ext != '.Rmd':
        if '.Rmd' in format:
            rmd_file = file + '.Rmd'
            nbrmd.writef(nbformat.notebooknode.from_dict(nb), rmd_file)
    elif ext != '.ipynb':
        if '.ipynb' in format:
            ipynb_file = file + '.ipynb'
            with open(ipynb_file, 'w') as fp:
                nbformat.write(nbformat.notebooknode.from_dict(nb), fp)


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
