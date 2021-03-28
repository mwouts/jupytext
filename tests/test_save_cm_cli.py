import nbformat
import pytest

import jupytext
from jupytext.cli import jupytext as jupytext_cli
from jupytext.compare import compare
from jupytext.formats import long_form_one_format

from .utils import notebook_model, requires_myst


@pytest.mark.parametrize(
    "fmt,input_fn",
    [
        ("md", "input-save-cm-cli-1.md"),
        ("md:myst", "input-save-cm-cli-1.md"),
        ("py:light", "input-save-cm-cli-1.md"),
        ("py:percent", "input-save-cm-cli-1.md"),
        ("md", "input-save-cm-cli-2.md"),
        ("md:myst", "input-save-cm-cli-2.md"),
        ("py:light", "input-save-cm-cli-2.md"),
        ("py:percent", "input-save-cm-cli-2.md"),
    ],
)
def test_save_in_cm_matches_cli(tmpdir, cwd_tmpdir, fmt, input_fn):

    # attributes of this format
    long_fmt = long_form_one_format(fmt)
    ext = long_fmt["extension"]
    # format_name = long_fmt.get('format_name', 'markdown')

    # the input file is md:myst
    requires_myst()

    # read sample input which is a md:myst notebook
    from pathlib import Path

    with (Path(__file__).parent / input_fn).open() as feed:
        myst_input = feed.read()
    nb = jupytext.reads(myst_input, "md:myst")
    nb.metadata["jupytext"]["formats"] = fmt

    # store notebook as ipynb in tmpdir
    ipynb_path = str(tmpdir.join("notebook.ipynb"))
    nbformat.write(nb, ipynb_path)

    # invoke jupytext to produce version1
    name1 = f"notebook1{ext}"
    jupytext_cli(["--to", fmt, "-o", name1, "notebook.ipynb"])

    # produce version2 with contents manager
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    name2 = f"notebook2{ext}"
    cm.save(model=notebook_model(nb), path=name2)

    text1 = tmpdir.join(name1).read()
    text2 = tmpdir.join(name2).read()

    compare(text1, text2)

    # yet another tour
    name3 = f"notebook3{ext}"
    jupytext_cli(["--to", fmt, "-o", name3, name1])
    text3 = tmpdir.join(name3).read()

    compare(text1, text3)
