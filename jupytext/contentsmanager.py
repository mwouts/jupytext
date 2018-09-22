"""ContentsManager that allows to open Rmd, py, R and ipynb files as notebooks
"""
import os
from datetime import timedelta
import nbformat
import mock
from tornado.web import HTTPError
from traitlets import Unicode, Float, Bool
from traitlets.config import Configurable

# import notebook.transutils before notebook.services.contents.filemanager #75
try:
    import notebook.transutils  # noqa
except ImportError:
    pass

from notebook.services.contents.filemanager import FileContentsManager

import jupytext
from .combine import combine_inputs_with_outputs
from .formats import check_file_version, NOTEBOOK_EXTENSIONS, \
    format_name_for_ext, parse_one_format, parse_formats


def _jupytext_writes(ext, format_name):
    def _writes(nbk, version=nbformat.NO_CONVERT, **kwargs):
        return jupytext.writes(nbk, version=version, ext=ext,
                               format_name=format_name, **kwargs)

    return _writes


def _jupytext_reads(ext, rst2md):
    def _reads(text, as_version, **kwargs):
        return jupytext.reads(text, ext=ext, rst2md=rst2md,
                              as_version=as_version, **kwargs)

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

        # Return ipynb on first position (save that file first, for #63)
        has_ipynb = False
        validated_group = []
        for fmt in group:
            try:
                fmt = u'' + fmt
            except UnicodeDecodeError:
                raise ValueError('Extensions should be strings among {}'
                                 ', not {}.\n{}'
                                 .format(str(formats.NOTEBOOK_EXTENSIONS),
                                         str(fmt),
                                         expected_format))
            if fmt == '':
                continue
            fmt, _ = parse_one_format(fmt)
            if not any([fmt.endswith(ext)
                        for ext in NOTEBOOK_EXTENSIONS]):
                raise ValueError('Group extension {} contains {}, '
                                 'which does not end with either {}.\n{}'
                                 .format(str(group), fmt,
                                         str(NOTEBOOK_EXTENSIONS),
                                         expected_format))
            if fmt == '.ipynb':
                has_ipynb = True
            else:
                validated_group.append(fmt)

        if has_ipynb:
            validated_group = ['.ipynb'] + validated_group

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

    nb_extensions = [ext for ext in NOTEBOOK_EXTENSIONS if ext != '.ipynb']

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
             'comma separated. If you want another format than the '
             'default one, append the format name to the extension, '
             'e.g. ipynb,py:percent to save the notebook to '
             'hydrogen/spyder/vscode compatible scripts',
        config=True)

    preferred_jupytext_formats = Unicode(
        u'',
        help='Preferred format when saving notebooks as text, per extension. '
             'Use "jl:percent,py:percent,R:percent" if you want to save '
             'Julia, Python and R scripts in the double percent format and '
             'only write "jupytext_formats": "py" in the notebook metadata.',
        config=True)

    sphinx_convert_rst2md = Bool(
        False,
        help='When opening a Sphinx Gallery script, convert the '
             'reStructuredText to markdown',
        config=True)

    outdated_text_notebook_margin = Float(
        1.0,
        help='Refuse to overwrite inputs of a ipynb notebooks with those of a'
             'text notebook when the text notebook plus margin is older than'
             'the ipynb notebook',
        config=True)

    def format_group(self, fmt, nbk=None):
        """Return the group of extensions that contains 'fmt'"""
        # Backward compatibility with nbrmd
        for key in ['nbrmd_formats', 'nbrmd_format_version']:
            if nbk and key in nbk.metadata:
                nbk.metadata[key.replace('nbrmd', 'jupytext')] = \
                    nbk.metadata.pop(key)

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

        # No such group, but 'ipynb'? Return current fmt + 'ipynb'
        if ['.ipynb'] in jupytext_formats:
            return ['.ipynb', fmt]

        return [fmt]

    def preferred_format(self, ext):
        """Returns the preferred format for that extension"""
        for fmt_ext, format_name in \
                parse_formats(self.preferred_jupytext_formats):
            if fmt_ext == ext:
                return format_name
        return None

    def _read_notebook(self, os_path, as_version=4):
        """Read a notebook from an os path."""
        _, ext = os.path.splitext(os_path)
        if ext in self.nb_extensions:
            with mock.patch('nbformat.reads',
                            _jupytext_reads(ext, self.sphinx_convert_rst2md)):
                return super(TextFileContentsManager, self) \
                    ._read_notebook(os_path, as_version)
        else:
            return super(TextFileContentsManager, self) \
                ._read_notebook(os_path, as_version)

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        os_file, fmt, _ = file_fmt_ext(os_path)
        for alt_fmt in self.format_group(fmt, nb):
            os_path_fmt = os_file + alt_fmt
            self.log.info("Saving %s", os.path.basename(os_path_fmt))
            alt_ext = '.' + alt_fmt.split('.')[-1]

            if alt_ext in self.nb_extensions:
                format_name = format_name_for_ext(nb.metadata, alt_ext) or \
                              self.preferred_format(alt_ext)
                with mock.patch('nbformat.writes',
                                _jupytext_writes(alt_ext, format_name)):
                    super(TextFileContentsManager, self) \
                        ._save_notebook(os_path_fmt, nb)
            else:
                super(TextFileContentsManager, self) \
                    ._save_notebook(os_path_fmt, nb)

    def get(self, path, content=True, type=None, format=None,
            load_alternative_format=True):
        """ Takes a path for an entity and returns its model"""
        path = path.strip('/')
        nb_file, fmt, ext = file_fmt_ext(path)

        if self.exists(path) and \
                (type == 'notebook' or
                 (type is None and ext in self.all_nb_extensions())):
            model = self._notebook_model(path, content=content)
            if not content:
                return model

            if not load_alternative_format:
                return model

            fmt_group = self.format_group(fmt, model['content'])

            source_format = fmt
            outputs_format = fmt

            # Source format is first non ipynb format found on disk
            if fmt.endswith('.ipynb'):
                for alt_fmt in fmt_group:
                    if not alt_fmt.endswith('.ipynb') and \
                            self.exists(nb_file + alt_fmt):
                        source_format = alt_fmt
                        break
            # Outputs taken from ipynb if in group, if file exists
            else:
                for alt_fmt in fmt_group:
                    if alt_fmt.endswith('.ipynb') and \
                            self.exists(nb_file + alt_fmt):
                        outputs_format = alt_fmt
                        break

            if source_format == outputs_format:
                return model

            if source_format != fmt:
                self.log.info(u'Reading SOURCE from {}'.format(
                    os.path.basename(nb_file + source_format)))
                model_outputs = model
                model = self.get(nb_file + source_format, content=content,
                                 type=type, format=format,
                                 load_alternative_format=False)
            elif outputs_format != fmt:
                self.log.info(u'Reading OUTPUTS from {}'.format(
                    os.path.basename(nb_file + outputs_format)))
                model_outputs = self.get(nb_file + outputs_format,
                                         content=content,
                                         type=type, format=format,
                                         load_alternative_format=False)

            try:
                check_file_version(model['content'],
                                   nb_file + source_format,
                                   nb_file + outputs_format)
            except ValueError as err:
                raise HTTPError(400, str(err))

            # Make sure we're not overwriting ipynb cells with an outdated
            # text file
            try:
                if model_outputs and model_outputs['last_modified'] > \
                        model['last_modified'] + \
                        timedelta(seconds=self.outdated_text_notebook_margin):
                    raise HTTPError(
                        400,
                        u'\n'
                        '{out} (last modified {out_last})\n'
                        'seems more recent than '
                        '{src} (last modified {src_last})\n'
                        'Please either:\n'
                        '- open {src} in a text editor, make sure it is '
                        'up to date, and save it,\n'
                        '- or delete {src} if not up to date,\n'
                        '- or increase check margin by adding, say, \n'
                        '    c.ContentsManager.'
                        'outdated_text_notebook_margin = 5 '
                        '# in seconds # or float("inf")\n'
                        'to your .jupyter/jupyter_notebook_config.py '
                        'file\n'.format(src=nb_file + source_format,
                                        src_last=model['last_modified'],
                                        out=nb_file + outputs_format,
                                        out_last=model_outputs[
                                            'last_modified']))
            except OverflowError:
                pass

            if model_outputs:
                combine_inputs_with_outputs(model['content'],
                                            model_outputs['content'])
            elif not fmt.endswith('.ipynb'):
                self.notary.sign(model['content'])
                self.mark_trusted_cells(model['content'], path)

            return model

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
