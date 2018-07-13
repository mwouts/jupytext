import notebook.transutils
from notebook.services.contents.filemanager import FileContentsManager
from tornado.web import HTTPError

import os
import nbrmd
import nbformat
import mock

from . import combine


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

    if isinstance(contents_manager, RmdFileContentsManager):
        formats = contents_manager.default_nbrmd_formats
    else:
        formats = ['.ipynb']

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


def _nbrmd_writes(nb, version=nbformat.NO_CONVERT, **kwargs):
    return nbrmd.writes(nb, **kwargs)


def _nbrmd_reads(s, as_version, **kwargs):
    return nbrmd.reads(s, **kwargs)


def _nbrmd_md_writes(nb, version=nbformat.NO_CONVERT, **kwargs):
    return nbrmd.nbrmd.md_writes(nb, **kwargs)


def _nbrmd_md_reads(s, as_version, **kwargs):
    return nbrmd.nbrmd.md_reads(s, **kwargs)


class RmdFileContentsManager(FileContentsManager):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), or in R Markdown format (.Rmd),
    or in plain Markdown format (.md)
    """
    nb_extensions = ['.ipynb', '.Rmd', '.md']
    default_nbrmd_formats = ['.ipynb']
    default_nbrmd_sourceonly_format = None

    def __init__(self, **kwargs):
        self.pre_save_hook = update_alternative_formats
        super(RmdFileContentsManager, self).__init__(**kwargs)

    def _read_notebook(self, os_path, as_version=4,
                       load_alternative_format=True):
        """Read a notebook from an os path."""
        file, ext = os.path.splitext(os_path)
        if ext == '.Rmd':
            with mock.patch('nbformat.reads', _nbrmd_reads):
                nb = super(RmdFileContentsManager, self) \
                    ._read_notebook(os_path, as_version)
        elif ext == '.md':
            with mock.patch('nbformat.reads', _nbrmd_md_reads):
                nb = super(RmdFileContentsManager, self) \
                    ._read_notebook(os_path, as_version)
        else:  # ext == '.ipynb':
            nb = super(RmdFileContentsManager, self) \
                ._read_notebook(os_path, as_version)

        if not load_alternative_format:
            return nb

        # Notebook formats: default, notebook metadata, or current extension
        nbrmd_formats = nb.metadata.get('nbrmd_formats') or \
                        self.default_nbrmd_formats

        if ext not in nbrmd_formats:
            nbrmd_formats.append(ext)

        # Source format is taken in metadata, contentsmanager, or is current
        # ext, or is first non .ipynb format that is found on disk
        source_format = nb.metadata.get('nbrmd_sourceonly_format') or \
                        self.default_nbrmd_sourceonly_format

        if source_format is None:
            if ext != '.ipynb':
                source_format = ext
            else:
                for fmt in nbrmd_formats:
                    if fmt != '.ipynb' and os.path.isfile(file + fmt):
                        source_format = fmt
                        break

        nb_outputs = None
        if source_format is not None and ext != source_format:
            self.log.info('Reading source from {} and outputs from {}' \
                          .format(file + source_format, os_path))
            nb_outputs = nb
            nb = self._read_notebook(file + source_format,
                                     as_version=as_version,
                                     load_alternative_format=False)
        elif ext != '.ipynb' and '.ipynb' in nbrmd_formats \
                and os.path.isfile(file + '.ipynb'):
            self.log.info('Reading source from {} and outputs from {}' \
                          .format(os_path, file + '.ipynb'))
            nb_outputs = self._read_notebook(file + '.ipynb',
                                             as_version=as_version,
                                             load_alternative_format=False)

        # We store in the metadata the alternative and sourceonly formats
        trusted = self.notary.check_signature(nb)
        nb.metadata['nbrmd_formats'] = nbrmd_formats
        nb.metadata['nbrmd_sourceonly_format'] = source_format

        if nb_outputs is not None:
            combine.combine_inputs_with_outputs(nb, nb_outputs)
            trusted = self.notary.check_signature(nb_outputs)

        if trusted:
            self.notary.sign(nb)

        return nb

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        file, ext = os.path.splitext(os_path)
        if ext == '.Rmd':
            with mock.patch('nbformat.writes', _nbrmd_writes):
                return super(RmdFileContentsManager, self) \
                    ._save_notebook(os_path, nb)
        elif ext == '.md':
            with mock.patch('nbformat.writes', _nbrmd_md_writes):
                return super(RmdFileContentsManager, self) \
                    ._save_notebook(os_path, nb)
        else:
            return super(RmdFileContentsManager, self) \
                ._save_notebook(os_path, nb)

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model

        Parameters
        ----------
        path : str
            the API path that describes the relative path for the target
        content : bool
            Whether to include the contents in the reply
        type : str, optional
            The requested type - 'file', 'notebook', or 'directory'.
            Will raise HTTPError 400 if the content doesn't match.
        format : str, optional
            The requested format for file contents. 'text' or 'base64'.
            Ignored if this returns a notebook or directory model.

        Returns
        -------
        model : dict
            the contents model. If content=True, returns the contents
            of the file or directory as well.
        """
        path = path.strip('/')

        if self.exists(path) and \
                (type == 'notebook' or
                 (type is None and
                  any([path.endswith(ext) for ext in self.nb_extensions]))):
            return self._notebook_model(path, content=content)
        else:
            return super(RmdFileContentsManager, self) \
                .get(path, content, type, format)

    def trust_notebook(self, path):
        file, ext = os.path.splitext(path)
        super(RmdFileContentsManager, self).trust_notebook(file + '.ipynb')

    def rename_file(self, old_path, new_path):
        old_file, org_ext = os.path.splitext(old_path)
        new_file, new_ext = os.path.splitext(new_path)
        if org_ext in self.nb_extensions and org_ext == new_ext:
            for ext in self.nb_extensions:
                if self.file_exists(old_file + ext):
                    super(RmdFileContentsManager, self) \
                        .rename_file(old_file + ext, new_file + ext)
        else:
            super(RmdFileContentsManager, self).rename_file(old_path, new_path)
