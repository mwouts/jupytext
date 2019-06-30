# Frequently Asked Questions

## What is Jupytext?

Jupytext is a Python package that can convert Jupyter notebooks to scripts or Markdown documents. It can also convert these text documents back to Jupyter notebooks.

## Why would I want to convert my notebooks to text?

The text representation have much cleaner diffs than the original notebook format. Merging multiple contributions to a notebook in any of these text formats is easier than with the JSON format. Last but not least, acting on a notebook represented as text (spell check, reformat, ...) is sometimes more comfortable than in Jupyter.

## How do I use Jupytext?

Open the notebook you want to version control. _Pair_ the notebook to a script or a Markdown file using either the [Jupytext Menu](https://github.com/mwouts/jupytext/blob/master/README.md#jupytext-menu-in-jupyter-notebook) in Jupyter Notebook or the [Jupytext Commands](https://github.com/mwouts/jupytext/blob/master/README.md#jupytext-commands-in-jupyterlab) in JupyterLab.

Save the notebook, and you get two copies of the notebook: the original `*.ipynb` file, together with its paired text representation.

## Which Jupytext format do you recommend?

I tend to use the Markdown format for notebooks that contain more text than code, as Markdown documents are conveniently edited in IDEs and also well rendered on GitHub.

Saving notebooks as scripts is a convenient choice when you want to refactor your notebook in an IDE (or import it in another notebook, etc). Use the `percent` format if you prefer to get explicit cell markers (compatible with VScode, PyCharm, Spyder, Hydrogen...). If you prefer to get the minimal amount of cell markers, go for the `light` format.

## Can I see a sample of each format?

Go to [our demo folder](https://github.com/mwouts/jupytext/tree/master/demo) and see how our sample `World population` notebook is represented in each format.

## Can I edit the paired text file?

Yes! And when you're done, refresh the notebook in Jupyter. Refreshing will bring the latest changes to your notebook.

## How do paired notebooks work?

The `.ipynb` file contains the full notebook. The paired text file only contains the input cells and selected metadata. When the notebook is loaded by Jupyter, input cells are loaded from the text file, while the output cells and the filtered metadata are restored using the `.ipynb` file.

## Can I create a notebook from a text file?

Certainly. Open your pre-existing scripts or Markdown files as notebooks with a click in Jupyter Notebook, and with the _Open as Notebook_ menu in JupyterLab. Pair these document to an `.ipynb` file if you want to see the outputs preserved when you refresh the notebook.

If you prefer to do that programmatically, use one of
```bash
jupytext --to ipynb *.md                        # convert all .md files to notebooks with no outputs
jupytext --to ipynb --execute *.md              # convert all .md files to notebooks and execute them
jupytext --set-formats ipynb,md --execute *.md  # convert all .md files to paired notebooks and execute them
```

## Which files should I version control?

Unless you want to version control the output cells, you should version the text file only (and add `*.ipynb` to `.gitignore`). As discussed above, Jupyter will let you open the text representation as a notebook and will re-create the `.ipynb` file when you save the notebook.

Note that if you version control both the `.md` and `.ipynb` files, you can configure `git diff` to [ignore the diffs on the `.ipynb` files](https://github.com/mwouts/jupytext/issues/251).

## Jupyter warns me that the file has changed on disk

By default, Jupyter saves your notebook every 2 minutes. Fortunately, it is also aware that you have edited the text file.

You can deactivate the autosave in Jupyter with the Jupytext Menu in Jupyter Notebook, and with the _Autosave Document_ setting in JupyterLab. See [here](https://stackoverflow.com/questions/25631344/turn-off-autosave-in-ipython-notebook/56549758#56549758) if you want to permanently deactivate the autosave in Jupyter Notebook.

## When I refresh, Jupyter warns me that my notebook has unsaved changes

Oh - you have edited both the notebook and the paired text file at the same time? Backup the text file (`git stash`), save the notebook, and merge your changes on the text file (`git stash pop`). When you're done, refresh the notebook in Jupyter.

If your IDE has the ability to compare the changes in memory versus on disk (like PyCharm), you can simply save the notebook and let your IDE do the merge.

## Jupyter complains that the `.ipynb` file is more recent than the text representation

This happens if you have edited the `.ipynb` file outside of Jupyter. Manual action is requested as the paired text representation may be outdated. Please edit (`touch`) the paired `.md` or `.py` file if it is not outdated, or if it is, delete it, or update it with
```bash
jupytext --sync notebook.ipynb
```

## Can I use Jupytext with Jupyter Hub, Binder, Nteract, Colab, Saturn or Azure?

Jupytext is compatible with Jupyter Hub (execute `pip install jupytext --user` to install it in user mode) and with Binder (add `jupytext` to the project requirements and `jupyter lab build` to `postBuild`).

If you use another editor than Jupyter Notebook, Lab or Hub, you probably can't get Jupytext there. However you can still use Jupytext at the command line to manually sync the two representations of the notebook:

```bash
jupytext --set-formats ipynb,py:light notebook.ipynb   # Pair a notebook to a light script
jupytext --sync notebook.ipynb                         # Sync the two representations
```

## If only I had known of Jupytext before!

Do you feel like rewriting the history of your repository and replacing every `.ipynb` file with its Jupytext Markdown representation? Technically that's just a matter of executing:
```bash
git filter-branch --tree-filter 'jupytext --to md */*.ipynb && rm -f */*.ipynb' HEAD
```

See the outcome on the [Python Data Science Handbook](https://github.com/mwouts/PythonDataScienceHandbook/tree/jupytext_no_ipynb)...
