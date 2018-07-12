import os
import nbrmd
import nbformat
import cm


def update_alternative_formats(model, path, contents_manager=None, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks
    under the alternative form. Target extensions are taken from
    notebook metadata 'nbrmd_formats', or when not available,
    from  contents_manager.default_nbrmd_formats
    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param contents_manager: ContentsManager instance
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

    formats = contents_manager.default_nbrmd_formats \
        if isinstance(contents_manager, cm.RmdFileContentsManager) else ['.ipynb']
    formats = nb.get('metadata', {}).get('nbrmd_formats', formats)
    if not isinstance(formats, list) or not set(formats).issubset(
            ['.Rmd', '.md', '.ipynb']):
        raise TypeError(u"Notebook metadata 'nbrmd_formats' "
                        u"should be subset of ['.Rmd', '.md', '.ipynb']")

    os_path = contents_manager._get_os_path(path) if contents_manager else path
    file, ext = os.path.splitext(path)
    os_file, ext = os.path.splitext(os_path)

    for alt_ext in formats:
        if ext != alt_ext:
            if contents_manager:
                contents_manager.log.info(
                    u"Saving file at /%s", file + alt_ext)
            nbrmd.writef(nbformat.notebooknode.from_dict(nb),
                         os_file + alt_ext)
