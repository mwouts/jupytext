"""List all the paths associated to a given notebook"""

import os
from .formats import long_form_multiple_formats


class InconsistentPath(ValueError):
    """An exception raised when the path of a notebook is not consistent with the jupytext.format
    information it contains"""
    pass


def base_path(main_path, fmt):
    """Given a path and options for a format (ext, suffix, prefix), return the corresponding base path"""
    fmt_ext = fmt['extension']
    suffix = fmt.get('suffix')
    prefix = fmt.get('prefix')

    base, ext = os.path.splitext(main_path)
    if ext != fmt_ext:
        raise InconsistentPath(u"Notebook path '{}' was expected to have extension '{}'".format(main_path, fmt_ext))

    if suffix:
        if not base.endswith(suffix):
            raise InconsistentPath(u"Notebook name '{}' was expected to end with suffix '{}'".format(base, suffix))
        base = base[:-len(suffix)]

    if prefix:
        prefix_dir, prefix_file_name = os.path.split(prefix)
        notebook_dir, notebook_file_name = os.path.split(base)
        sep = base[len(notebook_dir):-len(notebook_file_name)]
        if prefix_file_name:
            if not notebook_file_name.startswith(prefix_file_name):
                raise InconsistentPath(u"Notebook name '{}' was expected to start with prefix '{}'"
                                       .format(notebook_file_name, prefix_file_name))
            notebook_file_name = notebook_file_name[len(prefix_file_name):]
        if prefix_dir:
            if not notebook_dir.endswith(prefix_dir):
                raise InconsistentPath(u"Notebook directory '{}' was expected to end with directory prefix '{}'"
                                       .format(notebook_dir, prefix_dir))
            notebook_dir = notebook_dir[:-len(prefix_dir)]

            # Does notebook_dir ends with a path separator?
            if not os.path.split(notebook_dir)[1]:
                notebook_dir = notebook_dir[:-1]

        base = notebook_dir + sep + notebook_file_name

    return base


def full_path(base, format_options):
    """Return the full path for the notebook, given the base path"""
    ext = format_options['extension']
    suffix = format_options.get('suffix')
    prefix = format_options.get('prefix')

    full = base

    if prefix:
        prefix_dir, prefix_file_name = os.path.split(prefix)
        notebook_dir, notebook_file_name = os.path.split(base)
        sep = base[len(notebook_dir):-len(notebook_file_name)] or '/'
        if prefix_file_name:
            notebook_file_name = prefix_file_name + notebook_file_name
        if prefix_dir:
            notebook_dir = notebook_dir + sep + prefix_dir if notebook_dir else prefix_dir
        full = notebook_dir + sep + notebook_file_name if notebook_dir else notebook_file_name

    if suffix:
        full = full + suffix

    return full + ext


def find_base_path_and_format(main_path, formats):
    """Return the base path and the format corresponding to the given path"""
    for i, fmt in enumerate(formats):
        try:
            return base_path(main_path, fmt), i
        except InconsistentPath:
            continue

    raise InconsistentPath(u"Path '{}' matches none of the export formats. "
                           "Please make sure that jupytext.formats covers the current file "
                           "(e.g. add '{}' to the export formats)".format(main_path,
                                                                          os.path.splitext(main_path)[1][1:]))


def paired_paths(main_path, formats):
    """Return the list of paired notebooks, given main path, and the list of formats"""
    if not formats:
        return None

    formats = long_form_multiple_formats(formats)

    # Is there a format that matches the main path?
    base, _ = find_base_path_and_format(main_path, formats)
    paths = [full_path(base, fmt) for fmt in formats]

    if len(paths) > len(set(paths)):
        raise InconsistentPath(u"Duplicate paired paths for this notebook. Please fix jupytext.formats.")

    return list(zip(paths, formats))
