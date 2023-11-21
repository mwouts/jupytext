from nbformat.v4.nbbase import new_markdown_cell, new_notebook

import jupytext
from jupytext.compare import compare


def test_notebook_contents_is_unicode(ipynb_file):
    nb = jupytext.read(ipynb_file)

    for cell in nb.cells:
        assert isinstance(cell.source, str)


def test_rmd_notebook_contents_is_unicode(rmd_file):
    nb = jupytext.read(rmd_file)

    for cell in nb.cells:
        assert isinstance(cell.source, str)


def test_write_non_ascii(tmpdir):
    nb = jupytext.reads("Non-ascii contênt", "Rmd")
    jupytext.write(nb, str(tmpdir.join("notebook.Rmd")))
    jupytext.write(nb, str(tmpdir.join("notebook.ipynb")))


def test_no_encoding_in_python_scripts(no_jupytext_version_number):
    """No UTF encoding should not be added to Python scripts"""
    nb = new_notebook(
        cells=[new_markdown_cell("α")],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
        },
    )

    # Saving to and reading from py creates an encoding
    py_light = jupytext.writes(nb, "py:light")
    compare(
        py_light,
        """# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# α
""",
    )


def test_encoding_in_scripts_only(no_jupytext_version_number):
    """UTF encoding should not be added to markdown files"""
    nb = new_notebook(
        cells=[new_markdown_cell("α")],
        metadata={
            "encoding": "# -*- coding: utf-8 -*-",
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
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
