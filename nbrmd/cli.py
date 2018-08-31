"""Command line conversion tools `nbrmd` and `nbsrc`
"""

import os
import argparse
from nbformat import writes as ipynb_writes
from nbrmd import readf, writef
from nbrmd import writes
from .languages import default_language_from_metadata_and_ext
from .combine import combine_inputs_with_outputs
from .compare import test_round_trip_conversion
from .file_format_version import check_file_version


def convert(nb_files, markdown, in_place=True,
            test_round_trip=False, combine=True):
    """
    Export R markdown notebooks, python or R scripts, or Jupyter notebooks,
    to the opposite format
    :param nb_files: one or more notebooks
    :param markdown: R markdown to Jupyter, or scripts to Jupyter?
    :param in_place: should result of conversion be stored in file
    with opposite extension?
    :param test_round_trip: should round trip conversion be tested?
    :param combine: should the current outputs of .ipynb file be preserved,
    when a cell with corresponding input is found in .Rmd/.py or .R file?
    :return:
    """
    for nb_file in nb_files:
        file, ext = os.path.splitext(nb_file)
        if markdown:
            fmt = 'R Markdown'
            if ext not in ['.ipynb', '.Rmd']:
                raise TypeError(
                    'File {} is neither a Jupyter (.ipynb) nor a '
                    'R Markdown (.Rmd) notebook'.format(nb_file))
        else:
            fmt = 'source'
            if ext not in ['.ipynb', '.py', '.R']:
                raise TypeError(
                    'File {} is neither a Jupyter (.ipynb) nor a '
                    'python script (.py), nor a R script (.R)'.format(nb_file))

        notebook = readf(nb_file)
        main_language = default_language_from_metadata_and_ext(notebook, ext)
        ext_dest = '.Rmd' if markdown else '.R' \
            if main_language == 'R' else '.py'

        if test_round_trip:
            test_round_trip_conversion(notebook, ext_dest, combine)

        if in_place:
            if ext == '.ipynb':
                nb_dest = file + ext_dest
                print('Jupyter notebook "{}" being converted to '
                      '{} "{}"'.format(nb_file, fmt, nb_dest))
            else:
                nb_dest = file + '.ipynb'
                print('{} "{}" being converted to '
                      'Jupyter notebook "{}"'
                      .format(fmt.title(), nb_file, nb_dest))

            convert_notebook_in_place(notebook, nb_file, nb_dest, combine)
        elif not test_round_trip:
            if ext == '.ipynb':
                print(writes(notebook, ext=ext_dest))
            else:
                print(ipynb_writes(notebook))


def convert_notebook_in_place(notebook, nb_file, nb_dest, combine):
    """File to file notebook conversion"""
    if combine and os.path.isfile(nb_dest) and \
            os.path.splitext(nb_dest)[1] == '.ipynb':
        check_file_version(notebook, nb_file, nb_dest)
        nb_outputs = readf(nb_dest)
        combine_inputs_with_outputs(notebook, nb_outputs)

    writef(notebook, nb_dest)


def add_common_arguments(parser):
    """Add the common nbrmd and nbsrc arguments"""
    parser.add_argument('-p', '--preserve_outputs', action='store_true',
                        help='Preserve outputs of .ipynb '
                             'notebook when file exists and inputs match')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='Store the result of conversion '
                             'to file with opposite extension')
    group.add_argument('-t', '--test', action='store_true',
                       help='Test whether the notebook or script is '
                            'preserved in a round trip conversion')


def cli_nbrmd(args=None):
    """Command line parser for nbrmd"""
    parser = argparse.ArgumentParser(description='Jupyter notebook '
                                                 'from/to R Markdown')
    parser.add_argument('notebooks',
                        help='One or more .ipynb or .Rmd notebook(s) '
                             'to be converted to the alternate form',
                        nargs='+')
    add_common_arguments(parser)
    return parser.parse_args(args)


def cli_nbsrc(args=None):
    """Command line parser for nbsrc"""
    parser = argparse.ArgumentParser(description='Jupyter notebook '
                                                 'from/to R or Python script')
    parser.add_argument('notebooks',
                        help='One or more .ipynb or .R or .py script(s) '
                             'to be converted to the alternate form',
                        nargs='+')
    add_common_arguments(parser)
    return parser.parse_args(args)


def nbsrc(args=None):
    """Entry point for the nbsrc script"""
    args = cli_nbsrc(args)
    convert(args.notebooks, False, args.in_place,
            args.test, args.preserve_outputs)


def nbrmd(args=None):
    """Entry point for the nbrmd script"""
    args = cli_nbrmd(args)
    convert(args.notebooks, True, args.in_place, args.test,
            args.preserve_outputs)
