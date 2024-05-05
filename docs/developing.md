# Developing Jupytext

## How to test development versions from GitHub

If you want to test a feature that has been integrated in `main` but not delivered yet to `pip` or `conda`, use
```
HATCH_BUILD_HOOKS_ENABLE=true pip install git+https://github.com/mwouts/jupytext.git
```

The above requires `node`. You can install it with e.g.
```
conda install 'nodejs>=20' -c conda-forge
```

Alternatively you can build only Jupytext core (e.g. skip the JupyterLab extension). To do so, remove `HATCH_BUILD_HOOKS_ENABLE=true` in the above.

Finally, if you want to test a development branch, use
```
HATCH_BUILD_HOOKS_ENABLE=true pip install git+https://github.com/mwouts/jupytext.git@branch
```
where `branch` is the name of the branch you want to test.

## Install and develop Jupytext locally

Most of Jupytext's code is written in Python. To develop the Python part of Jupytext, you should clone Jupytext, then create a dedicated Python env:
```
conda env create --file environment.yml  # or conda env update --file ...
conda activate jupytext-dev
```

Install the `jupytext` package in development mode with
```
HATCH_BUILD_HOOKS_ENABLE=true pip install -e '.[dev]'
```

We use the [pre-commit](https://pre-commit.com) package to run pre-commit scripts like `black` and `ruff` on the code.
Install it with
```
pre-commit install
```

Tests are executed with `pytest`. You can run them in parallel with for instance
```
pytest -n 5
```

Some tests require a Jupyter kernel pointing to the current environment:
```
python -m ipykernel install --name jupytext-dev --user
```

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
