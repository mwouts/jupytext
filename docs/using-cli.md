# Using Jupytext at the command line

## Command line conversion

The package provides a `jupytext` script for command line conversion between the various notebook extensions:

```bash
jupytext --to py notebook.ipynb                 # convert notebook.ipynb to a .py file
jupytext --to py:percent notebook.ipynb         # convert notebook.ipynb to a .py file in the double percent format
jupytext --to py:percent --opt comment_magics=false notebook.ipynb   # same as above + do not comment magic commands
jupytext --to markdown notebook.ipynb           # convert notebook.ipynb to a .md file
jupytext --output script.py notebook.ipynb      # convert notebook.ipynb to a script.py file

jupytext --to notebook notebook.py              # convert notebook.py to an .ipynb file with no outputs
jupytext --update --to notebook notebook.py     # update the input cells in the .ipynb file and preserve outputs and metadata

jupytext --to md --test notebook.ipynb          # Test round trip conversion

jupytext --to md --output - notebook.ipynb      # display the markdown version on screen
jupytext --from ipynb --to py:percent           # read ipynb from stdin and write double percent script on stdout
```

Jupytext has a `--sync` mode that updates all the paired representations of a notebook based on timestamps:
```bash
jupytext --set-formats ipynb,py notebook.ipynb  # Turn notebook.ipynb into a paired ipynb/py notebook
jupytext --sync notebook.ipynb                  # Update whichever of notebook.ipynb/notebook.py is outdated
```

For convenience, when creating a notebook from text you can execute it:
```bash
jupytext --set-kernel - notebook.md             # create a YAML header with kernel metadata matching the current python executable
jupytext --set-formats md:myst notebook.md      # create a YAML header with an explicit jupytext format
jupytext --to notebook --execute notebook.md    # convert notebook.md to an .ipynb file and run it
```

If you wanted to convert a collection of Markdown files to paired notebooks, and execute them in the current Python environment, you could run:
```bash
jupytext --set-formats ipynb,md --execute *.md
```

You may also find useful to `--pipe` the text representation of a notebook into tools like `black`:
```bash
jupytext --sync --pipe black notebook.ipynb    # read most recent version of notebook, reformat with black, save
```

To reorder the imports in your notebook, use
```bash
jupytext --pipe 'isort - --treat-comment-as-code "# %%" --float-to-top' notebook.ipynb
```
(remove the `--float-to-top` argument if you prefer to run `isort` per cell).

For programs that don't accept pipes, use `{}` as a placeholder for the name of a temporary file that will contain the text representation of the notebook. For instance, run `pytest` on your notebook with:
```bash
jupytext --check 'pytest {}' notebook.ipynb    # export the notebook in format py:percent in a temp file, run pytest
```
Read more about running `pytest` on notebooks in our example [`Tests in a notebook.md`](https://github.com/mwouts/jupytext/blob/master/demo/Tests%20in%20a%20notebook.md#).
Note also that on Windows you need to use double quotes instead of single quotes and type e.g. `jupytext --check "pytest {}" notebook.ipynb`.

Execute `jupytext --help` to access the full documentation.

## Notebook and cell metadata filters

If you want to preserve (or filter out) certain notebook or cell metadata, change the value of either `notebook_metadata_filter` or `cell_metadata_filter` with the `--update-metadata` option. For instance, if you wish to convert an `.ipynb` document to a `.md` file and preserve all the notebook metadata in that document, run

```bash
jupytext --to md --update-metadata '{"jupytext": {"notebook_metadata_filter":"all"}}' notebook.ipynb
```

Read more on the default and possible values for the metadata filters in [this section](config.html#metadata-filtering).

## Testing the round-trip conversion

Representing Jupyter notebooks as scripts requires a solid round trip conversion. You don't want your notebooks (nor your scripts) to be modified because you are converting them to the other form. Our test suite includes a few hundred tests to ensure that round trip conversion is safe.

You can easily test that the round trip conversion preserves your Jupyter notebooks and scripts. Run for instance:
```bash
# Test the ipynb -> py:percent -> ipynb round trip conversion
jupytext --test notebook.ipynb --to py:percent

# Test the ipynb -> (py:percent + ipynb) -> ipynb (à la paired notebook) conversion
jupytext --test --update notebook.ipynb --to py:percent
```

Note that `jupytext --test` compares the resulting notebooks according to its expectations. If you wish to proceed to a strict comparison of the two notebooks, use `jupytext --test-strict`, and use the flag `-x` to report with more details on the first difference, if any.

Please note that
- Scripts opened with Jupyter have a default [metadata filter](config.html#metadata-filtering) that prevents additional notebook or cell
metadata to be added back to the script. Remove the filter if you want to store Jupytext's settings, or the kernel information, in the text file.
- Cell metadata are available in the `light` and `percent` formats, as well as in the Markdown and R Markdown formats. R scripts in `spin` format support cell metadata for code cells only. Sphinx Gallery scripts in `sphinx` format do not support cell metadata.
- By default, a few cell metadata are not included in the text representation of the notebook. And only the most standard notebook metadata are exported. Learn more on this in the sections for [notebook specific](config.html#per-notebook-configuration) and [global settings](config.html#metadata-filtering) for metadata filtering.
