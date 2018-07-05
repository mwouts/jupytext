import os
import nbrmd
import nbformat


def update_rmd_and_ipynb(model, path, contents_manager=None,
                         format=['.ipynb', '.Rmd'], **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks
    under the alternative form.
    When the notebook has extension '.ipynb', this creates a '.Rmd' file
    When the notebook has extension '.Rmd', this creates a '.ipynb' file
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param contents_manager: ContentsManager instance
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
    if not isinstance(format, list) or not set(format).issubset(
            ['.Rmd', '.md', '.ipynb']):
        raise TypeError(u"Notebook metadata 'nbrmd_formats' "
                        u"should be subset of ['.Rmd', '.md', '.ipynb']")

    os_path = contents_manager._get_os_path(path) if contents_manager else path
    file, ext = os.path.splitext(path)
    os_file, ext = os.path.splitext(os_path)

    for alt_ext in format:
        if ext != alt_ext:
            if contents_manager:
                contents_manager.log.info(
                    u"Saving file at /%s", file + alt_ext)
            nbrmd.writef(nbformat.notebooknode.from_dict(nb),
                         os_file + alt_ext)


def update_rmd(model, path, contents_manager=None, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks in '.Rmd' format when
    the notebook has extension '.ipynb'
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param contents_manager: ContentsManager instance
    :param kwargs: not used
    :return:
    """
    update_rmd_and_ipynb(model, path, contents_manager, format=['.Rmd'],
                         **kwargs)


def update_ipynb(model, path, contents_manager=None, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks in '.Rmd' format when
    the notebook has extension '.ipynb'
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param contents_manager: ContentsManager instance
    :param kwargs: not used
    :return:
    """
    update_rmd_and_ipynb(model, path, contents_manager, format=['.ipynb'],
                         **kwargs)


def update_selected_formats(model, path, contents_manager=None, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks in the formats
    selected in notebook metadata 'nbrmd_formats', that should be a list
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param contents_manager: ContentsManager instance
    :param kwargs: not used
    :return:
    """

    update_rmd_and_ipynb(model, path, contents_manager=None, format=[],
                         **kwargs)
