# Sample Use Cases for Jupytext

## Writing notebooks as plain text

You like to work with scripts? The good news is that plain scripts, which you can draft and test in your favorite IDE, open transparently as notebooks in Jupyter when using Jupytext. Run the notebook in Jupyter to generate the outputs, [associate](paired-notebooks.md) an `.ipynb` representation, save and share your research as either a plain script or as a traditional Jupyter notebook with outputs.

## Collaborating on Jupyter Notebooks

With Jupytext, collaborating on Jupyter notebooks with Git becomes as easy as collaborating on text files.

The setup is straightforward:
- Open your favorite notebook in Jupyter notebook
- [Associate](paired-notebooks.md) a `.py` representation (for instance) to that notebook
- Save the notebook, and put the Python script under Git control. Sharing the `.ipynb` file is possible, but not required.

Collaborating then works as follows:
- Your collaborator pulls your script.
- The script opens as a notebook in Jupyter, with no outputs (in JupyterLab right-click the script and use the open-with context menu).
- They run the notebook and save it. Outputs are regenerated, and a local `.ipynb` file is created.
- Note that, alternatively, the `.ipynb` file could have been regenerated with `jupytext --sync notebook.py`.
- They change the notebook, and push their updated script. The diff is nothing else than a standard diff on a Python script.
- You pull the changed script, and refresh your browser. Input cells are updated. The outputs from cells that were changed are removed. Your variables are untouched, so you have the option to run only the modified cells to get the new outputs.

## Code refactoring

In the animation below we propose a quick demo of Jupytext. While the example remains simple, it shows how your favorite text editor or IDE can be used to edit your Jupyter notebooks. IDEs are more convenient than Jupyter for navigating through code, editing and executing cells or fractions of cells, and debugging.

- We start with a Jupyter notebook.
- The notebook includes a plot of the world population. The plot legend is not in order of decreasing population, we'll fix this.
- We want the notebook to be saved as both a `.ipynb` and a `.py` file: we select _Pair Notebook with a light Script_ in either the [Jupytext menu](install.html#jupytext-menu-in-jupyter-notebook) in Jupyter Notebook, or in the [Jupytext commands](install.html#jupytext-commands-in-jupyterlab) in JupyterLab. This has the effect of adding a `"jupytext": {"formats": "ipynb,py:light"},` entry to the notebook metadata.
- The Python script can be opened with PyCharm:
  - Navigating in the code and documentation is easier than in Jupyter.
  - The console is convenient for quick tests. We don't need to create cells for this.
  - We find out that the columns of the data frame were not in the correct order. We update the corresponding cell, and get the correct plot.
- The Jupyter notebook is refreshed in the browser. Modified inputs are loaded from the Python script. Outputs and variables are preserved. We finally rerun the code and get the correct plot.

![](https://github.com/mwouts/jupytext-screenshots/raw/master/IntroducingJupytext/JupyterPyCharm.gif)

## Importing Jupyter Notebooks as modules

Jupytext allows to import code from other Jupyter notebooks in a very simple manner. Indeed, all you need to do is to pair the notebook that you wish to import with a script, and import the resulting script.

If the notebook contains demos and plots that you don't want to import, mark those cells as either
- _active_ only in the `ipynb` format, with the `{"active": "ipynb"}` cell metadata, or with an `active-ipynb` tag (you may use the [jupyterlab-celltags](https://github.com/jupyterlab/jupyterlab-celltags) extension for this). Use a `{"active": "ipynb,py"}` metadata or a an `active-ipynb-py` tag if you want the cell to be active only in the `ipynb` and `py` formats, but not in the R Markdown format.
- _frozen_, using the [freeze extension](https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/freeze/readme.html) for Jupyter notebook.
