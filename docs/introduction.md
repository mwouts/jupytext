# Introduction

[![](https://travis-ci.com/mwouts/jupytext.svg?branch=master)](https://travis-ci.com/mwouts/jupytext)
[![](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=master)](https://codecov.io/github/mwouts/jupytext?branch=master)
[![](https://img.shields.io/badge/lgtm-A+-brightgreen.svg)](https://lgtm.com/projects/g/mwouts/jupytext/context:python)

Have you always wished Jupyter notebooks were plain text documents? Wished you could edit them in your favorite IDE? And get clear and meaningful diffs when doing version control? Then... Jupytext may well be the tool you're looking for!

Jupytext can save Jupyter notebooks as
- Markdown and R Markdown documents,
- Scripts in many languages.

The languages that are currently supported by Jupytext are: Julia, Python, R, Bash, Scheme, Clojure, Matlab, Octave, C++, q/kdb+, IDL, TypeScript, Javascript, Scala, Rust/Evxcr, PowerShell, C#, F#, Robot Framework, Script of Script. Extending Jupytext to more languages should be easy - read more at [CONTRIBUTING.md](https://github.com/mwouts/jupytext/blob/master/CONTRIBUTING.md#). In addition, jupytext users can choose between two formats for notebooks as scripts:
- The `percent` format, compatible with several IDEs, including Spyder, Hydrogen, VScode and PyCharm. In that format, cells are delimited with a commented `%%`.
- The `light` format, designed for this project. Use that format to open standard scripts as notebooks, or to save notebooks as scripts with few cell markers - none when possible.

Jupytext can also convert these formats **into Jupyter Notebooks**, allowing
for two-directional syncing between formats. See below for a quick demo.

![](https://github.com/mwouts/jupytext-screenshots/raw/master/IntroducingJupytext/JupyterPyCharm.gif)

## How to use Jupytext

There are multiple ways to use `jupytext`:
- **Directly from Jupyter Notebook or JupyterLab.** Jupytext provides a _contents manager_ that allows Jupyter to save your notebook to your favorite format (`.py`, `.R`, `.jl`, `.md`, `.Rmd`...) in addition to (or in place of) the traditional `.ipynb` file. The text representation can be edited in your favorite editor. When you're done, refresh the notebook in Jupyter: inputs cells are loaded from the text file, while output cells are reloaded from the `.ipynb` file if present. Refreshing preserves kernel variables, so you can resume your work in the notebook and run the modified cells without having to rerun the notebook in full.
- **On the [command line](using-cli.md)**. `jupytext` converts Jupyter notebooks to their text representation, and back. The command line tool can act on notebooks in many ways. It can synchronize multiple representations of a notebook, pipe a notebook into a reformatting tool like `black`, etc... It can also work as a [pre-commit hook](using-cli.html#jupytext-as-a-git-pre-commit-hook) if you wish to automatically update the text representation when you commit the `.ipynb` file.
- **in Vim**: edit your Jupyter notebooks, represented as a Markdown document, or a Python script, with [jupytext.vim](https://github.com/goerz/jupytext.vim).

## Jupytext formats

Jupytext implements a series of text formats for notebooks, which are documented [here](formats.md).

In short: the Markdown representation of notebooks fits well the notebooks that contain narratives, while notebooks that mostly contain code are conveniently saved as scripts. The most popular formats for notebooks as scripts are:
- the `percent` format (in which cells are delimited with `# %%`) also used by Spyder, VSCode, PyCharm, and others, 
- and the `light` format which was developed to support this project. `light` uses as few cell markers as possible and is particularly suited for importing a pre-existing python script as a notebook with cell divisions automatically inferred from paragraph breaks in the source code.

## Demo time

[![](https://img.shields.io/badge/TDS-Introducing%20Jupytext-blue.svg)](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57)
[![](https://img.shields.io/badge/YouTube-PyParis-red.svg)](https://www.youtube.com/watch?v=y-VEZenk824)
[![](https://img.shields.io/badge/CFM%20insights-Jupytext%20&%20Papermill-00ab6c.svg)](https://medium.com/capital-fund-management/automated-reports-with-jupyter-notebooks-using-jupytext-and-papermill-619e60c37330)
[![](https://img.shields.io/badge/Binder-Try%20it!-blue.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb)

Looking for a demo?
- Read the original [announcement](https://towardsdatascience.com/introducing-jupytext-9234fdff6c57) in _Towards Data Science_ (Sept. 2018),
- Watch the [PyParis talk](https://github.com/mwouts/jupytext_pyparis_2018/blob/master/README.md) (Nov. 2018),
- Read our article on [Jupytext and Papermill](https://medium.com/capital-fund-management/automated-reports-with-jupyter-notebooks-using-jupytext-and-papermill-619e60c37330) in _CFM Insights_ (Sept. 2019)
- See how you can edit [Jupyter Notebooks in VS Code or PyCharm](https://towardsdatascience.com/jupyter-notebooks-in-the-ide-visual-studio-code-versus-pycharm-5e72218eb3e8) with (or without!) Jupytext (Jan. 2020)
- or, try Jupytext online with [binder](https://mybinder.org/v2/gh/mwouts/jupytext/master?urlpath=lab/tree/demo/get_started.ipynb)!

## Want to contribute?

Contributions are welcome. Please let us know how you use `jupytext` and how we could improve it. You think the documentation could be improved? Go ahead! And stay tuned for more demos on [medium](https://medium.com/@marc.wouts) and [twitter](https://twitter.com/marcwouts)!
