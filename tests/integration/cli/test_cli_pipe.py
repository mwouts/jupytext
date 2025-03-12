import pytest

from jupytext.cli import jupytext


@pytest.mark.requires_myst
@pytest.mark.requires_black
def test_cli_black_myst(
    tmp_path,
    no_jupytext_version_number,
    text="""---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Quantum yield efficiency of photosynthesis

```{code-cell} python
# I'm some code
x = 1
```
""",
):
    tmp_md = tmp_path / "notebook.md"
    tmp_md.write_text(text)

    jupytext(["--pipe", "black", str(tmp_md)])

    assert tmp_md.read_text() == text
