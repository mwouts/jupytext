"""ContentsManager that allows to open Rmd, py, R and ipynb files as notebooks
"""
import os
from datetime import timedelta
import nbformat
import mock
from tornado.web import HTTPError
from traitlets import Unicode, Float, Bool, Enum
from traitlets.config import Configurable

# import notebook.transutils before notebook.services.contents.filemanager #75
try:
    import notebook.transutils  # noqa
except ImportError:
    pass

from notebook.services.contents.filemanager import FileContentsManager
from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec

import jupytext
from .combine import combine_inputs_with_outputs
from .formats import check_file_version, NOTEBOOK_EXTENSIONS, \
    format_name_for_ext, parse_one_format, parse_formats, transition_to_jupytext_section_in_metadata
from .metadata_filter import metadata_filter_as_dict


def kernelspec_from_language(language):
    """Return the kernel specification for the first kernel with a matching language"""
    try:
        for name in find_kernel_specs():
            kernel_specs = get_kernel_spec(name)
            if kernel_specs.language == language or (language == 'c++' and kernel_specs.language.startswith('C++')):
                return {'name': name, 'language': language, 'display_name': kernel_specs.display_name}
    except (KeyError, ValueError):
        pass
    return None


def _jupytext_writes(ext, format_name):
    def _writes(nbk, version=nbformat.NO_CONVERT, **kwargs):
        return jupytext.writes(nbk, version=version, ext=ext, format_name=format_name, **kwargs)

    return _writes


def _jupytext_reads(ext, format_name, rst2md, freeze_metadata):
    def _reads(text, as_version, **kwargs):
        return jupytext.reads(text, ext=ext, format_name=format_name, rst2md=rst2md,
                              freeze_metadata=freeze_metadata,
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

    expected_format = ("Notebook metadata 'jupytext_formats' should be a list of extension groups, like 'ipynb,Rmd'.\n"
                       "Groups can be separated with colon, for instance: 'ipynb,nb.py;script.ipynb,py'")

    allowed_extension = NOTEBOOK_EXTENSIONS + ['auto']

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
            if not fmt:
                continue
            fmt, _ = parse_one_format(fmt.strip())
            if not any([fmt.endswith(ext) for ext in allowed_extension]):
                raise ValueError('Group extension {} contains {}, which does not end with either {}.\n{}'
                                 .format(str(group), fmt, str(allowed_extension), expected_format))
            if fmt.endswith('.ipynb'):
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
    if file and len(intermediate_ext) <= 4:
        return file, intermediate_ext + ext, ext
    return file + intermediate_ext, ext, ext


class TextFileContentsManager(FileContentsManager, Configurable):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), R Markdown notebooks (.Rmd), Julia (.jl),
    Python (.py) or R scripts (.R)
    """

    nb_extensions = [ext for ext in NOTEBOOK_EXTENSIONS if ext != '.ipynb']
    paired_notebooks = {}

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

    preferred_jupytext_formats_save = Unicode(
        u'',
        help='Preferred format when saving notebooks as text, per extension. '
             'Use "jl:percent,py:percent,R:percent" if you want to save '
             'Julia, Python and R scripts in the double percent format and '
             'only write "jupytext_formats": "py" in the notebook metadata.',
        config=True)

    preferred_jupytext_formats_read = Unicode(
        u'',
        help='Preferred format when reading notebooks from text, per '
             'extension. Use "py:sphinx" if you want to read all python '
             'scripts as Sphinx gallery scripts.',
        config=True)

    default_notebook_metadata_filter = Unicode(
        u'',
        help="Cell metadata that should be save in the text representations. "
             "Examples: 'all', '-all', 'widgets,nteract', 'kernelspec,jupytext-all'",
        config=True)

    default_cell_metadata_filter = Unicode(
        u'',
        help="Notebook metadata that should be saved in the text representations. "
             "Examples: 'all', 'hide_input,hide_output'",
        config=True)

    freeze_metadata = Bool(
        False,
        help='Filter notebook and cell metadata that are not in the text notebook. '
             'Use this to avoid creating a YAML header when editing text files.',
        config=True)

    comment_magics = Enum(
        values=[True, False],
        allow_none=True,
        help='Should Jupyter magic commands be commented out in the text representation?',
        config=True)

    sphinx_convert_rst2md = Bool(
        False,
        help='When opening a Sphinx Gallery script, convert the '
             'reStructuredText to markdown',
        config=True)

    outdated_text_notebook_margin = Float(
        1.0,
        help='Refuse to overwrite inputs of a ipynb notebooks with those of a '
             'text notebook when the text notebook plus margin is older than '
             'the ipynb notebook',
        config=True)

    def replace_auto_ext(self, group, auto_ext):
        """Replace any .auto extension with the given extension, and if none,
        removes that alternative format from the group"""
        result = []
        for fmt in group:
            if not fmt.endswith('.auto'):
                result.append(fmt)
            elif auto_ext:
                result.append(fmt.replace('.auto', auto_ext))
        return result

    def format_group(self, fmt, nbk=None):
        """Return the group of extensions that contains 'fmt'"""
        if nbk:
            transition_to_jupytext_section_in_metadata(nbk.metadata, fmt.endswith('.ipynb'))

        jupytext_formats = ((nbk.metadata.get('jupytext', {}).get('formats') if nbk else None) or
                            self.default_jupytext_formats)

        try:
            jupytext_formats = check_formats(jupytext_formats)
        except ValueError as err:
            raise HTTPError(400, str(err))

        auto_ext = nbk.metadata.get('language_info', {}).get('file_extension') if nbk else None
        if auto_ext == '.r':
            auto_ext = '.R'
        # Find group that contains the current format
        for group in jupytext_formats:
            if auto_ext and fmt.replace(auto_ext, '.auto') in group:
                return self.replace_auto_ext(group, auto_ext)
            if fmt in group:
                return self.replace_auto_ext(group, auto_ext)

        # No such group, but 'ipynb'? Return current fmt + 'ipynb'
        if ['.ipynb'] in jupytext_formats:
            return ['.ipynb', fmt]

        return [fmt]

    def preferred_format(self, ext, preferred):
        """Returns the preferred format for that extension"""
        for fmt_ext, format_name in parse_formats(preferred):
            if fmt_ext == ext:
                return format_name
            if not (ext.endswith('.md') or ext.endswith('.Rmd')):
                if fmt_ext == '.auto':
                    return format_name
                if fmt_ext.endswith('.auto'):
                    base_ext, ext_ext = os.path.splitext(ext)
                    base_fmt, _ = os.path.splitext(fmt_ext)
                    if base_ext == base_fmt and ext_ext:
                        return format_name

        return None

    def drop_paired_notebook(self, path):
        """Remove the current notebook from the list of paired notebooks"""
        if path not in self.paired_notebooks:
            return

        for alt_path in self.paired_notebooks.pop(path):
            if alt_path in self.paired_notebooks:
                self.drop_paired_notebook(alt_path)

    def update_paired_notebooks(self, path, fmt_group):
        """Update the list of paired notebooks to include/update the current pair"""
        if len(fmt_group) <= 1:
            self.drop_paired_notebook(path)
            return

        base_path, fmt, _ = file_fmt_ext(path)
        paths = [base_path + fmt for fmt in fmt_group]
        for alt_path in paths:
            self.drop_paired_notebook(alt_path)

        for alt_path in paths:
            self.paired_notebooks[alt_path] = paths

    def _read_notebook(self, os_path, as_version=4):
        """Read a notebook from an os path."""
        _, fmt, ext = file_fmt_ext(os_path)
        if ext in self.nb_extensions:
            format_name = self.preferred_format(fmt, self.preferred_jupytext_formats_read)
            with mock.patch('nbformat.reads', _jupytext_reads(fmt, format_name,
                                                              self.sphinx_convert_rst2md,
                                                              self.freeze_metadata)):
                return super(TextFileContentsManager, self)._read_notebook(os_path, as_version)
        else:
            return super(TextFileContentsManager, self)._read_notebook(os_path, as_version)

    def set_comment_magics_if_none(self, nb):
        """Set the 'comment_magics' metadata if default is not None"""
        if self.comment_magics is not None and 'comment_magics' not in nb.metadata.get('jupytext', {}):
            nb.metadata.setdefault('jupytext', {})['comment_magics'] = self.comment_magics

    def save(self, model, path=''):
        """Save the file model and return the model with no content."""
        if model['type'] == 'notebook':
            nb = nbformat.from_dict(model['content'])
            _, fmt, _ = file_fmt_ext(path)
            fmt_group = self.format_group(fmt, nb)
            self.update_paired_notebooks(path, fmt_group)

        return super(TextFileContentsManager, self).save(model, path)

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        self.set_comment_magics_if_none(nb)
        os_file, fmt, _ = file_fmt_ext(os_path)
        for alt_fmt in self.format_group(fmt, nb):
            os_path_fmt = os_file + alt_fmt
            self.log.info("Saving %s", os.path.basename(os_path_fmt))
            alt_ext = '.' + alt_fmt.split('.')[-1]

            if alt_ext in self.nb_extensions:
                format_name = format_name_for_ext(nb.metadata, alt_fmt, self.default_jupytext_formats,
                                                  explicit_default=False) or \
                              self.preferred_format(alt_fmt, self.preferred_jupytext_formats_save)
                with mock.patch('nbformat.writes', _jupytext_writes(alt_fmt, format_name)):
                    super(TextFileContentsManager, self)._save_notebook(os_path_fmt, nb)
            else:
                super(TextFileContentsManager, self)._save_notebook(os_path_fmt, nb)

    def get(self, path, content=True, type=None, format=None,
            load_alternative_format=True):
        """ Takes a path for an entity and returns its model"""
        path = path.strip('/')
        nb_file, fmt, ext = file_fmt_ext(path)

        if self.exists(path) and (type == 'notebook' or (type is None and ext in self.all_nb_extensions())):
            model = self._notebook_model(path, content=content)
            if not load_alternative_format:
                return model

            if not content:
                # Modification time of a paired notebook, in this context - Jupyter is checking timestamp
                # before saving - is the most recent among all representations #118
                for alt_path in self.paired_notebooks.get(path, []):
                    if alt_path != path and self.exists(alt_path):
                        alt_model = self._notebook_model(alt_path, content=False)
                        if alt_model['last_modified'] > model['last_modified']:
                            model['last_modified'] = alt_model['last_modified']

                return model

                # Otherwise, the modification time of a notebook is the timestamp of the source - see below.

            if fmt != ext:
                model['name'], _ = os.path.splitext(model['name'])

            source_format = fmt
            outputs_format = fmt
            org_model = model

            fmt_group = self.format_group(fmt, model['content'])
            self.update_paired_notebooks(path, fmt_group)

            # Source format is first non ipynb format found on disk
            if fmt.endswith('.ipynb'):
                for alt_fmt in fmt_group:
                    if not alt_fmt.endswith('.ipynb') and self.exists(nb_file + alt_fmt):
                        source_format = alt_fmt
                        break
            # Outputs taken from ipynb if in group, if file exists
            else:
                for alt_fmt in fmt_group:
                    if alt_fmt.endswith('.ipynb') and self.exists(nb_file + alt_fmt):
                        outputs_format = alt_fmt
                        break

            if source_format != fmt:
                self.log.info(u'Reading SOURCE from {}'.format(os.path.basename(nb_file + source_format)))
                model_outputs = model
                model = self.get(nb_file + source_format, content=content,
                                 type=type, format=format, load_alternative_format=False)
            elif outputs_format != fmt:
                self.log.info(u'Reading OUTPUTS from {}'.format(os.path.basename(nb_file + outputs_format)))
                model_outputs = self.get(nb_file + outputs_format, content=content,
                                         type=type, format=format, load_alternative_format=False)
            else:
                model_outputs = None

            try:
                check_file_version(model['content'], nb_file + source_format, nb_file + outputs_format)
            except ValueError as err:
                raise HTTPError(400, str(err))

            # Make sure we're not overwriting ipynb cells with an outdated
            # text file
            try:
                if model_outputs and model_outputs['last_modified'] > model['last_modified'] + \
                        timedelta(seconds=self.outdated_text_notebook_margin):
                    raise HTTPError(
                        400,
                        '''{out} (last modified {out_last})
                        seems more recent than {src} (last modified {src_last})
                        Please either:
                        - open {src} in a text editor, make sure it is up to date, and save it,
                        - or delete {src} if not up to date,
                        - or increase check margin by adding, say,
                            c.ContentsManager.outdated_text_notebook_margin = 5 # in seconds # or float("inf")
                        to your .jupyter/jupyter_notebook_config.py file
                        '''.format(src=nb_file + source_format,
                                   src_last=model['last_modified'],
                                   out=nb_file + outputs_format,
                                   out_last=model_outputs[
                                       'last_modified']))
            except OverflowError:
                pass

            jupytext_metadata = model['content']['metadata'].get('jupytext', {})
            if self.default_notebook_metadata_filter:
                (jupytext_metadata.setdefault('metadata_filter', {})
                 .setdefault('notebook', self.default_notebook_metadata_filter))
            if self.default_cell_metadata_filter:
                (jupytext_metadata.setdefault('metadata_filter', {})
                 .setdefault('cells', self.default_cell_metadata_filter))

            if jupytext_metadata:
                model['content']['metadata']['jupytext'] = jupytext_metadata

            if model_outputs:
                combine_inputs_with_outputs(model['content'], model_outputs['content'])
            elif not fmt.endswith('.ipynb'):
                nb = model['content']
                language = nb.metadata.get('jupytext', {}).get('main_language', 'python')
                if 'kernelspec' not in nb.metadata and language != 'python':
                    kernelspec = kernelspec_from_language(language)
                    if kernelspec:
                        nb.metadata['kernelspec'] = kernelspec

                self.notary.sign(nb)
                self.mark_trusted_cells(nb, path)

            # Path and name of the notebook is the one of the original path
            model['path'] = org_model['path']
            model['name'] = org_model['name']

            return model

        return super(TextFileContentsManager, self).get(path, content, type, format)

    def trust_notebook(self, path):
        """Trust the current notebook"""
        if path.endswith('.ipynb'):
            super(TextFileContentsManager, self).trust_notebook(path)
        else:
            # Otherwise, we need to read the notebook to determine
            # which extension ends with '.ipynb':
            model = self.get(path)
            file, fmt, _ = file_fmt_ext(path)
            for alt_fmt in self.format_group(fmt, model['content']):
                if alt_fmt.endswith('.ipynb'):
                    super(TextFileContentsManager, self).trust_notebook(file + alt_fmt)

    def rename_file(self, old_path, new_path):
        """Rename the current notebook, as well as its
         alternative representations"""
        old_file, org_fmt, _ = file_fmt_ext(old_path)
        new_file, new_fmt, _ = file_fmt_ext(new_path)

        alt_paths = self.paired_notebooks.get(old_path, [])
        self.drop_paired_notebook(old_path)
        self.drop_paired_notebook(new_path)

        if org_fmt == new_fmt:
            if alt_paths:
                fmt_group = [file_fmt_ext(alt_path)[1] for alt_path in alt_paths]
                self.update_paired_notebooks(new_path, fmt_group)
            else:
                fmt_group = self.format_group(org_fmt)

            for alt_fmt in fmt_group:
                if self.file_exists(old_file + alt_fmt):
                    super(TextFileContentsManager, self).rename_file(old_file + alt_fmt, new_file + alt_fmt)
        else:
            super(TextFileContentsManager, self).rename_file(old_path, new_path)
