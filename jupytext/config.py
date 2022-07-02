"""Find and read Jupytext configuration files"""
import json
import os
import warnings

import yaml
from traitlets import Bool, Dict, Enum, Float, List, Unicode, Union
from traitlets.config import Configurable
from traitlets.config.loader import PyFileConfigLoader
from traitlets.traitlets import TraitError

from .formats import (
    NOTEBOOK_EXTENSIONS,
    long_form_multiple_formats,
    long_form_one_format,
    short_form_multiple_formats,
)


class JupytextConfigurationError(ValueError):
    """Error in the specification of the format for the text notebook"""


JUPYTEXT_CONFIG_FILES = [
    "jupytext",
    "jupytext.toml",
    "jupytext.yml",
    "jupytext.yaml",
    "jupytext.json",
]

JUPYTEXT_CONFIG_FILES.extend(
    ["." + filename for filename in JUPYTEXT_CONFIG_FILES] + [".jupytext.py"]
)

PYPROJECT_FILE = "pyproject.toml"

JUPYTEXT_CEILING_DIRECTORIES = [
    path
    for path in os.environ.get("JUPYTEXT_CEILING_DIRECTORIES", "").split(":")
    if path
]


class JupytextConfiguration(Configurable):
    """Jupytext Configuration's options"""

    formats = Union(
        [Unicode(), List(Unicode()), Dict(Unicode())],
        help="Save notebooks to these file extensions. "
        "Can be any of ipynb,Rmd,md,jl,py,R,nb.jl,nb.py,nb.R "
        "comma separated. If you want another format than the "
        "default one, append the format name to the extension, "
        "e.g. ipynb,py:percent to save the notebook to "
        "hydrogen/spyder/vscode compatible scripts",
        config=True,
    )
    default_jupytext_formats = Unicode(
        help="Deprecated. Use 'formats' instead", config=True
    )

    preferred_jupytext_formats_save = Unicode(
        help="Preferred format when saving notebooks as text, per extension. "
        'Use "jl:percent,py:percent,R:percent" if you want to save '
        "Julia, Python and R scripts in the double percent format and "
        'only write "jupytext_formats": "py" in the notebook metadata.',
        config=True,
    )

    preferred_jupytext_formats_read = Unicode(
        help="Preferred format when reading notebooks from text, per "
        'extension. Use "py:sphinx" if you want to read all python '
        "scripts as Sphinx gallery scripts.",
        config=True,
    )

    notebook_metadata_filter = Unicode(
        help="Notebook metadata that should be save in the text representations. "
        "Examples: 'all', '-all', 'widgets,nteract', 'kernelspec,jupytext-all'",
        config=True,
    )

    default_notebook_metadata_filter = Unicode(
        "", help="Deprecated. Use 'notebook_metadata_filter' instead", config=True
    )

    hide_notebook_metadata = Enum(
        values=[True, False],
        allow_none=True,
        help="Should the notebook metadata be wrapped into an HTML comment in the Markdown format?",
        config=True,
    )

    root_level_metadata_as_raw_cell = Bool(
        True,
        help="Should the root level metadata of text documents (like the fields 'title' or 'author' in "
        "R Markdown document) appear as a raw cell in the notebook (True), or go to the notebook"
        "metadata?",
        config=True,
    )

    cell_metadata_filter = Unicode(
        help="Cell metadata that should be saved in the text representations. "
        "Examples: 'all', 'hide_input,hide_output'",
        config=True,
    )

    default_cell_metadata_filter = Unicode(
        "", help="Deprecated. Use 'cell_metadata_filter' instead", config=True
    )

    comment_magics = Enum(
        values=[True, False],
        allow_none=True,
        help="Should Jupyter magic commands be commented out in the text representation?",
        config=True,
    )

    split_at_heading = Bool(
        False,
        help="Split markdown cells on headings (Markdown and R Markdown formats only)",
        config=True,
    )

    sphinx_convert_rst2md = Bool(
        False,
        help="When opening a Sphinx Gallery script, convert the reStructuredText to markdown",
        config=True,
    )

    doxygen_equation_markers = Bool(
        False,
        help="Should equation markers use the DOxygen format? "
        "(see https://github.com/mwouts/jupytext/issues/517)",
        config=True,
    )

    outdated_text_notebook_margin = Float(
        1.0,
        help="Refuse to overwrite inputs of a ipynb notebooks with those of a "
        "text notebook when the text notebook plus margin is older than "
        "the ipynb notebook (NB: This option is ignored by Jupytext CLI)",
        config=True,
    )

    cm_config_log_level = Enum(
        values=["warning", "info", "info_if_changed", "debug", "none"],
        default_value="info_if_changed",
        help="The log level for config file logs in the Jupytext contents manager",
        config=True,
    )

    cell_markers = Unicode(
        help='Start and end cell markers for the light format, comma separated. Use "{{{,}}}" to mark cells'
        'as foldable regions in Vim, and "region,endregion" to mark cells as Vscode/PyCharm regions',
        config=True,
    )

    default_cell_markers = Unicode(
        help="Deprecated. Use 'cell_markers' instead", config=True
    )

    notebook_extensions = Union(
        [List(Unicode(), NOTEBOOK_EXTENSIONS), Unicode()],
        help="A list of notebook extensions",
        config=True,
    )

    custom_cell_magics = Unicode(
        help='A comma separated list of cell magics. Use e.g. custom_cell_magics = "configure,local" '
        'if you want code cells starting with the Spark magic cell commands "configure" and "local" '
        "to be commented out when converted to scripts.",
        config=True,
    )

    def set_default_format_options(self, format_options, read=False):
        """Set default format option"""
        if self.default_notebook_metadata_filter:
            warnings.warn(
                "The option 'default_notebook_metadata_filter' is deprecated. "
                "Please use 'notebook_metadata_filter' instead.",
                FutureWarning,
            )
            format_options.setdefault(
                "notebook_metadata_filter", self.default_notebook_metadata_filter
            )
        if self.notebook_metadata_filter:
            format_options.setdefault(
                "notebook_metadata_filter", self.notebook_metadata_filter
            )
        if self.default_cell_metadata_filter:
            warnings.warn(
                "The option 'default_cell_metadata_filter' is deprecated. "
                "Please use 'cell_metadata_filter' instead.",
                FutureWarning,
            )
            format_options.setdefault(
                "cell_metadata_filter", self.default_cell_metadata_filter
            )
        if self.cell_metadata_filter:
            format_options.setdefault("cell_metadata_filter", self.cell_metadata_filter)
        if self.hide_notebook_metadata is not None:
            format_options.setdefault(
                "hide_notebook_metadata", self.hide_notebook_metadata
            )
        if self.root_level_metadata_as_raw_cell is False:
            format_options.setdefault(
                "root_level_metadata_as_raw_cell", self.root_level_metadata_as_raw_cell
            )
        if self.comment_magics is not None:
            format_options.setdefault("comment_magics", self.comment_magics)
        if self.split_at_heading:
            format_options.setdefault("split_at_heading", self.split_at_heading)
        if self.doxygen_equation_markers:
            format_options.setdefault(
                "doxygen_equation_markers", self.doxygen_equation_markers
            )
        if not read:
            if self.default_cell_markers:
                warnings.warn(
                    "The option 'default_cell_markers' is deprecated. "
                    "Please use 'cell_markers' instead.",
                    FutureWarning,
                )
                format_options.setdefault("cell_markers", self.default_cell_markers)
            if self.cell_markers:
                format_options.setdefault("cell_markers", self.cell_markers)
        if read and self.sphinx_convert_rst2md:
            format_options.setdefault("rst2md", self.sphinx_convert_rst2md)
        if self.custom_cell_magics:
            format_options.setdefault("custom_cell_magics", self.custom_cell_magics)

    def default_formats(self, path):
        """Return the default formats, if they apply to the current path #157"""
        from .paired_paths import InconsistentPath, base_path

        if self.default_jupytext_formats:
            warnings.warn(
                "The option 'default_jupytext_formats' is deprecated. "
                "Please use 'formats' instead.",
                FutureWarning,
            )

        formats = self.formats or self.default_jupytext_formats
        for fmt in long_form_multiple_formats(formats):
            try:
                base_path(path, fmt)
                return formats
            except InconsistentPath:
                continue

        return None

    def __eq__(self, other):
        for key in self.class_trait_names():
            if getattr(self, key) != getattr(other, key):
                return False

        return True


def preferred_format(incomplete_format, preferred_formats):
    """Return the preferred format for the given extension"""
    incomplete_format = long_form_one_format(incomplete_format)
    if "format_name" in incomplete_format:
        return incomplete_format

    for fmt in long_form_multiple_formats(preferred_formats):
        if (
            (
                incomplete_format["extension"] == fmt["extension"]
                or (
                    fmt["extension"] == ".auto"
                    and incomplete_format["extension"]
                    not in [".md", ".markdown", ".Rmd", ".ipynb"]
                )
            )
            and incomplete_format.get("suffix")
            == fmt.get("suffix", incomplete_format.get("suffix"))
            and incomplete_format.get("prefix")
            == fmt.get("prefix", incomplete_format.get("prefix"))
        ):
            fmt.update(incomplete_format)
            return fmt

    return incomplete_format


def global_jupytext_configuration_directories():
    """Return the directories in which Jupytext will search for a configuration file"""

    config_dirs = []

    if "XDG_CONFIG_HOME" in os.environ:
        config_dirs.extend(os.environ["XDG_CONFIG_HOME"].split(":"))
    elif "USERPROFILE" in os.environ:
        config_dirs.append(os.environ["USERPROFILE"])
    elif "HOME" in os.environ:
        config_dirs.append(os.path.join(os.environ["HOME"], ".config"))
        config_dirs.append(os.environ["HOME"])

    if "XDG_CONFIG_DIRS" in os.environ:
        config_dirs.extend(os.environ["XDG_CONFIG_DIRS"].split(":"))
    elif "ALLUSERSPROFILE" in os.environ:
        config_dirs.append(os.environ["ALLUSERSPROFILE"])
    else:
        config_dirs.extend(["/usr/local/share/", "/usr/share/"])

    for config_dir in config_dirs:
        yield from [
            os.path.join(config_dir, "jupytext"),
            config_dir,
        ]


def find_global_jupytext_configuration_file():
    """Return the global Jupytext configuration file, if any"""

    for config_dir in global_jupytext_configuration_directories():
        config_file = find_jupytext_configuration_file(config_dir, False)
        if config_file:
            return config_file

    return None


def find_jupytext_configuration_file(path, search_parent_dirs=True):
    """Return the first jupytext configuration file in the current directory, or any parent directory"""
    if os.path.isdir(path):
        for filename in JUPYTEXT_CONFIG_FILES:
            full_path = os.path.join(path, filename)
            if os.path.isfile(full_path):
                return full_path

    pyproject_path = os.path.join(path, PYPROJECT_FILE)
    if os.path.isfile(pyproject_path):
        import toml

        with open(pyproject_path) as stream:
            doc = toml.loads(stream.read())
            if doc.get("tool", {}).get("jupytext") is not None:
                return pyproject_path

    if not search_parent_dirs:
        return None

    if JUPYTEXT_CEILING_DIRECTORIES and os.path.isdir(path):
        for ceiling_dir in JUPYTEXT_CEILING_DIRECTORIES:
            if os.path.isdir(ceiling_dir) and os.path.samefile(path, ceiling_dir):
                return None

    parent_dir = os.path.dirname(path)
    if parent_dir == path:
        return find_global_jupytext_configuration_file()

    return find_jupytext_configuration_file(parent_dir)


def parse_jupytext_configuration_file(jupytext_config_file, stream=None):
    """Read a Jupytext config file, and return a dict"""
    if not jupytext_config_file.endswith(".py") and stream is None:
        with open(jupytext_config_file, encoding="utf-8") as stream:
            return parse_jupytext_configuration_file(
                jupytext_config_file, stream.read()
            )

    try:
        if jupytext_config_file.endswith((".toml", "jupytext")):
            import toml

            doc = toml.loads(stream)
            if jupytext_config_file.endswith(PYPROJECT_FILE):
                return doc["tool"]["jupytext"]
            else:
                return doc

        if jupytext_config_file.endswith((".yml", ".yaml")):
            return yaml.safe_load(stream)

        if jupytext_config_file.endswith(".json"):
            return json.loads(stream)

        return PyFileConfigLoader(jupytext_config_file).load_config()
    except (ValueError, NameError) as err:
        raise JupytextConfigurationError(
            "The Jupytext configuration file {} is incorrect: {}".format(
                jupytext_config_file, err
            )
        )


def load_jupytext_configuration_file(config_file, stream=None):
    """Read and validate a Jupytext configuration file, and return a JupytextConfiguration object"""
    config_dict = parse_jupytext_configuration_file(config_file, stream)
    config = validate_jupytext_configuration_file(config_file, config_dict)
    # formats can be a dict prefix => format
    if isinstance(config.formats, dict):
        config.formats = [
            (prefix[:-1] if prefix.endswith("/") else prefix) + "///" + fmt
            for prefix, fmt in config.formats.items()
        ]
    config.formats = short_form_multiple_formats(config.formats)
    if isinstance(config.notebook_extensions, str):
        config.notebook_extensions = config.notebook_extensions.split(",")
    return config


def load_jupytext_config(nb_file):
    """Return the jupytext configuration file in the same folder, or in a parent folder, of the current file, if any"""
    config_file = find_jupytext_configuration_file(nb_file)
    if config_file is None:
        return None
    if os.path.isfile(nb_file) and os.path.samefile(config_file, nb_file):
        return None
    config_file = find_jupytext_configuration_file(nb_file)
    return load_jupytext_configuration_file(config_file)


def validate_jupytext_configuration_file(config_file, config_dict):
    """Turn a dict-like config into a JupytextConfiguration object"""
    if config_dict is None:
        return None
    try:
        config = JupytextConfiguration(**config_dict)
    except TraitError as err:
        raise JupytextConfigurationError(
            "The Jupytext configuration file {} is incorrect: {}".format(
                config_file, err
            )
        )
    invalid_options = set(config_dict).difference(dir(JupytextConfiguration()))
    if any(invalid_options):
        raise JupytextConfigurationError(
            "The Jupytext configuration file {} is incorrect: options {} are not supported".format(
                config_file, ",".join(invalid_options)
            )
        )
    return config


def notebook_formats(nbk, config, path, fallback_on_current_fmt=True):
    """Return the list of formats for the current notebook"""
    metadata = nbk.get("metadata")
    jupytext_metadata = metadata.get("jupytext", {})
    formats = (
        jupytext_metadata.get("formats")
        or metadata.get("jupytext_formats")
        or (config.default_formats(path) if config else None)
    )

    if not formats:
        if not fallback_on_current_fmt:
            return None
        text_repr = jupytext_metadata.get("text_representation", {})
        ext = os.path.splitext(path)[1]
        fmt = {"extension": ext}

        if ext == text_repr.get("extension") and text_repr.get("format_name"):
            fmt["format_name"] = text_repr.get("format_name")

        formats = [fmt]

    formats = long_form_multiple_formats(
        formats, metadata, auto_ext_requires_language_info=False
    )

    # Set preferred formats if no format name has been given yet
    if config:
        formats = [
            preferred_format(f, config.preferred_jupytext_formats_save) for f in formats
        ]

    return formats
