"""Convert Markdown equations to doxygen equations and back
See https://github.com/mwouts/jupytext/issues/517"""

import re


def markdown_to_doxygen(string):
    """Markdown to Doxygen equations"""
    long_equations = re.sub(
        r"(?<!\\)\$\$(.*?)(?<!\\)\$\$", r"\\f[\g<1>\\f]", string, flags=re.DOTALL
    )
    inline_equations = re.sub(r"(?<!(\\|\$))\$(?!\$)", r"\\f$", long_equations)
    return inline_equations


def doxygen_to_markdown(string):
    """Doxygen to Markdown equations"""
    long_equations = re.sub(r"\\f\[(.*?)\\f\]", r"$$\g<1>$$", string, flags=re.DOTALL)
    inline_equations = re.sub(r"\\f\$", "$", long_equations)
    return inline_equations
