"""List all the paths associated to a given notebook"""

import os

from .config import find_jupytext_configuration_file
from .formats import (
    NOTEBOOK_EXTENSIONS,
    long_form_multiple_formats,
    long_form_one_format,
    short_form_multiple_formats,
    short_form_one_format,
)


class InconsistentPath(ValueError):
    """An exception raised when the path of a notebook is not consistent with the jupytext.format
    information it contains"""


def split(path, sep):
    if sep not in path:
        return "", path

    return path.rsplit(sep, 1)


def join(left, right, sep):
    if left:
        return left + sep + right
    return right


def separator(path):
    """Return the local path separator (always / in the contents manager)"""
    if os.path.sep == "\\" and "\\" in path:
        return "\\"
    return "/"


def base_path(main_path, fmt, formats=None):
    """Given a path and options for a format (ext, suffix, prefix), return the corresponding base path"""
    fmt = long_form_one_format(fmt)

    base, ext = os.path.splitext(main_path)
    if "extension" not in fmt:
        fmt["extension"] = ext
        if ext not in NOTEBOOK_EXTENSIONS:
            raise InconsistentPath(
                "'{}' is not a notebook. Supported extensions are '{}'.".format(
                    main_path, "', '".join(NOTEBOOK_EXTENSIONS)
                )
            )

    if ext != fmt["extension"]:
        raise InconsistentPath(
            u"Notebook path '{}' was expected to have extension '{}'".format(
                main_path, fmt["extension"]
            )
        )

    # Is there a format that matches the main path?
    if formats is None:
        formats = [fmt]

    for f in formats:
        if f["extension"] != fmt["extension"]:
            continue
        if (
            "format_name" in fmt
            and "format_name" in f
            and f["format_name"] != fmt["format_name"]
        ):
            continue
        # extend 'fmt' with the format information (prefix, suffix) from f
        fmt = {key: fmt.get(key, value) for key, value in f.items()}
        break

    suffix = fmt.get("suffix")
    prefix = fmt.get("prefix")

    if suffix:
        if not base.endswith(suffix):
            raise InconsistentPath(
                u"Notebook name '{}' was expected to end with suffix '{}'".format(
                    base, suffix
                )
            )
        base = base[: -len(suffix)]

    if not prefix:
        return base

    if "//" in prefix:
        prefix_root, prefix = prefix.rsplit("//", 1)
    else:
        prefix_root = ""
    sep = separator(base)
    notebook_dir, notebook_file_name = split(base, sep)
    prefix_dir, prefix_file_name = split(prefix, "/")

    base_dir = None
    config_file = find_jupytext_configuration_file(notebook_dir)
    if config_file:
        config_file_dir = os.path.dirname(config_file)
        if notebook_dir.startswith(config_file_dir):
            base_dir = config_file_dir
            notebook_dir = notebook_dir[len(config_file_dir) :]

    if prefix_file_name:
        if not notebook_file_name.startswith(prefix_file_name):
            raise InconsistentPath(
                u"Notebook name '{}' was expected to start with prefix '{}'".format(
                    notebook_file_name, prefix_file_name
                )
            )
        notebook_file_name = notebook_file_name[len(prefix_file_name) :]

    if prefix_dir:
        parent_notebook_dir = notebook_dir
        parent_prefix_dir = prefix_dir
        actual_folders = list()
        while parent_prefix_dir:
            parent_prefix_dir, expected_folder = split(parent_prefix_dir, "/")
            if expected_folder == "..":
                if not actual_folders:
                    raise InconsistentPath(
                        u"Notebook directory '{}' does not match prefix '{}'".format(
                            notebook_dir, prefix_dir
                        )
                    )
                parent_notebook_dir = join(
                    parent_notebook_dir, actual_folders.pop(), sep
                )
            else:
                parent_notebook_dir, actual_folder = split(parent_notebook_dir, sep)
                actual_folders.append(actual_folder)

                if actual_folder != expected_folder:
                    raise InconsistentPath(
                        u"Notebook directory '{}' does not match prefix '{}'".format(
                            notebook_dir, prefix_dir
                        )
                    )
        notebook_dir = parent_notebook_dir

    if prefix_root:
        long_prefix_root = sep + prefix_root + sep
        long_notebook_dir = sep + notebook_dir + sep
        if long_prefix_root not in long_notebook_dir:
            raise InconsistentPath(
                u"Notebook directory '{}' does not match prefix root '{}'".format(
                    notebook_dir, prefix_root
                )
            )
        left, right = long_notebook_dir.rsplit(long_prefix_root, 1)
        notebook_dir = left + sep + "//" + right

        # We are going to remove the last char, but we need to insert it back in the end...
        if not right:
            sep = notebook_dir[-1]
        notebook_dir = notebook_dir[len(sep) : -len(sep)]

    if base_dir:
        notebook_dir = base_dir + notebook_dir

    if not notebook_dir:
        return notebook_file_name

    return notebook_dir + sep + notebook_file_name


def full_path(base, fmt):
    """Return the full path for the notebook, given the base path"""
    ext = fmt["extension"]
    suffix = fmt.get("suffix")
    prefix = fmt.get("prefix")

    full = base

    if prefix:
        if "//" in prefix:
            prefix_root, prefix = prefix.rsplit("//", 1)
        else:
            prefix_root = ""
        prefix_dir, prefix_file_name = split(prefix, "/")

        # Local path separator (\\ on windows)
        sep = separator(base)
        prefix_dir = prefix_dir.replace("/", sep)

        if (prefix_root != "") != ("//" in base):
            raise InconsistentPath(
                u"Notebook base name '{}' is not compatible with fmt={}. Make sure you use prefix roots "
                u"in either none, or all of the paired formats".format(
                    base, short_form_one_format(fmt)
                )
            )
        if prefix_root:
            left, right = base.rsplit("//", 1)
            right_dir, notebook_file_name = split(right, sep)
            notebook_dir = left + prefix_root + sep + right_dir
        else:
            notebook_dir, notebook_file_name = split(base, sep)

        if prefix_file_name:
            notebook_file_name = prefix_file_name + notebook_file_name

        if prefix_dir:
            dotdot = ".." + sep
            while prefix_dir.startswith(dotdot):
                prefix_dir = prefix_dir[len(dotdot) :]
                notebook_dir = split(notebook_dir, sep)[0]

            # Do not add a path separator when notebook_dir is '/'
            if notebook_dir and not notebook_dir.endswith(sep):
                notebook_dir = notebook_dir + sep

            notebook_dir = notebook_dir + prefix_dir

        if notebook_dir and not notebook_dir.endswith(sep):
            notebook_dir = notebook_dir + sep

        full = notebook_dir + notebook_file_name

    if suffix:
        full = full + suffix

    return full + ext


def find_base_path_and_format(main_path, formats):
    """Return the base path and the format corresponding to the given path"""
    for fmt in formats:
        try:
            return base_path(main_path, fmt), fmt
        except InconsistentPath:
            continue

    raise InconsistentPath(
        u"Path '{}' matches none of the export formats. "
        "Please make sure that jupytext.formats covers the current file "
        "(e.g. add '{}' to the export formats)".format(
            main_path, os.path.splitext(main_path)[1][1:]
        )
    )


def paired_paths(main_path, fmt, formats):
    """Return the list of paired notebooks, given main path, and the list of formats"""
    if not formats:
        return [(main_path, {"extension": os.path.splitext(main_path)[1]})]

    formats = long_form_multiple_formats(formats)

    # Is there a format that matches the main path?
    base = base_path(main_path, fmt, formats)
    paths = [full_path(base, f) for f in formats]

    if main_path not in paths:
        raise InconsistentPath(
            u"Paired paths '{}' do not include the current notebook path '{}'. "
            u"Current format is '{}', and paired formats are '{}'.".format(
                "','".join(paths),
                main_path,
                short_form_one_format(fmt),
                short_form_multiple_formats(formats),
            )
        )

    if len(paths) > len(set(paths)):
        raise InconsistentPath(
            u"Duplicate paired paths for this notebook. Please fix jupytext.formats."
        )

    return list(zip(paths, formats))
