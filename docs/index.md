# Jupyter notebooks as Markdown documents, Julia, Python or R scripts

[![](https://travis-ci.com/mwouts/jupytext.svg?branch=master)](https://travis-ci.com/mwouts/jupytext)
[![](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=master)](https://codecov.io/github/mwouts/jupytext?branch=master)
[![](https://img.shields.io/badge/lgtm-A+-brightgreen.svg)](https://lgtm.com/projects/g/mwouts/jupytext/context:python)

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext can save Jupyter notebooks as
- Markdown and R Markdown documents,
- Julia, Python, R, Bash, Scheme, Clojure, Matlab, Octave, C++ and q/kdb+ scripts.

The plain text formatting of the notebook cell divisions in scripts is configurable. Popular choices include the `percent` format [`# %%`] used by Spyder, VSCode, and others, and the `light` format which was developed to support this project. `light` uses as few cell markers as possible and is particularly suited for importing a pre-existing python script as a notebook with cell divisions automatically inferred from paragraph breaks in the source code.

## Site Contents

* [Install](install.md)
* [Using Jupytext from the Jupyter Server](using-server.md)
* [Using Jupytext from the Command Line](using-cli.md)
* [Formats supported in Jupytext](formats.md)
* [Examples](examples.md)
* [Advanced Usage](advanced.md)

## Quickstart

There are multiple ways to use `jupytext`:
- **Directly from Jupyter Notebook or JupyterLab.** Jupytext provides a _contents manager_ that allows Jupyter to save your notebook to your favorite format (`.py`, `.R`, `.jl`, `.md`, `.Rmd`...) in addition to (or in place of) the traditional `.ipynb` file. The text representation can be edited in your favorite editor. When you're done, refresh the notebook in Jupyter: inputs cells are loaded from the text file, while output cells are reloaded from the `.ipynb` file if present. Refreshing preserves kernel variables, so you can resume your work in the notebook and run the modified cells without having to rerun the notebook in full.
- **On the [command line](using-cli.html)**. `jupytext` converts Jupyter notebooks to their text representation, and back. The command line tool can act on notebooks in many ways. It can synchronize multiple representations of a notebook, pipe a notebook into a reformatting tool like `black`, etc... It can also work as a [pre-commit hook](#jupytext-as-a-git-pre-commit-hook) if you wish to automatically update the text representation when you commit the `.ipynb` file.
- **in Vim**: edit your Jupyter notebooks, represented as a Markdown document, or a Python script, with [jupytext.vim](https://github.com/goerz/jupytext.vim).

## Demo time

[![](https://img.shields.io/badge/TDS-Introducing%20Jupytext-blue.svg)](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57)
[![](https://img.shields.io/badge/YouTube-PyParis-red.svg)](https://www.youtube.com/watch?v=y-VEZenk824)
[![](https://img.shields.io/badge/Binder-Try%20it!-blue.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo)

Looking for a demo?
- Read the original [announcement](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57) in Towards Data Science,
- Watch the [PyParis talk](https://github.com/mwouts/jupytext_pyparis_2018/blob/master/README.md),
- or, try Jupytext online with [binder](https://mybinder.org/v2/gh/mwouts/jupytext/master?filepath=demo)!



## Want to contribute?

Contributions are welcome. Please let us know how you use `jupytext` and how we could improve it. You think the documentation could be improved? Go ahead! And stay tuned for more demos on [medium](https://medium.com/@marc.wouts) and [twitter](https://twitter.com/marcwouts)!
