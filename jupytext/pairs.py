from .formats import long_form_multiple_formats
from .paired_paths import (
    find_base_path_and_format,
    full_path,
)


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
