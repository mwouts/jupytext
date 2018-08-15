"""ContentsManager that allows to open Rmd, py, R and ipynb files as notebooks
"""
import os
import nbformat
import mock

try:
    import notebook.transutils  # noqa
except ImportError:
    pass
from notebook.services.contents.filemanager import FileContentsManager
from traitlets import Unicode
from traitlets.config import Configurable
import nbrmd

from . import combine


def _nbrmd_writes(ext):
    def _writes(nb, version=nbformat.NO_CONVERT, **kwargs):
        return nbrmd.writes(nb, version=version, ext=ext, **kwargs)

    return _writes


def _nbrmd_reads(ext):
    def _reads(text, as_version, **kwargs):
        return nbrmd.reads(text, as_version, ext=ext, **kwargs)

    return _reads


def check_formats(formats):
    """
    Parse, validate and return notebooks extensions
    :param formats: a list of notebook extensions, or a comma separated string
    :return: list of extensions
    """
    if not isinstance(formats, list):
        formats = formats.split(',')

    formats = [fmt if fmt.startswith('.') else '.' + fmt
               for fmt in formats if fmt != '']

    allowed = nbrmd.NOTEBOOK_EXTENSIONS + ['.nb.py', '.nb.R']
    if not isinstance(formats, list) or not set(formats).issubset(allowed):
        raise TypeError("Notebook metadata 'nbrmd_formats' "
                        "should be subset of {}, but was {}"
                        "".format(str(allowed), str(formats)))
    return formats


def file_fmt_ext(path):
    """
    Return file name, format (possibly .nb.py) and extension (.py)
    """
    file, ext = os.path.splitext(path)
    for fmt in ['.nb.py', '.nb.R']:
        if path.endswith(fmt):
            return path[:-len(fmt)], fmt, ext

    return file, ext, ext


class RmdFileContentsManager(FileContentsManager, Configurable):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), R Markdown notebooks (.Rmd),
    R scripts (.R) and python scripts (.py)
    """

    nb_extensions = [ext for ext in nbrmd.NOTEBOOK_EXTENSIONS if
                     ext != '.ipynb']

    def all_nb_extensions(self):
        """
        Notebook extensions, including ipynb
        :return:
        """
        return ['.ipynb'] + self.nb_extensions

    default_nbrmd_formats = Unicode(
        u'ipynb',
        help='Save notebooks to these file extensions. '
             'Can be any of ipynb,Rmd,py,R,nb.py,nb.R comma separated',
        config=True)

    def _read_notebook(self, os_path, as_version=4,
                       load_alternative_format=True):
        """Read a notebook from an os path."""
        file, fmt, ext = file_fmt_ext(os_path)
        if ext in self.nb_extensions:
            with mock.patch('nbformat.reads', _nbrmd_reads(ext)):
                nb = super(RmdFileContentsManager, self) \
                    ._read_notebook(os_path, as_version)
        else:
            nb = super(RmdFileContentsManager, self) \
                ._read_notebook(os_path, as_version)

        if not load_alternative_format:
            return nb

        ext = fmt

        # Notebook formats: default, notebook metadata, or current extension
        nbrmd_formats = (nb.metadata.get('nbrmd_formats') or
                         self.default_nbrmd_formats)

        nbrmd_formats = check_formats(nbrmd_formats)

        if ext not in nbrmd_formats:
            nbrmd_formats.append(ext)

        nbrmd_formats = check_formats(nbrmd_formats)

        # Source format is current ext, or is first non .ipynb format
        # that is found on disk
        source_format = None
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
        os_file, org_fmt, org_ext = file_fmt_ext(os_path)

        formats = (nb.get('metadata', {}).get('nbrmd_formats') or
                   self.default_nbrmd_formats)

        formats = check_formats(formats)

        if org_fmt not in formats:
            formats.append(org_fmt)

        formats = check_formats(formats)

        for fmt in formats:
            os_path_fmt = os_file + fmt
            self.log.info("Saving %s", os.path.basename(os_path_fmt))
            ext = fmt.replace('.nb.', '.')
            if ext in self.nb_extensions:
                with mock.patch('nbformat.writes', _nbrmd_writes(ext)):
                    super(RmdFileContentsManager, self) \
                        ._save_notebook(os_path_fmt, nb)
            else:
                super(RmdFileContentsManager, self) \
                    ._save_notebook(os_path_fmt, nb)

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model"""
        path = path.strip('/')

        if self.exists(path) and \
                (type == 'notebook' or
                 (type is None and
                  any([path.endswith(ext)
                       for ext in self.all_nb_extensions()]))):
            return self._notebook_model(path, content=content)

        return super(RmdFileContentsManager, self) \
            .get(path, content, type, format)

    def trust_notebook(self, path):
        """Trust the current notebook"""
        file, _ = os.path.splitext(path)
        super(RmdFileContentsManager, self).trust_notebook(file + '.ipynb')

    def rename_file(self, old_path, new_path):
        """Rename the current notebook, as well as its
         alternative representations"""
        old_file, org_fmt, org_ext = file_fmt_ext(old_path)
        new_file, new_fmt, new_ext = file_fmt_ext(new_path)
        if org_ext in self.all_nb_extensions() and org_ext == new_ext:
            for fmt in self.all_nb_extensions() + ['.nb.py', '.nb.R']:
                if self.file_exists(old_file + fmt):
                    super(RmdFileContentsManager, self) \
                        .rename_file(old_file + fmt, new_file + fmt)
        else:
            super(RmdFileContentsManager, self).rename_file(old_path, new_path)
