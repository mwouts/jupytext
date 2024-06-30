import pytest

from jupytext import reads, writes
from jupytext.compare import compare
from jupytext.config import load_jupytext_configuration_file


@pytest.mark.requires_myst
def test_myst_header_is_stable_1247_using_inline_filter(
    md="""---
jupytext:
  formats: md:myst
  notebook_metadata_filter: -jupytext.text_representation.jupytext_version,settings,mystnb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
mystnb:
  execution_mode: 'off'
settings:
  output_matplotlib_strings: remove
---
""",
):
    nb = reads(md, fmt="md")
    md2 = writes(nb, fmt="md")

    compare(md2, md)


@pytest.mark.requires_myst
def test_myst_header_is_stable_1247_using_config(
    jupytext_toml_content="""notebook_metadata_filter = "-jupytext.text_representation.jupytext_version,settings,mystnb"
""",
    md="""---
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
mystnb:
  execution_mode: 'off'
settings:
  output_matplotlib_strings: remove
---
""",
):
    config = load_jupytext_configuration_file("jupytext.toml", jupytext_toml_content)

    nb = reads(md, fmt="md", config=config)
    md2 = writes(nb, fmt="md", config=config)

    compare(md2, md)
