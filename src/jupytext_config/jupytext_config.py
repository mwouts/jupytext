"""
the code for
jupytext-config set-default-viewer
and related subcommands
"""

import sys
from argparse import ArgumentParser
from pathlib import Path

import jupyter_core.paths as jupyter_core_paths

from .labconfig import LabConfig


class SubCommand:
    """
    a subcommand for jupytext-config
    """

    def __init__(self, name, help):
        self.name = name
        self.help = help

    def main(self, args):
        """
        return 0 if all goes well
        """
        raise NotImplementedError()  # pragma: no cover


class ListDefaultViewer(SubCommand):
    def __init__(self):
        super().__init__("list-default-viewer", "Display current settings in labconfig")

    def main(self, args):
        LabConfig(settings_file=args.settings_file).read().list_default_viewer()
        return 0

    def fill_parser(self, subparser):
        pass


class SetDefaultViewer(SubCommand):
    def __init__(self):
        super().__init__("set-default-viewer", "Set default viewers for JupyterLab")

    def main(self, args):
        LabConfig(settings_file=args.settings_file).read().set_default_viewers(
            args.doctype
        ).write()
        return 0

    def fill_parser(self, subparser):
        subparser.add_argument(
            "doctype",
            nargs="*",
            help=f"the document types to be associated with the notebook editor; "
            f"defaults to {' '.join(LabConfig.DOCTYPES)}",
        )


class UnsetDefaultViewer(SubCommand):
    def __init__(self):
        super().__init__("unset-default-viewer", "Unset default viewers for JupyterLab")

    def main(self, args):
        LabConfig(settings_file=args.settings_file).read().unset_default_viewers(
            args.doctype
        ).write()
        return 0

    def fill_parser(self, subparser):
        subparser.add_argument(
            "doctype",
            nargs="*",
            help=f"the document types for which the default viewer will be unset; "
            f"defaults to {' '.join(LabConfig.DOCTYPES)}",
        )


# create the subcommands
SUBCOMMANDS = [
    ListDefaultViewer(),
    SetDefaultViewer(),
    UnsetDefaultViewer(),
]


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--settings-file",
        default=Path(jupyter_core_paths.jupyter_config_dir())
        / "labconfig"
        / "default_setting_overrides.json",
    )
    subparsers = parser.add_subparsers(required=True)
    for subcommand in SUBCOMMANDS:
        subparser = subparsers.add_parser(subcommand.name, help=subcommand.help)
        subparser.set_defaults(subcommand=subcommand)
        subcommand.fill_parser(subparser)
    args = parser.parse_args(sys.argv[1:] or ["--help"])
    return args.subcommand.main(args)
