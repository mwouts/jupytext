# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = "Jupytext"
copyright = "2018-2023, The Jupytext Team"
author = "The Jupytext Team"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx_copybutton", "myst_parser"]

# Auto-generated header anchors
myst_heading_anchors = 3

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "mwouts",  # Username
    "github_repo": "jupytext",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "alabaster"

html_sidebars = {"**": ["about.html", "navigation.html", "searchbox.html"]}

html_theme_options = {
    "github_button": True,
    "github_banner": True,
    "github_user": "mwouts",
    "github_repo": "jupytext",
    "github_type": "star",
    "logo": "logo.svg",
    "show_relbars": True,
}

pygments_style = "sphinx"
master_doc = "index"  # Makes `index.md` the main file

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "jupytext"
