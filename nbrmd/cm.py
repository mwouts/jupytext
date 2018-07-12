import notebook.transutils
from notebook.services.contents.filemanager import FileContentsManager
from tornado.web import HTTPError
import hooks
import combine

import os
import nbrmd
import nbformat
import mock


def _nbrmd_writes(ext):
    def _writes(nb, version=nbformat.NO_CONVERT, **kwargs):
        return nbrmd.writes(nb, version=version, ext=ext, **kwargs)

    return _writes


def _nbrmd_reads(ext):
    def _reads(s, as_version, **kwargs):
        return nbrmd.reads(s, as_version, ext=ext, **kwargs)

    return _reads


class RmdFileContentsManager(FileContentsManager):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), or in R Markdown (.Rmd), plain markdown
    (.md), R scripts (.R) or python scripts (.py)
    """

    nb_extensions = [ext for ext in nbrmd.notebook_extensions if
                     ext != '.ipynb']

    def all_nb_extensions(self):
        return ['.ipynb'] + self.nb_extensions

    default_nbrmd_formats = ['.ipynb']

    def __init__(self, **kwargs):
        self.pre_save_hook = hooks.update_alternative_formats
        super(RmdFileContentsManager, self).__init__(**kwargs)

    def _read_notebook(self, os_path, as_version=4):
        """Read a notebook from an os path."""
        file, ext = os.path.splitext(os_path)
        if ext in self.nb_extensions:
            with mock.patch('nbformat.reads', _nbrmd_reads(ext)):
                nb = super(RmdFileContentsManager, self)
        else:
        	nb = super(RmdFileContentsManager, self) \
                ._read_notebook(os_path, as_version)
                
        
        # Read outputs from .ipynb version if available
        if ext != '.ipynb':
            os_path_ipynb = file + '.ipynb'
            try:
                nb_outputs = self._read_notebook(
                    os_path_ipynb, as_version=as_version)
                combine.combine_inputs_with_outputs(nb, nb_outputs)
                if self.notary.check_signature(nb_outputs):
                    self.notary.sign(nb)
            except HTTPError:
                pass

        return nb

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        file, ext = os.path.splitext(os_path)
        if ext in self.nb_extensions:
            with mock.patch('nbformat.writes', _nbrmd_writes(ext)):
                return super(RmdFileContentsManager, self) \
                    ._save_notebook(os_path, nb)
        else:
            return super(RmdFileContentsManager, self) \
                ._save_notebook(os_path, nb)

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model"""
        path = path.strip('/')

        if self.exists(path) and \
                (type == 'notebook' or
                 (type is None and any([path.endswith(ext)
                                        for ext in
                                        self.all_nb_extensions()]))):
            nb = self._notebook_model(path, content=content)

            # Read outputs from .ipynb version if available
            if content and not path.endswith('.ipynb'):
                file, ext = os.path.splitext(path)
                path_ipynb = file + '.ipynb'
                if self.exists(path_ipynb):
                    try:
                        nb_outputs = self._notebook_model(
                            path_ipynb, content=content)
                        combine.combine_inputs_with_outputs(
                            nb['content'],
                            nb_outputs['content'])
                    except HTTPError:
                        pass

            return nb

    def trust_notebook(self, path):
        file, ext = os.path.splitext(path)
        super(RmdFileContentsManager, self).trust_notebook(file + '.ipynb')

    def rename_file(self, old_path, new_path):
        old_file, org_ext = os.path.splitext(old_path)
        new_file, new_ext = os.path.splitext(new_path)
        if org_ext in self.all_nb_extensions() and org_ext == new_ext:
            for ext in self.all_nb_extensions():
                if self.file_exists(old_file + ext):
                    super(RmdFileContentsManager, self) \
                        .rename_file(old_file + ext, new_file + ext)
        else:
            super(RmdFileContentsManager, self).rename_file(old_path, new_path)
