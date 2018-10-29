"""Command line conversion tools `jupytext` and `nbsrc`
"""

import os
import sys
import argparse
from .jupytext import readf, reads, writef, writes
from .formats import NOTEBOOK_EXTENSIONS, JUPYTEXT_FORMATS, check_file_version, one_format_as_string, parse_one_format
from .combine import combine_inputs_with_outputs
from .compare import test_round_trip_conversion, NotebookDifference
from .languages import _SCRIPT_EXTENSIONS
from .version import __version__


def convert_notebook_files(nb_files, fmt, input_format=None, output=None,
                           test_round_trip=False, test_round_trip_strict=False, stop_on_first_error=True,
                           update=True):
    """
    Export R markdown notebooks, python or R scripts, or Jupyter notebooks,
    to the opposite format
    :param nb_files: one or more notebooks files
    :param input_format: input format, e.g. "py:percent"
    :param fmt: destination format, e.g. "py:percent"
    :param output: None, destination file, or '-' for stdout
    :param test_round_trip: should round trip conversion be tested?
    :param test_round_trip_strict: should round trip conversion be tested, with strict notebook comparison?
    :param stop_on_first_error: when testing, should we stop on first error, or compare the full notebook?
    :param update: preserve the current outputs of .ipynb file
    when possible
    :return:
    """

    ext, format_name = parse_one_format(fmt)
    if ext not in NOTEBOOK_EXTENSIONS:
        raise TypeError('Destination extension {} is not a notebook'.format(ext))

    if not nb_files:
        if not input_format:
            raise ValueError('Reading notebook from the standard input requires the --from field.')
        parse_one_format(input_format)
        nb_files = [sys.stdin]

    if len(nb_files) > 1 and output:
        raise ValueError("Output argument can only be used with a single notebook")

    notebooks_in_error = 0

    for nb_file in nb_files:
        if nb_file == sys.stdin:
            dest = None
            current_ext, _ = parse_one_format(input_format)
            notebook = reads(nb_file.read(), ext=current_ext, format_name=format_name)
        else:
            dest, current_ext = os.path.splitext(nb_file)
            notebook = None

        if current_ext not in NOTEBOOK_EXTENSIONS:
            raise TypeError('File {} is not a notebook'.format(nb_file))

        if input_format:
            format_ext, format_name = parse_one_format(input_format)
            if current_ext != format_ext:
                raise ValueError("Format extension in --from field '{}' is "
                                 "not consistent with notebook extension "
                                 "'{}'".format(format_name, current_ext))
        else:
            input_format = None

        if not notebook:
            notebook = readf(nb_file, format_name=format_name)

        if test_round_trip or test_round_trip_strict:
            try:
                test_round_trip_conversion(notebook, ext, format_name, update,
                                           allow_expected_differences=not test_round_trip_strict,
                                           stop_on_first_error=stop_on_first_error)
            except NotebookDifference as error:
                notebooks_in_error += 1
                print('{}: {}'.format(nb_file, str(error)))
            continue

        if output == '-':
            sys.stdout.write(writes(notebook, ext=ext, format_name=format_name))
            continue

        if output:
            dest, dest_ext = os.path.splitext(output)
            if dest_ext != ext:
                raise TypeError('Destination extension {} is not consistent'
                                'with format {} '.format(dest_ext, ext))

        if os.path.isfile(dest + ext):
            if update:
                action = ' (destination file updated)'
            else:
                action = ' (destination file replaced)'
        else:
            action = ''

        sys.stdout.write("[jupytext] Converting '{org_file}' to '{dest_file}'{format}{action}\n"
                         .format(dest_file=dest + ext,
                                 org_file=nb_file,
                                 format=" using format '{}'".format(format_name) if format_name else '',
                                 action=action))

        save_notebook_as(notebook, nb_file, dest + ext, format_name, update)

    if notebooks_in_error:
        exit(notebooks_in_error)


def save_notebook_as(notebook, nb_file, nb_dest, format_name, combine):
    """Save notebook to file, in desired format"""
    if combine and os.path.isfile(nb_dest) and os.path.splitext(nb_dest)[1] == '.ipynb':
        check_file_version(notebook, nb_file, nb_dest)
        nb_outputs = readf(nb_dest)
        combine_inputs_with_outputs(notebook, nb_outputs)

    writef(notebook, nb_dest, format_name=format_name)


def canonize_format(format_or_ext, file_path=None):
    """Return the canonical form of the format"""
    if not format_or_ext:
        if file_path and file_path != '-':
            _, ext = os.path.splitext(file_path)
            if ext not in NOTEBOOK_EXTENSIONS:
                raise TypeError('Output extensions should be in {}'.format(", ".join(NOTEBOOK_EXTENSIONS)))
            return ext.replace('.', '')

        raise ValueError('Please specificy either --to or --output')

    if '.' + format_or_ext in NOTEBOOK_EXTENSIONS:
        return format_or_ext

    if ':' in format_or_ext:
        return format_or_ext

    for ext in _SCRIPT_EXTENSIONS:
        if _SCRIPT_EXTENSIONS[ext]['language'] == format_or_ext:
            return ext.replace('.', '')

    return {'notebook': 'ipynb', 'markdown': 'md', 'rmarkdown': 'Rmd'}[format_or_ext]


def cli_jupytext(args=None):
    """Command line parser for jupytext"""
    parser = argparse.ArgumentParser(
        description='Jupyter notebooks as markdown documents, '
                    'Julia, Python or R scripts')

    notebook_formats = (['notebook', 'rmarkdown', 'markdown'] +
                        [_SCRIPT_EXTENSIONS[ext]['language'] for ext in _SCRIPT_EXTENSIONS] +
                        [ext.replace('.', '') for ext in NOTEBOOK_EXTENSIONS] +
                        [one_format_as_string(fmt.extension, fmt.format_name)
                         for fmt in JUPYTEXT_FORMATS])

    parser.add_argument('--to',
                        choices=notebook_formats,
                        help="Destination format")
    parser.add_argument('--from',
                        dest='input_format',
                        choices=notebook_formats,
                        help="Input format")
    parser.add_argument('notebooks',
                        help='One or more notebook(s) to be converted. Input '
                             'is read from stdin when no notebook is '
                             'provided , but then the --from field is '
                             'mandatory',
                        nargs='*')
    parser.add_argument('-o', '--output',
                        help='Destination file. Defaults to original file, '
                             'with extension changed to destination format. '
                             "Use '-' for printing the notebook on stdout.")
    parser.add_argument('--update', action='store_true',
                        help='Preserve outputs of .ipynb destination '
                             '(when file exists and inputs match)')
    test = parser.add_mutually_exclusive_group()
    test.add_argument('--test', dest='test', action='store_true',
                      help='Test that notebook is stable under '
                           'round trip conversion, up to expected changes')
    test.add_argument('--test-strict', dest='test_strict', action='store_true',
                      help='Test that notebook is strictly stable under '
                           'round trip conversion')
    parser.add_argument('-x', '--stop', dest='stop_on_first_error', action='store_true',
                        help='Stop on first round trip conversion error, and report stack traceback')
    parser.add_argument('--version', action='store_true',
                        help="Show jupytext's version number and exit")
    args = parser.parse_args(args)

    if args.version:
        return args

    args.to = canonize_format(args.to, args.output)

    if args.input_format:
        args.input_format = canonize_format(args.input_format)
        if not args.notebooks and not args.output:
            args.output = '-'

    if not args.input_format:
        if not args.notebooks:
            raise ValueError('Please specificy either --from or notebooks')

    if args.update and not (args.test or args.test_strict) and args.to != 'ipynb':
        raise ValueError('--update works exclusively with --to notebook ')

    return args


def jupytext(args=None):
    """Entry point for the jupytext script"""
    try:
        args = cli_jupytext(args)

        if args.version:
            sys.stdout.write(__version__ + '\n')
            return

        convert_notebook_files(nb_files=args.notebooks,
                               fmt=args.to,
                               input_format=args.input_format,
                               output=args.output,
                               test_round_trip=args.test,
                               test_round_trip_strict=args.test_strict,
                               stop_on_first_error=args.stop_on_first_error,
                               update=args.update)
    except ValueError as err:  # (ValueError, TypeError, IOError) as err:
        print('jupytext: error: ' + str(err))
        exit(1)
