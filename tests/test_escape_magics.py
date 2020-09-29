import pytest
from nbformat.v4.nbbase import new_code_cell, new_notebook
from jupytext.compare import compare
from jupytext.magics import comment_magic, uncomment_magic, unesc, is_magic
from jupytext.compare import compare_notebooks
import jupytext
from .utils import notebook_model


def test_unesc():
    assert unesc("# comment", "python") == "comment"
    assert unesc("#comment", "python") == "comment"
    assert unesc("comment", "python") == "comment"


@pytest.mark.parametrize(
    "line",
    [
        "%matplotlib inline",
        "#%matplotlib inline",
        "##%matplotlib inline",
        "%%HTML",
        "%autoreload",
        "%store",
    ],
)
def test_escape(line):
    assert comment_magic([line]) == ["# " + line]
    assert uncomment_magic(comment_magic([line])) == [line]


@pytest.mark.parametrize("line", ["@pytest.fixture"])
def test_escape_magic_only(line):
    assert comment_magic([line]) == [line]


@pytest.mark.parametrize("line", ["%matplotlib inline #noescape"])
def test_force_noescape(line):
    assert comment_magic([line]) == [line]


@pytest.mark.parametrize("line", ["%matplotlib inline #noescape"])
def test_force_noescape_with_gbl_esc_flag(line):
    assert comment_magic([line], global_escape_flag=True) == [line]


@pytest.mark.parametrize("line", ["%matplotlib inline #escape"])
def test_force_escape_with_gbl_esc_flag(line):
    assert comment_magic([line], global_escape_flag=False) == ["# " + line]


@pytest.mark.parametrize(
    "fmt,commented",
    zip(
        [
            "md",
            "Rmd",
            "py:light",
            "py:percent",
            "py:sphinx",
            "R",
            "ss:light",
            "ss:percent",
        ],
        [False, True, True, True, True, True, True, True],
    ),
)
def test_magics_commented_default(fmt, commented):
    nb = new_notebook(cells=[new_code_cell("%pylab inline")])

    text = jupytext.writes(nb, fmt)
    assert ("%pylab inline" in text.splitlines()) != commented
    nb2 = jupytext.reads(text, fmt)

    if "sphinx" in fmt:
        nb2.cells = nb2.cells[1:]

    compare_notebooks(nb2, nb)


@pytest.mark.parametrize(
    "fmt",
    ["md", "Rmd", "py:light", "py:percent", "py:sphinx", "R", "ss:light", "ss:percent"],
)
def test_magics_are_commented(fmt):
    nb = new_notebook(
        cells=[new_code_cell("%pylab inline")],
        metadata={
            "jupytext": {
                "comment_magics": True,
                "main_language": "R"
                if fmt == "R"
                else "scheme"
                if fmt.startswith("ss")
                else "python",
            }
        },
    )

    text = jupytext.writes(nb, fmt)
    assert "%pylab inline" not in text.splitlines()
    nb2 = jupytext.reads(text, fmt)

    if "sphinx" in fmt:
        nb2.cells = nb2.cells[1:]

    compare_notebooks(nb2, nb)


@pytest.mark.parametrize(
    "fmt",
    ["md", "Rmd", "py:light", "py:percent", "py:sphinx", "R", "ss:light", "ss:percent"],
)
def test_magics_are_not_commented(fmt):
    nb = new_notebook(
        cells=[new_code_cell("%pylab inline")],
        metadata={
            "jupytext": {
                "comment_magics": False,
                "main_language": "R"
                if fmt == "R"
                else "scheme"
                if fmt.startswith("ss")
                else "python",
            }
        },
    )

    text = jupytext.writes(nb, fmt)
    assert "%pylab inline" in text.splitlines()
    nb2 = jupytext.reads(text, fmt)

    if "sphinx" in fmt:
        nb2.cells = nb2.cells[1:]

    compare_notebooks(nb2, nb)


def test_force_comment_using_contents_manager(tmpdir):
    tmp_py = "notebook.py"

    cm = jupytext.TextFileContentsManager()
    cm.preferred_jupytext_formats_save = "py:percent"
    cm.root_dir = str(tmpdir)

    nb = new_notebook(cells=[new_code_cell("%pylab inline")])

    cm.save(model=notebook_model(nb), path=tmp_py)
    with open(str(tmpdir.join(tmp_py))) as stream:
        assert "# %pylab inline" in stream.read().splitlines()

    cm.comment_magics = False
    cm.save(model=notebook_model(nb), path=tmp_py)
    with open(str(tmpdir.join(tmp_py))) as stream:
        assert "%pylab inline" in stream.read().splitlines()


@pytest.mark.parametrize(
    "magic_cmd",
    [
        "ls",
        "!ls",
        "ls -al",
        "!whoami",
        "# ls",
        "# mv a b",
        "! mkdir tmp",
        "!./script",
        "! ./script",
        "!./script args",
        "!./script.sh args",
        "! ./script.sh args",
        "!~/script.sh args",
        "! ~/script.sh args",
        "!../script.sh $ENV $USER",
        "! ../script.sh $ENV $USER",
        "!$HOME/script.sh $ENV $USER",
        "!/bin/sh $ENV $USER",
        "! /bin/sh $ENV $USER",
        r"! \bin\sh $ENV $USER",
        r"!\bin\sh $ENV $USER",
        "cat",
        "cat ",
        "cat hello.txt",
        "cat --option=value hello.txt",
    ],
)
def test_comment_bash_commands_in_python(magic_cmd):
    assert comment_magic([magic_cmd]) == ["# " + magic_cmd]
    assert uncomment_magic(["# " + magic_cmd]) == [magic_cmd]


@pytest.mark.parametrize(
    "not_magic_cmd",
    ["copy(a)", "copy.deepcopy", "cat = 3", "cat=5", "cat, other = 5,3", "cat(5)"],
)
def test_do_not_comment_python_cmds(not_magic_cmd):
    assert comment_magic([not_magic_cmd]) == [not_magic_cmd]
    assert uncomment_magic([not_magic_cmd]) == [not_magic_cmd]


@pytest.mark.parametrize(
    "magic_cmd", ["ls", "!ls", "ls -al", "!whoami", "# ls", "# mv a b"]
)
def test_do_not_comment_bash_commands_in_R(magic_cmd):
    assert comment_magic([magic_cmd], language="R") == [magic_cmd]
    assert uncomment_magic([magic_cmd], language="R") == [magic_cmd]


def test_markdown_image_is_not_magic():
    assert is_magic("# !cmd", "python")
    assert not is_magic("# ![Image name](image.png", "python")


def test_question_is_not_magic():
    assert is_magic("float?", "python", explicitly_code=True)
    assert is_magic("# float?", "python", explicitly_code=True)
    assert not is_magic("# question: float?", "python", explicitly_code=True)


def test_multiline_python_magic(no_jupytext_version_number):
    nb = new_notebook(
        cells=[
            new_code_cell(
                """%load_ext watermark
%watermark -u -n -t -z \\
    -p jupytext -v

def g(x):
    return x+1"""
            )
        ]
    )

    text = jupytext.writes(nb, "py")
    compare(
        text,
        """# +
# %load_ext watermark
# %watermark -u -n -t -z \\
#     -p jupytext -v

def g(x):
    return x+1
""",
    )
    compare_notebooks(jupytext.reads(text, "py"), nb)


def test_configure_magic(no_jupytext_version_number):
    nb = new_notebook(
        cells=[
            new_code_cell(
                """%%configure -f \\
{"executorMemory": "3072M", "executorCores": 4, "numExecutors":10}"""
            )
        ]
    )

    text = jupytext.writes(nb, "py")
    compare(
        text,
        """# %%configure -f \\
# {"executorMemory": "3072M", "executorCores": 4, "numExecutors":10}
""",
    )
    compare_notebooks(jupytext.reads(text, "py"), nb)


def test_indented_magic():
    assert is_magic("    !rm file", "python")
    assert is_magic("    # !rm file", "python")
    assert comment_magic(["    !rm file"]) == ["    # !rm file"]
    assert uncomment_magic(["    # !rm file"]) == ["    !rm file"]
