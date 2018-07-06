import os
import nbrmd
import nbformat


def check_extensions(extensions):
    if extensions is None:
        extensions = []
    if isinstance(extensions, str):
        extensions = [extensions]
    if not isinstance(extensions, list) or not set(extensions).issubset(
            nbrmd.notebook_extensions):
        raise TypeError('Notebook extensions '
                        'should be a subset of {},'
                        'but are {}'.format(str(nbrmd.notebook_extensions),
                                            str(extensions)))
    return extensions


def update_formats(extensions=None):
    """A function that generates a pre_save_hook for the desired extensions"""
    extensions = check_extensions(extensions)

    def pre_save_hook(model, path, contents_manager=None, **kwargs):
        return update_selected_formats(model, path,
                                       contents_manager,
                                       extensions=extensions, **kwargs)

    return pre_save_hook


def update_selected_formats(model, path, contents_manager=None,
                            extensions=None, **kwargs):
    """
    A pre-save hook for jupyter that saves notebooks to multiple files
    with the desired extensions.
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param contents_manager: ContentsManager instance
    :param extensions: list of alternative formats
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

    extensions = check_extensions(extensions)
    extensions = (nb.get('metadata', {}
                         ).get('nbrmd_formats', extensions)
                  or extensions)

    os_path = contents_manager._get_os_path(path) if contents_manager else path
    file, ext = os.path.splitext(path)
    os_file, ext = os.path.splitext(os_path)

    for alt_ext in extensions:
        if ext != alt_ext:
            if contents_manager:
                contents_manager.log.info(
                    u"Saving file at /%s", file + alt_ext)
            nbrmd.writef(nbformat.notebooknode.from_dict(nb),
                         os_file + alt_ext)


update_rmd_and_ipynb = update_formats(['.ipynb', '.Rmd'])
update_ipynb = update_formats('.ipynb')
update_rmd = update_formats('.Rmd')
update_md = update_formats('.md')
update_py = update_formats('.py')
update_py_and_ipynb = update_formats(['.ipynb', '.py'])
update_R = update_formats('.R')
