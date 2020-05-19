"""ContentsManager that allows to open Rmd, py, R and ipynb files as notebooks
"""
import os
from datetime import timedelta
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
from .combine import combine_inputs_with_outputs
from .formats import check_file_version
from .formats import long_form_multiple_formats
from .formats import short_form_one_format, short_form_multiple_formats
from .paired_paths import (
    paired_paths,
    find_base_path_and_format,
    base_path,
    full_path,
    InconsistentPath,
)
from .pairs import write_pair
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

        # Dictionary: notebook path => (fmt, formats) where fmt is the current format, and formats the paired formats.
        paired_notebooks = dict()

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
            base, fmt = find_base_path_and_format(path, formats)
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

            config = self.get_config(path)
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
            jupytext_formats = nbk.metadata.get("jupytext", {}).get(
                "formats"
            ) or config.default_formats(path)
            jupytext_formats = long_form_multiple_formats(
                jupytext_formats, nbk.metadata, auto_ext_requires_language_info=False
            )

            # Compute paired notebooks from formats
            alt_paths = [(path, fmt)]
            if jupytext_formats:
                try:
                    _, fmt = find_base_path_and_format(path, jupytext_formats)
                    alt_paths = paired_paths(path, fmt, jupytext_formats)
                    self.update_paired_notebooks(path, jupytext_formats)
                except InconsistentPath as err:
                    self.log.info("Unable to read paired notebook: %s", str(err))
            else:
                if path in self.paired_notebooks:
                    fmt, formats = self.paired_notebooks.get(path)
                    alt_paths = paired_paths(path, fmt, formats)

            if len(alt_paths) > 1 and ext == ".ipynb":
                # Apply default options (like saving and reloading would do)
                jupytext_metadata = model["content"]["metadata"].get("jupytext", {})
                config.set_default_format_options(jupytext_metadata, read=True)
                if jupytext_metadata:
                    model["content"]["metadata"]["jupytext"] = jupytext_metadata

            org_model = model
            fmt_inputs = fmt
            path_inputs = path_outputs = path
            model_outputs = None

            # Source format is the most recent non ipynb format found on disk
            if path.endswith(".ipynb"):
                source_timestamps = {}
                for alt_path, alt_fmt in alt_paths:
                    if not alt_path.endswith(".ipynb") and self.exists(alt_path):
                        source_timestamps[alt_path] = self._notebook_model(
                            alt_path, content=False
                        )["last_modified"]

                most_recent_timestamp = None
                for alt_path in source_timestamps:
                    alt_ts = source_timestamps[alt_path]
                    if len(source_timestamps) > 1:
                        self.log.info(
                            u"File {} was last modified at {}".format(alt_path, alt_ts)
                        )
                    if most_recent_timestamp is None or alt_ts > most_recent_timestamp:
                        most_recent_timestamp = alt_ts
                        model_outputs = model
                        path_inputs = alt_path
                        fmt_inputs = alt_fmt

                if most_recent_timestamp is not None:
                    self.log.info(u"Reading SOURCE from {}".format(path_inputs))
                    model = self.get(
                        path_inputs,
                        content=content,
                        type="notebook",
                        format=format,
                        load_alternative_format=False,
                    )

            # Outputs taken from ipynb if in group, if file exists
            else:
                for alt_path, _ in alt_paths:
                    if alt_path.endswith(".ipynb") and self.exists(alt_path):
                        self.log.info(u"Reading OUTPUTS from {}".format(alt_path))
                        path_outputs = alt_path
                        model_outputs = self.get(
                            alt_path,
                            content=content,
                            type="notebook",
                            format=format,
                            load_alternative_format=False,
                        )
                        break

            try:
                check_file_version(model["content"], path_inputs, path_outputs)
            except Exception as err:
                raise HTTPError(400, str(err))

            # Before we combine the two files, we make sure we're not overwriting ipynb cells
            # with an outdated text file
            try:
                if model_outputs and model_outputs["last_modified"] > model[
                    "last_modified"
                ] + timedelta(seconds=config.outdated_text_notebook_margin):
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
                            src=path_inputs,
                            src_last=model["last_modified"],
                            out=path_outputs,
                            out_last=model_outputs["last_modified"],
                        ),
                    )
            except OverflowError:
                pass

            if model_outputs:
                combine_inputs_with_outputs(
                    model["content"], model_outputs["content"], fmt_inputs
                )
            elif not path.endswith(".ipynb"):
                set_kernelspec_from_language(model["content"])

            # Trust code cells when they have no output
            for cell in model["content"].cells:
                if (
                    cell.cell_type == "code"
                    and not cell.outputs
                    and cell.metadata.get("trusted") is False
                ):
                    cell.metadata["trusted"] = True

            # Path and name of the notebook is the one of the original path
            model["path"] = org_model["path"]
            model["name"] = org_model["name"]

            return model

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

        def get_config(self, path):
            nb_file = self._get_os_path(path.strip("/"))
            return load_jupytext_config(nb_file) or self

    return JupytextContentsManager


try:
    from notebook.services.contents.largefilemanager import LargeFileManager

    TextFileContentsManager = build_jupytext_contents_manager_class(LargeFileManager)
except ImportError:
    # Older versions of notebook do not have the LargeFileManager #217
    from notebook.services.contents.filemanager import FileContentsManager

    TextFileContentsManager = build_jupytext_contents_manager_class(FileContentsManager)
