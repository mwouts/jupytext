"""ContentsManager that allows to open Rmd, py, R and ipynb files as notebooks
"""
import os
import nbformat
import mock
from tornado.web import HTTPError
from traitlets import Unicode
from traitlets.config import Configurable

from notebook.services.contents.filemanager import FileContentsManager

try:
    import notebook.transutils  # noqa
except ImportError:
    pass

import jupytext
from . import combine
from .file_format_version import check_file_version

try:
    unicode  # Python 2
except NameError:
    unicode = str  # Python 3


def _jupytext_writes(ext):
    def _writes(nbk, version=nbformat.NO_CONVERT, **kwargs):
        return jupytext.writes(nbk, version=version, ext=ext, **kwargs)

    return _writes


def _jupytext_reads(ext):
    def _reads(text, as_version, **kwargs):
        return jupytext.reads(text, ext, as_version, **kwargs)

    return _reads


def check_formats(formats):
    """
    Parse, validate and return notebooks extensions
    :param formats: a list of lists of notebook extensions,
    or a colon separated string of extension groups, comma separated
    :return: list of lists (groups) of notebook extensions
    """

    # Parse formats represented as strings
    if not isinstance(formats, list):
        formats = [group.split(',') for group in formats.split(';')]

    expected_format = ("Notebook metadata 'jupytext_formats' should "
                       "be a list of extension groups, like 'ipynb,Rmd'.\n"
                       "Groups can be separated with colon, for instance: "
                       "'ipynb,nb.py;script.ipynb,py'")

    validated_formats = []
    for group in formats:
        if not isinstance(group, list):
            # In early versions (0.4 and below), formats could be a list of
            # extensions. We understand this as a single group
            return check_formats([formats])
        validated_group = []
        for fmt in group:
            if not isinstance(fmt, unicode):
                raise ValueError('Extensions should be strings among {}'
                                 ', not {}.\n{}'
                                 .format(str(jupytext.NOTEBOOK_EXTENSIONS),
                                         str(fmt),
                                         expected_format))
            if fmt == '':
                continue
            if not fmt.startswith('.'):
                fmt = '.' + fmt
            if not any([fmt.endswith(ext)
                        for ext in jupytext.NOTEBOOK_EXTENSIONS]):
                raise ValueError('Group extension {} contains {}, '
                                 'which does not end with either {}.\n{}'
                                 .format(str(group), fmt,
                                         str(jupytext.NOTEBOOK_EXTENSIONS),
                                         expected_format))
            validated_group.append(fmt)

        if validated_group:
            validated_formats.append(validated_group)

    return validated_formats


def file_fmt_ext(path):
    """
    Return file name, format (possibly .nb.py) and extension (.py)
    """
    file, ext = os.path.splitext(path)
    file, intermediate_ext = os.path.splitext(file)
    return file, intermediate_ext + ext, ext


class TextFileContentsManager(FileContentsManager, Configurable):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), R Markdown notebooks (.Rmd), Julia (.jl),
    Python (.py) or R scripts (.R)
    """

    nb_extensions = [ext for ext in jupytext.NOTEBOOK_EXTENSIONS if
                     ext != '.ipynb']

    def all_nb_extensions(self):
        """
        Notebook extensions, including ipynb
        :return:
        """
        return ['.ipynb'] + self.nb_extensions

    default_jupytext_formats = Unicode(
        u'',
        help='Save notebooks to these file extensions. '
             'Can be any of ipynb,Rmd,md,jl,py,R,nb.jl,nb.py,nb.R '
             'comma separated',
        config=True)

    def format_group(self, fmt, nbk=None):
        """Return the group of extensions that contains 'fmt'"""
        jupytext_formats = ((nbk.metadata.get('jupytext_formats')
                             if nbk else None) or
                            self.default_jupytext_formats)

        try:
            jupytext_formats = check_formats(jupytext_formats)
        except ValueError as err:
            raise HTTPError(400, str(err))

        # Find group that contains the current format
        for group in jupytext_formats:
            if fmt in group:
                return group

        if ['.ipynb'] in jupytext_formats:
            return [fmt, '.ipynb']

        return [fmt]

    def _read_notebook(self, os_path, as_version=4,
                       load_alternative_format=True):
        """Read a notebook from an os path."""
        file, fmt, ext = file_fmt_ext(os_path)
        if ext in self.nb_extensions:
            with mock.patch('nbformat.reads', _jupytext_reads(ext)):
                nbk = super(TextFileContentsManager, self) \
                    ._read_notebook(os_path, as_version)
        else:
            nbk = super(TextFileContentsManager, self) \
                ._read_notebook(os_path, as_version)

        if not load_alternative_format:
            return nbk

        fmt_group = self.format_group(fmt, nbk)

        source_format = fmt
        outputs_format = fmt

        # Source format is first non ipynb format found on disk
        if fmt.endswith('.ipynb'):
            for alt_fmt in fmt_group:
                if not alt_fmt.endswith('.ipynb') and \
                        os.path.isfile(file + alt_fmt):
                    source_format = alt_fmt
                    break
        # Outputs taken from ipynb if in group, if file exists
        else:
            for alt_fmt in fmt_group:
                if alt_fmt.endswith('.ipynb') and \
                        os.path.isfile(file + alt_fmt):
                    outputs_format = alt_fmt
                    break

        if source_format != fmt:
            self.log.info(u'Reading SOURCE from {}'
                          .format(os.path.basename(file + source_format)))
            nb_outputs = nbk
            nbk = self._read_notebook(file + source_format,
                                      as_version=as_version,
                                      load_alternative_format=False)
        elif outputs_format != fmt:
            self.log.info(u'Reading OUTPUTS from {}'
                          .format(os.path.basename(file + outputs_format)))
            if outputs_format != fmt:
                nb_outputs = self._read_notebook(file + outputs_format,
                                                 as_version=as_version,
                                                 load_alternative_format=False)
        else:
            nb_outputs = None

        try:
            check_file_version(nbk, file + source_format,
                               file + outputs_format)
        except ValueError as err:
            raise HTTPError(400, str(err))

        if nb_outputs:
            combine.combine_inputs_with_outputs(nbk, nb_outputs)
            if self.notary.check_signature(nb_outputs):
                self.notary.sign(nbk)
        elif not fmt.endswith('.ipynb'):
            self.notary.sign(nbk)

        return nbk

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        os_file, fmt, _ = file_fmt_ext(os_path)
        for alt_fmt in self.format_group(fmt, nb):
            os_path_fmt = os_file + alt_fmt
            self.log.info("Saving %s", os.path.basename(os_path_fmt))
            alt_ext = '.' + alt_fmt.split('.')[-1]
            if alt_ext in self.nb_extensions:
                with mock.patch('nbformat.writes', _jupytext_writes(alt_ext)):
                    super(TextFileContentsManager, self) \
                        ._save_notebook(os_path_fmt, nb)
            else:
                super(TextFileContentsManager, self) \
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

        return super(TextFileContentsManager, self) \
            .get(path, content, type, format)

    def trust_notebook(self, path):
        """Trust the current notebook"""
        file, fmt, _ = file_fmt_ext(path)
        for alt_fmt in self.format_group(fmt):
            if alt_fmt.endswith('.ipynb'):
                super(TextFileContentsManager, self) \
                    .trust_notebook(file + alt_fmt)

    def rename_file(self, old_path, new_path):
        """Rename the current notebook, as well as its
         alternative representations"""
        old_file, org_fmt, _ = file_fmt_ext(old_path)
        new_file, new_fmt, _ = file_fmt_ext(new_path)

        if org_fmt == new_fmt:
            for alt_fmt in self.format_group(org_fmt):
                if self.file_exists(old_file + alt_fmt):
                    super(TextFileContentsManager, self) \
                        .rename_file(old_file + alt_fmt, new_file + alt_fmt)
        else:
            super(TextFileContentsManager, self) \
                .rename_file(old_path, new_path)
