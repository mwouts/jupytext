"""Functions to read or write paired notebooks"""

from collections import namedtuple
from .formats import (
    long_form_one_format,
    long_form_multiple_formats,
    check_file_version,
)
from .paired_paths import find_base_path_and_format, full_path, paired_paths
from .combine import combine_inputs_with_outputs

NotebookFile = namedtuple("notebook_file", "path fmt timestamp")


def write_pair(path, formats, write_one_file):
    """
    Call the function 'write_one_file' on each of the paired path/formats
    """
    formats = long_form_multiple_formats(formats)
    base, _ = find_base_path_and_format(path, formats)

    # Save as ipynb first
    return_value = None
    value = None
    for fmt in formats[::-1]:
        if fmt["extension"] != ".ipynb":
            continue

        alt_path = full_path(base, fmt)
        value = write_one_file(alt_path, fmt)
        if alt_path == path:
            return_value = value

    # And then to the other formats, in reverse order so that
    # the first format is the most recent
    for fmt in formats[::-1]:
        if fmt["extension"] == ".ipynb":
            continue

        alt_path = full_path(base, fmt)
        value = write_one_file(alt_path, fmt)
        if alt_path == path:
            return_value = value

    # Update modified timestamp to match that of the pair #207
    if isinstance(return_value, dict) and "last_modified" in return_value:
        return_value["last_modified"] = value["last_modified"]

    return return_value


def latest_inputs_and_outputs(
    path, fmt, formats, get_timestamp, contents_manager_mode=False
):
    """Given a notebook path, its format and paired formats, and a function that
    returns the timestamp for each (or None if the file does not exist), return
    the most recent notebook for the inputs and outputs, respectively"""

    timestamp_inputs = None
    timestamp_outputs = None
    inputs_path = None
    outputs_path = None
    input_fmt = None
    output_fmt = None

    fmt = long_form_one_format(fmt)
    formats = long_form_multiple_formats(formats)

    for alt_path, alt_fmt in paired_paths(path, fmt, formats):
        # In the contents manager, we don't read another text file if the current notebook is in already in text mode
        if (
            contents_manager_mode
            and alt_fmt["extension"] != ".ipynb"
            and fmt["extension"] != ".ipynb"
        ):
            if any(
                alt_fmt.get(key) != fmt.get(key)
                for key in ["extension", "suffix", "prefix"]
            ):
                continue

        timestamp = get_timestamp(alt_path)
        if timestamp is None:
            continue

        if alt_fmt["extension"] == ".ipynb":
            if not timestamp_outputs or timestamp > timestamp_outputs:
                timestamp_outputs = timestamp
                outputs_path, output_fmt = alt_path, alt_fmt
        elif not timestamp_inputs or timestamp > timestamp_inputs:
            timestamp_inputs = timestamp
            inputs_path, input_fmt = alt_path, alt_fmt

    if not timestamp_inputs or (
        not contents_manager_mode
        and timestamp_outputs
        and timestamp_outputs > timestamp_inputs
    ):
        timestamp_inputs = timestamp_outputs
        inputs_path, input_fmt = outputs_path, output_fmt

    return (
        NotebookFile(inputs_path, input_fmt, timestamp_inputs),
        NotebookFile(outputs_path, output_fmt, timestamp_outputs),
    )


def read_pair(inputs, outputs, read_one_file):
    """Read a notebook given its inputs and outputs path and formats"""
    if not outputs.path or outputs.path == inputs.path:
        return read_one_file(inputs.path, inputs.fmt)

    notebook = read_one_file(inputs.path, inputs.fmt)
    check_file_version(notebook, inputs.path, outputs.path)

    outputs = read_one_file(outputs.path, outputs.fmt)
    notebook = combine_inputs_with_outputs(notebook, outputs, fmt=inputs.fmt)

    return notebook
