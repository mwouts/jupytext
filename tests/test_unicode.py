# coding: utf-8
import pytest
import jupytext
from jupytext.compare import compare
from .utils import list_notebooks
from nbformat.v4.nbbase import new_notebook, new_markdown_cell

try:
    unicode  # Python 2
except NameError:
    unicode = str  # Python 3


@pytest.mark.parametrize("nb_file", list_notebooks() + list_notebooks("Rmd"))
def test_notebook_contents_is_unicode(nb_file):
    nb = jupytext.read(nb_file)

    for cell in nb.cells:
        assert cell.source == "" or isinstance(cell.source, unicode)


def test_write_non_ascii(tmpdir):
    nb = jupytext.reads(u"Non-ascii contênt", "Rmd")
    jupytext.write(nb, str(tmpdir.join("notebook.Rmd")))
    jupytext.write(nb, str(tmpdir.join("notebook.ipynb")))


def test_encoding_in_scripts_only(no_jupytext_version_number):
    """UTF encoding should not be added to markdown files"""
    nb = new_notebook(
        cells=[new_markdown_cell("α")],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
    )

    # Saving to and reading from py creates an encoding
    py_light = jupytext.writes(nb, "py:light")
    compare(
        py_light,
        """# -*- coding: utf-8 -*-
# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# α
""",
    )
    nb = jupytext.reads(py_light, "py:light")
    assert "encoding" in nb.metadata["jupytext"]

    py_percent = jupytext.writes(nb, "py:percent")
    compare(
        py_percent,
        """# -*- coding: utf-8 -*-
# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# α
""",
    )

    md = jupytext.writes(nb, "md")
    compare(
        md,
        """---
jupyter:
  jupytext:
    encoding: '# -*- coding: utf-8 -*-'
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

α
""",
    )

    rmd = jupytext.writes(nb, "Rmd")
    compare(
        rmd,
        """---
jupyter:
  jupytext:
    encoding: '# -*- coding: utf-8 -*-'
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

α
""",
    )
