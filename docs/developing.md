# Developing Jupytext

## How to test development versions from GitHub

If you want to test a feature that has been integrated in `main` but not delivered yet to `pip` or `conda`, use
```
pip install git+https://github.com/mwouts/jupytext.git
```

If you want to test Jupytext in JupyterLab 3 then you will have to build the extension for JupyterLab. To do so, make sure that you have a recent version of `node`, and prefix the command above with `BUILD_JUPYTERLAB_EXTENSION=1`.

Finally, if you want to test a development branch, use
```
pip install git+https://github.com/mwouts/jupytext.git@branch
```
where `branch` is the name of the branch you want to test (again, prefix the command above with `BUILD_JUPYTERLAB_EXTENSION=1` if you want to use Jupytext within JupyterLab 3).

## Install and develop Jupytext locally

Most of Jupytext's code is written in Python. To develop the Python part of Jupytext, you should clone Jupytext, then create a dedicated Python env:
```
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
BUILD_JUPYTERLAB_EXTENSION=1 python setup.py sdist bdist_wheel
pip install dist/jupytext-x.x.x-py3-none-any.whl
```

or with
```
BUILD_JUPYTERLAB_EXTENSION=1 pip install .
```

Finally, note that you can remove `BUILD_JUPYTERLAB_EXTENSION=1` if you don't need the lab extension - the build time will be much shorter.

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
