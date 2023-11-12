import pytest
from nbformat import NotebookNode

import jupytext
from jupytext.compare import compare, compare_cells

HEADER = {
    ".py": """# ---
# jupyter:
#   jupytext:
#     main_language: python
# ---

""",
    ".R": """# ---
# jupyter:
#   jupytext:
#     main_language: python
# ---

""",
    ".md": """---
jupyter:
  jupytext:
    main_language: python
---

""",
    ".Rmd": """---
jupyter:
  jupytext:
    main_language: python
---

""",
}

ACTIVE_ALL = {
    ".py": """# %% active="ipynb,py,R,Rmd"
# This cell is active in all extensions
""",
    ".Rmd": """```{python active="ipynb,py,R,Rmd"}
# This cell is active in all extensions
```
""",
    ".md": """```python active="ipynb,py,R,Rmd"
# This cell is active in all extensions
```
""",
    ".R": """# %% active="ipynb,py,R,Rmd"
# This cell is active in all extensions
""",
    ".ipynb": {
        "cell_type": "code",
        "source": "# This cell is active in all extensions",
        "metadata": {"active": "ipynb,py,R,Rmd"},
        "execution_count": None,
        "outputs": [],
    },
}


def check_active_cell(ext, active_dict):
    text = ("" if ext == ".py" else HEADER[ext]) + active_dict[ext]
    nb = jupytext.reads(text, ext)
    assert len(nb.cells) == 1
    compare(jupytext.writes(nb, ext), text)
    cell = NotebookNode(active_dict[".ipynb"])
    compare_cells(nb.cells, [cell], compare_ids=False)


@pytest.mark.parametrize("ext", [".Rmd", ".md", ".py", ".R"])
def test_active_all(ext, no_jupytext_version_number):
    check_active_cell(ext, ACTIVE_ALL)


ACTIVE_IPYNB = {
    ".py": """# %% active="ipynb"
# # This cell is active only in ipynb
# %matplotlib inline
""",
    ".Rmd": """```{python active="ipynb", eval=FALSE}
# This cell is active only in ipynb
%matplotlib inline
```
""",
    ".md": """```python active="ipynb"
# This cell is active only in ipynb
%matplotlib inline
```
""",
    ".R": """# %% active="ipynb"
# # This cell is active only in ipynb
# %matplotlib inline
""",
    ".ipynb": {
        "cell_type": "code",
        "source": "# This cell is active only in ipynb\n" "%matplotlib inline",
        "metadata": {"active": "ipynb"},
        "execution_count": None,
        "outputs": [],
    },
}


@pytest.mark.parametrize("ext", [".Rmd", ".md", ".py", ".R"])
def test_active_ipynb(ext, no_jupytext_version_number):
    check_active_cell(ext, ACTIVE_IPYNB)


ACTIVE_IPYNB_RMD_USING_TAG = {
    ".py": """# %% tags=["active-ipynb-Rmd"]
# # This cell is active only in ipynb and Rmd
# %matplotlib inline
""",
    ".Rmd": """```{python tags=c("active-ipynb-Rmd")}
# This cell is active only in ipynb and Rmd
# %matplotlib inline
```
""",
    ".md": """```python tags=["active-ipynb-Rmd"]
# This cell is active only in ipynb and Rmd
%matplotlib inline
```
""",
    ".R": """# %% tags=["active-ipynb-Rmd"]
# # This cell is active only in ipynb and Rmd
# %matplotlib inline
""",
    ".ipynb": {
        "cell_type": "code",
        "source": "# This cell is active only in ipynb and Rmd\n" "%matplotlib inline",
        "metadata": {"tags": ["active-ipynb-Rmd"]},
        "execution_count": None,
        "outputs": [],
    },
}


@pytest.mark.parametrize("ext", [".Rmd", ".md", ".py", ".R"])
def test_active_ipynb_rmd_using_tags(ext, no_jupytext_version_number):
    check_active_cell(ext, ACTIVE_IPYNB_RMD_USING_TAG)


ACTIVE_IPYNB_RSPIN = {
    ".R": """#+ active="ipynb", eval=FALSE
# # This cell is active only in ipynb
# 1 + 1
""",
    ".ipynb": {
        "cell_type": "code",
        "source": "# This cell is active only in ipynb\n" "1 + 1",
        "metadata": {"active": "ipynb"},
        "execution_count": None,
        "outputs": [],
    },
}


def test_active_ipynb_rspin(no_jupytext_version_number):
    nb = jupytext.reads(ACTIVE_IPYNB_RSPIN[".R"], "R:spin")
    assert len(nb.cells) == 1
    compare(jupytext.writes(nb, "R:spin"), ACTIVE_IPYNB_RSPIN[".R"])
    cell = NotebookNode(ACTIVE_IPYNB_RSPIN[".ipynb"])
    compare_cells(nb.cells, [cell], compare_ids=False)


ACTIVE_PY_IPYNB = {
    ".py": """# %% active="ipynb,py"
# This cell is active in py and ipynb extensions
""",
    ".Rmd": """```{python active="ipynb,py", eval=FALSE}
# This cell is active in py and ipynb extensions
```
""",
    ".md": """```python active="ipynb,py"
# This cell is active in py and ipynb extensions
```
""",
    ".R": """# %% active="ipynb,py"
# # This cell is active in py and ipynb extensions
""",
    ".ipynb": {
        "cell_type": "code",
        "source": "# This cell is active in py and " "ipynb extensions",
        "metadata": {"active": "ipynb,py"},
        "execution_count": None,
        "outputs": [],
    },
}


@pytest.mark.parametrize("ext", [".Rmd", ".md", ".py", ".R"])
def test_active_py_ipynb(ext, no_jupytext_version_number):
    check_active_cell(ext, ACTIVE_PY_IPYNB)


ACTIVE_PY_R_IPYNB = {
    ".py": """# %% active="ipynb,py,R"
# This cell is active in py, R and ipynb extensions
""",
    ".Rmd": """```{python active="ipynb,py,R", eval=FALSE}
# This cell is active in py, R and ipynb extensions
```
""",
    ".R": """# %% active="ipynb,py,R"
# This cell is active in py, R and ipynb extensions
""",
    ".ipynb": {
        "cell_type": "code",
        "source": "# This cell is active in py, R and " "ipynb extensions",
        "metadata": {"active": "ipynb,py,R"},
        "execution_count": None,
        "outputs": [],
    },
}


@pytest.mark.parametrize("ext", [".Rmd", ".py", ".R"])
def test_active_py_r_ipynb(ext, no_jupytext_version_number):
    check_active_cell(ext, ACTIVE_PY_R_IPYNB)


ACTIVE_RMD = {
    ".py": """# %% active="Rmd"
# # This cell is active in Rmd only
""",
    ".Rmd": """```{python active="Rmd"}
# This cell is active in Rmd only
```
""",
    ".R": """# %% active="Rmd"
# # This cell is active in Rmd only
""",
    ".ipynb": {
        "cell_type": "raw",
        "source": "# This cell is active in Rmd only",
        "metadata": {"active": "Rmd"},
    },
}


@pytest.mark.parametrize("ext", [".Rmd", ".py", ".R"])
def test_active_rmd(ext, no_jupytext_version_number):
    check_active_cell(ext, ACTIVE_RMD)


ACTIVE_NOT_INCLUDE_RMD = {
    ".py": """# %% tags=["remove_cell"] active="Rmd"
# # This cell is active in Rmd only
""",
    ".Rmd": """```{python include=FALSE, active="Rmd"}
# This cell is active in Rmd only
```
""",
    ".R": """# %% tags=["remove_cell"] active="Rmd"
# # This cell is active in Rmd only
""",
    ".ipynb": {
        "cell_type": "raw",
        "source": "# This cell is active in Rmd only",
        "metadata": {"active": "Rmd", "tags": ["remove_cell"]},
    },
}


@pytest.mark.parametrize("ext", [".Rmd", ".py", ".R"])
def test_active_not_include_rmd(ext, no_jupytext_version_number):
    check_active_cell(ext, ACTIVE_NOT_INCLUDE_RMD)


def test_active_cells_from_py_percent(
    text="""# %% active="py"
print('should only be displayed in py file')

# %% tags=["active-py"]
print('should only be displayed in py file')

# %% active="ipynb"
# print('only in jupyter')
""",
):
    """Example taken from https://github.com/mwouts/jupytext/issues/477"""
    nb = jupytext.reads(text, "py:percent")
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[1].cell_type == "raw"
    assert nb.cells[2].cell_type == "code"
    assert nb.cells[2].source == "print('only in jupyter')"

    text2 = jupytext.writes(nb, "py:percent")
    compare(text2, text)


def test_comments_work_in_active_cells_from_py_percent_1131(
    text="""# %% tags=["active-py"]
# this is a comment
""",
):
    nb = jupytext.reads(text, "py:percent")
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[0].source == "# this is a comment"

    text2 = jupytext.writes(nb, "py:percent")
    compare(text2, text)


def test_comments_work_in_active_cells_from_py_light_1131(
    text="""# + tags=["active-py"]
# this is a comment
""",
):
    nb = jupytext.reads(text, "py:light")
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[0].source == "# this is a comment"

    text2 = jupytext.writes(nb, "py:light")
    compare(text2, text)


def test_comments_plus_code_work_in_active_cells_from_py_percent_1131(
    text="""# %% tags=["active-py"]
# this is a comment
1 + 1
""",
):
    nb = jupytext.reads(text, "py:percent")
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[0].source == "# this is a comment\n1 + 1"

    text2 = jupytext.writes(nb, "py:percent")
    compare(text2, text)


def test_comments_plus_code_work_in_active_cells_from_py_light_1131(
    text="""# + tags=["active-py"]
# this is a comment
1 + 1
""",
):
    nb = jupytext.reads(text, "py:light")
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[0].source == "# this is a comment\n1 + 1"

    text2 = jupytext.writes(nb, "py:light")
    compare(text2, text)


def test_active_cells_from_py_light(
    text="""# + active="py"
print('should only be displayed in py file')

# + tags=["active-py"]
print('should only be displayed in py file')

# + active="ipynb"
# print('only in jupyter')
""",
):
    """Example adapted from https://github.com/mwouts/jupytext/issues/477"""
    nb = jupytext.reads(text, "py:light")
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[1].cell_type == "raw"
    assert nb.cells[2].cell_type == "code"
    assert nb.cells[2].source == "print('only in jupyter')"

    text2 = jupytext.writes(nb, "py")
    compare(text2, text)
