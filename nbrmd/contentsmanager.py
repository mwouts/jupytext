import notebook.transutils
from notebook.services.contents.filemanager import FileContentsManager
from tornado.web import HTTPError

import os
import nbrmd
import nbformat
import mock

from . import combine


def _nbrmd_writes(ext):
    def _writes(nb, version=nbformat.NO_CONVERT, **kwargs):
        return nbrmd.writes(nb, version=version, ext=ext, **kwargs)

    return _writes


def _nbrmd_reads(ext):
    def _reads(s, as_version, **kwargs):
        return nbrmd.reads(s, as_version, ext=ext, **kwargs)

    return _reads


def check_formats(formats):
    allowed = nbrmd.notebook_extensions
    if not isinstance(formats, list) or not set(formats).issubset(allowed):
        raise TypeError(u"Notebook metadata 'nbrmd_formats' "
                        u"should be subset of {}".format(str(allowed)))
    return formats


class RmdFileContentsManager(FileContentsManager):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), R Markdown notebooks (.Rmd),
    R scripts (.R) and python scripts (.py)
    """

    nb_extensions = [ext for ext in nbrmd.notebook_extensions if
                     ext != '.ipynb']

    def all_nb_extensions(self):
        return ['.ipynb'] + self.nb_extensions

    default_nbrmd_formats = ['.ipynb']
    default_nbrmd_sourceonly_format = None

    def _read_notebook(self, os_path, as_version=4,
                       load_alternative_format=True):
        """Read a notebook from an os path."""
        file, ext = os.path.splitext(os_path)
        if ext in self.nb_extensions:
            with mock.patch('nbformat.reads', _nbrmd_reads(ext)):
                nb = super(RmdFileContentsManager, self) \
                    ._read_notebook(os_path, as_version)
        else:
            nb = super(RmdFileContentsManager, self) \
                ._read_notebook(os_path, as_version)

        if not load_alternative_format:
            return nb

        # Notebook formats: default, notebook metadata, or current extension
        nbrmd_formats = (nb.metadata.get('nbrmd_formats') or
                         self.default_nbrmd_formats)

        if ext not in nbrmd_formats:
            nbrmd_formats.append(ext)

        nbrmd_formats = check_formats(nbrmd_formats)

        # Source format is taken in metadata, contentsmanager, or is current
        # ext, or is first non .ipynb format that is found on disk
        source_format = (nb.metadata.get('nbrmd_sourceonly_format') or
                         self.default_nbrmd_sourceonly_format)

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
            self.log.info('Reading SOURCE from {}'
                          .format(os.path.basename(file + source_format)))
            self.log.info('Reading OUTPUTS from {}'
                          .format(os.path.basename(os_path)))
            nb_outputs = nb
            nb = self._read_notebook(file + source_format,
                                     as_version=as_version,
                                     load_alternative_format=False)
        elif ext != '.ipynb' and '.ipynb' in nbrmd_formats \
                and os.path.isfile(file + '.ipynb'):
            self.log.info('Reading SOURCE from {}'
                          .format(os.path.basename(os_path)))
            self.log.info('Reading OUTPUTS from {}'
                          .format(os.path.basename(file + '.ipynb')))
            nb_outputs = self._read_notebook(file + '.ipynb',
                                             as_version=as_version,
                                             load_alternative_format=False)

        if nb_outputs is not None:
            combine.combine_inputs_with_outputs(nb, nb_outputs)
            if self.notary.check_signature(nb_outputs):
                self.notary.sign(nb)

        return nb

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        os_file, org_ext = os.path.splitext(os_path)

        formats = (nb.get('metadata', {}).get('nbrmd_formats') or
                   self.default_nbrmd_formats)

        if org_ext not in formats:
            formats.append(org_ext)

        formats = check_formats(formats)

        for ext in formats:
            os_path_ext = os_file + ext
            self.log.info("Saving %s", os.path.basename(os_path_ext))
            if ext in self.nb_extensions:
                with mock.patch('nbformat.writes', _nbrmd_writes(ext)):
                    super(RmdFileContentsManager, self) \
                        ._save_notebook(os_path_ext, nb)
            else:
                super(RmdFileContentsManager, self) \
                    ._save_notebook(os_path_ext, nb)

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model"""
        path = path.strip('/')

        if self.exists(path) and \
                (type == 'notebook' or
                 (type is None and
                  any([path.endswith(ext)
                       for ext in self.all_nb_extensions()]))):
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
        if org_ext in self.all_nb_extensions() and org_ext == new_ext:
            for ext in self.all_nb_extensions():
                if self.file_exists(old_file + ext):
                    super(RmdFileContentsManager, self) \
                        .rename_file(old_file + ext, new_file + ext)
        else:
            super(RmdFileContentsManager, self).rename_file(old_path, new_path)
