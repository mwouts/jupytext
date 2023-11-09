# Developing Jupytext

## How to test development versions from GitHub

If you want to test a feature that has been integrated in `main` but not delivered yet to `pip` or `conda`, use
```
pip install git+https://github.com/mwouts/jupytext.git
```

If you want only to build Jupytext core (e.g. not the JupyterLab extension) you can prefix the
above with `HATCH_BUILD_HOOKS_ENABLE=false`.

Finally, if you want to test a development branch, use
```
pip install git+https://github.com/mwouts/jupytext.git@branch
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
pip install '.[dev]'
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

Finally, you can build the package and install it with
```
pip install -U build wheel
python -m build
pip install dist/jupytext-x.x.x-py3-none-any.whl
```

Note that you can use `HATCH_BUILD_HOOKS_ENABLE=false` if you don't need the lab extension - the build time will be slightly shorter.

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
