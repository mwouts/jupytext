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
from .formats import rearrange_jupytext_metadata, check_file_version, set_auto_ext
from .formats import NOTEBOOK_EXTENSIONS, JupytextFormatError, long_form_one_format, long_form_multiple_formats
from .paired_paths import paired_paths, find_base_path_and_format, base_path, full_path, InconsistentPath


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


def preferred_format(incomplete_format, preferred_formats):
    """Return the preferred format for the given extension"""
    incomplete_format = long_form_one_format(incomplete_format)
    if 'format_name' in incomplete_format:
        return incomplete_format

    for fmt in long_form_multiple_formats(preferred_formats):
        if ((incomplete_format['extension'] == fmt['extension'] or (
                fmt['extension'] == '.auto' and
                incomplete_format['extension'] not in ['.md', '.Rmd', '.ipynb'])) and
                incomplete_format.get('suffix') == fmt.get('suffix') and
                incomplete_format.get('prefix') == fmt.get('prefix')):
            fmt.update(incomplete_format)
            return fmt

    return incomplete_format


def _jupytext_writes(fmt):
    def _writes(nbk, version=nbformat.NO_CONVERT, **kwargs):
        return jupytext.writes(nbk, fmt, version=version, **kwargs)

    return _writes


def _jupytext_reads(fmt):
    def _reads(text, as_version, **kwargs):
        return jupytext.reads(text, fmt, as_version=as_version, **kwargs)

    return _reads


class TextFileContentsManager(FileContentsManager, Configurable):
    """
    A FileContentsManager Class that reads and stores notebooks to classical
    Jupyter notebooks (.ipynb), R Markdown notebooks (.Rmd), Julia (.jl),
    Python (.py) or R scripts (.R)
    """

    nb_extensions = [ext for ext in NOTEBOOK_EXTENSIONS if ext != '.ipynb']

    # Dictionary: notebook path => list of associated (path, fmt) for the paired notebooks
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

    comment_magics = Enum(
        values=[True, False],
        allow_none=True,
        help='Should Jupyter magic commands be commented out in the text representation?',
        config=True)

    split_at_heading = Bool(
        False,
        help='Split markdown cells on headings (Markdown and R Markdown formats only)',
        config=True)

    sphinx_convert_rst2md = Bool(
        False,
        help='When opening a Sphinx Gallery script, convert the reStructuredText to markdown',
        config=True)

    outdated_text_notebook_margin = Float(
        1.0,
        help='Refuse to overwrite inputs of a ipynb notebooks with those of a '
             'text notebook when the text notebook plus margin is older than '
             'the ipynb notebook',
        config=True)

    def drop_paired_notebook(self, path):
        """Remove the current notebook from the list of paired notebooks"""
        if path not in self.paired_notebooks:
            return

        for alt_path, _ in self.paired_notebooks.pop(path):
            if alt_path in self.paired_notebooks:
                self.drop_paired_notebook(alt_path)

    def update_paired_notebooks(self, path, new_paired_paths):
        """Update the list of paired notebooks to include/update the current pair"""
        if not new_paired_paths or len(new_paired_paths) <= 1:
            self.drop_paired_notebook(path)
            return

        for alt_path, _ in new_paired_paths:
            self.drop_paired_notebook(alt_path)

        for alt_path, _ in new_paired_paths:
            self.paired_notebooks[alt_path] = new_paired_paths

    def set_default_format_options(self, metadata):
        """Set default format option"""
        if self.comment_magics is not None and 'comment_magics' not in metadata.get('jupytext', {}):
            metadata.setdefault('jupytext', {})['comment_magics'] = self.comment_magics
        if self.split_at_heading and 'split_at_heading' not in metadata.get('jupytext', {}):
            metadata.setdefault('jupytext', {})['split_at_heading'] = True

    def save(self, model, path=''):
        """Save the file model and return the model with no content."""
        if model['type'] != 'notebook':
            return super(TextFileContentsManager, self).save(model, path)

        nbk = model['content']
        try:
            metadata = nbk.get('metadata')
            rearrange_jupytext_metadata(metadata)
            self.set_default_format_options(metadata)
            jupytext_formats = metadata.get('jupytext', {}).get('formats', self.default_jupytext_formats)
            if not jupytext_formats:
                text_representation = metadata.get('jupytext', {}).get('text_representation', {})
                ext = os.path.splitext(path)[1]
                fmt = {'extension': ext}

                if ext == text_representation.get('extension') and text_representation.get('format_name'):
                    fmt['format_name'] = text_representation.get('format_name')

                jupytext_formats = [fmt]

            jupytext_formats = long_form_multiple_formats(jupytext_formats)
            jupytext_formats = set_auto_ext(jupytext_formats, metadata)

            # Set preferred formats if not format name is given yet
            jupytext_formats = [preferred_format(fmt, self.preferred_jupytext_formats_save) for fmt in jupytext_formats]

            base, _ = find_base_path_and_format(path, jupytext_formats)
            self.update_paired_notebooks(path, paired_paths(path, jupytext_formats))

            # Save as ipynb first
            latest_result = None
            for fmt in jupytext_formats:
                if fmt['extension'] != '.ipynb':
                    continue

                alt_path = full_path(base, fmt)
                self.log.info("Saving %s", os.path.basename(alt_path))
                latest_result = super(TextFileContentsManager, self).save(model, alt_path)

            # And then to the other formats
            for fmt in jupytext_formats:
                if fmt['extension'] == '.ipynb':
                    continue

                alt_path = full_path(base, fmt)
                self.log.info("Saving %s", os.path.basename(alt_path))
                with mock.patch('nbformat.writes', _jupytext_writes(fmt)):
                    latest_result = super(TextFileContentsManager, self).save(model, alt_path)

            return latest_result

        except JupytextFormatError as err:
            raise HTTPError(400, str(err))

    def get(self, path, content=True, type=None, format=None, load_alternative_format=True):
        """ Takes a path for an entity and returns its model"""
        path = path.strip('/')
        ext = os.path.splitext(path)[1]

        # Not a notebook?
        if not self.exists(path) or (type != 'notebook' if type else ext not in self.all_nb_extensions()):
            return super(TextFileContentsManager, self).get(path, content, type, format)

        fmt = preferred_format(ext, self.preferred_jupytext_formats_read)
        if ext == '.ipynb':
            model = self._notebook_model(path, content=content)
        else:
            with mock.patch('nbformat.reads', _jupytext_reads(fmt)):
                model = self._notebook_model(path, content=content)

        if not load_alternative_format:
            return model

        if not content:
            # Modification time of a paired notebook, in this context - Jupyter is checking timestamp
            # before saving - is the most recent among all representations #118
            for alt_path, _ in self.paired_notebooks.get(path, []):
                if alt_path != path and self.exists(alt_path):
                    alt_model = self._notebook_model(alt_path, content=False)
                    if alt_model['last_modified'] > model['last_modified']:
                        model['last_modified'] = alt_model['last_modified']

            return model

        # We will now read a second file if this is a paired notebooks.
        nbk = model['content']
        jupytext_formats = nbk.metadata.get('jupytext', {}).get('formats', self.default_jupytext_formats)
        jupytext_formats = long_form_multiple_formats(jupytext_formats)

        # Compute paired notebooks from formats
        if jupytext_formats:
            try:
                _, _ = find_base_path_and_format(path, jupytext_formats)
                alt_paths = paired_paths(path, jupytext_formats)
            except InconsistentPath as err:
                self.log.info("Unable to read paired notebook: %s", str(err))
                alt_paths = []
            self.update_paired_notebooks(path, alt_paths)
        else:
            alt_paths = self.paired_notebooks.get(path)

        if not alt_paths:
            alt_paths = [(path, fmt)]

        org_model = model
        path_inputs = path_outputs = path
        model_outputs = None

        # Source format is first non ipynb format found on disk
        if path.endswith('.ipynb'):
            for alt_path, _ in alt_paths:
                if not alt_path.endswith('.ipynb') and self.exists(alt_path):
                    self.log.info(u'Reading SOURCE from {}'.format(alt_path))
                    path_inputs = alt_path
                    model_outputs = model
                    model = self.get(alt_path, content=content, type=type, format=format,
                                     load_alternative_format=False)
                    break
        # Outputs taken from ipynb if in group, if file exists
        else:
            for alt_path, _ in alt_paths:
                if alt_path.endswith('.ipynb') and self.exists(alt_path):
                    self.log.info(u'Reading OUTPUTS from {}'.format(alt_path))
                    path_outputs = alt_path
                    model_outputs = self.get(alt_path, content=content, type=type, format=format,
                                             load_alternative_format=False)
                    break

        try:
            check_file_version(model['content'], path_inputs, path_outputs)
        except ValueError as err:
            raise HTTPError(400, str(err))

        # Before we combine the two files, we make sure we're not overwriting ipynb cells
        # with an outdated text file
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
                    '''.format(src=path_inputs, src_last=model['last_modified'],
                               out=path_outputs, out_last=model_outputs['last_modified']))
        except OverflowError:
            pass

        jupytext_metadata = model['content']['metadata'].get('jupytext', {})
        if self.default_notebook_metadata_filter:
            jupytext_metadata.setdefault('notebook_metadata_filter', self.default_notebook_metadata_filter)
        if self.default_cell_metadata_filter:
            jupytext_metadata.setdefault('cell_metadata_filter', self.default_cell_metadata_filter)

        if jupytext_metadata:
            model['content']['metadata']['jupytext'] = jupytext_metadata

        if model_outputs:
            combine_inputs_with_outputs(model['content'], model_outputs['content'])
        elif not path.endswith('.ipynb'):
            nbk = model['content']
            language = nbk.metadata.get('jupytext', {}).get('main_language', 'python')
            if 'kernelspec' not in nbk.metadata and language != 'python':
                kernelspec = kernelspec_from_language(language)
                if kernelspec:
                    nbk.metadata['kernelspec'] = kernelspec

            self.notary.sign(nbk)
            self.mark_trusted_cells(nbk, path)

        # Path and name of the notebook is the one of the original path
        model['path'] = org_model['path']
        model['name'] = org_model['name']

        return model

    def trust_notebook(self, path):
        """Trust the current notebook"""
        if path.endswith('.ipynb'):
            super(TextFileContentsManager, self).trust_notebook(path)
            return

        for alt_path, fmt in self.paired_notebooks.get(path):
            if fmt['extension'] == '.ipynb':
                super(TextFileContentsManager, self).trust_notebook(alt_path)

    def rename_file(self, old_path, new_path):
        """Rename the current notebook, as well as its alternative representations"""
        old_alt_paths = self.paired_notebooks.get(old_path, [])
        self.drop_paired_notebook(old_path)
        self.drop_paired_notebook(new_path)

        # Find the format for the current file (if any)
        fmt = None
        for old_alt_path, alt_fmt in old_alt_paths:
            if old_alt_path == old_path:
                fmt = alt_fmt
                break

        if not fmt:
            super(TextFileContentsManager, self).rename_file(old_path, new_path)
            return

        # Is the new file name consistent with suffix?
        try:
            new_base = base_path(new_path, fmt)
        except InconsistentPath as err:
            raise HTTPError(400, str(err))

        new_paired_paths = []
        for old_alt_path, alt_fmt in old_alt_paths:
            new_alt_path = full_path(new_base, alt_fmt)
            new_paired_paths.append((new_alt_path, alt_fmt))
            if self.exists(old_alt_path):
                super(TextFileContentsManager, self).rename_file(old_alt_path, new_alt_path)

        self.update_paired_notebooks(new_path, new_paired_paths)
