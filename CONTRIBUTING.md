# Contributing to Jupytext

Thanks for reading this. Contributions to this project are welcome.
And there are many ways you can contribute...

## Spread the word

You like Jupytext? Probably your friends and colleagues will like it too.
Show them what you've been able to do with: version control, collaboration on notebooks, refactoring of notebooks, notebooks integrated in library, notebook generated from Markdown documents...

By the way, we're also interested to know how you use Jupytext! There may well be applications we've not thought of!

## Improve the documentation

You think the documentation could be improved? You've spotted a typo, or you think you can rephrase a paragraph to make is easier to follow? Please follow the _Edit on Github_ link, edit the document, and submit a pull request.

## Report an issue

You have seen an issue with Jupytext, or you can't find your way in the [documentation](https://jupytext.readthedocs.io)?
Please let us know, and provide enough information so that we can reproduce the problem.

## Test the development version

If you want to test a feature that has been integrated in `master` but not delivered yet to `pip` or `conda`, use
```
pip install git+https://github.com/mwouts/jupytext.git
```

## Propose enhancements

You want to submit an enhancement on Jupytext? Unless this is a small change, we usually prefer that you let us know beforehand: open an issue that describe the problem you want to solve.

## Add support for another language

A pull request for which you do not need to contact us in advance is the addition of a new language to Jupytext. In principle that should be easy - you would only have to:
- document the language extension and comment by adding one line to `_SCRIPT_EXTENSIONS` in `languages.py`.
- add the language to `docs/languages.md`
- contribute a sample notebook in `tests/notebooks/ipynb_[language]`.
- run the tests suite (with just `pytest`). The mirror tests will generate various text representations corresponding to your notebook under  `tests/notebooks/mirror/`. Please verify that these files are valid scripts, and commit them.

# How to setup a development environment for Jupytext

## Jupytext as a Python package

Most of Jupytext's code is written in Python. To develop the Python part of Jupytext, you should clone Jupytext, then create a dedicated Python env:
```
cd jupytext
conda env create --file environment.yml  # or conda env update --file ...
conda activate jupytext-dev
python -m ipykernel install --name jupytext-dev --user
pip install -e .
```

We use the [pre-commit](https://pre-commit.com) package to run pre-commit scripts like `black` and `flake8` on the code.
Install it with
```
pre-commit install
```

Tests are executed with `pytest`. You can run them in parallel with for instance
```
pytest -n 5
```

We also have a `tox.ini` file available if you wish to test your contribution on multiple version of Python before making a PR - just run `tox`.

Build the `jupytext` package and install it with
```
python setup.py sdist bdist_wheel
pip install dist/jupytext-XXX.tar.gz
```

## Jupytext's extension for Jupyter Notebook

Our extension for Jupyter Notebook adds a Jupytext entry to Jupyter Notebook Menu. The code is found at `jupytext/nbextension/index.js`. Instructions to develop that extension are at `jupytext/nbextension/README.md`.

## Jupytext's extension for JupyterLab

Our extension for JupyterLab adds a series of Jupytext commands to JupyterLab. The code is in `packages/labextension`. See the `README.md` there for instructions on how to develop that extension.

## Jupytext's documentation

Install the documentation tools with
```
conda env create --file docs/environment.yml
conda activate jupytext-docs
cd docs
```
and build the HTML documentation locally with
```
rm -rf _build
make html
```
