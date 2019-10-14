# Frequently Asked Questions

## What is Jupytext?

Jupytext is a Python package that provides _two-way_ conversion between Jupyter Notebooks and several other text-based formats like Markdown documents or scripts.

## Why would I want to convert my notebooks to text?

The text representation only contains the part of the notebook that you wrote (not the outputs). You get a cleaner diff history. Thanks to the _two-way_ conversion, you can also act on the text file and then propagate the changes to the original `.ipynb` file. Refactor your code or merge multiple contributions easily!

## How do I use Jupytext?

Open the notebook that you want to version control. _Pair_ the notebook to a script or a Markdown file using either the [Jupytext Menu](https://github.com/mwouts/jupytext/blob/master/README.md#jupytext-menu-in-jupyter-notebook) in Jupyter Notebook or the [Jupytext Commands](https://github.com/mwouts/jupytext/blob/master/README.md#jupytext-commands-in-jupyterlab) in JupyterLab.

Save the notebook, and you get two copies of the notebook: the original `*.ipynb` file, together with its paired text representation.

Read more about how to use Jupytext in the [documentation](using-server.md).

## Which Jupytext format do you recommend?

Notebooks that contain more text than code are best represented as Markdown documents. These are conveniently edited in IDEs and are also well rendered on GitHub.

Saving notebooks as scripts is an appropriate choice when you want to act on the code (refactor the code, import it in another script or notebook, etc). Use the `percent` format if you prefer to get explicit cell markers (compatible with VScode, PyCharm, Spyder, Hydrogen...). And if you prefer to get the minimal amount of cell markers, go for the `light` format.

## Can I see a sample of each format?

Go to [our demo folder](https://github.com/mwouts/jupytext/tree/master/demo) and see how our sample `World population` notebook is represented in each format.

## Can I edit the paired text file?

Yes! When you're done, reload the notebook in Jupyter. There, you will see the updated input cells combined with the matching output cells from the `.ipynb` file.

## Do I need to close my notebook in Jupyter?

No, you don't (*). You can edit the paired text file and simply refresh your navigator to reload the updated input cells. When you refresh the notebook, the kernel variables are preserved, so you can continue your work where you left it.

(*) Please read about Jupyter's autosave below.

## How do paired notebooks work?

The `.ipynb` file contains the full notebook. The paired text file only contains the input cells and selected metadata. When the notebook is loaded by Jupyter, input cells are loaded from the text file, while the output cells and the filtered metadata are restored using the `.ipynb` file. When the notebook is saved in Jupyter, the two files are updated to match the current content of the notebook.

## Can I create a notebook from a text file?

Certainly. Open your pre-existing scripts or Markdown files as notebooks with a click in Jupyter Notebook, and with the _Open as Notebook_ menu in JupyterLab.

The text formats do not store the output cells. If you want to preserve these when you refresh the notebook, be sure to pair the text file to an `.ipynb` file.

If you want to convert text formats to notebooks programmatically, use one of
```bash
jupytext --to ipynb *.md                        # convert all .md files to notebooks with no outputs
jupytext --to ipynb --execute *.md              # convert all .md files to notebooks and execute them
jupytext --set-formats ipynb,md --execute *.md  # convert all .md files to paired notebooks and execute them
```

## I want a specific cell to be commented out in the paired script

Mark a code cell with an `"active": "ipynb"` metadata or with an `active-ipynb` tag if you want it to be commented out in the paired script.

Mark a raw cell with an `"active": "py"` metadata or with an `active-py` tag if you want it to be inactive in the notebook but active in the script.

## Which files should I version control?

Unless you want to version the outputs, you should version *only the text representation*. The paired `.ipynb` file can safely be deleted. It will be recreated locally the next time you open the notebook (from the text file) and save it.

Note that if you version both the `.md` and `.ipynb` files, you can configure `git diff` to [ignore the diffs on the `.ipynb` files](https://github.com/mwouts/jupytext/issues/251).

## Jupyter warns me that the file has changed on disk

By default, Jupyter saves your notebook every 2 minutes. Fortunately, it is also aware that you have edited the text file, yielding this message. 

You should simply click on _Reload_.

Note you can deactivate Jupyter's autosave function with the Jupytext Menu in Jupyter Notebook, and with the _Autosave Document_ setting in JupyterLab. If you want to permanently deactivate autosave in Jupyter Notebook, it is [recommended by Jupyter](https://github.com/jupyter/notebook/blob/master/docs/source/examples/Notebook/JavaScript%20Notebook%20Extensions.ipynb) to do so via a *custom.js* file:

```sh
mkdir -p ~/.jupyter/custom
echo "Jupyter.notebook.set_autosave_interval(0);" >> ~/.jupyter/custom/custom.js
```

## When I reload, Jupyter warns me that my notebook has unsaved changes

Oh - you have edited both the notebook and the paired text file at the same time? If you know which version you want to keep, save it and reload the other. If you want to compare and merge both versions, backup the text file (with e.g. `git stash`), save the notebook, and merge the updated paired file with the backup (with e.g. `git stash pop`). Then, refresh the notebook in Jupyter.

If your IDE has the ability to compare the changes in memory versus on disk (like PyCharm), you can simply save the notebook and let your IDE do the merge.

## Jupyter complains that the `.ipynb` file is more recent than the text representation

This happens if you have edited the `.ipynb` file outside of Jupyter. It is a safeguard to avoid overwriting the input cells of the notebook with an outdated text file.

Manual action is requested as the paired text representation may be outdated. Please edit (`touch`) the paired `.md` or `.py` file if it is not outdated, or if it is, delete it, or update it with
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

## Can I re-write my git history to use text files instead of notebooks?

Indeed, you could substitute every `.ipynb` file in the project history with its Jupytext Markdown representation.

Technically this is available in just one command, which results in a complete rewrite of the history. Please experiment that in a branch, and think twice before pushing the result...
```bash
git filter-branch --tree-filter 'jupytext --to md */*.ipynb && rm -f */*.ipynb' HEAD
```

See the result and the cleaner diff history in the case of the [Python Data Science Handbook](https://github.com/mwouts/PythonDataScienceHandbook/tree/jupytext_no_ipynb).
