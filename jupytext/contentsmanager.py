"""ContentsManager that allows to open Rmd, py, R and ipynb files as notebooks
"""
import os
import itertools
from datetime import timedelta, datetime
from collections import namedtuple
import nbformat

try:
    import unittest.mock as mock
except ImportError:
    import mock
from tornado.web import HTTPError

# import notebook.transutils before notebook.services.contents.filemanager #75
try:
    import notebook.transutils  # noqa
except ImportError:
    pass

from .jupytext import reads, writes
from .jupytext import create_prefix_dir as create_prefix_dir_from_path
from .formats import long_form_multiple_formats
from .formats import short_form_one_format, short_form_multiple_formats
from .paired_paths import (
    paired_paths,
    find_base_path_and_format,
    base_path,
    full_path,
    InconsistentPath,
)
from .pairs import write_pair, read_pair, latest_inputs_and_outputs
from .kernels import set_kernelspec_from_language
from .config import (
    JupytextConfiguration,
    preferred_format,
    load_jupytext_config,
    prepare_notebook_for_save,
)


def _jupytext_writes(fmt):
    def _writes(nbk, version=nbformat.NO_CONVERT, **kwargs):
        return writes(nbk, fmt, version=version, **kwargs)

    return _writes


def _jupytext_reads(fmt):
    def _reads(text, as_version, **kwargs):
        return reads(text, fmt, as_version=as_version, **kwargs)

    return _reads


def build_jupytext_contents_manager_class(base_contents_manager_class):
    """Derives a TextFileContentsManager class from the given base class"""

    class JupytextContentsManager(base_contents_manager_class, JupytextConfiguration):
        """
        A FileContentsManager Class that reads and stores notebooks to classical
        Jupyter notebooks (.ipynb), R Markdown notebooks (.Rmd), Julia (.jl),
        Python (.py) or R scripts (.R)
        """

        def __init__(self, **kwargs):
            # Dictionary: notebook path => (fmt, formats) where
            # fmt is the current format, and formats the paired formats.
            self.paired_notebooks = dict()

            # Configuration cache, useful when notebooks are listed in a given directory
            self.cached_config = namedtuple("cached_config", "path timestamp config")

            super(JupytextContentsManager, self).__init__(**kwargs)

        def all_nb_extensions(self):
            """All extensions that should be classified as notebooks"""
            return [
                ext if ext.startswith(".") else "." + ext
                for ext in self.notebook_extensions.split(",")
            ]

        def drop_paired_notebook(self, path):
            """Remove the current notebook from the list of paired notebooks"""
            if path not in self.paired_notebooks:
                return

            fmt, formats = self.paired_notebooks.pop(path)
            prev_paired_paths = paired_paths(path, fmt, formats)
            for alt_path, _ in prev_paired_paths:
                if alt_path in self.paired_notebooks:
                    self.drop_paired_notebook(alt_path)

        def update_paired_notebooks(self, path, formats):
            """Update the list of paired notebooks to include/update the current pair"""
            if not formats:
                self.drop_paired_notebook(path)
                return

            formats = long_form_multiple_formats(formats)
            _, fmt = find_base_path_and_format(path, formats)
            new_paired_paths = paired_paths(path, fmt, formats)
            for alt_path, _ in new_paired_paths:
                self.drop_paired_notebook(alt_path)

            if len(formats) == 1 and set(formats[0]) <= {"extension"}:
                return

            short_formats = short_form_multiple_formats(formats)
            for alt_path, alt_fmt in new_paired_paths:
                self.paired_notebooks[alt_path] = (
                    short_form_one_format(alt_fmt),
                    short_formats,
                )

        def create_prefix_dir(self, path, fmt):
            """Create the prefix dir, if missing"""
            create_prefix_dir_from_path(self._get_os_path(path.strip("/")), fmt)

        def save(self, model, path=""):
            """Save the file model and return the model with no content."""
            if model["type"] != "notebook":
                return super(JupytextContentsManager, self).save(model, path)

            path = path.strip("/")
            nbk = model["content"]
            try:
                config = self.get_config(path)
                jupytext_formats = prepare_notebook_for_save(nbk, config, path)
                self.update_paired_notebooks(path, jupytext_formats)

                def save_one_file(path, fmt):
                    if "format_name" in fmt and fmt["extension"] not in [
                        ".md",
                        ".markdown",
                        ".Rmd",
                    ]:
                        self.log.info(
                            "Saving %s in format %s:%s",
                            os.path.basename(path),
                            fmt["extension"][1:],
                            fmt["format_name"],
                        )
                    else:
                        self.log.info("Saving %s", os.path.basename(path))

                    self.create_prefix_dir(path, fmt)
                    if fmt["extension"] == ".ipynb":
                        return super(JupytextContentsManager, self).save(model, path)

                    with mock.patch("nbformat.writes", _jupytext_writes(fmt)):
                        return super(JupytextContentsManager, self).save(model, path)

                return write_pair(path, jupytext_formats, save_one_file)

            except Exception as err:
                raise HTTPError(400, str(err))

        def get(
            self,
            path,
            content=True,
            type=None,
            format=None,
            load_alternative_format=True,
        ):
            """ Takes a path for an entity and returns its model"""
            path = path.strip("/")

            os_path = self._get_os_path(path)
            ext = os.path.splitext(path)[1]

            # Not a notebook?
            if (
                not self.exists(path)
                or os.path.isdir(os_path)
                or (type != "notebook" if type else ext not in self.all_nb_extensions())
            ):
                return super(JupytextContentsManager, self).get(
                    path, content, type, format
                )

            config = self.get_config(path, use_cache=content is False)
            fmt = preferred_format(ext, config.preferred_jupytext_formats_read)
            if ext == ".ipynb":
                model = self._notebook_model(path, content=content)
            else:
                config.set_default_format_options(fmt, read=True)
                with mock.patch("nbformat.reads", _jupytext_reads(fmt)):
                    model = self._notebook_model(path, content=content)

            if not load_alternative_format:
                return model

            if not content:
                # Modification time of a paired notebook, in this context - Jupyter is checking timestamp
                # before saving - is the most recent among all representations #118
                if path not in self.paired_notebooks:
                    return model

                fmt, formats = self.paired_notebooks.get(path)
                for alt_path, _ in paired_paths(path, fmt, formats):
                    if alt_path != path and self.exists(alt_path):
                        alt_model = self._notebook_model(alt_path, content=False)
                        if alt_model["last_modified"] > model["last_modified"]:
                            model["last_modified"] = alt_model["last_modified"]

                return model

            # We will now read a second file if this is a paired notebooks.
            nbk = model["content"]
            formats = nbk.metadata.get("jupytext", {}).get(
                "formats"
            ) or config.default_formats(path)
            formats = long_form_multiple_formats(
                formats, nbk.metadata, auto_ext_requires_language_info=False
            )

            # Compute paired notebooks from formats
            alt_paths = [(path, fmt)]
            if formats:
                try:
                    _, fmt = find_base_path_and_format(path, formats)
                    alt_paths = paired_paths(path, fmt, formats)
                    self.update_paired_notebooks(path, formats)
                except InconsistentPath as err:
                    self.log.info("Unable to read paired notebook: %s", str(err))
            else:
                if path in self.paired_notebooks:
                    fmt, formats = self.paired_notebooks.get(path)
                    alt_paths = paired_paths(path, fmt, formats)
                    formats = long_form_multiple_formats(formats)

            if len(alt_paths) > 1 and ext == ".ipynb":
                # Apply default options (like saving and reloading would do)
                jupytext_metadata = model["content"]["metadata"].get("jupytext", {})
                config.set_default_format_options(jupytext_metadata, read=True)
                if jupytext_metadata:
                    model["content"]["metadata"]["jupytext"] = jupytext_metadata

            def get_timestamp(alt_path):
                if not self.exists(alt_path):
                    return None
                if alt_path == path:
                    return model["last_modified"]
                return self._notebook_model(alt_path, content=False)["last_modified"]

            def read_one_file(alt_path, alt_fmt):
                if alt_path == path:
                    return model["content"]
                if alt_path.endswith(".ipynb"):
                    self.log.info(u"Reading OUTPUTS from {}".format(alt_path))
                    return self._notebook_model(alt_path, content=True)["content"]

                self.log.info(u"Reading SOURCE from {}".format(alt_path))
                config.set_default_format_options(alt_fmt, read=True)
                with mock.patch("nbformat.reads", _jupytext_reads(alt_fmt)):
                    return self._notebook_model(alt_path, content=True)["content"]

            inputs, outputs = latest_inputs_and_outputs(
                path, fmt, formats, get_timestamp, contents_manager_mode=True
            )

            # Before we combine the two files, we make sure we're not overwriting ipynb cells
            # with an outdated text file
            try:
                if (
                    outputs.timestamp
                    and outputs.timestamp
                    > inputs.timestamp
                    + timedelta(seconds=config.outdated_text_notebook_margin)
                ):
                    raise HTTPError(
                        400,
                        """{out} (last modified {out_last})
                        seems more recent than {src} (last modified {src_last})
                        Please either:
                        - open {src} in a text editor, make sure it is up to date, and save it,
                        - or delete {src} if not up to date,
                        - or increase check margin by adding, say,
                            c.ContentsManager.outdated_text_notebook_margin = 5 # in seconds # or float("inf")
                        to your .jupyter/jupyter_notebook_config.py file
                        """.format(
                            src=inputs.path,
                            src_last=inputs.timestamp,
                            out=outputs.path,
                            out_last=outputs.timestamp,
                        ),
                    )
            except OverflowError:
                pass

            try:
                model["content"] = read_pair(inputs, outputs, read_one_file)
            except Exception as err:
                raise HTTPError(400, str(err))

            if not outputs.timestamp:
                set_kernelspec_from_language(model["content"])

            # Trust code cells when they have no output
            for cell in model["content"].cells:
                if (
                    cell.cell_type == "code"
                    and not cell.outputs
                    and cell.metadata.get("trusted") is False
                ):
                    cell.metadata["trusted"] = True

            return model

        def new_untitled(self, path="", type="", ext=""):
            """Create a new untitled file or directory in path

            We override the base function because that one does not take the 'ext' argument
            into account when type=="notebook". See https://github.com/mwouts/jupytext/issues/443
            """
            if type != "notebook" and ext != ".ipynb":
                return super(JupytextContentsManager, self).new_untitled(
                    path, type, ext
                )

            ext = ext or ".ipynb"
            if ":" in ext:
                ext, format_name = ext.split(":", 1)
            else:
                format_name = ""

            path = path.strip("/")
            if not self.dir_exists(path):
                raise HTTPError(404, "No such directory: %s" % path)

            untitled = self.untitled_notebook
            name = self.increment_notebook_filename(untitled + ext, path)
            path = u"{0}/{1}".format(path, name)

            model = {"type": "notebook"}
            if format_name:
                model["format"] = "json"
                model["content"] = nbformat.v4.nbbase.new_notebook(
                    metadata={"jupytext": {"formats": ext + ":" + format_name}}
                )

            return self.new(model, path)

        def increment_notebook_filename(self, filename, path=""):
            """Increment a notebook filename until it is unique, regardless of extension"""
            # Extract the full suffix from the filename (e.g. .tar.gz)
            path = path.strip("/")
            basename, dot, ext = filename.partition(".")
            ext = dot + ext

            for i in itertools.count():
                if i:
                    insert_i = "{}".format(i)
                else:
                    insert_i = ""
                basename_i = basename + insert_i
                name = basename_i + ext
                if not any(
                    self.exists(u"{}/{}{}".format(path, basename_i, nb_ext))
                    for nb_ext in self.notebook_extensions.split(",")
                ):
                    break
            return name

        def trust_notebook(self, path):
            """Trust the current notebook"""
            if path.endswith(".ipynb") or path not in self.paired_notebooks:
                super(JupytextContentsManager, self).trust_notebook(path)
                return

            fmt, formats = self.paired_notebooks[path]
            for alt_path, alt_fmt in paired_paths(path, fmt, formats):
                if alt_fmt["extension"] == ".ipynb":
                    super(JupytextContentsManager, self).trust_notebook(alt_path)

        def rename_file(self, old_path, new_path):
            """Rename the current notebook, as well as its alternative representations"""
            if old_path not in self.paired_notebooks:
                try:
                    # we do not know yet if this is a paired notebook (#190)
                    # -> to get this information we open the notebook
                    self.get(old_path, content=True)
                except Exception:
                    pass

            if old_path not in self.paired_notebooks:
                super(JupytextContentsManager, self).rename_file(old_path, new_path)
                return

            fmt, formats = self.paired_notebooks.get(old_path)
            old_alt_paths = paired_paths(old_path, fmt, formats)

            # Is the new file name consistent with suffix?
            try:
                new_base = base_path(new_path, fmt)
            except Exception as err:
                raise HTTPError(400, str(err))

            for old_alt_path, alt_fmt in old_alt_paths:
                new_alt_path = full_path(new_base, alt_fmt)
                if self.exists(old_alt_path):
                    super(JupytextContentsManager, self).rename_file(
                        old_alt_path, new_alt_path
                    )

            self.drop_paired_notebook(old_path)
            self.update_paired_notebooks(new_path, formats)

        def get_config(self, path, use_cache=False):
            """Return the Jupytext configuration for the given path"""
            nb_file = self._get_os_path(path.strip("/"))
            parent_dir = os.path.dirname(nb_file)

            # When listing the notebooks for the tree view, we use a one-second
            # cache for the configuration file
            if (
                not use_cache
                or parent_dir != self.cached_config.path
                or (
                    self.cached_config.timestamp + timedelta(seconds=1) < datetime.now()
                )
            ):
                self.cached_config.path = parent_dir
                self.cached_config.timestamp = datetime.now()
                self.cached_config.config = load_jupytext_config(parent_dir)

            return self.cached_config.config or self

    return JupytextContentsManager


try:
    from notebook.services.contents.largefilemanager import LargeFileManager

    TextFileContentsManager = build_jupytext_contents_manager_class(LargeFileManager)
except ImportError:
    # Older versions of notebook do not have the LargeFileManager #217
    from notebook.services.contents.filemanager import FileContentsManager

    TextFileContentsManager = build_jupytext_contents_manager_class(FileContentsManager)
