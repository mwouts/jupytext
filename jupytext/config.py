"""Find and read Jupytext configuration files"""
import os
import yaml
from traitlets import Unicode, Float, Bool, Enum
from traitlets.config import Configurable
from traitlets.config.loader import JSONFileConfigLoader, PyFileConfigLoader
from .formats import (
    NOTEBOOK_EXTENSIONS,
    long_form_one_format,
    long_form_multiple_formats,
)
from .paired_paths import (
    base_path,
    InconsistentPath,
)

VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES = [
    "jupytext",
    "jupytext.toml",
    "jupytext.yml",
    "jupytext.yaml",
    "jupytext.json",
    "jupytext.py",
]

VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES.extend(
    ["." + filename for filename in VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES]
)


class JupytextConfiguration(Configurable):
    default_jupytext_formats = Unicode(
        u"",
        help="Save notebooks to these file extensions. "
        "Can be any of ipynb,Rmd,md,jl,py,R,nb.jl,nb.py,nb.R "
        "comma separated. If you want another format than the "
        "default one, append the format name to the extension, "
        "e.g. ipynb,py:percent to save the notebook to "
        "hydrogen/spyder/vscode compatible scripts",
        config=True,
    )

    preferred_jupytext_formats_save = Unicode(
        u"",
        help="Preferred format when saving notebooks as text, per extension. "
        'Use "jl:percent,py:percent,R:percent" if you want to save '
        "Julia, Python and R scripts in the double percent format and "
        'only write "jupytext_formats": "py" in the notebook metadata.',
        config=True,
    )

    preferred_jupytext_formats_read = Unicode(
        u"",
        help="Preferred format when reading notebooks from text, per "
        'extension. Use "py:sphinx" if you want to read all python '
        "scripts as Sphinx gallery scripts.",
        config=True,
    )

    default_notebook_metadata_filter = Unicode(
        u"",
        help="Cell metadata that should be save in the text representations. "
        "Examples: 'all', '-all', 'widgets,nteract', 'kernelspec,jupytext-all'",
        config=True,
    )

    default_cell_metadata_filter = Unicode(
        u"",
        help="Notebook metadata that should be saved in the text representations. "
        "Examples: 'all', 'hide_input,hide_output'",
        config=True,
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

    outdated_text_notebook_margin = Float(
        1.0,
        help="Refuse to overwrite inputs of a ipynb notebooks with those of a "
        "text notebook when the text notebook plus margin is older than "
        "the ipynb notebook",
        config=True,
    )

    default_cell_markers = Unicode(
        u"",
        help='Start and end cell markers for the light format, comma separated. Use "{{{,}}}" to mark cells'
        'as foldable regions in Vim, and "region,endregion" to mark cells as Vscode/PyCharm regions',
        config=True,
    )

    notebook_extensions = Unicode(
        u",".join(NOTEBOOK_EXTENSIONS),
        help="A comma separated list of notebook extensions",
        config=True,
    )

    def set_default_format_options(self, format_options, read=False):
        """Set default format option"""
        if self.default_notebook_metadata_filter:
            format_options.setdefault(
                "notebook_metadata_filter", self.default_notebook_metadata_filter
            )
        if self.default_cell_metadata_filter:
            format_options.setdefault(
                "cell_metadata_filter", self.default_cell_metadata_filter
            )
        if self.comment_magics is not None:
            format_options.setdefault("comment_magics", self.comment_magics)
        if self.split_at_heading:
            format_options.setdefault("split_at_heading", self.split_at_heading)
        if not read and self.default_cell_markers:
            format_options.setdefault("cell_markers", self.default_cell_markers)
        if read and self.sphinx_convert_rst2md:
            format_options.setdefault("rst2md", self.sphinx_convert_rst2md)

    def default_formats(self, path):
        """Return the default formats, if they apply to the current path #157"""
        formats = long_form_multiple_formats(self.default_jupytext_formats)
        for fmt in formats:
            try:
                base_path(path, fmt)
                return self.default_jupytext_formats
            except InconsistentPath:
                continue

        return None


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


def find_jupytext_configuration_file(dir):
    """Return the first jupytext configuration file in the current directory, or any parent directory"""
    for filename in VALID_JUPYTEXT_CONFIGURATION_FILE_NAMES:
        full_path = os.path.join(dir, filename)
        if os.path.isfile(full_path):
            return full_path
    parent_dir = os.path.dirname(dir)
    if os.path.samefile(dir, parent_dir):
        return None
    return find_jupytext_configuration_file(parent_dir)


def load_jupytext_configuration_file(path):
    """Read the Jupytext config files, and return a JupytextConfig object"""

    if path.endswith((".toml", "jupytext")):
        import toml

        config = toml.load(path)
        return JupytextConfiguration(**config)

    if path.endswith((".yml", ".yaml")):
        with open(path) as fp:
            config = yaml.safe_load(fp)
        return JupytextConfiguration(**config)

    if path.endswith(".py"):
        return JupytextConfiguration(**PyFileConfigLoader(path).load_config())

    return JupytextConfiguration(**JSONFileConfigLoader(path).load_config())
