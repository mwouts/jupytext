"""`jupytext` as a command line tool"""

import os
import re
import sys
import glob
import subprocess
import argparse
import json
from copy import copy
from .jupytext import read, reads, write, writes
from .formats import _VALID_FORMAT_OPTIONS, _BINARY_FORMAT_OPTIONS, check_file_version
from .formats import long_form_one_format, long_form_multiple_formats, short_form_one_format, auto_ext_from_metadata
from .header import recursive_update
from .paired_paths import paired_paths, base_path, full_path, InconsistentPath
from .combine import combine_inputs_with_outputs
from .compare import test_round_trip_conversion, NotebookDifference, compare
from .kernels import kernelspec_from_language, find_kernel_specs, get_kernel_spec
from .reraise import reraise
from .version import __version__

try:
    from nbconvert.preprocessors import ExecutePreprocessor
except ImportError as ep_err:
    ExecutePreprocessor = reraise(ep_err)


def system(*args, **kwargs):
    """Execute the given bash command"""
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, _ = proc.communicate()
    if proc.returncode:
        raise SystemExit(proc.returncode)
    return out.decode('utf-8')


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


def parse_jupytext_args(args=None):
    """Command line parser for jupytext"""

    class RawTextArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter,
                                               argparse.ArgumentDefaultsHelpFormatter):
        """Keep the raw formatting in command line help, plus show the default values"""
        pass

    parser = argparse.ArgumentParser(
        description='Jupyter notebooks as markdown documents, Julia, Python or R scripts',
        formatter_class=RawTextArgumentDefaultsHelpFormatter)

    # Input
    parser.add_argument('notebooks',
                        help='One or more notebook(s).\n'
                             'Notebook is read from stdin when this argument\n'
                             'is empty.',
                        nargs='*')
    parser.add_argument('--from',
                        dest='input_format',
                        help='Jupytext format for the input(s). Inferred from the\n'
                             'file extension and content when missing.')
    parser.add_argument('--pre-commit',
                        action='store_true',
                        help='Ignore the notebook argument, and instead apply Jupytext\n'
                             'on the notebooks found in the git index, which have an\n'
                             'extension that matches the (optional) --from argument.\n')
    # Destination format & act on metadata
    parser.add_argument('--to',
                        help="Destination format: either one of 'notebook', 'markdown',\n"
                             "'rmarkdown', 'script', any valid notebook extension, or a\n"
                             "full format description, i.e.\n"
                             "'[prefix_path//][suffix.]ext[:format_name]")
    parser.add_argument('--format-options', '--opt',
                        action='append',
                        help='Set format options with e.g.\n'
                             '    --opt comment_magics=true\n'
                             '    --opt notebook_metadata_filter=-kernelspec.\n')
    parser.add_argument('--set-formats',
                        type=str,
                        help='Set jupytext.formats metadata to the given value. Use this to\n'
                             'activate pairing on a notebook, with e.g.\n'
                             '    --set-formats ipynb,py:light.\n'
                             'The --set-formats option also triggers the creation/update\n'
                             'of all paired files')
    parser.add_argument('--set-kernel', '-k',
                        type=str,
                        help="Set the kernel with the given name on the notebook.\n"
                             "Use\n"
                             "    --set-kernel -\n"
                             "to set a kernel matching the current\n"
                             "environment on Python notebooks, and matching the notebook\n"
                             "language otherwise (get the list of available kernels with\n"
                             "'jupyter kernelspec list')")
    parser.add_argument('--update-metadata',
                        default={},
                        type=json.loads,
                        help='Update the notebook metadata with the desired dictionary.\n'
                             'Argument must be given in JSON format. For instance, if you\n'
                             'want to activate a pairing in the generated file, use e.g.\n'
                             """    --update-metadata '{"jupytext":{"formats":"ipynb,py:light"}}'\n"""
                             "See also the '--opt' and '--set-formats' options for other ways\n"
                             "to operate on the Jupytext metadata."
                        )

    # Destination file
    parser.add_argument('-o', '--output',
                        help="Destination file. Defaults to the original file,\n"
                             "with prefix/suffix/extension changed according to\n"
                             "the destination format.\n"
                             "Use '-' to print the notebook on stdout.")
    parser.add_argument('--update', action='store_true',
                        help='Preserve the output cells when the destination\n'
                             'notebook is a .ipynb file that already exists')

    # Action: convert(default)/version/list paired paths/sync/apply/test
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--version', '-v',
                        action='store_true',
                        help="Show jupytext's version number and exit")
    action.add_argument('--paired-paths', '-p',
                        help='List the locations of the alternative representations\n'
                             'for this notebook.',
                        action='store_true')
    action.add_argument('--sync', '-s',
                        help='Synchronize the content of the paired representations of\n'
                             'the given notebook. Input cells are taken from the file that\n'
                             'was last modified, and outputs are read from the ipynb file,\n'
                             'if present.',
                        action='store_true')
    action.add_argument('--warn-only', '-w',
                        action='store_true',
                        help='Only issue a warning and continue processing other notebooks\n'
                             'when the conversion of a given notebook fails')
    action.add_argument('--test',
                        action='store_true',
                        help='Test that notebook is stable under a round trip conversion,\n'
                             'up to the expected changes')
    action.add_argument('--test-strict',
                        action='store_true',
                        help='Test that notebook is strictly stable under a round trip\n'
                             'conversion')
    parser.add_argument('--stop', '-x',
                        dest='stop_on_first_error',
                        action='store_true',
                        help='In --test mode, stop on first round trip conversion error, and report\n'
                             'stack traceback')

    # Pipe notebook inputs into other commands
    parser.add_argument('--pipe',
                        action='append',
                        help='Pipe the text representation of the notebook into another\n'
                             'program, and read the notebook back. For instance, reformat\n'
                             'your notebook with:\n'
                             "    jupytext notebook.ipynb --pipe black\n"
                             'If you want to reformat it and sync the paired representation, execute:\n'
                             "    jupytext notebook.ipynb --sync --pipe black\n")
    parser.add_argument('--check',
                        action='append',
                        help='Pipe the text representation of the notebook into another program,\n'
                             'and test that the returned value is non zero. For instance,\n'
                             'test that your notebook is pep8 compliant with:\n'
                             "    jupytext notebook.ipynb --check flake8\n")
    parser.add_argument('--pipe-fmt',
                        default='auto:percent',
                        help='The format in which the notebook should be piped to other programs,\n'
                             'when using the --pipe and/or --check commands.')

    # Execute the notebook
    parser.add_argument('--execute',
                        action='store_true',
                        help='Execute the notebook with the given kernel')

    parser.add_argument('--quiet', '-q',
                        action='store_true',
                        default=False,
                        help='Quiet mode: do not comment about files being updated\n'
                             'or created')

    return parser.parse_args(args)


def jupytext(args=None):
    """Entry point for the jupytext script"""
    args = parse_jupytext_args(args)

    def log(text):
        if not args.quiet:
            sys.stdout.write(text + '\n')

    if args.version:
        log(__version__)
        return 0

    if args.pre_commit:
        if args.notebooks:
            raise ValueError('--pre-commit takes notebooks from the git index. Do not pass any notebook here.')
        args.notebooks = notebooks_in_git_index(args.input_format)
        log('[jupytext] Notebooks in git index are:')
        for nb_file in args.notebooks:
            log(nb_file)

    # Read notebook from stdin
    if not args.notebooks:
        if not args.pre_commit:
            args.notebooks = ['-']

    if args.set_formats is not None:
        # Replace empty string with None
        args.update_metadata = recursive_update(args.update_metadata,
                                                {'jupytext': {'formats': args.set_formats or None}})
        args.sync = True

    if args.paired_paths:
        if len(args.notebooks) != 1:
            raise ValueError('--paired-paths applies to a single notebook')
        print_paired_paths(args.notebooks[0], args.input_format)
        return 1

    if (args.test or args.test_strict) and not args.to and not args.output and not args.sync:
        raise ValueError('Please provide one of --to, --output or --sync')

    if not args.to and not args.output and not args.sync \
            and not args.pipe and not args.check \
            and not args.update_metadata and not args.set_kernel \
            and not args.execute:
        raise ValueError('Please provide one of --to, --output, --sync, --pipe, '
                         '--check, --update_metadata, --set-kernel or --execute')

    if args.output and len(args.notebooks) != 1:
        raise ValueError('Please input a single notebook when using --output')

    if args.input_format:
        args.input_format = long_form_one_format(args.input_format)

    if args.to:
        args.to = long_form_one_format(args.to)
        set_format_options(args.to, args.format_options)

    # Wildcard extension on Windows #202
    notebooks = []
    for pattern in args.notebooks:
        if '*' in pattern or '?' in pattern:
            notebooks.extend(glob.glob(pattern))
        else:
            notebooks.append(pattern)

    # Count how many file have round-trip issues when testing
    exit_code = 0
    for nb_file in notebooks:
        if not args.warn_only:
            exit_code += jupytext_single_file(nb_file, args, log)
        else:
            try:
                exit_code += jupytext_single_file(nb_file, args, log)
            except Exception as err:
                sys.stderr.write('[jupytext] Error: {}\n'.format(str(err)))

    return exit_code


def jupytext_single_file(nb_file, args, log):
    """Apply the jupytext commmand, with given arguments, to a single file"""
    if nb_file == '-' and args.sync:
        raise ValueError('Cannot sync a notebook on stdin')

    nb_dest = args.output or (None if not args.to
                              else ('-' if nb_file == '-' else
                                    full_path(base_path(nb_file, args.input_format), args.to)))

    # Just acting on metadata / pipe => save in place
    if not nb_dest and not args.sync:
        nb_dest = nb_file

    if nb_dest == '-':
        args.quiet = True

    # I. ### Read the notebook ###
    fmt = copy(args.input_format) or {}
    set_format_options(fmt, args.format_options)
    log('[jupytext] Reading {}{}'.format(
        nb_file if nb_file != '-' else 'stdin',
        ' in format {}'.format(short_form_one_format(fmt)) if 'extension' in fmt else ''))

    notebook = read(nb_file, fmt=fmt)
    if not fmt:
        text_representation = notebook.metadata.get('jupytext', {}).get('text_representation', {})
        ext = os.path.splitext(nb_file)[1]
        if text_representation.get('extension') == ext:
            fmt = {key: text_representation[key] for key in text_representation if
                   key in ['extension', 'format_name']}
        elif ext:
            fmt = {'extension': ext}

    # Compute actual extension when using script/auto, and update nb_dest if necessary
    dest_fmt = args.to
    if dest_fmt and dest_fmt['extension'] == '.auto':
        check_auto_ext(dest_fmt, notebook.metadata, '--to')
        if not args.output and nb_file != '-':
            nb_dest = full_path(base_path(nb_file, args.input_format), dest_fmt)

    # Set the kernel
    set_kernel = args.set_kernel
    if (not set_kernel) and args.execute and notebook.metadata.get('kernelspec', {}).get('name') is None:
        set_kernel = '-'

    if set_kernel:
        if set_kernel == '-':
            language = notebook.metadata.get('jupytext', {}).get('main_language') \
                       or notebook.metadata['kernelspec']['language']

            if not language:
                raise ValueError('Cannot infer a kernel as notebook language is not defined')

            kernelspec = kernelspec_from_language(language)

            if not kernelspec:
                raise ValueError('Found no kernel for {}'.format(language))
        else:
            try:
                kernelspec = get_kernel_spec(set_kernel)
            except KeyError:
                raise KeyError('Please choose a kernel name among {}'
                               .format(find_kernel_specs().keys()))

            kernelspec = {'name': args.set_kernel,
                          'language': kernelspec.language,
                          'display_name': kernelspec.display_name}

        log("[jupytext] Setting kernel {}".format(kernelspec.get('name')))
        args.update_metadata['kernelspec'] = kernelspec

    # Update the metadata
    if args.update_metadata:
        log("[jupytext] Updating notebook metadata with '{}'".format(json.dumps(args.update_metadata)))
        # Are we updating a text file that has a metadata filter? #212
        if notebook.metadata.get('jupytext', {}).get('notebook_metadata_filter') == '-all':
            notebook.metadata.get('jupytext', {}).pop('notebook_metadata_filter')
        recursive_update(notebook.metadata, args.update_metadata)

        if 'kernelspec' in args.update_metadata and 'main_language' in notebook.metadata.get('jupytext', {}):
            notebook.metadata['jupytext'].pop('main_language')

    # Read paired notebooks
    if args.sync:
        set_prefix_and_suffix(fmt, notebook, nb_file)
        try:
            notebook, inputs_nb_file, outputs_nb_file = load_paired_notebook(notebook, fmt, nb_file, log)
        except NotAPairedNotebook as err:
            sys.stderr.write('[jupytext] Warning: ' + str(err) + '\n')
            return 0

    # II. ### Apply commands onto the notebook ###
    # Pipe the notebook into the desired commands
    for cmd in args.pipe or []:
        notebook = pipe_notebook(notebook, cmd, args.pipe_fmt)

    # and/or test the desired commands onto the notebook
    for cmd in args.check or []:
        pipe_notebook(notebook, cmd, args.pipe_fmt, update=False)

    # Execute the notebook
    if args.execute:
        kernel_name = notebook.metadata.get('kernelspec', {}).get('name')
        log("[jupytext] Executing notebook with kernel {}".format(kernel_name))
        exec_proc = ExecutePreprocessor(timeout=None, kernel_name=kernel_name)
        exec_proc.preprocess(notebook, resources={})

    # III. ### Possible actions ###
    modified = args.update_metadata or args.pipe or args.execute
    # a. Test round trip conversion
    if args.test or args.test_strict:
        try:
            # Round trip from an ipynb document
            if fmt['extension'] == '.ipynb':
                test_round_trip_conversion(notebook, dest_fmt,
                                           update=args.update,
                                           allow_expected_differences=not args.test_strict,
                                           stop_on_first_error=args.stop_on_first_error)

            # Round trip from a text file
            else:
                with open(nb_file) as fp:
                    org_text = fp.read()

                # If the destination is not ipynb, we convert to/back that format
                if dest_fmt['extension'] != '.ipynb':
                    dest_text = writes(notebook, fmt=dest_fmt)
                    notebook = reads(dest_text, fmt=dest_fmt)

                text = writes(notebook, fmt=fmt)
                compare(org_text, text)

        except (NotebookDifference, AssertionError) as err:
            sys.stdout.write('{}: {}'.format(nb_file, str(err)))
            return 1
        return 0

    # b. Output to the desired file or format
    if nb_dest:
        if nb_dest == nb_file and not dest_fmt:
            dest_fmt = fmt

        # Test consistency between dest name and output format
        if dest_fmt and nb_dest != '-':
            base_path(nb_dest, dest_fmt)

        # Describe what jupytext is doing
        if os.path.isfile(nb_dest) and args.update:
            if not nb_dest.endswith('.ipynb'):
                raise ValueError('--update is only for ipynb files')
            action = ' (destination file updated)'
            check_file_version(notebook, nb_file, nb_dest)
            combine_inputs_with_outputs(notebook, read(nb_dest), fmt=fmt)
        elif os.path.isfile(nb_dest):
            action = ' (destination file replaced)'
        else:
            action = ''

        log('[jupytext] Writing {nb_dest}{format}{action}'
            .format(nb_dest=nb_dest,
                    format=' in format ' + short_form_one_format(
                        dest_fmt) if dest_fmt and 'format_name' in dest_fmt else '',
                    action=action))
        write(notebook, nb_dest, fmt=dest_fmt)
        if args.pre_commit:
            system('git', 'add', nb_dest)

    # c. Synchronize paired notebooks
    if args.sync:
        # Also update the original notebook if the notebook was modified
        if modified:
            inputs_nb_file = outputs_nb_file = None
        formats = notebook.metadata['jupytext']['formats']

        for ipynb in [True, False]:
            # Write first format last so that it is the most recent file
            for alt_path, alt_fmt in paired_paths(nb_file, fmt, formats)[::-1]:
                # Write ipynb first for compatibility with our contents manager
                if alt_path.endswith('.ipynb') != ipynb:
                    continue
                # Do not write the ipynb file if it was not modified
                # But, always write text representations to make sure they are the most recent
                if alt_path == inputs_nb_file and alt_path == outputs_nb_file:
                    continue
                log("[jupytext] Updating '{}'".format(alt_path))
                write(notebook, alt_path, fmt=alt_fmt)
                if args.pre_commit:
                    system('git', 'add', alt_path)
    elif os.path.isfile(nb_file) and nb_dest.endswith('.ipynb') and not nb_file.endswith('.ipynb'):
        # Update the original text file timestamp, as required by our Content Manager
        # Otherwise Jupyter will refuse to open the paired notebook #335
        log("[jupytext] Sync timestamp of '{}'".format(nb_file))
        os.utime(nb_file, None)

    return 0


def notebooks_in_git_index(fmt):
    """Return the list of modified and deleted ipynb files in the git index that match the given format"""
    git_status = system('git', 'status', '--porcelain')
    re_modified = re.compile(r'^[AM]+\s+(?P<name>.*)', re.MULTILINE)
    modified_files_in_git_index = re_modified.findall(git_status)
    files = []
    for nb_file in modified_files_in_git_index:
        if nb_file.startswith('"') and nb_file.endswith('"'):
            nb_file = nb_file[1:-1]
        try:
            base_path(nb_file, fmt)
            files.append(nb_file)
        except InconsistentPath:
            continue
    return files


def print_paired_paths(nb_file, fmt):
    """Display the paired paths for this notebook"""
    notebook = read(nb_file, fmt=fmt)
    formats = notebook.metadata.get('jupytext', {}).get('formats')
    if formats:
        for path, _ in paired_paths(nb_file, fmt, formats):
            if path != nb_file:
                sys.stdout.write(path + '\n')


def set_format_options(fmt, format_options):
    """Apply the desired format options to the format description fmt"""
    if not format_options:
        return

    for opt in format_options:
        try:
            key, value = opt.split('=')
        except ValueError:
            raise ValueError("Format options are expected to be of the form key=value, not '{}'".format(opt))

        if key not in _VALID_FORMAT_OPTIONS:
            raise ValueError("'{}' is not a valid format option. Expected one of '{}'"
                             .format(key, "', '".join(_VALID_FORMAT_OPTIONS)))

        if key in _BINARY_FORMAT_OPTIONS:
            value = str2bool(value)

        fmt[key] = value


def set_prefix_and_suffix(fmt, notebook, nb_file):
    """Add prefix and suffix information from jupytext.formats if format and path matches"""
    for alt_fmt in long_form_multiple_formats(notebook.metadata.get('jupytext', {}).get('formats')):
        if (alt_fmt['extension'] == fmt['extension']
                and fmt.get('format_name') == alt_fmt.get('format_name')):
            try:
                base_path(nb_file, alt_fmt)
                fmt.update(alt_fmt)
                return
            except InconsistentPath:
                continue


class NotAPairedNotebook(ValueError):
    """An error raised when a notebook is not a paired notebook"""


def load_paired_notebook(notebook, fmt, nb_file, log):
    """Update the notebook with the inputs and outputs of the most recent paired files"""
    formats = notebook.metadata.get('jupytext', {}).get('formats')

    if not formats:
        raise NotAPairedNotebook("'{}' is not a paired notebook".format(nb_file))

    max_mtime_inputs = None
    max_mtime_outputs = None
    latest_inputs = None
    latest_outputs = None
    for alt_path, alt_fmt in paired_paths(nb_file, fmt, formats):
        if not os.path.isfile(alt_path):
            continue
        info = os.lstat(alt_path)
        if not max_mtime_inputs or info.st_mtime > max_mtime_inputs:
            max_mtime_inputs = info.st_mtime
            latest_inputs, input_fmt = alt_path, alt_fmt

        if alt_path.endswith('.ipynb'):
            if not max_mtime_outputs or info.st_mtime > max_mtime_outputs:
                max_mtime_outputs = info.st_mtime
                latest_outputs = alt_path

    if latest_outputs and latest_outputs != latest_inputs:
        log("[jupytext] Loading input cells from '{}'".format(latest_inputs))
        inputs = notebook if latest_inputs == nb_file else read(latest_inputs, fmt=input_fmt)
        check_file_version(inputs, latest_inputs, latest_outputs)
        log("[jupytext] Loading output cells from '{}'".format(latest_outputs))
        outputs = notebook if latest_outputs == nb_file else read(latest_outputs)
        combine_inputs_with_outputs(inputs, outputs, fmt=input_fmt)
        return inputs, latest_inputs, latest_outputs

    log("[jupytext] Loading notebook from '{}'".format(latest_inputs))
    if latest_inputs != nb_file:
        notebook = read(latest_inputs, fmt=input_fmt)
    return notebook, latest_inputs, latest_outputs


def check_auto_ext(fmt, metadata, option):
    """Raise a ValueError when the .auto extension cannot be determined"""
    if fmt['extension'] != '.auto':
        return

    auto_ext = auto_ext_from_metadata(metadata)
    if auto_ext:
        fmt['extension'] = auto_ext
        return

    raise ValueError("The notebook does not have a 'language_info' metadata. "
                     "Please replace 'auto' with the actual language extension in the {} option (currently {})."
                     .format(option, short_form_one_format(fmt)))


def pipe_notebook(notebook, command, fmt='py:percent', update=True):
    """Pipe the notebook, in the desired representation, to the given command. Update the notebook
    with the returned content if desired."""
    if command in ['black', 'flake8', 'autopep8']:
        command = command + ' -'

    fmt = long_form_one_format(fmt, notebook.metadata, auto_ext_requires_language_info=False)
    check_auto_ext(fmt, notebook.metadata, '--pipe-fmt')
    text = writes(notebook, fmt)
    process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    cmd_output, err = process.communicate(input=text.encode('utf-8'))

    if process.returncode:
        sys.stderr.write("Command '{}' exited with code {}: {}"
                         .format(command, process.returncode, err or cmd_output))
        raise SystemExit(process.returncode)

    if not update:
        return notebook

    if not cmd_output:
        sys.stderr.write("[jupytext] The command '{}' had no output. As a result, the notebook is empty. "
                         "Is this expected? If not, use --check rather than --pipe for this command.".format(command))

    piped_notebook = reads(cmd_output.decode('utf-8'), fmt)

    if fmt['extension'] != '.ipynb':
        combine_inputs_with_outputs(piped_notebook, notebook, fmt)

    # Remove jupytext / text_representation entry
    piped_notebook.metadata.pop('jupytext')
    if 'jupytext' in notebook.metadata:
        piped_notebook.metadata['jupytext'] = notebook.metadata['jupytext']

    return piped_notebook
