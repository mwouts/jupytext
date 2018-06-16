"""Pre-save hook for jupyter

This hook maintains an up-to-date Rmd version of notebooks edited in jupyter.

To use it,
* create a jupyter config file (unless you have one already) with
```bash
jupyter notebook --generate-config
```
* edit the file and include
```python
from nbrmd import pre_save_hook
c.ContentsManager.pre_save_hook = pre_save_hook
```

Authors:

* Marc Wouts
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import nbrmd
from nbformat.notebooknode import from_dict

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------


def pre_save_hook(model, path, **kwargs):
    """
    A pre-save hook for jupyter that saves the notebooks cells (source only) as a Rmd file.

    :param model: data model, that may contain the notebook
    :param path: full name for ipython notebook
    :param kwargs: not used
    :return:
    """
    # only run on notebooks
    if model['type'] != 'notebook':
        return

    # only run on nbformat v4
    nb = model['content']
    if nb['nbformat'] != 4:
        return

    file, ipynb_ext = os.path.splitext(path)
    rmd_file = file + '.Rmd'

    nbrmd.writef(from_dict(nb), rmd_file)
