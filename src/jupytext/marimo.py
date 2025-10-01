"""Jupyter notebook to Marimo py format and back, using Marimo"""

from packaging.version import parse
import tempfile
import subprocess
import nbformat


class MarimoError(OSError):
    """An error related to Marimo"""


def is_marimo_available(min_version="0.15", max_version=None):
    """Is Marimo>=0.15 available?"""
    try:
        raise_if_marimo_is_not_available(min_version=min_version, max_version=max_version)
        return True
    except MarimoError:
        return False


def raise_if_marimo_is_not_available(min_version="0.15", max_version=None):
    """Raise with an informative error message if Marimo is not available"""
    version = marimo_version()
    if version == "N/A":
        raise MarimoError(f"The Marimo format requires 'Marimo>={min_version}', but Marimo was not found")

    if parse(version) < parse(min_version):
        raise MarimoError(f"The Marimo format requires 'Marimo>={min_version}', but Marimo version {version} was found")

    if max_version and parse(version) > parse(max_version):
        raise MarimoError(f"The Marimo format requires 'Marimo<={max_version}', but Marimo version {version} was found")

    return version


def marimo_version():
    """Marimo's version number"""
    try:
        return marimo("--version")
    except OSError:
        return "N/A"


def marimo_py_to_notebook(text):
    """Convert a Marimo script to a Jupyter notebook, using Marimo"""
    raise_if_marimo_is_not_available()
    tmp_py_file = tempfile.NamedTemporaryFile(suffix=".py")
    tmp_ipynb_file = tempfile.NamedTemporaryFile(suffix=".ipynb")

    with open(tmp_py_file.name, "w") as fp:
        fp.write(text)

    marimo(
        "export",
        "ipynb",
        # Keep the current order to minimize diffs on round trips
        "--sort",
        "top-down",
        tmp_py_file.name,
        "-o",
        tmp_ipynb_file.name,
    )

    notebook = nbformat.read(tmp_ipynb_file, as_version=4)

    tmp_ipynb_file.close()
    tmp_py_file.close()

    return notebook


def notebook_to_marimo_py(notebook):
    """Convert a notebook to its Marimo script"""
    raise_if_marimo_is_not_available()
    tmp_py_file = tempfile.NamedTemporaryFile(suffix=".py")
    tmp_ipynb_file = tempfile.NamedTemporaryFile(suffix=".ipynb")

    with open(tmp_ipynb_file.name, "w") as fp:
        nbformat.write(notebook, fp)

    marimo("convert", tmp_ipynb_file.name, "-o", tmp_py_file.name)

    with open(tmp_py_file.name) as fp:
        text = fp.read()

    tmp_ipynb_file.close()
    tmp_py_file.close()

    return "\n".join(text.splitlines())


def marimo(*args: str):
    cmd = ["marimo"] + list(args)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode:
        raise MarimoError(f"marimo exited with return code {proc.returncode}\n{str(err)}")

    return out.decode("utf-8")
