# -*- coding: utf-8 -*-

import os
import sys
import time
import unittest.mock as mock
import warnings
from argparse import ArgumentTypeError
from contextlib import contextmanager
from io import StringIO
from shutil import copyfile
from subprocess import check_call

import nbformat
import pytest
from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook

from jupytext import __version__, read, reads, write, writes
from jupytext.cli import jupytext, parse_jupytext_args, str2bool, system
from jupytext.compare import compare, compare_notebooks
from jupytext.formats import JupytextFormatError, long_form_one_format
from jupytext.paired_paths import InconsistentPath, paired_paths

from .utils import (
    list_notebooks,
    requires_jupytext_installed,
    requires_myst,
    requires_pandoc,
    requires_sphinx_gallery,
    requires_user_kernel_python3,
    skip_on_windows,
)


def test_str2bool():
    assert str2bool("d") is None
    assert str2bool("TRUE") is True
    assert str2bool("0") is False
    with pytest.raises(ArgumentTypeError):
        str2bool("UNEXPECTED")


@pytest.mark.parametrize("nb_file", list_notebooks())
def test_cli_single_file(nb_file):
    assert parse_jupytext_args([nb_file] + ["--to", "py"]).notebooks == [nb_file]


@pytest.mark.parametrize("nb_files", [list_notebooks()])
def test_cli_multiple_files(nb_files):
    assert parse_jupytext_args(nb_files + ["--to", "py"]).notebooks == nb_files


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_convert_single_file_in_place(nb_file, tmpdir):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    copyfile(nb_file, nb_org)

    base, ext = os.path.splitext(nb_org)
    nb_other = base + ".py"

    jupytext([nb_org, "--to", "py"])

    nb1 = read(nb_org)
    nb2 = read(nb_other)

    compare_notebooks(nb2, nb1)


@requires_jupytext_installed
def test_convert_single_file_in_place_m(tmpdir):
    nb_file = list_notebooks("ipynb_py")[0]
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    copyfile(nb_file, nb_org)

    base, ext = os.path.splitext(nb_org)

    for fmt_ext in ("py", "Rmd"):
        nb_other = base + "." + fmt_ext

        check_call([sys.executable, "-m", "jupytext", nb_org, "--to", fmt_ext])

        nb1 = read(nb_org)
        nb2 = read(nb_other)

        compare_notebooks(nb2, nb1)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb") + list_notebooks("Rmd"))
def test_convert_single_file(nb_file, tmpdir, capsys):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    copyfile(nb_file, nb_org)

    nb1 = read(nb_file)
    pynb = writes(nb1, "py")
    jupytext([nb_org, "--to", "py", "-o", "-"])

    out, err = capsys.readouterr()
    assert err == ""
    compare(out, pynb)


def test_jupytext_version(capsys):
    jupytext(["--version"])

    out, err = capsys.readouterr()
    assert err == ""
    compare(out, __version__ + "\n")


def test_wildcard(tmpdir):
    nb1_ipynb = str(tmpdir.join("nb1.ipynb"))
    nb2_ipynb = str(tmpdir.join("nb2.ipynb"))

    nb1_py = str(tmpdir.join("nb1.py"))
    nb2_py = str(tmpdir.join("nb2.py"))

    write(new_notebook(metadata={"notebook": 1}), nb1_ipynb)
    write(new_notebook(metadata={"notebook": 2}), nb2_ipynb)

    os.chdir(str(tmpdir))
    jupytext(["nb*.ipynb", "--to", "py"])

    assert os.path.isfile(nb1_py)
    assert os.path.isfile(nb2_py)

    with pytest.raises(IOError):
        jupytext(["nb3.ipynb", "--to", "py"])


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_cpp"))
def test_to_cpluplus(nb_file, tmpdir, capsys):
    nb_org = str(tmpdir.join(os.path.basename(nb_file)))
    copyfile(nb_file, nb_org)
    nb1 = read(nb_org)

    text_cpp = writes(nb1, "cpp")
    jupytext([nb_org, "--to", "c++", "--output", "-"])

    out, err = capsys.readouterr()
    assert err == ""
    compare(out, text_cpp)


@pytest.mark.parametrize("nb_files", [list_notebooks("ipynb_py")])
def test_convert_multiple_file(nb_files, tmpdir):
    nb_orgs = []
    nb_others = []

    for nb_file in nb_files:
        nb_org = str(tmpdir.join(os.path.basename(nb_file)))
        base, ext = os.path.splitext(nb_org)
        nb_other = base + ".py"
        copyfile(nb_file, nb_org)
        nb_orgs.append(nb_org)
        nb_others.append(nb_other)

    jupytext(nb_orgs + ["--to", "py"])

    for nb_org, nb_other in zip(nb_orgs, nb_others):
        nb1 = read(nb_org)
        nb2 = read(nb_other)
        compare_notebooks(nb2, nb1)


def test_error_not_notebook_ext_input(tmpdir, capsys):
    tmp_file = str(tmpdir.join("notebook.ext"))
    with open(tmp_file, "w") as fp:
        fp.write("\n")

    with pytest.raises(
        InconsistentPath, match="is not a notebook. Supported extensions are"
    ):
        jupytext([tmp_file, "--to", "py"])


@pytest.fixture
def tmp_ipynb(tmpdir):
    tmp_file = str(tmpdir.join("notebook.ipynb"))
    write(new_notebook(), tmp_file)
    return tmp_file


@pytest.fixture
def tmp_py(tmpdir):
    tmp_file = str(tmpdir.join("notebook.py"))
    with open(tmp_file, "w") as fp:
        fp.write("\n")
    return tmp_file


def test_error_not_notebook_ext_to(tmp_ipynb):
    with pytest.raises(JupytextFormatError, match="'ext' is not a notebook extension"):
        jupytext([tmp_ipynb, "--to", "ext"])


def test_error_not_notebook_ext_output(tmp_ipynb, tmpdir):
    with pytest.raises(
        JupytextFormatError,
        match="Extension '.ext' is not a notebook extension. Please use one of",
    ):
        jupytext([tmp_ipynb, "-o", str(tmpdir.join("not.ext"))])


def test_error_not_same_ext(tmp_ipynb, tmpdir):
    with pytest.raises(InconsistentPath):
        jupytext([tmp_ipynb, "--to", "py", "-o", str(tmpdir.join("not.md"))])


def test_error_no_action(tmp_ipynb):
    with pytest.raises(ValueError, match="Please provide one of"):
        jupytext([tmp_ipynb])


def test_error_update_not_ipynb(tmp_py):
    with pytest.raises(ValueError, match="--update is only for ipynb files"):
        jupytext([tmp_py, "--to", "py", "--update"])


def test_error_multiple_input(tmp_ipynb):
    with pytest.raises(
        ValueError, match="Please input a single notebook when using --output"
    ):
        jupytext([tmp_ipynb, tmp_ipynb, "--to", "py", "-o", "notebook.py"])


def test_error_opt_missing_equal(tmp_ipynb):
    with pytest.raises(ValueError, match="key=value"):
        jupytext([tmp_ipynb, "--to", "py", "--opt", "missing_equal"])


def test_error_unknown_opt(tmp_ipynb):
    with pytest.raises(ValueError, match="is not a valid format option"):
        jupytext([tmp_ipynb, "--to", "py", "--opt", "unknown=true"])


def test_combine_same_version_ok(tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_nbpy = str(tmpdir.join("notebook.py"))
    tmp_rmd = str(tmpdir.join("notebook.Rmd"))

    with open(tmp_nbpy, "w") as fp:
        fp.write(
            """# ---
# jupyter:
#   jupytext_formats: ipynb,py
#   jupytext_format_version: '1.2'
# ---

# New cell
"""
        )

    nb = new_notebook(metadata={"jupytext_formats": "ipynb,py"})
    write(nb, tmp_ipynb)

    # to jupyter notebook
    jupytext([tmp_nbpy, "--to", "ipynb", "--update"])
    # test round trip
    jupytext([tmp_nbpy, "--to", "notebook", "--test"])
    # test ipynb to rmd
    jupytext([tmp_ipynb, "--to", "rmarkdown"])

    nb = read(tmp_ipynb)
    cells = nb["cells"]
    assert len(cells) == 1
    assert cells[0].cell_type == "markdown"
    assert cells[0].source == "New cell"

    nb = read(tmp_rmd)
    cells = nb["cells"]
    assert len(cells) == 1
    assert cells[0].cell_type == "markdown"
    assert cells[0].source == "New cell"


def test_combine_lower_version_raises(tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_nbpy = str(tmpdir.join("notebook.py"))

    with open(tmp_nbpy, "w") as fp:
        fp.write(
            """# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '55.4'
#       jupytext_version: 42.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# New cell
"""
        )

    nb = new_notebook(metadata={"jupytext_formats": "ipynb,py"})
    write(nb, tmp_ipynb)

    with pytest.raises(
        ValueError,
        match="The file notebook.py was generated with jupytext version 42.1.1 but you have .* installed. "
        "Please upgrade jupytext to version 42.1.1, or remove either notebook.py or notebook.ipynb. "
        "This error occurs because notebook.py is in the light format in version 55.4, "
        "while jupytext version .* installed at .* can only read the light format in versions .*",
    ):
        jupytext([tmp_nbpy, "--to", "ipynb", "--update"])


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_ipynb_to_py_then_update_test(nb_file, tmpdir):
    """Reproduce https://github.com/mwouts/jupytext/issues/83"""
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_nbpy = str(tmpdir.join("notebook.py"))

    copyfile(nb_file, tmp_ipynb)

    jupytext(["--to", "py", tmp_ipynb])
    jupytext(["--test", "--update", "--to", "ipynb", tmp_nbpy])


def test_test_to_ipynb_ignore_version_number_414(
    tmpdir,
    text="""# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# A short markdown cell

# Followed by a code cell
2 + 2
""",
):
    tmp_py = str(tmpdir.join("script.py"))
    with open(tmp_py, "w") as fp:
        fp.write(text)

    assert jupytext(["--test", "--to", "ipynb", tmp_py]) == 0


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_convert_to_percent_format(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_nbpy = str(tmpdir.join("notebook.py"))

    copyfile(nb_file, tmp_ipynb)

    jupytext(["--to", "py:percent", tmp_ipynb])

    with open(tmp_nbpy) as stream:
        py_script = stream.read()
        assert "format_name: percent" in py_script

    nb1 = read(tmp_ipynb)
    nb2 = read(tmp_nbpy)

    compare_notebooks(nb2, nb1)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_convert_to_percent_format_and_keep_magics(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_nbpy = str(tmpdir.join("notebook.py"))

    copyfile(nb_file, tmp_ipynb)

    jupytext(["--to", "py:percent", "--opt", "comment_magics=False", tmp_ipynb])

    with open(tmp_nbpy) as stream:
        py_script = stream.read()
        assert "format_name: percent" in py_script
        assert "comment_magics: false" in py_script
        assert "# %%time" not in py_script

    nb1 = read(tmp_ipynb)
    nb2 = read(tmp_nbpy)

    compare_notebooks(nb2, nb1)


@pytest.mark.parametrize("py_file", list_notebooks("python"))
def test_set_formats(py_file, tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))

    copyfile(py_file, tmp_py)

    jupytext([tmp_py, "--set-formats", "ipynb,py:light"])
    nb = read(tmp_ipynb)
    assert nb.metadata["jupytext"]["formats"] == "ipynb,py:light"


@pytest.mark.parametrize("py_file", list_notebooks("python"))
def test_update_metadata(py_file, tmpdir, capsys):
    tmp_py = str(tmpdir.join("notebook.py"))
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))

    copyfile(py_file, tmp_py)

    jupytext(
        [
            "--to",
            "ipynb",
            tmp_py,
            "--update-metadata",
            '{"jupytext":{"formats":"ipynb,py:light"}}',
        ]
    )

    nb = read(tmp_ipynb)
    assert nb.metadata["jupytext"]["formats"] == "ipynb,py:light"

    jupytext(
        ["--to", "py", tmp_ipynb, "--update-metadata", '{"jupytext":{"formats":null}}']
    )

    nb = read(tmp_py)
    assert "formats" not in nb.metadata["jupytext"]

    with pytest.raises(SystemExit):
        jupytext(["--to", "ipynb", tmp_py, "--update-metadata", '{"incorrect": "JSON"'])

    out, err = capsys.readouterr()
    assert "invalid" in err


@pytest.mark.parametrize("py_file", list_notebooks("python"))
def test_set_kernel_inplace(py_file, tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))

    copyfile(py_file, tmp_py)

    jupytext([tmp_py, "--set-kernel", "-"])

    nb = read(tmp_py)
    kernel_name = nb.metadata["kernelspec"]["name"]
    cmd = get_kernel_spec(kernel_name).argv[0]
    assert cmd == "python" or os.path.samefile(cmd, sys.executable)


@pytest.mark.parametrize("py_file", list_notebooks("python"))
def test_set_kernel_auto(py_file, tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))

    copyfile(py_file, tmp_py)

    jupytext(["--to", "ipynb", tmp_py, "--set-kernel", "-"])

    nb = read(tmp_ipynb)
    kernel_name = nb.metadata["kernelspec"]["name"]
    cmd = get_kernel_spec(kernel_name).argv[0]
    assert cmd == "python" or os.path.samefile(cmd, sys.executable)


@pytest.mark.parametrize("py_file", list_notebooks("python"))
def test_set_kernel_with_name(py_file, tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))

    copyfile(py_file, tmp_py)

    for kernel in find_kernel_specs():
        jupytext(["--to", "ipynb", tmp_py, "--set-kernel", kernel])

        nb = read(tmp_ipynb)
        assert nb.metadata["kernelspec"]["name"] == kernel

    with pytest.raises(KeyError):
        jupytext(["--to", "ipynb", tmp_py, "--set-kernel", "non_existing_env"])


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_paired_paths(nb_file, tmpdir, capsys):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    nb = read(nb_file)
    nb.metadata.setdefault("jupytext", {})[
        "formats"
    ] = "ipynb,_light.py,_percent.py:percent"
    write(nb, tmp_ipynb)

    jupytext(["--paired-paths", tmp_ipynb])

    out, err = capsys.readouterr()
    assert not err

    formats = nb.metadata.get("jupytext", {}).get("formats")
    assert set(out.splitlines()).union([tmp_ipynb]) == set(
        [path for path, _ in paired_paths(tmp_ipynb, "ipynb", formats)]
    )


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_sync(nb_file, tmpdir, cwd_tmpdir, capsys):
    tmp_ipynb = "notebook.ipynb"
    tmp_py = "notebook.py"
    tmp_rmd = "notebook.Rmd"
    nb = read(nb_file)
    write(nb, tmp_ipynb)

    # Test that sync issues a warning when the notebook is not paired
    jupytext(["--sync", tmp_ipynb])
    _, err = capsys.readouterr()
    assert "is not a paired notebook" in err

    # Now with a pairing information
    nb.metadata.setdefault("jupytext", {})["formats"] = "py,Rmd,ipynb"
    write(nb, tmp_ipynb)

    # Test that missing files are created
    jupytext(["--sync", tmp_ipynb])

    assert os.path.isfile(tmp_py)
    compare_notebooks(read(tmp_py), nb)

    assert os.path.isfile(tmp_rmd)
    compare_notebooks(read(tmp_rmd), nb, "Rmd")

    write(nb, tmp_rmd, fmt="Rmd")
    jupytext(["--sync", tmp_ipynb])

    nb2 = read(tmp_ipynb)
    compare_notebooks(nb2, nb, "Rmd", compare_outputs=True)

    write(nb, tmp_py, fmt="py")
    jupytext(["--sync", tmp_ipynb])

    nb2 = read(tmp_ipynb)
    compare_notebooks(nb2, nb, compare_outputs=True)

    # Finally we recreate the ipynb
    os.remove(tmp_ipynb)

    time.sleep(0.1)
    jupytext(["--sync", tmp_py])

    nb2 = read(tmp_ipynb)
    compare_notebooks(nb2, nb)

    # ipynb must be older than py file, otherwise our Contents Manager will complain
    assert os.path.getmtime(tmp_ipynb) <= os.path.getmtime(tmp_py)


@requires_pandoc
@pytest.mark.parametrize(
    "nb_file", list_notebooks("ipynb_py", skip="(Notebook with|flavors|305)")
)
def test_sync_pandoc(nb_file, tmpdir, cwd_tmpdir, capsys):
    tmp_ipynb = "notebook.ipynb"
    tmp_md = "notebook.md"
    nb = read(nb_file)
    write(nb, tmp_ipynb)

    # Test that sync issues a warning when the notebook is not paired
    jupytext(["--sync", tmp_ipynb])
    _, err = capsys.readouterr()
    assert "is not a paired notebook" in err

    # Now with a pairing information
    nb.metadata.setdefault("jupytext", {})["formats"] = "ipynb,md:pandoc"
    write(nb, tmp_ipynb)

    # Test that missing files are created
    jupytext(["--sync", tmp_ipynb])

    assert os.path.isfile(tmp_md)
    compare_notebooks(read(tmp_md), nb, "md:pandoc")

    with open(tmp_md) as fp:
        assert "pandoc" in fp.read()


@pytest.mark.parametrize(
    "nb_file,ext",
    [(nb_file, ".py") for nb_file in list_notebooks("ipynb_py")]
    + [(nb_file, ".R") for nb_file in list_notebooks("ipynb_R")]
    + [(nb_file, ".jl") for nb_file in list_notebooks("ipynb_julia")],
)
def test_cli_can_infer_jupytext_format(nb_file, ext, tmpdir, cwd_tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_text = "notebook" + ext
    nb = read(nb_file)

    # Light format to Jupyter notebook
    write(nb, tmp_text)
    jupytext(["--to", "notebook", tmp_text])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb2, nb)

    # Percent format to Jupyter notebook
    write(nb, tmp_text, fmt=ext + ":percent")
    jupytext(["--to", "notebook", tmp_text])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb2, nb)


@pytest.mark.parametrize(
    "nb_file,ext",
    [(nb_file, ".py") for nb_file in list_notebooks("ipynb_py")]
    + [(nb_file, ".R") for nb_file in list_notebooks("ipynb_R")],
)
def test_cli_to_script(nb_file, ext, tmpdir, cwd_tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_text = "notebook" + ext
    nb = read(nb_file)

    write(nb, tmp_ipynb)
    jupytext(["--to", "script", tmp_ipynb])
    nb2 = read(tmp_text)
    compare_notebooks(nb2, nb)


@pytest.mark.parametrize(
    "nb_file,ext",
    [(nb_file, ".py") for nb_file in list_notebooks("ipynb_py")]
    + [(nb_file, ".R") for nb_file in list_notebooks("ipynb_R")],
)
def test_cli_to_auto(nb_file, ext, tmpdir, cwd_tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_text = "notebook" + ext
    nb = read(nb_file)

    write(nb, tmp_ipynb)
    jupytext(["--to", "auto", tmp_ipynb])
    nb2 = read(tmp_text)
    compare_notebooks(nb2, nb)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_cli_can_infer_jupytext_format_from_stdin(nb_file, tmpdir, cwd_tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_py = "notebook.py"
    tmp_rmd = "notebook.Rmd"
    nb = read(nb_file)

    # read ipynb notebook on stdin, write to python
    with open(nb_file) as fp, mock.patch("sys.stdin", fp):
        jupytext(["--to", "py:percent", "-o", tmp_py])
    nb2 = read(tmp_py)
    compare_notebooks(nb2, nb)

    # read python notebook on stdin, write to ipynb
    with open(tmp_py) as fp, mock.patch("sys.stdin", fp):
        jupytext(["-o", tmp_ipynb])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb2, nb)

    # read ipynb notebook on stdin, write to R markdown
    with open(nb_file) as fp, mock.patch("sys.stdin", fp):
        jupytext(["-o", tmp_rmd])
    nb2 = read(tmp_rmd)
    compare_notebooks(nb2, nb, "Rmd")

    # read markdown notebook on stdin, write to ipynb
    with open(tmp_rmd) as fp, mock.patch("sys.stdin", fp):
        jupytext(["-o", tmp_ipynb])
    nb2 = read(tmp_ipynb)
    compare_notebooks(nb2, nb, "Rmd")


def test_set_kernel_works_with_pipes_326(capsys):
    md = u"""```python
1 + 1
```"""

    with mock.patch("sys.stdin", StringIO(md)):
        jupytext(["--to", "ipynb", "--set-kernel", "-", "-"])

    out, err = capsys.readouterr()
    assert err == ""
    nb = reads(out, "ipynb")
    assert "kernelspec" in nb.metadata


@skip_on_windows
@pytest.mark.filterwarnings("ignore")
def test_utf8_out_331(capsys, caplog):
    py = u"from IPython.core.display import HTML; HTML(u'\xd7')"

    with mock.patch("sys.stdin", StringIO(py)):
        jupytext(["--to", "ipynb", "--execute", "-"])

    out, err = capsys.readouterr()

    assert err == ""
    nb = reads(out, "ipynb")
    assert len(nb.cells) == 1
    print(nb.cells[0].outputs)
    assert nb.cells[0].outputs[0]["data"]["text/html"] == u"\xd7"


@requires_jupytext_installed
@pytest.mark.filterwarnings("ignore:The --pre-commit argument is deprecated")
def test_cli_expect_errors(tmp_ipynb):
    with pytest.raises(ValueError):
        jupytext([])
    with pytest.raises(ValueError):
        jupytext(["--sync"])
    with pytest.raises(ValueError):
        jupytext([tmp_ipynb, tmp_ipynb, "--paired-paths"])
    with pytest.raises(ValueError):
        jupytext(["--pre-commit", "notebook.ipynb"])
    with pytest.raises(ValueError):
        jupytext(["notebook.ipynb", "--from", "py:percent", "--to", "md"])
    with pytest.raises(ValueError):
        jupytext([])
    with pytest.raises(
        (SystemExit, TypeError)
    ):  # SystemExit on Windows, TypeError on Linux
        system("jupytext", ["notebook.ipynb", "--from", "py:percent", "--to", "md"])


@pytest.mark.filterwarnings(
    "ignore:You have passed a file name to the '--to' option, "
    "when a format description was expected. "
    "Maybe you want to use the '-o' option instead?"
)
def test_format_prefix_suffix(tmpdir, cwd_tmpdir):
    os.makedirs("notebooks")
    tmp_ipynb = "notebooks/notebook_name.ipynb"
    tmp_py = "scripts/notebook_name.py"
    write(new_notebook(), tmp_ipynb)

    jupytext([tmp_ipynb, "--to", "../scripts//py"])
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)

    jupytext([tmp_ipynb, "--to", "scripts//py", "--from", "notebooks//ipynb"])
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)

    tmp_ipynb = "notebooks/nb_prefix_notebook_name.ipynb"
    tmp_py = "scripts/script_prefix_notebook_name.py"
    write(new_notebook(), tmp_ipynb)

    jupytext(
        [
            tmp_ipynb,
            "--to",
            "scripts/script_prefix_/py",
            "--from",
            "notebooks/nb_prefix_/ipynb",
        ]
    )
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)

    tmp_ipynb = "notebooks/nb_prefix_notebook_name_nb_suffix.ipynb"
    tmp_py = "scripts/script_prefix_notebook_name_script_suffix.py"
    write(new_notebook(), tmp_ipynb)

    jupytext(
        [
            tmp_ipynb,
            "--to",
            "scripts/script_prefix_/_script_suffix.py",
            "--from",
            "notebooks/nb_prefix_/_nb_suffix.ipynb",
        ]
    )
    assert os.path.isfile(tmp_py)
    os.remove(tmp_py)


def test_cli_sync_file_with_suffix(tmpdir, cwd_tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_pct_py = "notebook.pct.py"
    tmp_lgt_py = "notebook.lgt.py"
    tmp_rmd = "notebook.Rmd"
    nb = new_notebook(
        cells=[new_code_cell(source="1+1")],
        metadata={"jupytext": {"formats": "ipynb,.pct.py:percent,.lgt.py:light,Rmd"}},
    )

    write(nb, tmp_pct_py, fmt=".pct.py:percent")
    jupytext(["--sync", tmp_pct_py])
    assert os.path.isfile(tmp_lgt_py)
    assert os.path.isfile(tmp_rmd)
    assert os.path.isfile(tmp_ipynb)

    jupytext(["--sync", tmp_lgt_py])
    jupytext(["--sync", tmp_ipynb])

    with open(tmp_lgt_py) as fp:
        assert fp.read().splitlines()[-2:] == ["", "1+1"]
    with open(tmp_pct_py) as fp:
        fp.read().splitlines()[-3:] == ["", "# %%", "1+1"]
    with open(tmp_rmd) as fp:
        fp.read().splitlines()[-4:] == ["", "```{python}", "1+1", "```"]


@requires_sphinx_gallery
def test_rst2md(tmpdir, cwd_tmpdir):
    tmp_py = "notebook.py"
    tmp_ipynb = "notebook.ipynb"

    # Write notebook in sphinx format
    nb = new_notebook(
        cells=[
            new_markdown_cell("A short sphinx notebook"),
            new_markdown_cell(":math:`1+1`"),
        ]
    )
    write(nb, tmp_py, fmt="py:sphinx")

    jupytext(
        [
            tmp_py,
            "--from",
            "py:sphinx",
            "--to",
            "ipynb",
            "--opt",
            "rst2md=True",
            "--opt",
            "cell_metadata_filter=-all",
        ]
    )

    assert os.path.isfile(tmp_ipynb)
    nb = read(tmp_ipynb)

    assert nb.metadata["jupytext"]["cell_metadata_filter"] == "-all"
    assert nb.metadata["jupytext"]["rst2md"] is False

    # Was rst to md conversion effective?
    assert nb.cells[2].source == "$1+1$"


def test_remove_jupytext_metadata(tmpdir, cwd_tmpdir):
    tmp_ipynb = "notebook.ipynb"
    nb = new_notebook(
        metadata={
            "jupytext": {
                "main_language": "python",
                "text_representation": {
                    "extension": ".md",
                    "format_name": "markdown",
                    "format_version": "1.0",
                    "jupytext_version": "0.8.6",
                },
            }
        }
    )

    nbformat.write(nb, tmp_ipynb, version=nbformat.NO_CONVERT)
    # Jupytext removes the 'text_representation' information from the notebook
    jupytext([tmp_ipynb, "--update-metadata", '{"jupytext":{"main_language":null}}'])
    nb2 = read(tmp_ipynb)
    assert not nb2.metadata

    nbformat.write(nb, tmp_ipynb, version=nbformat.NO_CONVERT)
    jupytext([tmp_ipynb, "--set-formats", "ipynb,py:light"])

    nb2 = read(tmp_ipynb)
    assert nb2.metadata == {
        "jupytext": {"formats": "ipynb,py:light", "main_language": "python"}
    }


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
@pytest.mark.parametrize("fmt", ["py:light", "py:percent", "md"])
def test_convert_and_update_preserves_notebook(nb_file, fmt, tmpdir, cwd_tmpdir):
    # cannot encode magic parameters in markdown yet
    if ("magic" in nb_file or "LateX" in nb_file) and fmt == "md":
        return

    tmp_ipynb = "notebook.ipynb"
    copyfile(nb_file, tmp_ipynb)
    ext = long_form_one_format(fmt)["extension"]
    tmp_text = "notebook" + ext

    jupytext(["--to", fmt, tmp_ipynb])
    jupytext(["--to", "ipynb", "--update", tmp_text])

    nb_org = read(nb_file)
    nb_now = read(tmp_ipynb)

    # The cell marker changes from """ to r""" on the LateX notebook #836
    if "LateX" in nb_file and fmt == "py:percent":
        last_cell = nb_now.cells[-1]
        last_cell.metadata["cell_marker"] = last_cell.metadata["cell_marker"][1:]

    compare(nb_now, nb_org)


def test_incorrect_notebook_causes_early_exit(tmpdir, cwd_tmpdir):
    incorrect_ipynb = "incorrect.ipynb"
    incorrect_md = "incorrect.md"
    with open(incorrect_ipynb, "w") as fp:
        fp.write(
            '{"nbformat": 4, "nbformat_minor": 2, "metadata": {INCORRECT}, "cells": []}'
        )

    correct_ipynb = "correct.ipynb"
    correct_md = "correct.md"
    with open(correct_ipynb, "w") as fp:
        fp.write('{"nbformat": 4, "nbformat_minor": 2, "metadata": {}, "cells": []}')

    with pytest.raises(
        nbformat.reader.NotJSONError, match="Notebook does not appear to be JSON"
    ):
        jupytext([incorrect_ipynb, correct_ipynb, "--to", "md"])

    assert not os.path.exists(incorrect_md)
    assert not os.path.exists(correct_md)


def test_warn_only_skips_incorrect_notebook(tmpdir, cwd_tmpdir, capsys):
    incorrect_ipynb = "incorrect.ipynb"
    incorrect_md = "incorrect.md"
    with open(incorrect_ipynb, "w") as fp:
        fp.write(
            '{"nbformat": 4, "nbformat_minor": 2, "metadata": {INCORRECT}, "cells": []}'
        )

    correct_ipynb = "correct.ipynb"
    correct_md = "correct.md"
    with open(correct_ipynb, "w") as fp:
        fp.write('{"nbformat": 4, "nbformat_minor": 2, "metadata": {}, "cells": []}')

    jupytext([incorrect_ipynb, correct_ipynb, "--to", "md", "--warn-only"])

    _, err = capsys.readouterr()
    assert "Notebook does not appear to be JSON" in str(err)

    assert not os.path.exists(incorrect_md)
    assert os.path.exists(correct_md)


@pytest.mark.parametrize("fmt", ["md", "Rmd", "py", "py:percent", "py:hydrogen"])
def test_339_ipynb(tmpdir, cwd_tmpdir, fmt):
    tmp_ipynb = "test.ipynb"
    nb = new_notebook(cells=[new_code_cell("cat = 42")])
    nbformat.write(nb, tmp_ipynb)

    assert jupytext([tmp_ipynb, "--to", fmt, "--test-strict"]) == 0


def test_339_py(tmpdir, cwd_tmpdir):
    """Test that an incorrect round trip conversion on the text file is detected"""
    tmp_py = "test.py"
    with open(tmp_py, "w") as fp:
        fp.write(
            """# %%
cat = 42
"""
        )

    def erroneous_is_magic(line, language, comment_magics, explicitly_code):
        return "cat" in line

    with mock.patch("jupytext.magics.is_magic", erroneous_is_magic):
        assert jupytext([tmp_py, "--to", "ipynb", "--test-strict"]) != 0


def test_339_require_to(tmpdir, cwd_tmpdir):
    """Test that the `--to` argument is asked for when a `--test` command is provided"""
    with pytest.raises(ValueError, match="--to"):
        jupytext(["test.py", "--test-strict"])


def test_399_to_script_then_set_formats(tmpdir, cwd_tmpdir):
    nb = new_notebook(cells=[new_code_cell("1 + 1")])
    tmp_py = "notebook_first.py"
    tmp_ipynb = "notebook_first.ipynb"
    nbformat.write(nb, tmp_ipynb)

    jupytext(["--to", "py:percent", tmp_ipynb])
    assert os.path.isfile(tmp_py)

    jupytext(["--set-formats", "ipynb,py:percent", tmp_ipynb])


def test_set_format_with_subfolder(tmpdir, cwd_tmpdir):
    """Here we reproduce issue #450"""
    py = """# %% [markdown]
# A short notebook
"""

    tmpdir.mkdir("python_scripts").join("01_tabular_data_exploration.py").write(py)

    jupytext(
        [
            "--set-formats",
            "python_scripts//py:percent,notebooks//ipynb",
            "python_scripts/01_tabular_data_exploration.py",
        ]
    )


@requires_myst
@requires_pandoc
@pytest.mark.parametrize("format_name", ["md", "md:myst", "md:pandoc"])
def test_create_header_with_set_formats(format_name, cwd_tmpdir, tmpdir):
    """Test jupytext --set-formats <format_name> #485"""

    tmpdir.join("notebook.md").write("\n")

    jupytext(["--set-formats", format_name, "notebook.md"])

    nb = read("notebook.md")
    assert nb["metadata"]["jupytext"]["formats"] == format_name


@requires_myst
@requires_pandoc
@pytest.mark.parametrize(
    "format_name", ["md", "md:myst", "md:pandoc", "py:light", "py:percent"]
)
def test_create_header_with_set_formats_and_set_kernel(format_name, tmpdir, cwd_tmpdir):
    """Test jupytext --set-formats <format_name> --set-kernel - #485"""

    ext = format_name.split(":")[0]
    tmp_nb = "notebook." + ext
    tmpdir.join(tmp_nb).write("\n")

    jupytext(["--set-formats", format_name, "--set-kernel", "-", tmp_nb])

    nb = read(tmp_nb)
    assert nb["metadata"]["jupytext"]["formats"] == format_name
    assert "kernelspec" in nb["metadata"]


def test_set_option_split_at_heading(tmpdir, cwd_tmpdir):
    tmp_rmd = tmpdir.join("notebook.Rmd")
    tmp_rmd.write(
        """A paragraph

# H1 Header
"""
    )

    jupytext(["notebook.Rmd", "--opt", "split_at_heading=true"])
    assert "split_at_heading: true" in tmp_rmd.read()
    nb = read("notebook.Rmd")

    nb_expected = new_notebook(
        cells=[new_markdown_cell("A paragraph"), new_markdown_cell("# H1 Header")]
    )
    compare_notebooks(nb, nb_expected)


def test_pair_in_tree(tmpdir):
    nb_file = tmpdir.mkdir("notebooks").mkdir("subfolder").join("example.ipynb")
    py_file = tmpdir.mkdir("scripts").mkdir("subfolder").join("example.py")

    write(new_notebook(cells=[new_markdown_cell("A markdown cell")]), str(nb_file))

    jupytext(["--set-formats", "notebooks///ipynb,scripts///py:percent", str(nb_file)])

    assert py_file.exists()
    assert "A markdown cell" in py_file.read()


def test_pair_in_tree_and_parent(tmpdir):
    nb_file = (
        tmpdir.mkdir("notebooks")
        .mkdir("subfolder")
        .mkdir("a")
        .mkdir("b")
        .join("example.ipynb")
    )
    py_file = tmpdir.mkdir("scripts").mkdir("subfolder").mkdir("c").join("example.py")

    write(new_notebook(cells=[new_markdown_cell("A markdown cell")]), str(nb_file))

    jupytext(
        ["--set-formats", "notebooks//a/b//ipynb,scripts//c//py:percent", str(nb_file)]
    )

    assert py_file.exists()
    assert "A markdown cell" in py_file.read()


@requires_pandoc
def test_sync_pipe_config(tmpdir):
    """Sync a notebook to a script paired in a tree, and reformat the markdown cells using pandoc"""

    tmpdir.join("jupytext.toml").write(
        """# By default, the notebooks in this repository are in the notebooks subfolder
# and they are paired to scripts in the script subfolder.
formats = "notebooks///ipynb,scripts///py:percent"
"""
    )

    nb_file = tmpdir.mkdir("notebooks").join("wrap_markdown.ipynb")
    long_text = "This is a " + ("very " * 24) + "long sentence."
    assert len(long_text) > 100
    nb = new_notebook(cells=[new_markdown_cell(long_text)])
    write(nb, str(nb_file))

    jupytext(
        [
            "--sync",
            "--pipe-fmt",
            "ipynb",
            "--pipe",
            "pandoc --from ipynb --to ipynb --atx-headers",
            str(nb_file),
        ]
    )

    py_text = tmpdir.join("scripts").join("wrap_markdown.py").read()
    assert "This is a very very" in py_text
    for line in py_text.splitlines():
        assert len(line) <= 79

    nb = read(nb_file, as_version=4)
    text = nb.cells[0].source
    assert len(text.splitlines()) == 3
    assert text != long_text


def test_sync_script_dotdot_folder_564(tmpdir):
    """Reproduce the setting of issue #564"""
    nb_file = tmpdir.mkdir("colabs").mkdir("colabs").join("rigid_object_tutorial.ipynb")
    py_file = tmpdir.join("colabs").mkdir("nb_python").join("rigid_object_tutorial.py")
    py_file.write("1 + 1\n")

    jupytext(
        ["--set-formats", "../nb_python//py:percent,../colabs//ipynb", str(py_file)]
    )

    assert nb_file.exists()

    jupytext(["--sync", str(py_file)])
    jupytext(["--sync", str(nb_file)])


@contextmanager
def no_warning():
    with pytest.warns(None) as records:
        yield

    # There should be no warning
    for record in records:
        # Temporary exception for for this one, see #865
        if (
            "Passing a schema to Validator.iter_errors is deprecated "
            "and will be removed in a future release" in str(record.message)
        ):
            continue
        raise RuntimeError(record)


def test_no_warning():
    with pytest.raises(RuntimeError, match="a sample warning"):
        with no_warning():
            warnings.warn("a sample warning")


def test_jupytext_to_file_emits_a_warning(tmpdir):
    """The user may type
        jupytext notebook.ipynb --to script.py
    meaning
        jupytext notebook.ipynb -o script.py
    """
    os.chdir(str(tmpdir))

    nb_file = tmpdir.join("notebook.ipynb")
    write(new_notebook(), str(nb_file))

    with no_warning():
        jupytext(["notebook.ipynb", "-o", "script.py"])

    with pytest.warns(UserWarning, match="Maybe you want to use the '-o' option"):
        jupytext(["notebook.ipynb", "--to", "script.py"])


def test_jupytext_set_formats_file_gives_an_informative_error(tmpdir, cwd_tmpdir):
    """The user may type
        jupytext --set-formats notebook.md
    meaning
        jupytext --sync notebook.md
    """
    cfg_file = tmpdir.join("jupytext.toml")
    cfg_file.write('formats = "md,ipynb,py:percent"')

    md_file = tmpdir.join("notebook.md")
    py_file = tmpdir.join("notebook.py")
    nb_file = tmpdir.join("notebook.ipynb")
    md_file.write("Some text")

    with no_warning():
        jupytext(["--sync", "notebook.md"])

    assert py_file.exists()
    assert nb_file.exists()

    with pytest.raises(ValueError, match="jupytext --sync notebook.md"):
        jupytext(["--set-formats", "notebook.md"])

    # Remove the config file, otherwise test_jupytext_jupyter_fs_metamanager fails later on!
    cfg_file.remove()


def test_diff(tmpdir, cwd_tmpdir, capsys):
    write(new_notebook(cells=[new_code_cell("1 + 1")]), "test.ipynb")
    write(new_notebook(cells=[new_code_cell("2 + 2")]), "test.py", fmt="py:percent")

    jupytext(["--diff", "test.py", "test.ipynb"])
    captured = capsys.readouterr()
    assert "-2 + 2\n+1 + 1" in captured.out


def test_show_changes(tmpdir, cwd_tmpdir, capsys):
    write(new_notebook(cells=[new_code_cell("1 + 1")]), "test.ipynb")
    write(new_notebook(cells=[new_code_cell("2 + 2")]), "test.py", fmt="py:percent")

    jupytext(["--to", "py:percent", "test.ipynb", "--show-changes"])
    captured = capsys.readouterr()
    assert "-2 + 2\n+1 + 1" in captured.out


@requires_user_kernel_python3
def test_skip_execution(tmpdir, cwd_tmpdir, tmp_repo, python_notebook, capsys):
    write(
        new_notebook(cells=[new_code_cell("1 + 1")], metadata=python_notebook.metadata),
        "test.ipynb",
    )
    tmp_repo.index.add("test.ipynb")

    jupytext(["--execute", "--pre-commit-mode", "test.ipynb"])
    captured = capsys.readouterr()
    assert "Executing notebook" in captured.out

    nb = read("test.ipynb")
    assert nb.cells[0].execution_count == 1

    jupytext(["--execute", "--pre-commit-mode", "test.ipynb"])
    captured = capsys.readouterr()
    assert "skipped" in captured.out


def test_glob_recursive(tmpdir, cwd_tmpdir):
    tmpdir.mkdir("subfolder").join("test.py").write("1 + 1\n")
    tmpdir.join("test.py").write("2 + 2\n")
    jupytext(["--to", "ipynb", "**/*.py"])

    assert tmpdir.join("test.ipynb").isfile()
    assert tmpdir.join("subfolder").join("test.ipynb").isfile()


def test_jupytext_sync_preserves_cell_ids(tmpdir, cwd_tmpdir, notebook_with_outputs):
    write(notebook_with_outputs, "test.ipynb")

    # Sync with a py file, this should not change the cell id
    jupytext(["--set-formats", "ipynb,py:percent", "test.ipynb"])
    nb = read("test.ipynb")
    assert nb.cells[0].source == "1+1"
    assert nb.cells[0].id == notebook_with_outputs.cells[0].id

    # Change the py file and sync. This should not change the cell id neither
    py_nb = tmpdir.join("test.py")
    py = py_nb.read()
    py_nb.write(py.replace("1+1", "2+2"))

    jupytext(["--sync", "test.ipynb"])
    nb = read("test.ipynb")
    assert nb.cells[0].source == "2+2"
    assert nb.cells[0].id == notebook_with_outputs.cells[0].id


def test_jupytext_update_preserves_cell_ids(tmpdir, cwd_tmpdir, notebook_with_outputs):
    write(notebook_with_outputs, "test.ipynb")

    # Sync with a py file, this should not change the cell id
    jupytext(["--to", "py:percent", "test.ipynb"])
    nb = read("test.ipynb")
    assert nb.cells[0].source == "1+1"
    assert nb.cells[0].id == notebook_with_outputs.cells[0].id

    # Change the py file and update the ipynb file.
    # This should not change the cell id neither
    py_nb = tmpdir.join("test.py")
    py = py_nb.read()
    py_nb.write(py.replace("1+1", "2+2"))

    jupytext(["--to", "notebook", "--update", "test.py"])
    nb = read("test.ipynb")
    assert nb.cells[0].source == "2+2"
    assert nb.cells[0].id == notebook_with_outputs.cells[0].id


def test_jupytext_to_ipynb_suggests_update(tmpdir, cwd_tmpdir, capsys):
    tmpdir.join("test.py").write("1 + 1\n")
    jupytext(["--to", "ipynb", "test.py"])
    capture = capsys.readouterr()
    assert "update" not in capture.out

    jupytext(["--to", "ipynb", "test.py"])
    capture = capsys.readouterr()
    assert "update" in capture.out


@pytest.mark.parametrize("formats", ["", "py:percent", "py", "py:percent,ipynb"])
def test_jupytext_to_ipynb_does_not_update_timestamp_if_output_not_in_pair(
    tmpdir, cwd_tmpdir, python_notebook, capsys, formats
):
    # Write a text notebook
    nb = python_notebook
    if formats:
        nb.metadata["jupytext"] = {"formats": formats}

    test_py = tmpdir.join("test.py")
    write(nb, str(test_py))

    # make it read-only
    test_py.chmod(0o444)

    # py -> ipynb
    if "ipynb" not in formats:
        jupytext(["--to", "ipynb", "test.py"])
    else:
        jupytext(["--to", "ipynb", "test.py", "-o", "another.ipynb"])

    capture = capsys.readouterr()
    assert "Updating the timestamp" not in capture.out


@pytest.mark.parametrize("formats", ["py:percent", "py", None])
def test_jupytext_to_ipynb_does_not_update_timestamp_if_not_paired(
    tmpdir, cwd_tmpdir, python_notebook, capsys, formats
):
    # Write a text notebook
    nb = python_notebook
    if formats:
        nb.metadata["jupytext"] = {"formats": formats}

    test_py = tmpdir.join("test.py")
    write(nb, str(test_py))

    # make it read-only
    test_py.chmod(0o444)

    # py -> ipynb
    jupytext(["--to", "ipynb", "test.py"])

    capture = capsys.readouterr()
    assert "Updating the timestamp" not in capture.out


@pytest.mark.parametrize("formats", ["ipynb,py", "py:percent", "py", None])
def test_use_source_timestamp(tmpdir, cwd_tmpdir, python_notebook, capsys, formats):
    # Write a text notebook
    nb = python_notebook
    if formats:
        nb.metadata["jupytext"] = {"formats": formats}

    test_py = tmpdir.join("test.py")
    test_ipynb = tmpdir.join("test.ipynb")
    write(nb, str(test_py))
    src_timestamp = test_py.stat().mtime

    # Wait...
    time.sleep(0.1)

    # py -> ipynb
    jupytext(["--to", "ipynb", "test.py", "--use-source-timestamp"])

    capture = capsys.readouterr()
    assert "Updating the timestamp" not in capture.out

    dest_timestamp = test_ipynb.stat().mtime
    # on Mac OS the dest_timestamp is truncated at the microsecond (#790)
    assert src_timestamp - 1e-6 <= dest_timestamp <= src_timestamp

    # Make sure that we can open the file in Jupyter
    from jupytext.contentsmanager import TextFileContentsManager

    cm = TextFileContentsManager()
    cm.outdated_text_notebook_margin = 0.001
    cm.root_dir = str(tmpdir)

    # No error here
    cm.get("test.ipynb")

    # But now if we don't use --use-source-timestamp
    jupytext(["--to", "ipynb", "test.py"])
    os.utime(test_py, (src_timestamp, src_timestamp))

    # Then we can't open paired notebooks
    if formats == "ipynb,py":
        from tornado.web import HTTPError

        with pytest.raises(HTTPError, match="is more recent than test.py"):
            cm.get("test.ipynb")
    else:
        cm.get("test.ipynb")


def test_round_trip_with_null_metadata_792(tmpdir, cwd_tmpdir, python_notebook):
    nb = python_notebook
    nb.metadata.kernelspec = {
        "argv": ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "Python 3",
        "env": None,
        "interrupt_mode": "signal",
        "language": "python",
        "metadata": None,
        "name": "python3",
    }
    write(nb, "test.ipynb")
    jupytext(["--to", "py:percent", "test.ipynb"])
    jupytext(["--to", "ipynb", "test.py"])
    nb = read("test.ipynb")
    assert nb.metadata.kernelspec.env is None
