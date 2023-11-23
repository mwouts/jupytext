"""Jupyter notebook to Quarto Markdown and back, using 'quarto convert'"""

import os
import subprocess
import tempfile

# Copy nbformat reads and writes to avoid them being patched in the contents manager!!
from nbformat import reads as ipynb_reads
from nbformat import writes as ipynb_writes
from packaging.version import parse

QUARTO_MIN_VERSION = "0.2.134"


class QuartoError(OSError):
    """An error related to Quarto"""


def quarto(args, filein=None):
    """Execute quarto with the given arguments"""
    cmd = ["quarto"] + args.split()

    if filein:
        cmd.append(filein)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode:
        raise QuartoError(
            f"{' '.join(cmd)} exited with return code {proc.returncode}\n{err.decode('utf-8')}"
        )

    return out.decode("utf-8")


def is_quarto_available(min_version=QUARTO_MIN_VERSION):
    """Is Quarto available?"""
    try:
        raise_if_quarto_is_not_available(min_version=min_version)
        return True
    except QuartoError:
        return False


def raise_if_quarto_is_not_available(min_version=QUARTO_MIN_VERSION):
    """Raise with an informative error message if quarto is not available"""
    version = quarto_version()
    if version == "N/A":
        raise QuartoError(
            f"The Quarto Markdown format requires 'quarto>={min_version}', "
            "but quarto was not found"
        )

    if parse(version) < parse(min_version):
        raise QuartoError(
            f"The Quarto Markdown format requires 'quarto>={min_version}', "
            f"but quarto version {version} was not found"
        )

    return version


def quarto_version():
    """Quarto's version number"""
    try:
        return quarto("--version").strip()
    except OSError:
        return "N/A"


def qmd_to_notebook(text):
    """Convert a Quarto Markdown notebook to a Jupyter notebook"""
    raise_if_quarto_is_not_available()
    tmp_qmd_file = tempfile.NamedTemporaryFile(delete=False, suffix=".qmd")
    tmp_qmd_file.write(text.encode("utf-8"))
    tmp_qmd_file.close()

    quarto("convert --log-level warning", tmp_qmd_file.name)

    tmp_ipynb_file_name = tmp_qmd_file.name[:-4] + ".ipynb"

    with open(tmp_ipynb_file_name, encoding="utf-8") as ipynb_file:
        notebook = ipynb_reads(ipynb_file.read(), as_version=4)

    os.unlink(tmp_qmd_file.name)
    os.unlink(tmp_ipynb_file_name)

    return notebook


def notebook_to_qmd(notebook):
    """Convert a Jupyter notebook to its Quarto Markdown representation"""
    raise_if_quarto_is_not_available()
    tmp_ipynb_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ipynb")
    tmp_ipynb_file.write(ipynb_writes(notebook).encode("utf-8"))
    tmp_ipynb_file.close()

    quarto("convert --log-level warning", tmp_ipynb_file.name)

    tmp_qmd_file_name = tmp_ipynb_file.name[:-6] + ".qmd"

    with open(tmp_qmd_file_name, encoding="utf-8") as qmd_file:
        text = qmd_file.read()

    os.unlink(tmp_ipynb_file.name)
    os.unlink(tmp_qmd_file_name)

    return "\n".join(text.splitlines())
