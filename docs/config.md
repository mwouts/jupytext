# Configuration

## Per-notebook configuration

The pairing information for one or multiple notebooks can be set on the command line:
```
jupytext --set-formats ipynb,py [--sync] notebook.ipynb
```
You can pair a notebook to as many text representations as you want (see our _World population_ notebook in the demo folder). Format specifications are of the form
```
[[root_folder//][path/][prefix]/][suffix.]ext[:format_name]
```
where
- `ext` is one of `ipynb`, `md`, `Rmd`, `jl`, `py`, `R`, `sh`, `cpp`, `q`. Use the `auto` extension to have the script extension chosen according to the Jupyter kernel.
- `format_name` (optional) is either `light` (default for scripts), `nomarker`, `percent`, `hydrogen`, `sphinx` (Python only), `spin` (R only) &mdash; see the [format specifications](formats.md).
- `root_folder`, `path`, `prefix` and `suffix` allow to save the text representation to files with different names, or in different folders (see the [configuration files examples](config.html#configuring-paired-notebooks-globally)).

Jupytext accepts a few additional options. These options should be added to the `"jupytext"` section in the metadata &mdash; use either the metadata editor or the `--opt/--format-options` argument on the command line.
- `comment_magics`: By default, Jupyter magics are commented when notebooks are exported to any other format than markdown. If you prefer otherwise, use this boolean option, or its global counterpart (see below).
- `notebook_metadata_filter`: By default, Jupytext only exports the `kernelspec` and `jupytext` metadata to the text files. Set `"jupytext": {"notebook_metadata_filter": "-all"}` if you want that the script has no notebook metadata at all. The value for `notebook_metadata_filter` is a comma separated list of additional/excluded (negated) entries, with `all` a keyword that allows to exclude all entries. Use dots to filter recursively the metadata. For instance, use `notebook_metadata_filter="-jupytext.text_representation.jupytext_version"` to remove the `jupytext_version` field in the `jupytext.text_representation` metadata.
- `cell_metadata_filter`: By default, cell metadata `autoscroll`, `collapsed`, `scrolled`, `trusted` and `ExecuteTime` are not included in the text representation. Add or exclude more cell metadata with this option.

## Jupytext configuration file

### Possible locations and formats

Jupytext's contents manager, and the command line interface, can load some configuration options
from a configuration file.

The configuration file should be either in the local or a parent directory, or in any directory listed in
```python
from jupytext.config import global_jupytext_configuration_directories
list(global_jupytext_configuration_directories())
```
which include `XDG_CONFIG_HOME` (defaults to `$HOME/.config`) and `XDG_CONFIG_DIR`.

The name for the configuration file can be any of `jupytext.config.JUPYTEXT_CONFIG_FILES`, i.e. `.jupytext` (in TOML), `jupytext.toml`, `jupytext.yml`, `jupytext.yaml`, `jupytext.json` or `jupytext.py`, and their dot-file versions.

If you want to know, for a given directory, which configuration file Jupytext is using, please execute:
```python
from jupytext.config import find_jupytext_configuration_file
find_jupytext_configuration_file('.')
```

If you want to limit the search for a configuration file to a given parent directory, you can create an empty `.jupytext` configuration file in that directory. Alternatively, you can set the search boundaries with an environment variable `JUPYTEXT_CEILING_DIRECTORIES` - a colon-separated list of absolute paths.

If `JUPYTEXT_CEILING_DIRECTORIES` is defined, Jupytext will stop searching for configuration files when it meets one of these path. This can be helpful to avoid searching for configuration files on slow filesystems. It can also be useful if you don't want to use a global configuration - for instance, when running `pytest` on Jupytext, we use `JUPYTEXT_CEILING_DIRECTORIES="/tmp"`.

### Configuring paired notebooks globally

The examples below assume that you use a `.jupytext`, `jupytext.toml` or `.jupytext.toml` Jupyter configuration file in TOML format. If you use another extension, please adapt the examples. For instance, if you want to use `jupytext.yml` in YAML format, replace the `=` sign with `:` and remove the double quotes. See also [`test_config.py`](https://github.com/mwouts/jupytext/blob/master/tests/test_config.py) for short examples in all the supported formats.

Say you want to always associate every `.ipynb` notebook with a `.md` file  (and reciprocally). This is done by adding the following to your `jupytext.toml` or `.jupytext.toml` Jupyter configuration file:
```
# Always pair ipynb notebooks to md files
default_jupytext_formats = "ipynb,md"
```

If you prefer to use a default `ipynb` - `py:percent` pairing, then that would be:
```
# Always pair ipynb notebooks to py:percent files
default_jupytext_formats = "ipynb,py:percent"
```

You can pair notebooks in trees with a `root_prefix` separated with three slashes, e.g.
```
# Pair notebooks in subfolders of 'notebooks' to scripts in subfolders of 'scripts'
default_jupytext_formats = "notebooks///ipynb,scripts///py:percent"
```
The `root_prefix` is matched with the top-most parent folder of the matching name, not above the Jupytext configuration file.
A document is not considered a paired notebook when its path does not match the paired path specifications.


With only two slashes, notebooks are paired in directories but not in subfolders:
```
# Pair notebooks in folders named 'notebooks' to folders named 'scripts'
default_jupytext_formats = "notebooks//ipynb,scripts//py:percent"
```

To disable the default pairing for an individual notebook, set formats to a single format, with e.g.:
```bash
jupytext --set-formats ipynb notebook.ipynb
```

Please note that, while Jupytext is Jupyter acts accordingly to both local or global Jupytext configuration files, the Jupytext menu in Jupyter, and the Jupyter commands in JupyterLab, only display the pairing information set in the notebooks itself and are not aware of the global configuration ([#177](https://github.com/mwouts/jupytext/issues/177)).

### Metadata filtering

You can specify which metadata to include or exclude in the text files created by Jupytext by setting `default_notebook_metadata_filter` (notebook metadata) and `default_cell_metadata_filter` (cell metadata) in the configuration file. They accept a string of comma separated keywords. A minus sign `-` in front of a keyword means exclusion.

Suppose you want to keep all the notebook metadata but `widgets` and `varInspector` in the YAML header. For cell metadata, you want to allow `ExecuteTime` and `autoscroll`, but not `hide_output`. You can set
```python
default_notebook_metadata_filter = "all,-widgets,-varInspector"
default_cell_metadata_filter = "ExecuteTime,autoscroll,-hide_output"
```

If you want that the text files created by Jupytext have no metadata, you may use the global metadata filters below. Please note that with this setting, the metadata is only preserved in the `.ipynb` file.
```python
default_notebook_metadata_filter = "-all"
default_cell_metadata_filter = "-all"
```

It is possible to filter nested metadata. For example, if you want to preserve the Jupytext metadata, but not the Jupytext version number, you can use:
```python
default_notebook_metadata_filter = "-jupytext.text_representation.jupytext_version"
```

Finally, to hide the notebook metadata in an HTML comment in Markdown files, use the option `hide_notebook_metadata`.

### More options

There are a couple more options available - please have a look at the `JupytextConfiguration` class in [config.py](https://github.com/mwouts/jupytext/blob/master/jupytext/config.py).
