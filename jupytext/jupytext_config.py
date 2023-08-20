from argparse import ArgumentParser

from .labconfig import LabConfig

# list of subcommands - filled by SubCommand.__init__
SUBCOMMANDS = []


class SubCommand:
    def __init__(self, name, help):
        self.name = name
        self.help = help
        SUBCOMMANDS.append(self)

    def main(self, args):
        """
        return 0 if all goes well
        """
        print(
            f"{self.__class__.__name__}: redefine main() to implement this subcommand"
        )
        return 1


class List(SubCommand):
    def __init__(self):
        super().__init__("list", "Display current settings in labconfig/")

    def main(self, args):
        LabConfig().read().list()
        return 0

    def fill_parser(self, subparser):
        pass


class SetDefaultViewer(SubCommand):
    def __init__(self):
        super().__init__("set-default-viewer", "Set default viewers for JupyterLab")

    def main(self, args):
        LabConfig().read().set_default_viewers(args.language).write()
        return 0

    def fill_parser(self, subparser):
        subparser.add_argument(
            "language", nargs="*", help="the language(s) that the viewer applies to"
        )


# create the subcommands
List()
SetDefaultViewer()


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    for subcommand in SUBCOMMANDS:
        subparser = subparsers.add_parser(subcommand.name, help=subcommand.help)
        subparser.set_defaults(subcommand=subcommand)
        subcommand.fill_parser(subparser)
    args = parser.parse_args()
    return args.subcommand.main(args)
