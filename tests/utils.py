import itertools
import json
import re
from pathlib import Path

from jupytext.cli import system
from jupytext.formats import JUPYTEXT_FORMATS
from jupytext.myst import is_myst_available
from jupytext.pandoc import is_pandoc_available


def tool_version(tool):
    try:
        args = tool.split(" ")
        args.append("--version")
        return system(*args)
    except (OSError, SystemExit):  # pragma: no cover
        return None


def formats_with_support_for_cell_metadata():
    for fmt in JUPYTEXT_FORMATS:
        if fmt.format_name == "myst" and not is_myst_available():
            continue
        if fmt.format_name == "pandoc" and not is_pandoc_available():
            continue
        if fmt.format_name not in ["sphinx", "nomarker", "spin", "quarto"]:
            yield f"{fmt.extension[1:]}:{fmt.format_name}"


def list_notebooks(path="ipynb", skip=""):
    """All notebooks in the directory notebooks/path,
    or in the package itself"""
    if path == "ipynb":
        return (
            list_notebooks("ipynb_julia", skip=skip)
            + list_notebooks("ipynb_py", skip=skip)
            + list_notebooks("ipynb_R", skip=skip)
        )

    nb_path = Path(__file__).parent / "data" / "notebooks" / "inputs"

    if path == "ipynb_all":
        return itertools.chain(
            *(
                list_notebooks(folder.name, skip=skip)
                for folder in nb_path.iterdir()
                if folder.name.startswith("ipynb_")
            )
        )

    if path == "all":
        return itertools.chain(
            *(list_notebooks(folder.name, skip=skip) for folder in nb_path.iterdir())
        )

    if path.startswith("."):
        nb_path = Path(__file__).parent / ".." / path
    else:
        nb_path = nb_path / path

    if skip:
        skip_re = re.compile(".*" + skip + ".*")
        return [
            str(nb_file)
            for nb_file in nb_path.iterdir()
            if nb_file.is_file() and not skip_re.match(nb_file.name)
        ]

    return [str(nb_file) for nb_file in nb_path.iterdir() if nb_file.is_file()]


def notebook_model(nb):
    """Return a notebook model, with content a dictionary rather than a notebook object"""
    return dict(type="notebook", content=json.loads(json.dumps(nb)))
