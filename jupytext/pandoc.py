"""Jupyter notebook to Markdown and back, using Pandoc"""

import os
import subprocess
import tempfile

# Copy nbformat reads and writes to avoid them being patched in the contents manager!!
from nbformat import reads as ipynb_reads, writes as ipynb_writes


class PandocError(OSError):
    """An error related to Pandoc"""


def pandoc(args, filein=None, fileout=None):
    """Execute pandoc with the given arguments"""
    cmd = [u"pandoc"]

    if filein:
        cmd.append(filein)

    if fileout:
        cmd.append("-o")
        cmd.append(fileout)

    cmd.extend(args.split())

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode:
        raise PandocError(
            "pandoc exited with return code {}\n{}".format(proc.returncode, str(err))
        )
    return out.decode("utf-8")


def is_pandoc_available():
    """Is Pandoc>=2.7.2 available?"""
    try:
        raise_if_pandoc_is_not_available()
        return True
    except PandocError:
        return False


def raise_if_pandoc_is_not_available():
    """Raise with an informative error message if pandoc is not available"""
    try:
        from pkg_resources import parse_version
    except ImportError:
        raise PandocError("Please install pkg_resources")

    version = pandoc_version()
    if version == "N/A":
        raise PandocError(
            "The Pandoc Markdown format requires 'pandoc>=2.7.2', "
            "but pandoc was not found"
        )

    if parse_version(version) < parse_version("2.7.2"):
        raise PandocError(
            "The Pandoc Markdown format requires 'pandoc>=2.7.2', "
            "but pandoc version {} was not found".format(version)
        )

    return version


def pandoc_version():
    """Pandoc's version number"""
    try:
        return pandoc(u"--version").splitlines()[0].split()[1]
    except (IOError, OSError):
        return "N/A"


def md_to_notebook(text):
    """Convert a Markdown text to a Jupyter notebook, using Pandoc"""
    raise_if_pandoc_is_not_available()
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(text.encode("utf-8"))
    tmp_file.close()

    pandoc(
        u"--from markdown --to ipynb -s --atx-headers --wrap=preserve --preserve-tabs",
        tmp_file.name,
        tmp_file.name,
    )

    with open(tmp_file.name, encoding="utf-8") as opened_file:
        notebook = ipynb_reads(opened_file.read(), as_version=4)
    os.unlink(tmp_file.name)

    return notebook


def notebook_to_md(notebook):
    """Convert a notebook to its Markdown representation, using Pandoc"""
    raise_if_pandoc_is_not_available()
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(ipynb_writes(notebook).encode("utf-8"))
    tmp_file.close()

    pandoc(
        u"--from ipynb --to markdown -s --atx-headers --wrap=preserve --preserve-tabs",
        tmp_file.name,
        tmp_file.name,
    )

    with open(tmp_file.name, encoding="utf-8") as opened_file:
        text = opened_file.read()

    os.unlink(tmp_file.name)
    return "\n".join(text.splitlines())
