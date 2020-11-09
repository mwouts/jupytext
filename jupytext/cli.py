"""`jupytext` as a command line tool"""

import os
import re
import sys
import glob
import shlex
import subprocess
import argparse
import json
import warnings
from copy import copy
from tempfile import NamedTemporaryFile
from .jupytext import read, reads, write, writes
from .formats import JUPYTEXT_FORMATS
from .formats import _VALID_FORMAT_OPTIONS, _BINARY_FORMAT_OPTIONS, check_file_version
from .formats import (
    long_form_one_format,
    long_form_multiple_formats,
    short_form_one_format,
    check_auto_ext,
)
from .languages import _SCRIPT_EXTENSIONS
from .header import recursive_update
from .paired_paths import (
    paired_paths,
    base_path,
    full_path,
    InconsistentPath,
    find_base_path_and_format,
)
from .pairs import write_pair, latest_inputs_and_outputs, read_pair
from .combine import combine_inputs_with_outputs
from .compare import test_round_trip_conversion, NotebookDifference, compare
from .config import load_jupytext_config, prepare_notebook_for_save
from .kernels import kernelspec_from_language, find_kernel_specs, get_kernel_spec
from .reraise import reraise
from .version import __version__

try:
    from nbconvert.preprocessors import ExecutePreprocessor
except ImportError as ep_err:
    ExecutePreprocessor = reraise(ep_err)


def system(*args, **kwargs):
    """Execute the given bash command"""
    kwargs.setdefault("stdout", subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, _ = proc.communicate()
    if proc.returncode:
        raise SystemExit(proc.returncode)
    return out.decode("utf-8")


def str2bool(value):
    """Parse Yes/No/Default string
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse"""
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if value.lower() in ("no", "false", "f", "n", "0"):
        return False
    if value.lower() in ("d", "default", ""):
        return None
    raise argparse.ArgumentTypeError("Expected: (Y)es/(T)rue/(N)o/(F)alse/(D)efault")


def parse_jupytext_args(args=None):
    """Command line parser for jupytext"""

    parser = argparse.ArgumentParser(
        description="Jupyter Notebooks as Markdown Documents, Julia, Python or R Scripts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Input
    parser.add_argument(
        "notebooks",
        help="One or more notebook(s). "
        "Notebook is read from stdin when this argument is empty.",
        nargs="*",
    )
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Ignore the notebook argument, and instead apply Jupytext "
        "on the notebooks found in the git index, which have an "
        "extension that matches the (optional) --from argument.",
    )
    parser.add_argument(
        "--from",
        dest="input_format",
        help="Jupytext format for the input(s). Inferred from the "
        "file extension and content when missing.",
    )
    # Destination format & act on metadata
    parser.add_argument(
        "--to",
        dest="output_format",
        help=(
            "The destination format: 'ipynb', 'markdown' or 'script', or a file extension: "
            "'md', 'Rmd', 'jl', 'py', 'R', ..., 'auto' (script extension matching the notebook language), "
            "or a combination of an extension and a format name, e.g. {} ".format(
                ", ".join(
                    set(
                        "md:{}".format(fmt.format_name)
                        for fmt in JUPYTEXT_FORMATS
                        if fmt.extension == ".md"
                    )
                )
            )
            + " or {}. ".format(
                ", ".join(
                    set(
                        "py:{}".format(fmt.format_name)
                        for fmt in JUPYTEXT_FORMATS
                        if fmt.extension == ".py"
                    )
                )
            )
            + "The default format for scripts is the 'light' format, "
            "which uses few cell markers (none when possible). "
            "Alternatively, a format compatible with many editors is the "
            "'percent' format, which uses '# %%%%' as cell markers. "
            "The main formats (markdown, light, percent) preserve "
            "notebooks and text documents in a roundtrip. Use the "
            "--test and and --test-strict commands to test the roundtrip on your files. "
            "Read more about the available formats at "
            "https://jupytext.readthedocs.io/en/latest/formats.html"
        ),
    )

    # Destination file
    parser.add_argument(
        "-o",
        "--output",
        help="Destination file. Defaults to the original file, "
        "with prefix/suffix/extension changed according to "
        "the destination format. "
        "Use '-' to print the notebook on stdout.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Preserve the output cells when the destination "
        "notebook is an .ipynb file that already exists",
    )

    parser.add_argument(
        "--set-formats",
        type=str,
        help="Turn the notebook or text document to one or more alternative representations "
        "with e.g. '--set-formats ipynb,py:light'. "
        "The --set-formats option also triggers the creation/update of all paired files",
    )

    # Action: convert(default)/version/list paired paths/sync/apply/test
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--sync",
        "-s",
        help="Synchronize the content of the paired representations of "
        "the given notebook. Input cells are taken from the file that "
        "was last modified, and outputs are read from the ipynb file, "
        "if present.",
        action="store_true",
    )
    action.add_argument(
        "--paired-paths",
        "-p",
        help="List the locations of the alternative representations for this notebook.",
        action="store_true",
    )
    parser.add_argument(
        "--format-options",
        "--opt",
        action="append",
        help="Set format options with e.g. "
        "'--opt comment_magics=true' or '--opt notebook_metadata_filter=-kernelspec'.",
    )
    parser.add_argument(
        "--update-metadata",
        default={},
        type=json.loads,
        help="Update the notebook metadata with the desired dictionary. "
        "Argument must be given in JSON format. For instance, if you "
        "want to activate a pairing in the generated file, use e.g. "
        """--update-metadata '{"jupytext":{"formats":"ipynb,py:light"}}' """
        "See also the --opt and --set-formats options for other ways "
        "to operate on the Jupytext metadata.",
    )
    action.add_argument(
        "--warn-only",
        "-w",
        action="store_true",
        help="Only issue a warning and continue processing other notebooks "
        "when the conversion of a given notebook fails",
    )
    action.add_argument(
        "--test",
        action="store_true",
        help="Test that the notebook is stable under a round trip conversion, "
        "up to the expected changes",
    )
    action.add_argument(
        "--test-strict",
        action="store_true",
        help="Test that the notebook is strictly stable under a round trip conversion",
    )
    parser.add_argument(
        "--stop",
        "-x",
        dest="stop_on_first_error",
        action="store_true",
        help="In --test mode, stop on first round trip conversion error, and report stack traceback",
    )

    # Pipe notebook inputs into other commands
    parser.add_argument(
        "--pipe",
        action="append",
        help="Pipe the text representation (in format --pipe-fmt) of the notebook into "
        "another program, and read the notebook back. For instance, reformat "
        "your notebook with: "
        "'jupytext notebook.ipynb --pipe black' "
        "If you want to reformat it and sync the paired representation, execute: "
        "'jupytext notebook.ipynb --sync --pipe black' "
        "In case the program that you want to execute does not accept pipes, use {} "
        "as a placeholder for a temporary file name into which jupytext will "
        "write the text representation of the notebook, e.g.: "
        "jupytext notebook.ipynb --pipe 'black {}'",
    )
    parser.add_argument(
        "--check",
        action="append",
        help="Pipe the text representation (in format --pipe-fmt) of the notebook into "
        "another program, and test that the returned value is non zero. For "
        "instance, test that your notebook is pep8 compliant with: "
        "'jupytext notebook.ipynb --check flake8' "
        "or run pytest on your notebook with: "
        "'jupytext notebook.ipynb --check pytest' "
        "In case the program that you want to execute does not accept pipes, use {} "
        "as a placeholder for a temporary file name into which jupytext will "
        "write the text representation of the notebook, e.g.: "
        "jupytext notebook.ipynb --check 'pytest {}'",
    )
    parser.add_argument(
        "--pipe-fmt",
        default="auto:percent",
        help="The format in which the notebook should be piped to other programs, "
        "when using the --pipe and/or --check commands.",
    )

    # Execute the notebook
    parser.add_argument(
        "--set-kernel",
        "-k",
        type=str,
        help="Set the kernel with the given name on the notebook. "
        "Use '--set-kernel -' to set a kernel matching the current "
        "environment on Python notebooks, and matching the notebook "
        "language otherwise (get the list of available kernels with "
        "'jupyter kernelspec list')",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the notebook with the given kernel",
    )
    parser.add_argument(
        "--run-path",
        type=str,
        help="Execute the notebook at the given path (defaults to the notebook parent directory)",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Quiet mode: do not comment about files being updated or created",
    )

    action.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show jupytext's version number and exit",
    )

    return parser.parse_args(args)


def jupytext(args=None):
    """Entry point for the jupytext script"""
    args = parse_jupytext_args(args)

    def log(text):
        if not args.quiet:
            sys.stdout.write(text + "\n")

    if args.version:
        log(__version__)
        return 0

    if args.pre_commit:
        if args.notebooks:
            raise ValueError(
                "--pre-commit takes notebooks from the git index. Do not pass any notebook here."
            )
        args.notebooks = notebooks_in_git_index(args.input_format)
        log("[jupytext] Notebooks in git index are:")
        for nb_file in args.notebooks:
            log(nb_file)

    # Read notebook from stdin
    if not args.notebooks:
        if not args.pre_commit:
            args.notebooks = ["-"]

    if args.set_formats is not None:
        # Replace empty string with None
        args.update_metadata = recursive_update(
            args.update_metadata, {"jupytext": {"formats": args.set_formats or None}}
        )
        args.sync = True

    if args.paired_paths:
        if len(args.notebooks) != 1:
            raise ValueError("--paired-paths applies to a single notebook")
        print_paired_paths(args.notebooks[0], args.input_format)
        return 1

    if args.run_path:
        args.execute = True

    if (
        (args.test or args.test_strict)
        and not args.output_format
        and not args.output
        and not args.sync
    ):
        raise ValueError("Please provide one of --to, --output or --sync")

    if (
        not args.output_format
        and not args.output
        and not args.sync
        and not args.pipe
        and not args.check
        and not args.update_metadata
        and not args.format_options
        and not args.set_kernel
        and not args.execute
    ):
        raise ValueError(
            "Please provide one of --to, --output, --set-formats, --sync, --pipe, "
            "--check, --update-metadata, --format-options, --set-kernel or --execute"
        )

    if args.output and len(args.notebooks) != 1:
        raise ValueError("Please input a single notebook when using --output")

    # Warn if '--to' is used in place of '--output'
    if (
        not args.output
        and args.output_format
        and "." in args.output_format
        and not args.output_format.startswith(".")
        and "//" not in args.output_format
    ):

        def single_line(msg, *args, **kwargs):
            return "[warning] {}\n".format(msg)

        warnings.formatwarning = single_line
        warnings.warn(
            "You have passed a file name to the '--to' option, "
            "when a format description was expected. Maybe you want to use the '-o' option instead?"
        )

    if args.input_format:
        args.input_format = long_form_one_format(args.input_format)

    if args.output_format:
        args.output_format = long_form_one_format(args.output_format)
        set_format_options(args.output_format, args.format_options)

    # Wildcard extension on Windows #202
    notebooks = []
    for pattern in args.notebooks:
        if "*" in pattern or "?" in pattern:
            # Exclude the .jupytext.py configuration file
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
                sys.stderr.write("[jupytext] Error: {}\n".format(str(err)))

    return exit_code


def jupytext_single_file(nb_file, args, log):
    """Apply the jupytext commmand, with given arguments, to a single file"""
    if nb_file == "-" and args.sync:
        msg = "Missing notebook path."
        if args.set_formats is not None and os.path.isfile(args.set_formats):
            msg += " Maybe you mean 'jupytext --sync {}' ?".format(args.set_formats)
        raise ValueError(msg)

    nb_dest = args.output or (
        None
        if not args.output_format
        else (
            "-"
            if nb_file == "-"
            else full_path(base_path(nb_file, args.input_format), args.output_format)
        )
    )

    config = load_jupytext_config(os.path.abspath(nb_file))

    # Just acting on metadata / pipe => save in place
    if not nb_dest and not args.sync:
        nb_dest = nb_file

    if nb_dest == "-":
        args.quiet = True

    # I. ### Read the notebook ###
    fmt = copy(args.input_format) or {}
    if not fmt:
        ext = os.path.splitext(nb_file)[1]
        if ext:
            fmt = {"extension": ext}
    if fmt:
        if config:
            config.set_default_format_options(fmt)
        set_format_options(fmt, args.format_options)
    log(
        "[jupytext] Reading {}{}".format(
            nb_file if nb_file != "-" else "stdin",
            " in format {}".format(short_form_one_format(fmt))
            if "extension" in fmt
            else "",
        )
    )

    notebook = read(nb_file, fmt=fmt)
    if "extension" in fmt and "format_name" not in fmt:
        text_representation = notebook.metadata.get("jupytext", {}).get(
            "text_representation", {}
        )
        if text_representation.get("extension") == fmt["extension"]:
            fmt["format_name"] = text_representation["format_name"]

    if config and "formats" not in notebook.metadata.get("jupytext", {}):
        default_formats = config.default_formats(nb_file)
        if default_formats:
            notebook.metadata.setdefault("jupytext", {})["formats"] = default_formats

    # Compute actual extension when using script/auto, and update nb_dest if necessary
    dest_fmt = args.output_format
    if dest_fmt and config:
        config.set_default_format_options(dest_fmt)
    if dest_fmt and dest_fmt["extension"] == ".auto":
        dest_fmt = check_auto_ext(dest_fmt, notebook.metadata, "--to")
        if not args.output and nb_file != "-":
            nb_dest = full_path(base_path(nb_file, args.input_format), dest_fmt)

    # Set the kernel
    set_kernel = args.set_kernel
    if (
        (not set_kernel)
        and args.execute
        and notebook.metadata.get("kernelspec", {}).get("name") is None
    ):
        set_kernel = "-"

    if set_kernel:
        if set_kernel == "-":
            language = (
                notebook.metadata.get("jupytext", {}).get("main_language")
                or notebook.metadata["kernelspec"]["language"]
            )

            if not language:
                raise ValueError(
                    "Cannot infer a kernel as notebook language is not defined"
                )

            kernelspec = kernelspec_from_language(language)
        else:
            try:
                kernelspec = get_kernel_spec(set_kernel)
            except KeyError:
                raise KeyError(
                    "Please choose a kernel name among {}".format(
                        find_kernel_specs().keys()
                    )
                )

            kernelspec = {
                "name": args.set_kernel,
                "language": kernelspec.language,
                "display_name": kernelspec.display_name,
            }

        log("[jupytext] Setting kernel {}".format(kernelspec.get("name")))
        args.update_metadata["kernelspec"] = kernelspec

    # Are we updating a text file that has a metadata filter? #212
    if args.update_metadata or args.format_options:
        if (
            notebook.metadata.get("jupytext", {}).get("notebook_metadata_filter")
            == "-all"
        ):
            notebook.metadata.get("jupytext", {}).pop("notebook_metadata_filter")

    # Update the metadata
    if args.update_metadata:
        log(
            "[jupytext] Updating notebook metadata with '{}'".format(
                json.dumps(args.update_metadata)
            )
        )

        if (
            "kernelspec" in args.update_metadata
            and "main_language" in notebook.metadata.get("jupytext", {})
        ):
            notebook.metadata["jupytext"].pop("main_language")

        recursive_update(notebook.metadata, args.update_metadata)

    # Read paired notebooks, except if the pair is being created
    if args.sync:
        set_prefix_and_suffix(fmt, notebook, nb_file)
        if args.set_formats is None:
            try:
                notebook, inputs_nb_file, outputs_nb_file = load_paired_notebook(
                    notebook, fmt, nb_file, log
                )
            except NotAPairedNotebook as err:
                sys.stderr.write("[jupytext] Warning: " + str(err) + "\n")
                return 0

    # II. ### Apply commands onto the notebook ###
    # Pipe the notebook into the desired commands
    prefix = None if nb_file == "-" else os.path.splitext(os.path.basename(nb_file))[0]
    for cmd in args.pipe or []:
        notebook = pipe_notebook(notebook, cmd, args.pipe_fmt, prefix=prefix)

    # and/or test the desired commands onto the notebook
    for cmd in args.check or []:
        pipe_notebook(notebook, cmd, args.pipe_fmt, update=False, prefix=prefix)

    # Execute the notebook
    if args.execute:
        kernel_name = notebook.metadata.get("kernelspec", {}).get("name")
        log("[jupytext] Executing notebook with kernel {}".format(kernel_name))
        exec_proc = ExecutePreprocessor(timeout=None, kernel_name=kernel_name)

        if nb_dest is not None and nb_dest != "-":
            nb_path = os.path.dirname(nb_dest)
        elif nb_file != "-":
            nb_path = os.path.dirname(nb_file)
        else:
            nb_path = None

        run_path = args.run_path or nb_path
        if args.run_path and not os.path.isdir(run_path):
            # is this a relative directory?
            for base_dir in [nb_path, os.getcwd()]:
                try_path = os.path.join(base_dir, run_path)
                if os.path.isdir(try_path):
                    run_path = try_path
                    break
            if not os.path.isdir(run_path):
                raise ValueError(
                    "--run-path={} is not a valid path".format(args.run_path)
                )

        if run_path:
            resources = {"metadata": {"path": run_path}}
        else:
            resources = {}
        exec_proc.preprocess(notebook, resources=resources)

    # III. ### Possible actions ###
    modified = args.update_metadata or args.pipe or args.execute
    # a. Test round trip conversion
    if args.test or args.test_strict:
        try:
            # Round trip from an ipynb document
            if fmt["extension"] == ".ipynb":
                test_round_trip_conversion(
                    notebook,
                    dest_fmt,
                    update=args.update,
                    allow_expected_differences=not args.test_strict,
                    stop_on_first_error=args.stop_on_first_error,
                )

            # Round trip from a text file
            else:
                with open(nb_file) as fp:
                    org_text = fp.read()

                # If the destination is not ipynb, we convert to/back that format
                if dest_fmt["extension"] != ".ipynb":
                    dest_text = writes(notebook, fmt=dest_fmt)
                    notebook = reads(dest_text, fmt=dest_fmt)

                text = writes(notebook, fmt=fmt)

                if args.test_strict:
                    compare(text, org_text)
                else:
                    # we ignore the YAML header in the comparison #414
                    comment = _SCRIPT_EXTENSIONS.get(fmt["extension"], {}).get(
                        "comment", ""
                    )
                    # white spaces between the comment char and the YAML delimiters are allowed
                    if comment:
                        comment = comment + r"\s*"
                    yaml_header = re.compile(
                        r"^{comment}---\s*\n.*\n{comment}---\s*\n".format(
                            comment=comment
                        ),
                        re.MULTILINE | re.DOTALL,
                    )
                    compare(
                        re.sub(yaml_header, "", text), re.sub(yaml_header, "", org_text)
                    )

        except (NotebookDifference, AssertionError) as err:
            sys.stdout.write("{}: {}".format(nb_file, str(err)))
            return 1
        return 0

    # b. Output to the desired file or format
    if nb_dest:
        if nb_dest == nb_file and not dest_fmt:
            dest_fmt = fmt

        # Test consistency between dest name and output format
        if dest_fmt and nb_dest != "-":
            base_path(nb_dest, dest_fmt)

        # Describe what jupytext is doing
        if os.path.isfile(nb_dest) and args.update:
            if not nb_dest.endswith(".ipynb"):
                raise ValueError("--update is only for ipynb files")
            action = " (destination file updated)"
            check_file_version(notebook, nb_file, nb_dest)
            notebook = combine_inputs_with_outputs(notebook, read(nb_dest), fmt=fmt)
        elif os.path.isfile(nb_dest):
            action = " (destination file replaced)"
        else:
            action = ""

        log(
            "[jupytext] Writing {nb_dest}{format}{action}".format(
                nb_dest=nb_dest,
                format=" in format " + short_form_one_format(dest_fmt)
                if dest_fmt and "format_name" in dest_fmt
                else "",
                action=action,
            )
        )
        write(notebook, nb_dest, fmt=dest_fmt)
        if args.pre_commit:
            system("git", "add", nb_dest)

    # c. Synchronize paired notebooks
    if args.sync:
        # Also update the original notebook if the notebook was modified
        if modified:
            inputs_nb_file = outputs_nb_file = None

        def write_function(path, fmt):
            # Do not write the ipynb file if it was not modified
            # But, always write text representations to make sure they are the most recent
            if path == inputs_nb_file and path == outputs_nb_file:
                return
            log("[jupytext] Updating '{}'".format(path))
            write(notebook, path, fmt=fmt)
            if args.pre_commit:
                system("git", "add", path)

        formats = prepare_notebook_for_save(notebook, config, nb_file)
        write_pair(nb_file, formats, write_function)
    elif (
        os.path.isfile(nb_file)
        and nb_dest.endswith(".ipynb")
        and not nb_file.endswith(".ipynb")
        and notebook.metadata.get("jupytext", {}).get("formats") is not None
    ):
        # Update the original text file timestamp, as required by our Content Manager
        # Otherwise Jupyter will refuse to open the paired notebook #335
        log("[jupytext] Sync timestamp of '{}'".format(nb_file))
        os.utime(nb_file, None)

    return 0


def notebooks_in_git_index(fmt):
    """Return the list of modified and deleted ipynb files in the git index that match the given format"""
    git_status = system("git", "status", "--porcelain")
    re_modified = re.compile(r"^[AM]+\s+(?P<name>.*)", re.MULTILINE)
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
    formats = notebook.metadata.get("jupytext", {}).get("formats")
    if formats:
        for path, _ in paired_paths(nb_file, fmt, formats):
            if path != nb_file:
                sys.stdout.write(path + "\n")


def set_format_options(fmt, format_options):
    """Apply the desired format options to the format description fmt"""
    if not format_options:
        return

    for opt in format_options:
        try:
            key, value = opt.split("=")
        except ValueError:
            raise ValueError(
                "Format options are expected to be of the form key=value, not '{}'".format(
                    opt
                )
            )

        if key not in _VALID_FORMAT_OPTIONS:
            raise ValueError(
                "'{}' is not a valid format option. Expected one of '{}'".format(
                    key, "', '".join(_VALID_FORMAT_OPTIONS)
                )
            )

        if key in _BINARY_FORMAT_OPTIONS:
            value = str2bool(value)

        fmt[key] = value


def set_prefix_and_suffix(fmt, notebook, nb_file):
    """Add prefix and suffix information from jupytext.formats if format and path matches"""
    for alt_fmt in long_form_multiple_formats(
        notebook.metadata.get("jupytext", {}).get("formats")
    ):
        if alt_fmt["extension"] == fmt["extension"] and fmt.get(
            "format_name"
        ) == alt_fmt.get("format_name"):
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
    formats = notebook.metadata.get("jupytext", {}).get("formats")

    if not formats:
        raise NotAPairedNotebook("'{}' is not a paired notebook".format(nb_file))

    formats = long_form_multiple_formats(formats)
    _, fmt_with_prefix_suffix = find_base_path_and_format(nb_file, formats)
    fmt.update(fmt_with_prefix_suffix)

    def get_timestamp(path):
        if not os.path.isfile(path):
            return None
        return os.lstat(path).st_mtime

    def read_one_file(path, fmt):
        if path == nb_file:
            return notebook

        log("[jupytext] Loading '{}'".format(path))
        return read(path, fmt=fmt)

    inputs, outputs = latest_inputs_and_outputs(nb_file, fmt, formats, get_timestamp)
    notebook = read_pair(inputs, outputs, read_one_file)

    return notebook, inputs.path, outputs.path


def exec_command(command, input=None, capture=False):
    """Execute the desired command, and pipe the given input into it"""
    assert isinstance(command, list)
    sys.stdout.write("[jupytext] Executing {}\n".format(" ".join(command)))
    process = subprocess.Popen(
        command,
        **(
            dict(stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            if input is not None
            else {}
        )
    )
    out, err = process.communicate(input=input)
    if out and not capture:
        sys.stdout.write(out.decode("utf-8"))
    if err:
        sys.stderr.write(err.decode("utf-8"))

    if process.returncode:
        sys.stderr.write(
            "[jupytext] Error: The command '{}' exited with code {}\n".format(
                " ".join(command), process.returncode
            )
        )
        raise SystemExit(process.returncode)

    return out


def pipe_notebook(notebook, command, fmt="py:percent", update=True, prefix=None):
    """Pipe the notebook, in the desired representation, to the given command. Update the notebook
    with the returned content if desired."""
    if command in ["black", "flake8", "autopep8"]:
        command = command + " -"
    elif command in ["pytest", "unittest"]:
        command = command + " {}"

    fmt = long_form_one_format(
        fmt, notebook.metadata, auto_ext_requires_language_info=False
    )
    fmt = check_auto_ext(fmt, notebook.metadata, "--pipe-fmt")
    text = writes(notebook, fmt)

    command = shlex.split(command)
    if "{}" in command:
        if prefix is not None:
            prefix = prefix + (" " if " " in prefix else "_")
        tmp_file_args = dict(
            mode="w+",
            encoding="utf8",
            prefix=prefix,
            suffix=fmt["extension"],
            delete=False,
        )
        try:
            tmp = NamedTemporaryFile(**tmp_file_args)
        except TypeError:
            # NamedTemporaryFile does not have an 'encoding' argument on pypy
            tmp_file_args.pop("encoding")
            tmp = NamedTemporaryFile(**tmp_file_args)
        try:
            tmp.write(text)
            tmp.close()

            exec_command(
                [cmd if cmd != "{}" else tmp.name for cmd in command], capture=update
            )

            if not update:
                return notebook

            piped_notebook = read(tmp.name, fmt=fmt)
        finally:
            os.remove(tmp.name)
    else:
        cmd_output = exec_command(command, text.encode("utf-8"), capture=update)

        if not update:
            return notebook

        if not cmd_output:
            sys.stderr.write(
                "[jupytext] The command '{}' had no output. As a result, the notebook is empty. "
                "Is this expected? If not, use --check rather than --pipe for this command.".format(
                    command
                )
            )

        piped_notebook = reads(cmd_output.decode("utf-8"), fmt)

    if fmt["extension"] != ".ipynb":
        piped_notebook = combine_inputs_with_outputs(piped_notebook, notebook, fmt)

    # Remove jupytext / text_representation entry
    piped_notebook.metadata.pop("jupytext")
    if "jupytext" in notebook.metadata:
        piped_notebook.metadata["jupytext"] = notebook.metadata["jupytext"]

    return piped_notebook
