"""Command line conversion tools `jupytext` and `nbsrc`
"""

import os
import argparse
from .jupytext import readf, writef, writes
from .formats import NOTEBOOK_EXTENSIONS, check_file_version
from .combine import combine_inputs_with_outputs
from .compare import test_round_trip_conversion


def convert_notebook_files(nb_files, ext, output=None,
                           test_round_trip=False, preserve_outputs=True):
    """
    Export R markdown notebooks, python or R scripts, or Jupyter notebooks,
    to the opposite format
    :param nb_files: one or more notebooks files
    :param ext: extension of destination
    :param output: None, destination file, or '-' for stdout
    :param test_round_trip: should round trip conversion be tested?
    :param preserve_outputs: preserve the current outputs of .ipynb file
    when possible
    :return:
    """

    if len(nb_files) > 1 and output:
        raise ValueError(
            "Output argument can only be used with a single notebook")

    for nb_file in nb_files:
        dest, current_ext = os.path.splitext(nb_file)
        if current_ext not in NOTEBOOK_EXTENSIONS:
            raise TypeError('File {} is not a notebook'.format(nb_file))

        if ext not in NOTEBOOK_EXTENSIONS:
            raise TypeError('Destination extension {} is not a notebook'
                            .format(nb_file))

        notebook = readf(nb_file)
        if test_round_trip:
            test_round_trip_conversion(notebook, ext, preserve_outputs)
            continue

        if output == '-':
            print(writes(notebook, ext=ext))
            continue

        if output:
            dest, dest_ext = os.path.splitext(output)
            if dest_ext != ext:
                raise TypeError('Destination extension {} is not consistent'
                                'with format {} '.format(dest_ext, ext))

        save_notebook_as(notebook, nb_file, dest + ext, preserve_outputs)


def save_notebook_as(notebook, nb_file, nb_dest, combine):
    """Save notebook to file, in desired format"""
    if combine and os.path.isfile(nb_dest) and \
            os.path.splitext(nb_dest)[1] == '.ipynb':
        check_file_version(notebook, nb_file, nb_dest)
        nb_outputs = readf(nb_dest)
        combine_inputs_with_outputs(notebook, nb_outputs)

    writef(notebook, nb_dest)


def cli_jupytext(args=None):
    """Command line parser for jupytext"""
    parser = argparse.ArgumentParser(
        description='Jupyter notebooks as markdown documents, '
                    'Julia, Python or R scripts')

    parser.add_argument(
        '--to',
        choices=['notebook', 'python', 'julia', 'r', 'markdown',
                 'rmarkdown'] + [ext.replace('.', '') for ext in
                                 NOTEBOOK_EXTENSIONS],
        help="Destination format")
    parser.add_argument('notebooks',
                        help='One or more notebook(s) to be converted',
                        nargs='+')
    parser.add_argument('-o', '--output',
                        help='Destination file. Defaults to original file, '
                             'with extension changed to destination format. '
                             "Use '-' for printing the notebook on stdout.")
    parser.add_argument('--update', action='store_true',
                        help='Preserve outputs of .ipynb destination '
                             '(when file exists and inputs match)')
    parser.add_argument('--test', dest='test', action='store_true',
                        help='Test that notebook is stable under '
                             'round trip conversion')
    args = parser.parse_args(args)

    if not args.to:
        if args.output and args.output != '-':
            _, ext = os.path.splitext(args.output)
        else:
            raise TypeError('Please specificy either --to or --output')
    elif args.to in NOTEBOOK_EXTENSIONS:
        pass
    elif '.' + args.to in NOTEBOOK_EXTENSIONS:
        ext = '.' + args.to
    else:
        ext = {'notebook': '.ipynb',
               'python': '.py',
               'julia': '.jl',
               'r': '.R',
               'markdown': '.md',
               'rmarkdown': '.Rmd'}[args.to]

    if ext not in NOTEBOOK_EXTENSIONS:
        raise TypeError('Output extensions should be in {}'
                        .format(", ".join(NOTEBOOK_EXTENSIONS)))

    if args.update and ext != '.ipynb':
        raise ValueError('--update works exclusively with --to notebook')

    args.to = ext

    return args


def jupytext(args=None):
    """Entry point for the jupytext script"""
    try:
        args = cli_jupytext(args)
        convert_notebook_files(nb_files=args.notebooks,
                               ext=args.to,
                               output=args.output,
                               test_round_trip=args.test,
                               preserve_outputs=args.update)
    except (ValueError, TypeError, IOError) as err:
        print('jupytext: error: ' + str(err))
        exit(1)
