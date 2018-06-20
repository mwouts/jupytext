from notebook.services.contents.filemanager import FileContentsManager

import os
import nbrmd
import nbformat

_nbformat_writes = nbformat.writes
_nbformat_reads = nbformat.reads


def _nbrmd_writes(nb, version=nbformat.NO_CONVERT, **kwargs):
    return nbrmd.writes(nb, **kwargs)


def _nbrmd_reads(s, as_version, **kwargs):
    return nbrmd.reads(s, **kwargs)


class RmdFileContentsManager(FileContentsManager):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), or in Rmarkdown format (.Rmd), in either .Rmd or .md files
    """
    nb_extensions = ['.ipynb', '.Rmd', '.md']

    def _read_notebook(self, os_path, as_version=4):
        """Read a notebook from an os path."""
        nbformat.reads = _nbformat_reads if os_path.endswith('.ipynb') else _nbrmd_reads
        return super()._read_notebook(os_path, as_version)

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        nbformat.writes = _nbformat_writes if os_path.endswith('.ipynb') else _nbrmd_writes
        return super()._save_notebook(os_path, nb)

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
            return super().get(path, content, type, format)

    def rename_file(self, old_path, new_path):
        old_file, org_ext = os.path.splitext(old_path)
        new_file, new_ext = os.path.splitext(new_path)
        if org_ext in self.nb_extensions and org_ext == new_ext:
            for ext in self.nb_extensions:
                if self.file_exists(old_file + ext):
                    super().rename_file(old_file + ext, new_file + ext)
        else:
            super().rename_file(old_path, new_path)
