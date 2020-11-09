"""ContentsManager that allows to open Rmd, py, R and ipynb files as notebooks
"""
import os
import itertools
from datetime import timedelta, datetime
from collections import namedtuple
import nbformat
from tornado.web import HTTPError

# import notebook.transutils before notebook.services.contents.filemanager #75
try:
    import notebook.transutils  # noqa
except ImportError:
    pass

import jupytext
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
    JupytextConfigurationError,
    JUPYTEXT_CONFIG_FILES,
    find_global_jupytext_configuration_file,
    load_jupytext_configuration_file,
    validate_jupytext_configuration_file,
    preferred_format,
    prepare_notebook_for_save,
)


def build_jupytext_contents_manager_class(base_contents_manager_class):
    """Derives a TextFileContentsManager class from the given base class"""

    class JupytextContentsManager(base_contents_manager_class, JupytextConfiguration):
        """
        A FileContentsManager Class that reads and stores notebooks to classical
        Jupyter notebooks (.ipynb), R Markdown notebooks (.Rmd), Julia (.jl),
        Python (.py) or R scripts (.R)
        """

        def __init__(self, *args, **kwargs):
            # Dictionary: notebook path => (fmt, formats) where
            # fmt is the current format, and formats the paired formats.
            self.paired_notebooks = dict()

            # Configuration cache, useful when notebooks are listed in a given directory
            self.cached_config = namedtuple(
                "cached_config", "path timestamp config_file config"
            )
            self.super = super(JupytextContentsManager, self)
            self.super.__init__(*args, **kwargs)

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
            if "prefix" in fmt and "/" in path:
                parent_dir = self.get_parent_dir(path)
                if not self.dir_exists(parent_dir):
                    self.create_prefix_dir(parent_dir, fmt)
                    self.log.info("Creating directory %s", parent_dir)
                    self.super.save(dict(type="directory"), parent_dir)

        def save(self, model, path=""):
            """Save the file model and return the model with no content."""
            if model["type"] != "notebook":
                return self.super.save(model, path)

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
                        return self.super.save(model, path)

                    if (
                        model["content"]["metadata"]
                        .get("jupytext", {})
                        .get("notebook_metadata_filter")
                        == "-all"
                    ):
                        self.log.warning(
                            "Stripping metadata from {} as 'Include Metadata' is off "
                            "(toggle 'Include Metadata' in the Jupytext Menu or Commands if desired)".format(
                                path
                            )
                        )

                    text_model = dict(
                        type="file",
                        format="text",
                        content=jupytext.writes(
                            nbformat.from_dict(model["content"]), fmt=fmt
                        ),
                    )

                    return self.super.save(text_model, path)

                return write_pair(path, jupytext_formats, save_one_file)

            except Exception as e:
                self.log.error(
                    u"Error while saving file: %s %s", path, e, exc_info=True
                )
                raise HTTPError(
                    500, u"Unexpected error while saving file: %s %s" % (path, e)
                )

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
            ext = os.path.splitext(path)[1]

            # Not a notebook?
            if (
                not self.file_exists(path)
                or self.dir_exists(path)
                or (type != "notebook" if type else ext not in self.all_nb_extensions())
            ):
                return self.super.get(path, content, type, format)

            config = self.get_config(path, use_cache=content is False)
            fmt = preferred_format(ext, config.preferred_jupytext_formats_read)
            if ext == ".ipynb":
                model = self.super.get(path, content, type="notebook", format=format)
            else:
                model = self.super.get(path, content, type="file", format=format)
                model["type"] = "notebook"
                config.set_default_format_options(fmt, read=True)
                if content:
                    try:
                        model["content"] = jupytext.reads(model["content"], fmt=fmt)
                    except Exception as err:
                        self.log.error(
                            u"Error while reading file: %s %s", path, err, exc_info=True
                        )
                        raise HTTPError(500, str(err))

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
                        alt_model = self.super.get(alt_path, content=False)
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
                    self.log.error(
                        u"Unable to read paired notebook: %s %s",
                        path,
                        err,
                        exc_info=True,
                    )
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
                return self.super.get(alt_path, content=False)["last_modified"]

            def read_one_file(alt_path, alt_fmt):
                if alt_path == path:
                    return model["content"]
                if alt_path.endswith(".ipynb"):
                    self.log.info(u"Reading OUTPUTS from {}".format(alt_path))
                    return self.super.get(
                        alt_path, content=True, type="notebook", format=format
                    )["content"]

                self.log.info(u"Reading SOURCE from {}".format(alt_path))
                config.set_default_format_options(alt_fmt, read=True)
                text = self.super.get(
                    alt_path, content=True, type="file", format=format
                )["content"]
                return jupytext.reads(text, fmt=alt_fmt)

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
                            outdated_text_notebook_margin = 5  # default is 1 (second)
                        to your jupytext.toml file
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
            except HTTPError:
                raise
            except Exception as err:
                self.log.error(
                    u"Error while reading file: %s %s", path, err, exc_info=True
                )
                raise HTTPError(500, str(err))

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
                return self.super.new_untitled(path, type, ext)

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
                self.super.trust_notebook(path)
                return

            fmt, formats = self.paired_notebooks[path]
            for alt_path, alt_fmt in paired_paths(path, fmt, formats):
                if alt_fmt["extension"] == ".ipynb":
                    self.super.trust_notebook(alt_path)

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
                self.super.rename_file(old_path, new_path)
                return

            fmt, formats = self.paired_notebooks.get(old_path)
            old_alt_paths = paired_paths(old_path, fmt, formats)

            # Is the new file name consistent with suffix?
            try:
                new_base = base_path(new_path, fmt)
            except HTTPError:
                raise
            except Exception as err:
                self.log.error(
                    u"Error while renaming file from %s to %s: %s",
                    old_path,
                    new_path,
                    err,
                    exc_info=True,
                )
                raise HTTPError(500, str(err))

            for old_alt_path, alt_fmt in old_alt_paths:
                new_alt_path = full_path(new_base, alt_fmt)
                if self.exists(old_alt_path):
                    self.super.rename_file(old_alt_path, new_alt_path)

            self.drop_paired_notebook(old_path)
            self.update_paired_notebooks(new_path, formats)

        def get_parent_dir(self, path):
            """The parent directory"""
            if "/" in path:
                return path.rsplit("/", 1)[0]
            # jupyter-fs
            if ":" in path and hasattr(self, "_managers"):
                if path.endswith(":"):
                    return ""
                return path.rsplit(":", 1)[0] + ":"
            return ""

        def get_config_file(self, directory):
            """Return the jupytext configuration file, if any"""
            for jupytext_config_file in JUPYTEXT_CONFIG_FILES:
                path = directory + "/" + jupytext_config_file
                if self.file_exists(path):
                    return path

            if not directory:
                return None

            parent_dir = self.get_parent_dir(directory)
            return self.get_config_file(parent_dir)

        def load_config_file(self, config_file, is_os_path=False):
            """Load the configuration file"""
            if config_file is None:
                return None
            self.log.info("Loading Jupytext configuration file at %s", config_file)
            if config_file.endswith(".py") and not is_os_path:
                config_file = self._get_os_path(config_file)
                is_os_path = True
            if is_os_path:
                config_dict = load_jupytext_configuration_file(config_file)
            else:
                model = self.super.get(config_file, content=True, type="file")
                config_dict = load_jupytext_configuration_file(
                    config_file, model["content"]
                )
            return validate_jupytext_configuration_file(config_file, config_dict)

        def get_config(self, path, use_cache=False):
            """Return the Jupytext configuration for the given path"""
            parent_dir = self.get_parent_dir(path)

            # When listing the notebooks for the tree view, we use a one-second
            # cache for the configuration file
            if (
                not use_cache
                or parent_dir != self.cached_config.path
                or (
                    self.cached_config.timestamp + timedelta(seconds=1) < datetime.now()
                )
            ):
                try:
                    config_file = self.get_config_file(parent_dir)
                    if config_file:
                        self.cached_config.config = self.load_config_file(config_file)
                    else:
                        config_file = find_global_jupytext_configuration_file()
                        self.cached_config.config = self.load_config_file(
                            config_file, True
                        )
                    self.cached_config.config_file = config_file
                    self.cached_config.path = parent_dir
                    self.cached_config.timestamp = datetime.now()
                except JupytextConfigurationError as err:
                    self.log.error(
                        u"Error while reading config file: %s %s",
                        config_file,
                        err,
                        exc_info=True,
                    )
                    raise HTTPError(500, "{}".format(err))

            if self.cached_config.config is not None:
                self.log.debug(
                    "Configuration file for %s is %s",
                    path,
                    self.cached_config.config_file,
                )
                return self.cached_config.config
            return self

    return JupytextContentsManager


try:
    from notebook.services.contents.largefilemanager import LargeFileManager

    TextFileContentsManager = build_jupytext_contents_manager_class(LargeFileManager)
except ImportError:
    # Older versions of notebook do not have the LargeFileManager #217
    from notebook.services.contents.filemanager import FileContentsManager

    TextFileContentsManager = build_jupytext_contents_manager_class(FileContentsManager)
