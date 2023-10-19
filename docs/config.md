# Jupytext's configuration file

Jupytext can use either `jupytext.toml` or `pyproject.toml` as its configuration file.

## Global pairing

To [pair](paired-notebooks.md) all the notebooks in the current folder and subfolders, all you need to do is to create a `jupytext.toml` file with this content:

```
# Pair ipynb notebooks to py:percent text notebooks
formats = "ipynb,py:percent"
```

With the above configuration, saving `notebook.ipynb` (or `notebook.py`) in Jupyter will have the effect to update both `notebook.ipynb` and `notebook.py` on disk.

You can use other text formats like `md`, `md:myst`, `Rmd` or `qmd`. The percent format is available for many languages. Use `auto:percent` to infer the file extension from the programmation language used in the notebook.

You can also configure Jupytext in a `pyproject.toml` config file rather than `jupytext.toml`. In that case, a sample configuration would be:
```
[tool.jupytext]
formats = "ipynb,py:percent"
```

## Pairing in subfolders

If you want to store your `.ipynb` notebooks in a `notebooks` folder, and their `.py` representation in a `scripts` folder, you can use this `jupytext.toml` configuration:
```
[formats]
"notebooks/" = "ipynb"
"scripts/" = "py:percent"
```

or this `pyproject.toml` configuration:
```
[tool.jupytext.formats]
"notebooks/" = "ipynb"
"scripts/" = "py:percent"
```

The `notebook/` prefix above is matched with the top-most parent folder of the matching name, not above the Jupytext configuration file.

## Global pairing vs individual pairing

Alternatively, notebooks can be paired individually using either the Jupytext commands in Jupyter Lab, or the command line interface:

```bash
jupytext --set-formats ipynb,py:percent notebook.ipynb
```

The individual pairing takes precedence over the global pairing. You can disable the global pairing for an individual notebook by setting formats to a single format:
```bash
jupytext --set-formats ipynb notebook.ipynb
```

Please note that, while Jupytext is Jupyter acts accordingly to both local or global Jupytext configuration files, the Jupyter commands in JupyterLab and the Jupytext menu in Jupyter only display the pairing information set in the notebooks itself and are not aware of the global configuration ([#177](https://github.com/mwouts/jupytext/issues/177)).

## Possible locations for the Jupytext configuration files

The Jupytext configuration file(s) should be either in the local or a parent directory, or in any directory listed in
```python
from jupytext.config import global_jupytext_configuration_directories
list(global_jupytext_configuration_directories())
```
which include `XDG_CONFIG_HOME` (defaults to `$HOME/.config`) and `XDG_CONFIG_DIR`.

The name for the configuration file can be any of `jupytext.config.JUPYTEXT_CONFIG_FILES`, i.e. `.jupytext` (in TOML),
`jupytext.toml`, `jupytext.yml`, `jupytext.yaml`, `jupytext.json` or `jupytext.py` (dot-files
like `.jupytext.toml` are accepted by the CLI version of Jupytext, but are not effective in Jupyter).

As mentionned above, you can also use your Python project's `pyproject.toml` file.

If you want to know, for a given directory, which configuration file is used by Jupytext, run this in a Python shell:
```python
from jupytext.config import find_jupytext_configuration_file
find_jupytext_configuration_file('.')
```

If you want to limit the search for a configuration file to a given parent directory, you can create an empty `.jupytext` configuration file in that directory. Alternatively, you can set the search boundaries with an environment variable `JUPYTEXT_CEILING_DIRECTORIES` - a colon-separated list of absolute paths.

If `JUPYTEXT_CEILING_DIRECTORIES` is defined, Jupytext will stop searching for configuration files when it meets one of these path. This can be helpful to avoid searching for configuration files on slow filesystems. It can also be useful if you don't want to use a global configuration - for instance, when running `pytest` on Jupytext, we use `JUPYTEXT_CEILING_DIRECTORIES="/tmp"`.
