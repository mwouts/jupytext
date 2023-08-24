"""
the code for
jupytext-config set-default-viewer
and related subcommands
"""

import sys
from argparse import ArgumentParser

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
        print(
            f"{self.__class__.__name__}: redefine main() to implement this subcommand"
        )
        return 1


class ListDefaultViewer(SubCommand):
    def __init__(self):
        super().__init__(
            "list-default-viewer", "Display current settings in labconfig/"
        )

    def main(self, args):
        LabConfig().read().list_default_viewer()
        return 0

    def fill_parser(self, subparser):
        pass


class SetDefaultViewer(SubCommand):
    def __init__(self):
        super().__init__("set-default-viewer", "Set default viewers for JupyterLab")

    def main(self, args):
        LabConfig().read().set_default_viewers(args.doctype).write()
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
        LabConfig().read().unset_default_viewers(args.doctype).write()
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
    subparsers = parser.add_subparsers(required=True)
    for subcommand in SUBCOMMANDS:
        subparser = subparsers.add_parser(subcommand.name, help=subcommand.help)
        subparser.set_defaults(subcommand=subcommand)
        subcommand.fill_parser(subparser)
    args = parser.parse_args(sys.argv[1:] or ["--help"])
    return args.subcommand.main(args)
