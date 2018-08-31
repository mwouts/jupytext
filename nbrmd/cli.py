"""Command line conversion tools `nbrmd` and `nbsrc`
"""

import os
import argparse
from nbrmd import readf, writef, writes
from nbrmd import NOTEBOOK_EXTENSIONS
from .combine import combine_inputs_with_outputs
from .compare import test_round_trip_conversion
from .file_format_version import check_file_version


def convert_notebook_files(nb_files, nb_dest,
                           test_round_trip=False, preserve_outputs=True):
    """
    Export R markdown notebooks, python or R scripts, or Jupyter notebooks,
    to the opposite format
    :param nb_files: one or more notebooks files
    :param nb_dest: destination file, extension ('.py') or format ('py')
    :param test_round_trip: should round trip conversion be tested?
    :param preserve_outputs: preserve the current outputs of .ipynb file
    when possible
    :return:
    """

    if len(nb_files) > 1 and nb_dest not in NOTEBOOK_EXTENSIONS:
        raise ValueError(
            "Converting multiple files requires "
            "that destination be one of '{}'".format(
                "', '".join(NOTEBOOK_EXTENSIONS)))

    for nb_file in nb_files:
        file, current_ext = os.path.splitext(nb_file)
        if current_ext not in NOTEBOOK_EXTENSIONS:
            raise TypeError('File {} is not a notebook'.format(nb_file))

        notebook = readf(nb_file)
        dest, dest_ext = os.path.splitext(nb_dest)
        if not dest_ext:
            dest = file
            if nb_dest in NOTEBOOK_EXTENSIONS:
                dest_ext = nb_dest
            else:
                dest_ext = '.' + nb_dest

        if dest_ext not in NOTEBOOK_EXTENSIONS:
            raise TypeError('Destination extension {} is not a notebook'
                            .format(dest_ext))

        if test_round_trip:
            test_round_trip_conversion(notebook, dest_ext, preserve_outputs)

        if '.' in nb_dest:
            save_notebook_as(notebook, nb_file, dest + dest_ext,
                             preserve_outputs)
        elif not test_round_trip:
            print(writes(notebook, ext=dest_ext))


def save_notebook_as(notebook, nb_file, nb_dest, combine):
    """Save notebook to file, in desired format"""
    if combine and os.path.isfile(nb_dest) and \
            os.path.splitext(nb_dest)[1] == '.ipynb':
        check_file_version(notebook, nb_file, nb_dest)
        nb_outputs = readf(nb_dest)
        combine_inputs_with_outputs(notebook, nb_outputs)

    writef(notebook, nb_dest)


def cli_nbrmd(args=None):
    """Command line parser for nbrmd"""
    parser = argparse.ArgumentParser(
        description='Jupyter notebooks as markdown documents, '
                    'Python or R scripts')
    parser.add_argument('notebooks',
                        help='One or more notebook(s) '
                             'to be converted, with extension among'
                             "'{}'".format("', '".join(NOTEBOOK_EXTENSIONS)),
                        nargs='+')
    parser.add_argument('to',
                        help="Destination notebook 'notebook.md', "
                             "extension '.md', "
                             "or format 'md' (for on screen display)")
    parser.add_argument('-p', '--preserve_outputs', action='store_true',
                        help='Preserve outputs of .ipynb destination '
                             '(when file exists and inputs match)')
    parser.add_argument('--test', dest='test', action='store_true',
                        help='Test that notebook is stable under '
                             'round trip conversion')
    return parser.parse_args(args)


def nbrmd(args=None):
    """Entry point for the nbrmd script"""
    args = cli_nbrmd(args)
    convert_notebook_files(nb_files=args.notebooks, nb_dest=args.to,
                           test_round_trip=args.test,
                           preserve_outputs=args.preserve_outputs)
