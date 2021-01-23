import pytest

import jupytext
from jupytext.compare import compare_notebooks


def test_as_version_has_appropriate_type():
    with pytest.raises(TypeError):
        jupytext.read("script.py", "py:percent")


def test_read_file_with_explicit_fmt(tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))

    with open(tmp_py, "w") as fp:
        fp.write(
            """# %%
1 + 1
"""
        )

    nb1 = jupytext.read(tmp_py)
    nb2 = jupytext.read(tmp_py, fmt="py:percent")

    compare_notebooks(nb2, nb1)
