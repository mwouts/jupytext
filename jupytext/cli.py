"""Command line conversion tools `jupytext` and `nbsrc`
"""

import os
import re
import sys
import subprocess
import argparse
import json
from .jupytext import readf, reads, writef, writes
from .formats import NOTEBOOK_EXTENSIONS, JUPYTEXT_FORMATS, check_file_version
from .formats import long_form_one_format
from .paired_paths import paired_paths
from .combine import combine_inputs_with_outputs
from .compare import test_round_trip_conversion, NotebookDifference
from .languages import _SCRIPT_EXTENSIONS
from .version import __version__


def convert_notebook_files(nb_files, fmt, input_format=None, output=None, pre_commit=False,
                           test_round_trip=False, test_round_trip_strict=False, stop_on_first_error=True,
                           update=True, comment_magics=None, update_metadata=None):
    """
    Export R markdown notebooks, python or R scripts, or Jupyter notebooks,
    to the opposite format
    :param nb_files: one or more notebooks files
    :param input_format: input format, e.g. "py:percent"
    :param fmt: destination format, e.g. "py:percent"
    :param output: None, destination file, or '-' for stdout
    :param pre_commit: convert notebooks in the git index?
    :param test_round_trip: should round trip conversion be tested?
    :param test_round_trip_strict: should round trip conversion be tested, with strict notebook comparison?
    :param stop_on_first_error: when testing, should we stop on first error, or compare the full notebook?
    :param update: preserve the current outputs of .ipynb file
    :param comment_magics: comment, or not, Jupyter magics when possible
    :param update_metadata: update the notebook metadata with the given JSON dictionary
    :return:
    """

    fmt = long_form_one_format(fmt)
    ext = fmt['extension']
    if ext not in NOTEBOOK_EXTENSIONS:
        raise TypeError('Destination extension {} is not a notebook'.format(ext))

    if pre_commit:
        input_format = input_format or 'ipynb'
        input_ext = long_form_one_format(input_format)['extension']
        modified, deleted = modified_and_deleted_files(input_ext)

        for file in modified:
            dest_file = file[:-len(input_ext)] + ext
            notebook = readf(file)
            writef(notebook, dest_file, fmt)
            system('git', 'add', dest_file)

        for file in deleted:
            dest_file = file[:-len(input_ext)] + ext
            system('git', 'rm', dest_file)

        return

    if not nb_files:
        if not input_format:
            raise ValueError('Reading notebook from the standard input requires the --from field.')
        input_format = long_form_one_format(input_format)
        nb_files = [sys.stdin]

    if len(nb_files) > 1 and output:
        raise ValueError("Output argument can only be used with a single notebook")

    notebooks_in_error = 0

    for nb_file in nb_files:
        if nb_file == sys.stdin:
            dest = None
            current_ext = long_form_one_format(input_format)['extension']
            notebook = reads(nb_file.read(), input_format)
        else:
            dest, current_ext = os.path.splitext(nb_file)
            notebook = None

        if current_ext not in NOTEBOOK_EXTENSIONS:
            raise TypeError('File {} is not a notebook'.format(nb_file))

        if input_format:
            if current_ext != input_format['extension']:
                raise ValueError("Format extension in --from field '{}' is "
                                 "not consistent with notebook extension "
                                 "'{}'".format(input_format, current_ext))
        else:
            input_format = None

        if not notebook:
            notebook = readf(nb_file, input_format)

        if test_round_trip or test_round_trip_strict:
            try:
                test_round_trip_conversion(notebook, fmt, update,
                                           allow_expected_differences=not test_round_trip_strict,
                                           stop_on_first_error=stop_on_first_error)
            except NotebookDifference as error:
                notebooks_in_error += 1
                print('{}: {}'.format(nb_file, str(error)))
            continue

        if update_metadata:
            try:
                updated_metadata = json.loads(update_metadata)
            except ValueError as exception:
                raise ValueError("Could not parse --update-metadata {}. JSONDecodeError: {}".
                                 format(update_metadata, str(exception)))
            recursive_update(notebook.metadata, updated_metadata)

        if comment_magics is not None:
            notebook.metadata.setdefault('jupytext', {})['comment_magics'] = comment_magics

        if output == '-':
            sys.stdout.write(writes(notebook, fmt))
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
                                 format=" using format '{}'".format(fmt['format_name']) if 'format_name' in fmt else '',
                                 action=action))

        save_notebook_as(notebook, nb_file, dest + ext, fmt, update)

    if notebooks_in_error:
        exit(notebooks_in_error)


def system(*args, **kwargs):
    """Execute the given bash command"""
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, _ = proc.communicate()
    return out


def modified_and_deleted_files(ext):
    """Return the list of modified and deleted ipynb files in the git index"""
    re_modified = re.compile(r'^[AM]+\s+(?P<name>.*{})'.format(ext.replace('.', r'\.')), re.MULTILINE)
    re_deleted = re.compile(r'^[D]+\s+(?P<name>.*{})'.format(ext.replace('.', r'\.')), re.MULTILINE)
    files = system('git', 'status', '--porcelain').decode('utf-8')
    return re_modified.findall(files), re_deleted.findall(files)


def save_notebook_as(notebook, nb_file, nb_dest, fmt, combine):
    """Save notebook to file, in desired format"""
    if combine and os.path.isfile(nb_dest) and os.path.splitext(nb_dest)[1] == '.ipynb':
        check_file_version(notebook, nb_file, nb_dest)
        nb_outputs = readf(nb_dest)
        combine_inputs_with_outputs(notebook, nb_outputs)

    writef(notebook, nb_dest, fmt)


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


def str2bool(value):
    """Parse Yes/No/Default string
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse"""
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    if value.lower() in ('d', 'default', ''):
        return None
    raise argparse.ArgumentTypeError('Expected: (Y)es/(T)rue/(N)o/(F)alse/(D)efault')


def recursive_update(target, update):
    """ Update recursively a (nested) dictionary with the content of another.
    Inspired from https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for key in update:
        value = update[key]
        if value is None:
            del target[key]
        elif isinstance(value, dict):
            target[key] = recursive_update(target.get(key, {}), value)
        else:
            target[key] = value
    return target


def cli_jupytext(args=None):
    """Command line parser for jupytext"""
    parser = argparse.ArgumentParser(
        description='Jupyter notebooks as markdown documents, Julia, Python or R scripts',
        formatter_class=argparse.RawTextHelpFormatter)

    notebook_formats = (['notebook', 'rmarkdown', 'markdown'] +
                        [_SCRIPT_EXTENSIONS[ext]['language'] for ext in _SCRIPT_EXTENSIONS] +
                        [ext.replace('.', '') for ext in NOTEBOOK_EXTENSIONS] +
                        [fmt.extension[1:] + ':' + fmt.format_name for fmt in JUPYTEXT_FORMATS])

    parser.add_argument('--to',
                        choices=notebook_formats,
                        help="Destination format")
    parser.add_argument('--from',
                        dest='input_format',
                        choices=notebook_formats,
                        help="Input format")
    parser.add_argument('notebooks',
                        help='One or more notebook(s). Input is read from stdin when no notebook '
                             'is provided, but then the --from field is mandatory',
                        nargs='*')
    parser.add_argument('--paired-paths', '-p',
                        help='Return the locations of the alternative representations for this notebook.',
                        action='store_true')
    parser.add_argument('--sync', '-s',
                        help='Synchronize the content of the paired representations of the given notebook. Input cells '
                             'are taken from the file that was last modified, and outputs are read from the ipynb file,'
                             ' if present.',
                        action='store_true')
    parser.add_argument('--pre-commit', action='store_true',
                        help="""Run Jupytext on the ipynb files in the git index.
Create a pre-commit hook with:

echo '#!/bin/sh
jupytext --to py:light --pre-commit' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit""")
    parser.add_argument('-o', '--output',
                        help='Destination file. Defaults to original file, '
                             'with extension changed to destination format. '
                             "Use '-' for printing the notebook on stdout.")
    parser.add_argument('--update', action='store_true',
                        help='Preserve outputs of .ipynb destination '
                             '(when file exists and inputs match)')
    parser.add_argument('--comment-magics',
                        type=str2bool,
                        nargs='?',
                        default=None,
                        help='Should Jupyter magic commands be commented? (Y)es/(T)rue/(N)o/(F)alse/(D)efault')
    parser.add_argument('--update-metadata',
                        default=None,
                        help='Update the notebook metadata with the desired dictionary. Argument must be given in JSON '
                             'format. For instance, if you want to activate a pairing in the generated file, '
                             """use e.g. '{"jupytext":{"formats":"ipynb,py:light"}}'""")
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

    if args.input_format:
        args.input_format = canonize_format(args.input_format)
        if not args.notebooks and not args.output:
            args.output = '-'

    if args.paired_paths:
        if len(args.notebooks) != 1:
            raise ValueError('--paired-paths applies to a single notebook')
        return args

    if args.sync:
        if not args.notebooks:
            raise ValueError('Please give the path to at least one notebook')
        return args

    if not args.input_format:
        if not args.notebooks and not args.pre_commit:
            raise ValueError('Please specificy either --from, --pre-commit or notebooks')

    args.to = canonize_format(args.to, args.output)

    if args.update and not (args.test or args.test_strict) and args.to != 'ipynb':
        raise ValueError('--update works exclusively with --to notebook ')

    if args.pre_commit:
        if args.notebooks:
            raise ValueError('--pre-commit takes notebooks from the git index. Do not pass any notebook here.')
        if args.test or args.test_strict:
            raise ValueError('--pre-commit cannot be used with --test or --test-strict')

    return args


def sync_paired_notebooks(nb_file, nb_fmt):
    """Read the notebook from the given file, read the inputs and outputs from the most recent text and ipynb
    representation, and update all paired files."""
    notebook = readf(nb_file, nb_fmt)
    formats = notebook.metadata.get('jupytext', {}).get('formats')
    if not formats:
        sys.stderr.write("[jupytext] '{}' is not paired to any other file\n".format(nb_file))
        return

    max_mtime_inputs = None
    max_mtime_outputs = None
    latest_inputs = None
    latest_outputs = None
    for path, fmt in paired_paths(nb_file, formats):
        if not os.path.isfile(path):
            continue
        info = os.lstat(path)
        if not max_mtime_inputs or info.st_mtime > max_mtime_inputs:
            max_mtime_inputs = info.st_mtime
            latest_inputs, input_fmt = path, fmt

        if path.endswith('.ipynb'):
            if not max_mtime_outputs or info.st_mtime > max_mtime_outputs:
                max_mtime_outputs = info.st_mtime
                latest_outputs = path

    if latest_outputs and latest_outputs != latest_inputs[0]:
        sys.stdout.write("[jupytext] Loading input cells from '{}'\n".format(latest_inputs))
        inputs = notebook if latest_inputs == nb_file else readf(latest_inputs, input_fmt)
        sys.stdout.write("[jupytext] Loading output cells from '{}'\n".format(latest_outputs))
        outputs = notebook if latest_outputs == nb_file else readf(latest_outputs)
        notebook = combine_inputs_with_outputs(inputs, outputs)
    else:
        sys.stdout.write("[jupytext] Loading notebook from '{}'\n".format(latest_inputs))
        notebook = notebook if latest_inputs == nb_file else readf(latest_inputs, input_fmt)

    for path, fmt in paired_paths(nb_file, formats):
        if path == latest_inputs and (path == latest_outputs or not path.endswith('.ipynb')):
            continue
        sys.stdout.write("[jupytext] Updating '{}'\n".format(path))
        writef(notebook, path, fmt)


def jupytext(args=None):
    """Entry point for the jupytext script"""
    try:
        args = cli_jupytext(args)

        if args.version:
            sys.stdout.write(__version__ + '\n')
            return

        if args.paired_paths:
            main_path = args.notebooks[0]
            notebook = readf(main_path, args.input_format)
            formats = notebook.metadata.get('jupytext', {}).get('formats')
            if formats:
                for path, _ in paired_paths(main_path, formats):
                    if path != main_path:
                        sys.stdout.write(path + '\n')
            return

        if args.sync:
            for nb_file in args.notebooks:
                sync_paired_notebooks(nb_file, args.input_format)
            return

        convert_notebook_files(nb_files=args.notebooks,
                               fmt=args.to,
                               input_format=args.input_format,
                               output=args.output,
                               pre_commit=args.pre_commit,
                               test_round_trip=args.test,
                               test_round_trip_strict=args.test_strict,
                               stop_on_first_error=args.stop_on_first_error,
                               update=args.update,
                               comment_magics=args.comment_magics,
                               update_metadata=args.update_metadata)
    except (ValueError, TypeError, IOError) as err:
        sys.stderr.write('jupytext: error: ' + str(err) + '\n')
        exit(1)
